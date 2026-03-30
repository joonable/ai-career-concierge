from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from langchain_core.prompts import PromptTemplate

from agent.schemas.pipeline_job import PipelineJob
from common.errors import PromptLoadError

PROMPT_SCHEMA_VERSION = "2"

EVALUATION_PROMPT_TEMPLATE = """당신은 한 명의 사용자를 기준으로 채용 공고 적합도를 평가하는 심사자입니다.
재현율보다 정밀도를 우선하고, 애매하면 보수적으로 판단하세요.
목표 직무: {role}
경력 연차: {years_of_experience}
필수 조건: {must_haves}
결격 사유: {deal_breakers}
최근 싫어요 메모: {recent_memory}
채용 공고 제목: {job_title}
회사명: {company}
채용 공고 설명: {job_description}
반드시 아래 키만 가진 유효한 JSON 객체만 반환하세요:
{{
  "fit_score": 1부터 100 사이의 정수,
  "summary": 2~3줄 이내의 짧은 문자열,
  "strengths": 핵심 강점 문자열 배열,
  "concerns": 우려 포인트 문자열 배열,
  "must_have_matches": 충족한 필수 조건 문자열 배열,
  "deal_breaker_flags": 감지된 결격 사유 문자열 배열,
  "confidence": "HIGH", "MEDIUM", "LOW" 중 하나
}}
마크다운 코드펜스나 추가 설명은 절대 포함하지 마세요."""

MEMORY_SUMMARY_PROMPT_TEMPLATE = (
    "최근 싫어요 사유와 유사한 공고는 피하세요: {joined_reasons}."
)


@dataclass(frozen=True)
class PromptMetadata:
    prompt_name: str
    prompt_version: str
    prompt_variant: str
    schema_version: str
    prompt_identifier: str = ""
    requested_prompt_identifier: str = ""
    prompt_reference: str = ""
    prompt_tag: str = ""
    prompt_commit_hash: str = ""
    prompt_owner: str = ""
    prompt_repo: str = ""
    source: str = "local"


@dataclass(frozen=True)
class RenderedPrompt:
    text: str
    metadata: PromptMetadata


