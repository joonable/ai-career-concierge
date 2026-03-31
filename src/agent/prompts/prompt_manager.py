from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from langchain_core.prompts import PromptTemplate

from agent.schemas.pipeline_job import PipelineJob
from common.errors import PromptLoadError

PROMPT_SCHEMA_VERSION = "3"

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
평가 원칙:
- `fit_score`는 단순 호감 점수가 아니라 실제 추천 운영 점수입니다.
- `80~100`: 강한 추천. 역할 정렬이 높고, 핵심 must-have 대부분이 충족되며, 뚜렷한 deal-breaker가 없어야 합니다.
- `60~79`: 검토 가능. 관련성은 높지만 일부 must-have 공백, 소유권 불명확성, 역할 경계가 남아 있는 경우입니다.
- `40~59`: 인접 직무 또는 전환 가능성. 직접적인 타깃 역할은 아니지만 transferable skill이 분명하고 탐색 가치는 있는 경우입니다.
- `1~39`: 비추천. 핵심 역할 불일치가 크거나, must-have 결손이 심하거나, 추천을 보수적으로 막아야 할 사유가 있는 경우입니다.
인접 직무 판단 규칙:
- 직무명이 달라도 실제 책임이 MLE와 충분히 겹치면 자동 저점 처리하지 마세요.
- backend/model serving, ML platform, experimentation infra, data engineer for ML 같은 역할은 transferable skill이 강하면 `40~59` 또는 `60~79` 후보가 될 수 있습니다.
- 단, 관련 기술이 일부 겹친다는 이유만으로 `80+`를 주지 마세요. 역할 정렬과 실제 ownership을 함께 보세요.
must-have 판단 규칙:
- must-have는 있으면 가산점이 아니라, 없으면 감점 또는 상한 제한을 만드는 핵심 조건입니다.
- 핵심 must-have 대부분이 충족되면 `80+` 후보가 될 수 있습니다.
- 일부만 충족하면 보통 `60~79` 또는 `40~59`로 제한하세요.
- 타깃 역할의 핵심 축이 빠져 있으면 transferable skill이 있어도 `80+`로 올리지 마세요.
deal-breaker 판단 규칙:
- 명시적 deal-breaker가 감지되면 추천 여부를 보수적으로 판단하세요.
- hard deal-breaker가 있으면 높은 기술 적합도가 보여도 강한 추천으로 올리지 마세요.
- 역할 불일치가 매우 크거나 hard deal-breaker가 있으면 `fit_score`는 `80` 미만이어야 합니다.
transferable skill 판단 규칙:
- transferable skill은 역할 불일치를 완전히 상쇄하지는 않지만, 인접 직무를 `1~39`에서 `40~59` 이상으로 끌어올릴 수 있는 근거입니다.
- 단순 키워드 중복만 보지 말고, Python/SQL/infra 경험이 실제 ML workflow, serving, experimentation, deployment ownership과 이어지는지 보세요.
출력 규칙:
- 먼저 역할 정렬, must-have 충족 수준, deal-breaker 심각도, transferable skill 수준을 판단한 뒤 점수를 정하세요.
- `summary`는 2~3줄 이내로, 왜 이 점수대인지와 핵심 추천 판단을 짧게 요약하세요.
- `strengths`는 추천 근거가 되는 강점만 짧은 bullet-style 문자열로 쓰세요.
- `concerns`는 점수를 제한한 이유, 부족한 must-have, ownership 공백, deal-breaker 우려만 쓰세요.
- `confidence`는 점수 자체와 별개로 판단 근거의 명확성을 나타냅니다. 낮은 점수여도 근거가 명확하면 `HIGH`가 가능하고, 높은 점수여도 정보가 모호하면 `MEDIUM` 또는 `LOW`가 가능합니다.
반드시 아래 키만 가진 유효한 JSON 객체만 반환하세요:
{{
  "fit_score": 1부터 100 사이의 정수,
  "summary": 2~3줄 이내의 짧은 문자열,
  "strengths": 핵심 강점 문자열 배열,
  "concerns": 우려 포인트 문자열 배열,
  "must_have_matches": 충족한 필수 조건 문자열 배열,
  "deal_breaker_flags": 감지된 결격 사유 문자열 배열,
  "confidence": "HIGH", "MEDIUM", "LOW" 중 하나,
  "role_alignment": "HIGH", "MEDIUM", "LOW" 중 하나,
  "must_have_coverage": "STRONG", "PARTIAL", "WEAK" 중 하나,
  "deal_breaker_severity": "NONE", "SOFT", "HARD" 중 하나,
  "transferable_skills": "HIGH", "MEDIUM", "LOW" 중 하나
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
        eval_prompt_version="local-v3",
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
