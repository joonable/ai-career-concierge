from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol

from pydantic import ValidationError

from agent.prompts.prompt_manager import PromptManager, RenderedPrompt
from agent.schemas.evaluation_result import LLMEvaluationResult
from common.errors import ProviderRequestError, ProviderResponseParseError


class LLMEvaluator(Protocol):
    async def evaluate(
        self,
        *,
        job,
        prompt: str,
        user_context: Dict[str, Any],
        recent_memory: str,
        prompt_metadata: Optional[Dict[str, Any]] = None,
        evaluation_id: Optional[str] = None,
    ) -> Dict[str, Any]: ...


@dataclass(frozen=True)
class EvaluationExecutionResult:
    result: LLMEvaluationResult
    rendered_prompt: RenderedPrompt
    provider_metadata: Dict[str, Any]
    raw_response_text: Optional[str]


async def evaluate_job(
    *,
    evaluator: LLMEvaluator,
    prompt_manager: PromptManager,
    tracer: Any,
    user_context: Dict[str, Any],
    recent_memory: str,
    job,
    evaluation_id: str,
) -> EvaluationExecutionResult:
    """
    단일 채용 공고(PipelineJob)에 대해 실제로 LLM 평가를 구동하는 핵심 서비스(Service) 레이어입니다.
    (LLMEvalNode 내에서 주로 호출됩니다.)

    핵심 흐름:
    1. PromptManager: 사용자 프로필, 결격 사유, 단기 기억(최근 피드백)을 조합해 실제 전송할 프롬프트를 렌더링합니다.
    2. Telemetry (Tracer): LangSmith 같은 옵저버빌리티 도구에 입출력 데이터, 프롬프트 버전, 실행 시간 등을 로깅합니다.
    3. LLM API Call: Gemini 모델을 호출해 구조화된 JSON(fit_score, reasoning 등) 응답을 받아옵니다.
    4. Validation & Parsing: 결과를 LLMEvaluationResult Pydantic 스키마로 검증하고 반환합니다.
    """
    rendered_prompt = prompt_manager.render_evaluation_prompt(
        user_context=user_context,
        recent_memory=recent_memory,
        job=job,
    )
    trace_inputs = _build_trace_inputs(
        user_context=user_context,
        recent_memory=recent_memory,
        job=job,
        rendered_prompt=rendered_prompt.text,
    )
    trace_metadata = {
        "evaluation_id": evaluation_id,
        "job_id": str(job.job_id),
        "external_job_id": job.external_job_id,
        "platform": job.platform,
        "title": job.title,
        "job_company": job.company,
        "prompt_name": rendered_prompt.metadata.prompt_name,
        "prompt_version": rendered_prompt.metadata.prompt_version,
        "prompt_variant": rendered_prompt.metadata.prompt_variant,
        "schema_version": rendered_prompt.metadata.schema_version,
        "prompt_source": rendered_prompt.metadata.source,
        "prompt_identifier": rendered_prompt.metadata.prompt_identifier,
        "requested_prompt_identifier": rendered_prompt.metadata.requested_prompt_identifier,
        "prompt_reference": rendered_prompt.metadata.prompt_reference,
        "prompt_tag": rendered_prompt.metadata.prompt_tag,
        "prompt_commit_hash": rendered_prompt.metadata.prompt_commit_hash,
        "prompt_owner": rendered_prompt.metadata.prompt_owner,
        "prompt_repo": rendered_prompt.metadata.prompt_repo,
    }
    evaluator_model = getattr(evaluator, "model", "unknown")
    prompt_tag = rendered_prompt.metadata.prompt_tag or rendered_prompt.metadata.prompt_version

    with tracer.llm_run(
        name="gemini.evaluate",
        inputs=trace_inputs,
        metadata=trace_metadata,
        tags=[
            "pipeline_eval",
            f"platform:{job.platform}",
            f"prompt:{rendered_prompt.metadata.prompt_name}",
            f"prompt_version:{rendered_prompt.metadata.prompt_version}",
            f"model:{evaluator_model}",
            f"prompt_source:{rendered_prompt.metadata.source}",
            f"prompt_tag:{prompt_tag}",
        ],
    ) as llm_trace:
        try:
            payload = await evaluator.evaluate(
                job=job,
                prompt=rendered_prompt.text,
                user_context=user_context,
                recent_memory=recent_memory,
                prompt_metadata=rendered_prompt.metadata.__dict__,
                evaluation_id=evaluation_id,
            )
            provider_metadata = payload.pop("_provider_metadata", {}) if isinstance(payload, dict) else {}
            raw_response_text = payload.pop("_raw_response_text", None) if isinstance(payload, dict) else None
            llm_trace.add_metadata(provider_metadata)

            result = LLMEvaluationResult.model_validate(
                {
                    "evaluation_id": evaluation_id,
                    "job_id": job.job_id,
                    "platform": job.platform,
                    "title": job.title,
                    "company": job.company,
                    "url": job.url,
                    **payload,
                }
            )
            llm_trace.set_outputs(
                {
                    "fit_score": result.fit_score,
                    "reasoning": result.reasoning,
                    "summary": result.summary,
                    "strengths": result.strengths,
                    "concerns": result.concerns,
                    "must_have_matches": result.must_have_matches,
                    "deal_breaker_flags": result.deal_breaker_flags,
                    "confidence": result.confidence,
                    "role_alignment": result.role_alignment,
                    "must_have_coverage": result.must_have_coverage,
                    "deal_breaker_severity": result.deal_breaker_severity,
                    "transferable_skills": result.transferable_skills,
                    "must_have_hits": result.must_have_hits,
                    "deal_breakers_found": result.deal_breakers_found,
                    "parsed_payload": payload,
                    "raw_response_text": raw_response_text,
                }
            )
            return EvaluationExecutionResult(
                result=result,
                rendered_prompt=rendered_prompt,
                provider_metadata=provider_metadata,
                raw_response_text=raw_response_text,
            )
        except ProviderRequestError:
            llm_trace.add_metadata({"failure_stage": "provider_request"})
            raise
        except ProviderResponseParseError:
            llm_trace.add_metadata({"failure_stage": "json_parse"})
            raise
        except ValidationError:
            llm_trace.add_metadata({"failure_stage": "schema_validate"})
            raise
        except Exception:
            llm_trace.add_metadata({"failure_stage": "unknown"})
            raise


def _build_trace_inputs(
    *,
    user_context: Dict[str, Any],
    recent_memory: str,
    job,
    rendered_prompt: str,
) -> Dict[str, Any]:
    profile_data = user_context.get("profile_data", {})
    notification_settings = user_context.get("notification_settings", {})
    return {
        "rendered_prompt": rendered_prompt,
        "job": {
            "job_id": str(job.job_id),
            "external_job_id": job.external_job_id,
            "platform": job.platform,
            "title": job.title,
            "company": job.company,
            "url": job.url,
        },
        "user_context": {
            "user_id": str(user_context.get("user_id", "")),
            "role": profile_data.get("role", ""),
            "years_of_experience": profile_data.get("years_of_experience"),
            "minimum_fit_score": notification_settings.get("minimum_fit_score"),
        },
        "recent_memory": recent_memory,
    }
