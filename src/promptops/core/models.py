from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field


PromptStage = Literal["candidate", "staging", "production"]
ReviewStatus = Literal["pending", "in_review", "approved", "rejected"]
FailureCategory = Literal["prompt", "context", "dataset", "policy", "feature"]


class PromptMetadata(BaseModel):
    """Metadata describing how a prompt family is managed."""

    owner: str = Field(min_length=1)
    backend: str = Field(default="langsmith")
    identifier: str = Field(min_length=1)
    local_version: str = Field(min_length=1)
    schema_version: int = Field(ge=1)
    tags: Dict[PromptStage, str] = Field(default_factory=dict)


class PromptRevision(BaseModel):
    """Recorded prompt revision shape for PromptOps iteration tracking."""

    family_key: str = Field(min_length=1)
    revision_id: str = Field(min_length=1)
    stage: PromptStage
    summary: str = Field(default="")
    change_reason: str = Field(default="")


class PromptFamily(BaseModel):
    """Logical prompt family managed by PromptOps."""

    key: str = Field(min_length=1)
    description: str = Field(default="")
    project_key: str = Field(min_length=1)
    active_stage: PromptStage = "candidate"
    metadata: PromptMetadata
    revisions: List[PromptRevision] = Field(default_factory=list)


class ExperimentSpec(BaseModel):
    """Generic experiment request shape."""

    prompt_family: str = Field(min_length=1)
    dataset_name: str = Field(min_length=1)
    evaluator_bundle: str = Field(min_length=1)
    fixture_path: str = Field(default="")
    experiment_prefix: str = Field(default="promptops")
    model: str | None = None
    backend: str = Field(default="langsmith")
    metadata: Dict[str, str] = Field(default_factory=dict)
    candidate_revision_id: str | None = None
    baseline_revision_id: str | None = None


class IterationRecord(BaseModel):
    """Single prompt-improvement loop record."""

    prompt_family: str = Field(min_length=1)
    goal: str = Field(min_length=1)
    stage: PromptStage = "candidate"
    prompt_revision_id: str | None = None
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


class DatasetSyncSpec(BaseModel):
    """Dataset sync request for PromptOps experiments."""

    dataset_name: str = Field(min_length=1)
    fixture_path: str = Field(min_length=1)
    description: str = Field(min_length=1)


class DatasetSyncResult(BaseModel):
    """Dataset sync result summary."""

    dataset_name: str = Field(min_length=1)
    dataset_id: str = Field(default="")
    example_count: int = Field(ge=0)
    created: int = Field(default=0, ge=0)
    updated: int = Field(default=0, ge=0)
    skipped: int = Field(default=0, ge=0)


class ExperimentRunResult(BaseModel):
    """Experiment execution result returned by a backend adapter."""

    prompt_family: str = Field(min_length=1)
    dataset_name: str = Field(min_length=1)
    experiment_name: str = Field(default="")
    session_id: str = Field(default="")
    compare_url: str = Field(default="")
    metadata: Dict[str, str] = Field(default_factory=dict)


class IterationSummary(BaseModel):
    """PromptOps iteration-level summary for one experiment cycle."""

    prompt_family: str = Field(min_length=1)
    dataset_name: str = Field(min_length=1)
    sync_result: DatasetSyncResult
    experiment_result: ExperimentRunResult
    compare_url: str = Field(default="")