class PromptManager:
    def __init__(
        self,
        *,
        client: Optional[Any],
        eval_prompt_identifier: str,
        eval_prompt_name: str,
        eval_prompt_version: str,
        eval_prompt_variant: str,
        memory_prompt_identifier: str,
        memory_prompt_name: str,
        memory_prompt_version: str,
        memory_prompt_variant: str,
    ) -> None:
        self.client = client
        self.eval_prompt_identifier = eval_prompt_identifier
        self.eval_prompt_name = eval_prompt_name
        self.eval_prompt_version = eval_prompt_version
        self.eval_prompt_variant = eval_prompt_variant
        self.memory_prompt_identifier = memory_prompt_identifier
        self.memory_prompt_name = memory_prompt_name
        self.memory_prompt_version = memory_prompt_version
        self.memory_prompt_variant = memory_prompt_variant
        self._fallback_eval_prompt = PromptTemplate.from_template(EVALUATION_PROMPT_TEMPLATE)
        self._fallback_memory_prompt = PromptTemplate.from_template(MEMORY_SUMMARY_PROMPT_TEMPLATE)

    @classmethod
    def from_settings(cls, settings: Any, *, client: Optional[Any] = None) -> "PromptManager":
        return cls(
            client=client,
            eval_prompt_identifier=settings.langsmith_eval_prompt_identifier,
            eval_prompt_name=settings.langsmith_eval_prompt_name,
            eval_prompt_version=settings.langsmith_eval_prompt_version,
            eval_prompt_variant=settings.langsmith_eval_prompt_variant,
            memory_prompt_identifier=settings.langsmith_memory_prompt_identifier,
            memory_prompt_name=settings.langsmith_memory_prompt_name,
            memory_prompt_version=settings.langsmith_memory_prompt_version,
            memory_prompt_variant=settings.langsmith_memory_prompt_variant,
        )

    def render_evaluation_prompt(
        self,
        *,
        user_context: Dict[str, Any],
        recent_memory: str,
        job: PipelineJob,
    ) -> RenderedPrompt:
        variables = {
            "role": user_context.get("profile_data", {}).get("role", "unknown"),
            "years_of_experience": user_context.get("profile_data", {}).get(
                "years_of_experience", "unknown"
            ),
            "must_haves": ", ".join(user_context.get("guidelines", {}).get("must_haves", []))
            or "None provided",
            "deal_breakers": ", ".join(user_context.get("guidelines", {}).get("deal_breakers", []))
            or "None provided",
            "recent_memory": recent_memory or "No recent dislike memory.",
            "job_title": job.title,
            "company": job.company,
            "job_description": job.jd_raw_text,
        }
        return self._render_prompt(
            identifier=self.eval_prompt_identifier,
            fallback_prompt=self._fallback_eval_prompt,
            variables=variables,
            metadata=PromptMetadata(
                prompt_name=self.eval_prompt_name,
                prompt_version=self.eval_prompt_version,
                prompt_variant=self.eval_prompt_variant,
                schema_version=PROMPT_SCHEMA_VERSION,
                prompt_identifier=self.eval_prompt_identifier,
            ),
        )

    def render_memory_summary(self, dislike_reasons: Iterable[str]) -> RenderedPrompt:
        cleaned = [reason.strip() for reason in dislike_reasons if reason and reason.strip()]
        if not cleaned:
            return RenderedPrompt(
                text="",
                metadata=PromptMetadata(
                    prompt_name=self.memory_prompt_name,
                    prompt_version=self.memory_prompt_version,
                    prompt_variant=self.memory_prompt_variant,
                    schema_version=PROMPT_SCHEMA_VERSION,
                    prompt_identifier=self.memory_prompt_identifier,
                    source="local",
                ),
            )

        joined_reasons = "; ".join(list(dict.fromkeys(cleaned))[:10])
        return self._render_prompt(
            identifier=self.memory_prompt_identifier,
            fallback_prompt=self._fallback_memory_prompt,
            variables={"joined_reasons": joined_reasons},
            metadata=PromptMetadata(
                prompt_name=self.memory_prompt_name,
                prompt_version=self.memory_prompt_version,
                prompt_variant=self.memory_prompt_variant,
                schema_version=PROMPT_SCHEMA_VERSION,
                prompt_identifier=self.memory_prompt_identifier,
            ),
        )

    def _render_prompt(
        self,
        *,
        identifier: str,
        fallback_prompt: PromptTemplate,
        variables: Dict[str, Any],
        metadata: PromptMetadata,
    ) -> RenderedPrompt:
        local_metadata = PromptMetadata(
            prompt_name=metadata.prompt_name,
            prompt_version=metadata.prompt_version,
            prompt_variant=metadata.prompt_variant,
            schema_version=metadata.schema_version,
            prompt_identifier="",
            requested_prompt_identifier=identifier,
            prompt_reference=self._resolve_identifier_reference(identifier),
            source="local",
        )
        if self.client is None or not identifier:
            return RenderedPrompt(
                text=fallback_prompt.invoke(variables).to_string(),
                metadata=local_metadata,
            )

        try:
            pulled_prompt = self.client.pull_prompt(identifier)
            rendered = pulled_prompt.invoke(variables).to_string()
            hub_metadata = getattr(pulled_prompt, "metadata", {}) or {}
            commit_hash = str(hub_metadata.get("lc_hub_commit_hash", "") or "")
            prompt_reference = self._resolve_identifier_reference(identifier)
            prompt_tag = prompt_reference if prompt_reference and prompt_reference != commit_hash else ""
            version = prompt_tag or commit_hash or metadata.prompt_version
            return RenderedPrompt(
                text=rendered,
                metadata=PromptMetadata(
                    prompt_name=metadata.prompt_name,
                    prompt_version=version,
                    prompt_variant=metadata.prompt_variant,
                    schema_version=metadata.schema_version,
                    prompt_identifier=identifier,
                    requested_prompt_identifier=identifier,
                    prompt_reference=prompt_reference or commit_hash,
                    prompt_tag=prompt_tag,
                    prompt_commit_hash=commit_hash,
                    prompt_owner=str(hub_metadata.get("lc_hub_owner", "") or ""),
                    prompt_repo=str(hub_metadata.get("lc_hub_repo", "") or ""),
                    source="langsmith",
                ),
            )
        except Exception:
            return RenderedPrompt(
                text=fallback_prompt.invoke(variables).to_string(),
                metadata=local_metadata,
            )

    @staticmethod
    def _resolve_identifier_reference(identifier: str) -> str:
        if ":" not in identifier:
            return ""
        return identifier.split(":", 1)[1].strip()


def build_evaluation_prompt(
    user_context: Dict[str, Any],
    recent_memory: str,
    job: PipelineJob,
) -> str:
    manager = PromptManager(
        client=None,
        eval_prompt_identifier="",
        eval_prompt_name="job-evaluation",
        eval_prompt_version="local-v1",
        eval_prompt_variant="default",
        memory_prompt_identifier="",
        memory_prompt_name="memory-summary",
        memory_prompt_version="local-v1",
        memory_prompt_variant="default",
    )
    return manager.render_evaluation_prompt(
        user_context=user_context,
        recent_memory=recent_memory,
        job=job,
    ).text


def ensure_prompt_rendered(rendered_prompt: Optional[RenderedPrompt]) -> RenderedPrompt:
    if rendered_prompt is None:
        raise PromptLoadError("Prompt rendering returned no result.")
    return rendered_prompt
