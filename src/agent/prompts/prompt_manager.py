from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, Optional

from langchain_core.prompts import PromptTemplate

from agent.schemas.pipeline_job import PipelineJob
from common.errors import PromptLoadError

PROMPT_SCHEMA_VERSION = "1"

EVALUATION_PROMPT_TEMPLATE = """You are evaluating whether a job is a strong match for one user.
Be conservative and optimize for precision over recall.
Target role: {role}
Years of experience: {years_of_experience}
Must-haves: {must_haves}
Deal-breakers: {deal_breakers}
Recent dislike memory: {recent_memory}
Job title: {job_title}
Company: {company}
Job description: {job_description}
Return only valid JSON with exactly these keys:
{{
  "fit_score": integer from 1 to 100,
  "reasoning": short string within 2-3 concise lines,
  "must_have_hits": array of strings,
  "deal_breakers_found": array of strings
}}
Do not include markdown fences or extra commentary."""

MEMORY_SUMMARY_PROMPT_TEMPLATE = (
    "Avoid jobs similar to these recent dislikes: {joined_reasons}."
)


@dataclass(frozen=True)
class PromptMetadata:
    prompt_name: str
    prompt_version: str
    prompt_variant: str
    schema_version: str
    prompt_identifier: str = ""
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
        if self.client is None or not identifier:
            return RenderedPrompt(
                text=fallback_prompt.invoke(variables).to_string(),
                metadata=metadata,
            )

        try:
            pulled_prompt = self.client.pull_prompt(identifier)
            rendered = pulled_prompt.invoke(variables).to_string()
            version = self._resolve_identifier_version(identifier, metadata.prompt_version)
            return RenderedPrompt(
                text=rendered,
                metadata=PromptMetadata(
                    prompt_name=metadata.prompt_name,
                    prompt_version=version,
                    prompt_variant=metadata.prompt_variant,
                    schema_version=metadata.schema_version,
                    prompt_identifier=identifier,
                    source="langsmith",
                ),
            )
        except Exception:
            return RenderedPrompt(
                text=fallback_prompt.invoke(variables).to_string(),
                metadata=metadata,
            )

    @staticmethod
    def _resolve_identifier_version(identifier: str, default_version: str) -> str:
        if ":" not in identifier:
            return default_version
        version = identifier.split(":", 1)[1].strip()
        return version or default_version


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
