from __future__ import annotations

from typing import List, Literal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


RoleAlignment = Literal["HIGH", "MEDIUM", "LOW"]
MustHaveCoverage = Literal["STRONG", "PARTIAL", "WEAK"]
DealBreakerSeverity = Literal["NONE", "SOFT", "HARD"]
TransferableSkillsLevel = Literal["HIGH", "MEDIUM", "LOW"]


class LLMEvaluationResult(BaseModel):
    evaluation_id: UUID
    job_id: UUID
    platform: str
    title: str
    company: str
    url: str
    fit_score: int = Field(ge=1, le=100)
    reasoning: str = Field(default="")
    summary: str = Field(min_length=1)
    strengths: List[str] = Field(default_factory=list)
    concerns: List[str] = Field(default_factory=list)
    must_have_matches: List[str] = Field(default_factory=list)
    deal_breaker_flags: List[str] = Field(default_factory=list)
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    role_alignment: RoleAlignment
    must_have_coverage: MustHaveCoverage
    deal_breaker_severity: DealBreakerSeverity
    transferable_skills: TransferableSkillsLevel
    must_have_hits: List[str] = Field(default_factory=list)
    deal_breakers_found: List[str] = Field(default_factory=list)

    @model_validator(mode="after")
    def normalize_legacy_fields(self) -> "LLMEvaluationResult":
        if not self.reasoning:
            self.reasoning = self.summary.strip()
        else:
            self.reasoning = self.reasoning.strip()

        self.summary = self.summary.strip()

        if not self.must_have_hits and self.must_have_matches:
            self.must_have_hits = list(self.must_have_matches)
        if not self.must_have_matches and self.must_have_hits:
            self.must_have_matches = list(self.must_have_hits)

        if not self.deal_breakers_found and self.deal_breaker_flags:
            self.deal_breakers_found = list(self.deal_breaker_flags)
        if not self.deal_breaker_flags and self.deal_breakers_found:
            self.deal_breaker_flags = list(self.deal_breakers_found)

        if hasattr(self, "transferable_skill_level") and getattr(self, "transferable_skill_level", None):
            self.transferable_skills = getattr(self, "transferable_skill_level")

        return self

    @model_validator(mode="before")
    @classmethod
    def normalize_alias_fields(cls, data):
        if not isinstance(data, dict):
            return data
        payload = dict(data)
        if "transferable_skills" not in payload and payload.get("transferable_skill_level"):
            payload["transferable_skills"] = payload["transferable_skill_level"]
        return payload

    @field_validator("reasoning")
    @classmethod
    def reasoning_must_be_short(cls, value: str) -> str:
        if not value:
            return value
        if len(value.splitlines()) > 3:
            raise ValueError("Reasoning must stay concise.")
        return value.strip()

    @field_validator("summary")
    @classmethod
    def summary_must_be_short(cls, value: str) -> str:
        if len(value.splitlines()) > 3:
            raise ValueError("Summary must stay concise.")
        return value.strip()

    @field_validator("strengths", "concerns", "must_have_matches", "deal_breaker_flags")
    @classmethod
    def list_items_must_be_non_empty(cls, value: List[str]) -> List[str]:
        return [item.strip() for item in value if item and item.strip()]
