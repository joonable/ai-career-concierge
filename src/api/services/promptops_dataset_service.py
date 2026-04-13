from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from agent.evals.dataset_workflow import load_curated_examples
from api.schemas.users import PromptOpsDatasetItem, PromptOpsDatasetResponse

DEFAULT_FIXTURE_PATH = (
    Path(__file__).parents[3] / "agent" / "evals" / "fixtures" / "job_eval_gold.json"
)


class PromptOpsDatasetService:
    def __init__(self, fixture_path: Path = DEFAULT_FIXTURE_PATH) -> None:
        self.fixture_path = fixture_path

    def get_dataset(self) -> PromptOpsDatasetResponse:
        examples = load_curated_examples(self.fixture_path)
        items = [_to_dataset_item(ex) for ex in examples]
        return PromptOpsDatasetResponse(total=len(items), items=items)


def _to_dataset_item(example: Dict[str, Any]) -> PromptOpsDatasetItem:
    outputs = example.get("outputs", {})
    metadata = example.get("metadata", {})
    fit_score_range = outputs.get("fit_score_range", {})
    job = example.get("inputs", {}).get("job", {})

    return PromptOpsDatasetItem(
        id=str(example["id"]),
        scenario_type=metadata.get("scenario_type", ""),
        scenario_family=metadata.get("scenario_family", ""),
        difficulty=metadata.get("difficulty", ""),
        should_pass=bool(outputs.get("should_pass", False)),
        fit_score_min=int(fit_score_range.get("min", 0)),
        fit_score_max=int(fit_score_range.get("max", 0)),
        scoring_note=str(outputs.get("scoring_note", "")),
        job_title=str(job.get("title", "")),
    )
