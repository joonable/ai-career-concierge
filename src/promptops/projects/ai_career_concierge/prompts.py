"""Prompt family declarations for AI Career Concierge."""

from promptops.core.models import PromptFamily, PromptMetadata, PromptRevision
from promptops.projects.ai_career_concierge import PROJECT_KEY


PROMPT_FAMILIES = [
    PromptFamily(
        key="job-evaluation",
        description="Structured evaluation prompt for job recommendation scoring.",
        project_key=PROJECT_KEY,
        active_stage="staging",
        metadata=PromptMetadata(
            owner="agent",
            backend="langsmith",
            identifier="job-evaluation",
            local_version="local-v3",
            schema_version=3,
            tags={
                "candidate": "job-evaluation",
                "staging": "job-evaluation:staging",
                "production": "job-evaluation:latest",
            },
        ),
        revisions=[
            PromptRevision(
                family_key="job-evaluation",
                revision_id="local-v3",
                stage="staging",
                summary="Score-policy-aware structured evaluation prompt.",
                change_reason="Introduced v3 score policy and structured judgment axes.",
            )
        ],
    ),
    PromptFamily(
        key="memory-summary",
        description="Short-term dislike feedback summarization prompt.",
        project_key=PROJECT_KEY,
        active_stage="staging",
        metadata=PromptMetadata(
            owner="agent",
            backend="langsmith",
            identifier="memory-summary",
            local_version="local-v1",
            schema_version=1,
            tags={
                "candidate": "memory-summary",
                "staging": "memory-summary:staging",
                "production": "memory-summary:latest",
            },
        ),
        revisions=[
            PromptRevision(
                family_key="memory-summary",
                revision_id="local-v1",
                stage="staging",
                summary="Summarize recent dislike feedback into reusable memory.",
                change_reason="Initial PromptOps registry baseline for memory prompt management.",
            )
        ],
    ),
]
