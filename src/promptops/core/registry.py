from __future__ import annotations

from promptops.core.models import PromptFamily
from promptops.projects.ai_career_concierge.prompts import PROMPT_FAMILIES


def list_prompt_families() -> list[PromptFamily]:
    """Return registered prompt families across project bindings."""

    return [*PROMPT_FAMILIES]


def get_prompt_family(key: str) -> PromptFamily:
    """Fetch a single prompt family by key."""

    for family in list_prompt_families():
        if family.key == key:
            return family
    raise KeyError(f"Unknown prompt family: {key}")


def list_prompt_families_by_stage(stage: str) -> list[PromptFamily]:
    """Return prompt families currently assigned to a lifecycle stage."""

    return [family for family in list_prompt_families() if family.active_stage == stage]
