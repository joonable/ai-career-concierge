from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Union
from uuid import UUID

from langsmith.schemas import ExampleCreate
from pydantic import BaseModel, ConfigDict, Field


class CuratedExampleOutputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    should_pass: bool
    fit_score_range: Dict[str, int]
    expected_must_have_matches: List[str] = Field(default_factory=list)
    expected_deal_breaker_flags: List[str] = Field(default_factory=list)
    expected_strength_keywords: List[str] = Field(default_factory=list)
    expected_concern_keywords: List[str] = Field(default_factory=list)
    expected_confidence: str = Field(default="")


class CuratedExample(BaseModel):
    model_config = ConfigDict(extra="allow")

    id: UUID
    inputs: Dict[str, Any]
    outputs: CuratedExampleOutputs
    metadata: Dict[str, Any] = Field(default_factory=dict)


def load_curated_examples(path: Union[str, Path]) -> List[Dict[str, Any]]:
    dataset_path = Path(path)
    payload = json.loads(dataset_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("Dataset fixture must be a list of examples.")
    return [CuratedExample.model_validate(example).model_dump(mode="json") for example in payload]


def ensure_dataset(client, *, dataset_name: str, description: str) -> Any:
    existing = next(iter(client.list_datasets(dataset_name=dataset_name, limit=1)), None)
    if existing is not None:
        return existing
    return client.create_dataset(
        dataset_name=dataset_name,
        description=description,
        metadata={"source": "curated", "owner": "ai-career-concierge"},
    )


def sync_examples(client, *, dataset_name: str, examples: List[Dict[str, Any]]) -> Any:
    existing_ids = {
        str(example.id)
        for example in client.list_examples(dataset_name=dataset_name, limit=500)
    }
    serialized = [
        ExampleCreate(
            id=UUID(str(example["id"])),
            inputs=example["inputs"],
            outputs=example["outputs"],
            metadata=example.get("metadata", {}),
            split=["gold", example.get("metadata", {}).get("scenario_type", "default")],
        )
        for example in examples
        if str(example["id"]) not in existing_ids
    ]
    if not serialized:
        return {"dataset_name": dataset_name, "created": 0, "skipped": len(examples)}
    return client.create_examples(dataset_name=dataset_name, examples=serialized)
