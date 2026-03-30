from __future__ import annotations

from typing import Iterable

from agent.prompts.prompt_manager import PromptManager, RenderedPrompt

def summarize_recent_dislikes(dislike_reasons: Iterable[str]) -> str:
    return build_memory_summary(dislike_reasons).text


def build_memory_summary(dislike_reasons: Iterable[str]) -> RenderedPrompt:
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
    return manager.render_memory_summary(dislike_reasons)
