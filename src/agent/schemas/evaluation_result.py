from __future__ import annotations

from typing import List
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class LLMEvaluationResult(BaseModel):
    evaluation_id: UUID
    job_id: UUID
    platform: str
    title: str
    company: str
    url: str
    fit_score: int = Field(ge=1, le=100)
    reasoning: str = Field(min_length=1)
    must_have_hits: List[str] = Field(default_factory=list)
    deal_breakers_found: List[str] = Field(default_factory=list)

    @field_validator("reasoning")
    @classmethod
    def reasoning_must_be_short(cls, value: str) -> str:
        if len(value.splitlines()) > 3:
            raise ValueError("Reasoning must stay concise.")
        return value.strip()
