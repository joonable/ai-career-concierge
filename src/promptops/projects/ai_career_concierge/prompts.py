"""Prompt family declarations for AI Career Concierge."""

from promptops.core.models import PromptFamily
from promptops.projects.ai_career_concierge import PROJECT_KEY


PROMPT_FAMILIES = [
    PromptFamily(
        key="job-evaluation",
        description="Structured evaluation prompt for job recommendation scoring.",
        project_key=PROJECT_KEY,
        active_stage="staging",
    ),
    PromptFamily(
        key="memory-summary",
        description="Short-term dislike feedback summarization prompt.",
        project_key=PROJECT_KEY,
        active_stage="staging",
    ),
]
