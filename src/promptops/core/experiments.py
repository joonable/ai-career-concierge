from __future__ import annotations

from promptops.core.models import ExperimentSpec


def run_experiment(spec: ExperimentSpec) -> dict[str, str]:
    """Run a PromptOps experiment through the configured backend.

    The real orchestration will land in later sprints.
    """

    return {"status": "not_implemented", "prompt_family": spec.prompt_family}
