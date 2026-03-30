from __future__ import annotations

from contextlib import contextmanager
from uuid import uuid4

import pytest

from agent.evaluation_service import evaluate_job
from agent.prompts.prompt_manager import PromptManager
from agent.schemas.pipeline_job import PipelineJob


class FakePrompt:
    metadata = {
        "lc_hub_owner": "personal",
        "lc_hub_repo": "job-evaluation",
        "lc_hub_commit_hash": "commit-123",
    }

    def invoke(self, variables):
        class Value:
            def __init__(self, value: str) -> None:
                self.value = value

            def to_string(self) -> str:
                return self.value

        return Value(f"Hub prompt for {variables['job_title']}")


class FakeClient:
    def pull_prompt(self, identifier: str):
        assert identifier == "job-evaluation:staging"
        return FakePrompt()


class FakeEvaluator:
    model = "gemini-2.5-flash-lite"

    async def evaluate(self, **kwargs):
        del kwargs
        return {
            "fit_score": 91,
            "reasoning": "Strong fit\nMatches must-haves",
            "must_have_hits": ["Python"],
            "deal_breakers_found": [],
            "_provider_metadata": {"model": self.model, "latency_ms": 25},
            "_raw_response_text": '{"fit_score": 91}',
        }


class FakeTraceHandle:
    def __init__(self) -> None:
        self.outputs = None
        self.metadata = {}

    def add_metadata(self, metadata):
        self.metadata.update(metadata)

    def set_outputs(self, outputs):
        self.outputs = outputs


class FakeTracer:
    def __init__(self) -> None:
        self.calls = []

    @contextmanager
    def llm_run(self, *, name, inputs, metadata, tags):
        self.calls.append(
            {
                "name": name,
                "inputs": inputs,
                "metadata": metadata,
                "tags": tags,
            }
        )
        yield FakeTraceHandle()


@pytest.mark.asyncio
async def test_evaluate_job_records_prompt_tag_and_commit_hash():
    prompt_manager = PromptManager(
        client=FakeClient(),
        eval_prompt_identifier="job-evaluation:staging",
        eval_prompt_name="job-evaluation",
        eval_prompt_version="local-v1",
        eval_prompt_variant="default",
        memory_prompt_identifier="memory-summary:staging",
        memory_prompt_name="memory-summary",
        memory_prompt_version="local-v1",
        memory_prompt_variant="default",
    )
    tracer = FakeTracer()
    job = PipelineJob(
        job_id=uuid4(),
        platform="linkedin",
        external_job_id="job-1",
        title="Senior Machine Learning Engineer",
        company="Signal Labs",
        jd_raw_text="Build production ML systems.",
        url="https://example.com/jobs/job-1",
    )

    execution = await evaluate_job(
        evaluator=FakeEvaluator(),
        prompt_manager=prompt_manager,
        tracer=tracer,
        user_context={
            "user_id": str(uuid4()),
            "profile_data": {"role": "Machine Learning Engineer", "years_of_experience": 7},
            "guidelines": {"must_haves": ["Python"], "deal_breakers": []},
            "notification_settings": {"minimum_fit_score": 85},
        },
        recent_memory="Avoid weak infra roles.",
        job=job,
        evaluation_id=str(uuid4()),
    )

    trace_call = tracer.calls[0]
    assert execution.rendered_prompt.metadata.prompt_tag == "staging"
    assert execution.rendered_prompt.metadata.prompt_commit_hash == "commit-123"
    assert trace_call["metadata"]["prompt_identifier"] == "job-evaluation:staging"
    assert trace_call["metadata"]["prompt_tag"] == "staging"
    assert trace_call["metadata"]["prompt_commit_hash"] == "commit-123"
    assert "prompt_tag:staging" in trace_call["tags"]
    assert trace_call["inputs"]["rendered_prompt"] == "Hub prompt for Senior Machine Learning Engineer"
