from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from api.services.promptops_dataset_service import PromptOpsDatasetService

MINIMAL_ITEM = {
    "id": "f7c5f30e-286e-4f20-b0fa-c767b3f6c101",
    "inputs": {
        "user_context": {
            "user_id": "11111111-1111-1111-1111-111111111111",
            "profile_data": {"role": "Machine Learning Engineer", "years_of_experience": 6},
            "guidelines": {"must_haves": ["Python"], "deal_breakers": []},
            "notification_settings": {"minimum_fit_score": 80, "delivery_channel": "slack"},
        },
        "recent_memory": "",
        "job": {
            "job_id": "18f3fb52-d02c-4f2a-b0df-20467365ad27",
            "platform": "curated",
            "external_job_id": "gold-001",
            "title": "시니어 머신러닝 엔지니어",
            "company": "시그널 랩스",
            "jd_raw_text": "Python, SQL, MLOps",
            "url": "https://example.com/jobs/gold-001",
        },
    },
    "outputs": {
        "should_pass": True,
        "fit_score_range": {"min": 80, "max": 100},
        "expected_must_have_matches": ["Python"],
        "expected_deal_breaker_flags": [],
        "expected_strength_keywords": ["python"],
        "expected_concern_keywords": [],
        "expected_confidence": "HIGH",
        "expected_role_alignment": "HIGH",
        "expected_must_have_coverage": "STRONG",
        "expected_deal_breaker_severity": "NONE",
        "expected_transferable_skill_level": "HIGH",
        "scoring_note": "직접적인 역할 일치입니다.",
    },
    "metadata": {
        "scenario_type": "강한_일치",
        "scenario_family": "직접_mle_일치",
        "platform": "curated",
        "difficulty": "쉬움",
        "source": "선별",
    },
}


def _write_fixture(path: Path, items: list) -> None:
    path.write_text(json.dumps(items), encoding="utf-8")


def test_get_dataset_returns_item_count_and_fields():
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture = Path(tmpdir) / "gold.json"
        _write_fixture(fixture, [MINIMAL_ITEM])

        service = PromptOpsDatasetService(fixture_path=fixture)
        result = service.get_dataset()

    assert result.total == 1
    assert len(result.items) == 1

    item = result.items[0]
    assert item.id == "f7c5f30e-286e-4f20-b0fa-c767b3f6c101"
    assert item.scenario_type == "강한_일치"
    assert item.scenario_family == "직접_mle_일치"
    assert item.difficulty == "쉬움"
    assert item.should_pass is True
    assert item.fit_score_min == 80
    assert item.fit_score_max == 100
    assert item.scoring_note == "직접적인 역할 일치입니다."
    assert item.job_title == "시니어 머신러닝 엔지니어"


def test_get_dataset_handles_multiple_items():
    second = {**MINIMAL_ITEM, "id": "f7c5f30e-286e-4f20-b0fa-c767b3f6c102"}
    second["outputs"] = {**MINIMAL_ITEM["outputs"], "should_pass": False, "fit_score_range": {"min": 0, "max": 39}}
    second["metadata"] = {**MINIMAL_ITEM["metadata"], "scenario_type": "명확한_거부"}

    with tempfile.TemporaryDirectory() as tmpdir:
        fixture = Path(tmpdir) / "gold.json"
        _write_fixture(fixture, [MINIMAL_ITEM, second])

        service = PromptOpsDatasetService(fixture_path=fixture)
        result = service.get_dataset()

    assert result.total == 2
    assert result.items[1].should_pass is False
    assert result.items[1].scenario_type == "명확한_거부"


def test_get_dataset_raises_on_missing_file():
    service = PromptOpsDatasetService(fixture_path=Path("/nonexistent/path/gold.json"))
    with pytest.raises(Exception):
        service.get_dataset()


def test_get_dataset_raises_on_invalid_json():
    with tempfile.TemporaryDirectory() as tmpdir:
        fixture = Path(tmpdir) / "gold.json"
        fixture.write_text("not valid json", encoding="utf-8")

        service = PromptOpsDatasetService(fixture_path=fixture)
        with pytest.raises(Exception):
            service.get_dataset()
