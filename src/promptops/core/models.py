from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field


PromptStage = Literal["candidate", "staging", "production"]
ReviewStatus = Literal["pending", "in_review", "approved", "rejected"]
FailureCategory = Literal["prompt", "context", "dataset", "policy", "feature"]


class PromptFamily(BaseModel):
    """Logical prompt family managed by PromptOps."""

    key: str = Field(min_length=1)
    description: str = Field(default="")
    project_key: str = Field(min_length=1)
    active_stage: PromptStage = "candidate"


class ExperimentSpec(BaseModel):
    """Generic experiment request shape."""

    prompt_family: str = Field(min_length=1)
    dataset_name: str = Field(min_length=1)
    evaluator_bundle: str = Field(min_length=1)
    backend: str = Field(default="langsmith")
    metadata: Dict[str, str] = Field(default_factory=dict)


class IterationRecord(BaseModel):
    """Single prompt-improvement loop record."""

    prompt_family: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    baseline_experiment_id: str | None = None
    candidate_experiment_id: str | None = None
    failure_categories: List[FailureCategory] = Field(default_factory=list)
    summary: str = Field(default="")


class ReviewItem(BaseModel):
    """Human or machine review unit."""

    item_id: str = Field(min_length=1)
    prompt_family: str = Field(min_length=1)
    status: ReviewStatus = "pending"
    notes: str = Field(default="")
