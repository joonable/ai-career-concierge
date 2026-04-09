from __future__ import annotations

import json
from collections.abc import Iterable
from pathlib import Path
from typing import Any, Dict, List, Literal, Union
from uuid import UUID

from langsmith.schemas import ExampleCreate
from pydantic import BaseModel, ConfigDict, Field, model_validator

RoleAlignment = Literal["HIGH", "MEDIUM", "LOW"]
MustHaveCoverage = Literal["STRONG", "PARTIAL", "WEAK"]
DealBreakerSeverity = Literal["NONE", "SOFT", "HARD"]
TransferableSkillLevel = Literal["HIGH", "MEDIUM", "LOW"]


class CuratedExampleOutputs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    should_pass: bool
    fit_score_range: Dict[str, int]
    expected_must_have_matches: List[str] = Field(default_factory=list)
    expected_deal_breaker_flags: List[str] = Field(default_factory=list)
    expected_strength_keywords: List[str] = Field(default_factory=list)
    expected_concern_keywords: List[str] = Field(default_factory=list)
    expected_confidence: str = Field(default="")
    expected_role_alignment: RoleAlignment
    expected_must_have_coverage: MustHaveCoverage
    expected_deal_breaker_severity: DealBreakerSeverity
    expected_transferable_skill_level: TransferableSkillLevel
    scoring_note: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_fit_score_range(self) -> CuratedExampleOutputs:
        minimum = self.fit_score_range.get("min")
        maximum = self.fit_score_range.get("max")
        if minimum is None or maximum is None:
            raise ValueError("fit_score_range must include both min and max.")
        if minimum > maximum:
            raise ValueError("fit_score_range min cannot exceed max.")
        return self


class CuratedExampleMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    scenario_type: str = Field(min_length=1)
    scenario_family: str = Field(min_length=1)
    platform: str = Field(default="curated")
    difficulty: str = Field(default="medium")
    source: str = Field(default="curated")


class CuratedExample(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    inputs: Dict[str, Any]
    outputs: CuratedExampleOutputs
    metadata: CuratedExampleMetadata


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


def _desired_split(example: Dict[str, Any]) -> List[str]:
    return ["gold", example.get("metadata", {}).get("scenario_type", "default")]


def _normalize_split(split: Any) -> List[str]:
    if split is None:
        return []
    if isinstance(split, str):
        return [split]
    if isinstance(split, Iterable):
        return list(split)
    return [str(split)]


def _example_needs_update(
    existing: Any, *, inputs: Dict[str, Any], outputs: Dict[str, Any], metadata: Dict[str, Any], split: List[str]
) -> bool:
    return any(
        [
            getattr(existing, "inputs", None) != inputs,
            getattr(existing, "outputs", None) != outputs,
            getattr(existing, "metadata", None) != metadata,
            _normalize_split(getattr(existing, "split", None)) != split,
        ]
    )


def sync_examples(client, *, dataset_name: str, examples: List[Dict[str, Any]]) -> Any:
    existing_examples = {
        str(example.id): example for example in client.list_examples(dataset_name=dataset_name, limit=500)
    }
    created_payload = [
        ExampleCreate(
            id=UUID(str(example["id"])),
            inputs=example["inputs"],
            outputs=example["outputs"],
            metadata=example.get("metadata", {}),
            split=_desired_split(example),
        )
        for example in examples
        if str(example["id"]) not in existing_examples
    ]
    updated = 0
    skipped = 0

    for example in examples:
        existing = existing_examples.get(str(example["id"]))
        if existing is None:
            continue

        inputs = example["inputs"]
        outputs = example["outputs"]
        metadata = example.get("metadata", {})
        split = _desired_split(example)

        if _example_needs_update(
            existing,
            inputs=inputs,
            outputs=outputs,
            metadata=metadata,
            split=split,
        ):
            client.update_example(
                example["id"],
                inputs=inputs,
                outputs=outputs,
                metadata=metadata,
                split=split,
            )
            updated += 1
        else:
            skipped += 1

    if created_payload:
        client.create_examples(dataset_name=dataset_name, examples=created_payload)

    return {
        "dataset_name": dataset_name,
        "created": len(created_payload),
        "updated": updated,
        "skipped": skipped,
    }
