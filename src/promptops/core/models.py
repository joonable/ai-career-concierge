from __future__ import annotations

from typing import Dict, List, Literal

from pydantic import BaseModel, Field


PromptStage = Literal["candidate", "staging", "production"]
ReviewStatus = Literal["pending", "in_review", "approved", "rejected"]
FailureCategory = Literal["prompt", "context", "dataset", "policy", "feature"]
ReviewMode = Literal["llm_judge", "human"]
ReviewQueueMode = Literal["single", "pairwise"]
BacklogPriority = Literal["P0", "P1", "P2", "P3"]
FailureTaxonomyKey = Literal[
    "prompt.role_alignment",
    "prompt.must_have_coverage",
    "prompt.transferable_skill_credit",
    "prompt.summary_usefulness",
    "dataset.gold_expectation_gap",
    "dataset.borderline_coverage_gap",
    "context.normalization_gap",
    "policy.deal_breaker_handling",
    "policy.score_band_definition",
    "feature.onboarding_signal_missing",
]


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
    experiment_id: str = Field(default="")
    run_id: str = Field(default="")
    dataset_example_id: str = Field(default="")
    queue_name: str = Field(default="")
    mode: ReviewMode = "human"
    status: ReviewStatus = "pending"
    reasons: List[str] = Field(default_factory=list)
    notes: str = Field(default="")


class ReviewRubricCriterion(BaseModel):
    """Single rubric criterion used by human or LLM review."""

    key: str = Field(min_length=1)
    label: str = Field(min_length=1)
    description: str = Field(min_length=1)
    required: bool = True


class ReviewQueueSpec(BaseModel):
    """Review queue definition that can be mapped to a backend annotation queue."""

    queue_name: str = Field(min_length=1)
    prompt_family: str = Field(min_length=1)
    queue_mode: ReviewQueueMode = "single"
    backend: str = Field(default="langsmith")
    rubric_keys: List[str] = Field(default_factory=list)
    description: str = Field(default="")


class ReviewFeedbackRecord(BaseModel):
    """Persistable review feedback shape across human and LLM judges."""

    review_item_id: str = Field(min_length=1)
    reviewer_type: ReviewMode
    reviewer_id: str = Field(default="")
    scores: Dict[str, str] = Field(default_factory=dict)
    notes: str = Field(default="")
    decision: str = Field(default="")
    backlog_candidates: List[str] = Field(default_factory=list)


class FailureRecord(BaseModel):
    """Structured failure record produced from review or evaluator results."""

    taxonomy_key: FailureTaxonomyKey
    category: FailureCategory
    summary: str = Field(min_length=1)
    evidence: List[str] = Field(default_factory=list)
    source_review_item_id: str = Field(default="")


class BacklogItem(BaseModel):
    """Actionable backlog item derived from PromptOps review and failure analysis."""

    item_key: str = Field(min_length=1)
    category: FailureCategory
    priority: BacklogPriority
    title: str = Field(min_length=1)
    action: str = Field(min_length=1)
    linked_taxonomy_keys: List[FailureTaxonomyKey] = Field(default_factory=list)
    evidence: List[str] = Field(default_factory=list)


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
