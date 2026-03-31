import asyncio
import json
import os
from datetime import datetime
from pathlib import Path
from uuid import uuid4

from langsmith import Client
from langsmith.evaluation import aevaluate

from agent.evaluation_service import evaluate_job
from agent.evals.dataset_workflow import ensure_dataset, load_curated_examples, sync_examples
from agent.evals.rule_based_evaluators import RULE_BASED_EVALUATORS
from agent.prompts import PromptManager
from agent.schemas.pipeline_job import PipelineJob
from api.services.gemini_evaluator import GeminiEvaluator
from common.config import get_settings
from common.telemetry import LangSmithTracer

# 설정 및 경로
DEFAULT_FIXTURE_PATH = Path("src/agent/evals/fixtures/job_eval_gold.json")
ITERATIONS_DIR = Path("docs/promptops/iterations")

async def run_iteration(iteration_id: str, description: str = "Prompt optimization iteration"):
    settings = get_settings()
    client = Client(api_key=settings.langsmith_api_key)
    tracer = LangSmithTracer.from_settings(settings)
    prompt_manager = PromptManager.from_settings(settings, client=client)
    evaluator = GeminiEvaluator(api_key=settings.gemini_api_key, model=settings.gemini_model)
    
    dataset_name = settings.langsmith_eval_dataset_name
    experiment_prefix = f"iter-{iteration_id}"
    
    print(f"🚀 Starting Iteration {iteration_id}...")
    
    # 1. Sync Dataset
    try:
        print(f"📦 Syncing dataset '{dataset_name}' from {DEFAULT_FIXTURE_PATH}...")
        examples = load_curated_examples(str(DEFAULT_FIXTURE_PATH))
        ensure_dataset(client, dataset_name=dataset_name, description="Curated gold set for job evaluation experiments.")
        sync_examples(client, dataset_name=dataset_name, examples=examples)
    except Exception as e:
        print(f"⚠️ Dataset sync failed, but continuing: {e}")
        examples = [] # list_runs will still work if experiment was created
    
    # 2. Run Experiment
    print(f"🧪 Running experiment...")
    
    async def target(inputs):
        job = PipelineJob.model_validate(inputs["job"])
        execution = await evaluate_job(
            evaluator=evaluator,
            prompt_manager=prompt_manager,
            tracer=tracer,
            user_context=inputs["user_context"],
            recent_memory=inputs.get("recent_memory", ""),
            job=job,
            evaluation_id=str(uuid4()),
        )
        payload = execution.result.model_dump()
        payload["prompt_metadata"] = execution.rendered_prompt.metadata.__dict__
        return payload

    experiment_results = None
    try:
        experiment_results = await aevaluate(
            target,
            data=dataset_name,
            evaluators=RULE_BASED_EVALUATORS,
            experiment_prefix=experiment_prefix,
            description=description,
            client=client,
            blocking=True,
            max_concurrency=2,
        )
    except Exception as e:
        print(f"⚠️ Experiment run encountered errors (possibly API 503), will attempt to report partial results: {e}")
    
    # 3. Generate Report
    print(f"📝 Generating markdown report...")
    # Find the most recent experiment matching prefix if results is None
    project_name = getattr(experiment_results, "experiment_name", None)
    if not project_name:
        projects = list(client.list_projects(reference_dataset_name=dataset_name))
        matching = [p for p in projects if p.name.startswith(experiment_prefix)]
        if matching:
            # Sort by creation time desc
            matching.sort(key=lambda x: x.start_time, reverse=True)
            project_name = matching[0].name

    if project_name:
        report_path = await generate_markdown_report(iteration_id, description, project_name, client)
        print(f"\n✅ Iteration {iteration_id} Complete!")
        print(f"📄 Report saved to: {report_path}")
    else:
        print("❌ Could not find an experiment to report on.")

async def generate_markdown_report(iteration_id: str, description: str, project_name: str, client: Client):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_file = ITERATIONS_DIR / f"iteration_{iteration_id}.md"
    
    # Get detailed results for reporting
    runs = list(client.list_runs(project_name=project_name, execution_order=1))
    
    total_cases = len(runs)
    passed_cases = 0
    failure_details = []

    for run in runs:
        # Check feedback/scores
        feedbacks = list(client.list_feedback(run_ids=[run.id]))
        all_passed = all(f.score == 1 for f in feedbacks if f.score is not None)
        
        # Safe access to outputs
        outputs = run.outputs or {}
        
        if all_passed and outputs:
            passed_cases += 1
        else:
            scenario = ((run.extra or {}).get("metadata") or {}).get("scenario_type", "Unknown")
            failed_rules = [f"{f.key}: {f.comment}" for f in feedbacks if f.score == 0]
            failure_details.append({
                "run_id": str(run.id),
                "scenario": scenario,
                "input_title": run.inputs.get("job", {}).get("title") if run.inputs else "Unknown",
                "failed_rules": failed_rules,
                "reasoning": outputs.get("summary") or "N/A (Run Failed/Incomplete)"
            })

    pass_rate = (passed_cases / total_cases * 100) if total_cases > 0 else 0
    
    content = f"""# Iteration {iteration_id} Report
- **Date:** {timestamp}
- **Description:** {description}
- **Pass Rate:** {pass_rate:.1f}% ({passed_cases}/{total_cases})
- **LangSmith Project:** {project_name}

## Summary
{"모든 테스트를 통과했습니다!" if pass_rate == 100 else f"{total_cases - passed_cases}개의 케이스에서 실패가 발생했습니다. 아래 상세 내용을 확인하세요."}

## Failure Analysis (Annotation Queue Candidate)
| Scenario | Job Title | Failed Rules | Reasoning Snippet |
| :--- | :--- | :--- | :--- |
"""
    for fail in failure_details:
        rules_str = "<br>".join(fail["failed_rules"])
        content += f"| {fail['scenario']} | {fail['input_title']} | {rules_str} | {fail['reasoning'][:100]}... |\n"

    content += """
## Action Items
- [ ] 실패한 케이스에 대해 프롬프트 가이드라인 보완
- [ ] LangSmith Annotation Queue에서 정답(Ground Truth) 재검토
"""

    ITERATIONS_DIR.mkdir(parents=True, exist_ok=True)
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(content)
        
    return report_file

if __name__ == "__main__":
    import sys
    iter_id = sys.argv[1] if len(sys.argv) > 1 else datetime.now().strftime("%H%M%S")
    asyncio.run(run_iteration(iter_id, "Automated iteration run"))
