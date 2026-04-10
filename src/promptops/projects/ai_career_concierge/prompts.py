"""Prompt family declarations for AI Career Concierge."""

from promptops.core.models import PromptFamily, PromptMetadata
from promptops.projects.ai_career_concierge import PROJECT_KEY

PROMPT_FAMILIES = [
    PromptFamily(
        key="job-evaluation",
        description="Structured evaluation prompt for job recommendation scoring.",
        project_key=PROJECT_KEY,
        metadata=PromptMetadata(
            owner="agent",
            backend="langsmith",
            identifier="job-evaluation",
            schema_version=3,
            tags={
                "candidate": "job-evaluation",
                "staging": "job-evaluation:staging",
                "production": "job-evaluation:latest",
            },
        ),
    ),
    PromptFamily(
        key="memory-summary",
        description="Short-term dislike feedback summarization prompt.",
        project_key=PROJECT_KEY,
        metadata=PromptMetadata(
            owner="agent",
            backend="langsmith",
            identifier="memory-summary",
            schema_version=1,
            tags={
                "candidate": "memory-summary",
                "staging": "memory-summary:staging",
                "production": "memory-summary:latest",
            },
        ),
    ),
]
