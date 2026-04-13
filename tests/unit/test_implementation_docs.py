from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_docs.py"
SPEC = importlib.util.spec_from_file_location("implementation_docs_script", SCRIPT_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


TODO_TEMPLATE = """# TODO.md

이 문서는 implementation plan package 인덱스입니다.

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
placeholder
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
"""

MILESTONE_TEMPLATE = """# MILESTONE.md

이 문서는 milestone 인덱스입니다.

<!-- BEGIN MANAGED:MILESTONE_INDEX -->
placeholder
<!-- END MANAGED:MILESTONE_INDEX -->
"""

STATUS_TEMPLATE = """# 내부 대시보드 상태판

## 최근 완료 작업 (Done)

<!-- BEGIN MANAGED:STATUS_DONE -->
placeholder
<!-- END MANAGED:STATUS_DONE -->

## 다음 action

<!-- BEGIN MANAGED:STATUS_NEXT_ACTIONS -->
placeholder
<!-- END MANAGED:STATUS_NEXT_ACTIONS -->
"""


def bootstrap_repo(tmp_path: Path) -> None:
    (tmp_path / "docs" / "implementation" / "active").mkdir(parents=True)
    (tmp_path / "docs" / "implementation" / "archive").mkdir(parents=True)
    (tmp_path / "docs" / "internal").mkdir(parents=True)
    (tmp_path / "TODO.md").write_text(TODO_TEMPLATE, encoding="utf-8")
    (tmp_path / "MILESTONE.md").write_text(MILESTONE_TEMPLATE, encoding="utf-8")
    (tmp_path / "docs" / "internal" / "status.md").write_text(STATUS_TEMPLATE, encoding="utf-8")


def test_extract_plan_markdown_from_claude_stop_payload():
    payload = {
        "hook_event_name": "Stop",
        "last_assistant_message": "prefix\n<proposed_plan>\n# Hook Plan\n\n## Summary\n\n- one\n</proposed_plan>\npostfix",
    }

    extracted = MODULE.extract_markdown_from_hook_payload(payload, "Stop")

    assert extracted == "# Hook Plan\n\n## Summary\n\n- one"


def test_extract_plan_markdown_from_gemini_after_agent_payload():
    payload = {
        "hook_event_name": "AfterAgent",
        "prompt_response": "<proposed_plan>\n# Gemini Plan\n\n## Summary\n\nText\n</proposed_plan>",
    }

    extracted = MODULE.extract_markdown_from_hook_payload(payload, "AfterAgent")

    assert extracted == "# Gemini Plan\n\n## Summary\n\nText"


def test_save_plan_splits_large_markdown_and_writes_frontmatter(tmp_path: Path):
    bootstrap_repo(tmp_path)
    intro = "긴 설명 문단입니다. " * 500
    markdown = f"""# 문서 운영 구조 재편 및 계획 자동 저장 체계

{intro}

## Summary

summary

## Implementation Changes

implementation

## Test Plan

test

## Assumptions

assumptions
"""
    source_path = tmp_path / "plan.md"
    source_path.write_text(markdown, encoding="utf-8")
    args = MODULE.build_parser().parse_args(
        [
            "--repo-root",
            str(tmp_path),
            "save-plan",
            "--agent",
            "claude",
            "--milestone",
            "Phase 2: 하네스 엔지니어링",
            "--source-file",
            str(source_path),
            "--created-at",
            "2026-04-10T09:00:00+09:00",
            "--updated-at",
            "2026-04-10T09:00:00+09:00",
        ]
    )

    saved_dir = MODULE.save_plan(args)

    assert saved_dir is not None
    index_path = saved_dir / "index.md"
    index_text = index_path.read_text(encoding="utf-8")
    assert "plan_id: 2026-04-10-문서-운영-구조-재편-및-계획-자동-저장-체계" in index_text
    assert "status: active" in index_text
    assert "01-summary.md" in index_text
    assert (saved_dir / "01-summary.md").exists()
    assert (saved_dir / "02-implementation.md").exists()
    assert (saved_dir / "03-test-plan.md").exists()
    assert (saved_dir / "04-assumptions.md").exists()


def test_sync_indexes_groups_active_and_archive_items(tmp_path: Path):
    bootstrap_repo(tmp_path)
    active_dir = tmp_path / "docs" / "implementation" / "active" / "2026-04-10-doc-system"
    archive_dir = tmp_path / "docs" / "implementation" / "archive" / "2026" / "2026-04-01-legacy-plan"
    active_dir.mkdir(parents=True)
    archive_dir.mkdir(parents=True)
    active_index = """---
plan_id: 2026-04-10-doc-system
title: 문서 운영 구조 재편 및 계획 자동 저장 체계
status: active
milestone: Phase 2: 하네스 엔지니어링
source_agent: codex
created_at: 2026-04-10T09:00:00+09:00
updated_at: 2026-04-10T10:00:00+09:00
---
# 문서 운영 구조 재편 및 계획 자동 저장 체계
"""
    archive_index = """---
plan_id: 2026-04-01-legacy-plan
title: 레거시 계획
status: archived
milestone: Backlog
source_agent: manual
created_at: 2026-04-01T09:00:00+09:00
updated_at: 2026-04-02T09:00:00+09:00
---
# 레거시 계획
"""
    (active_dir / "index.md").write_text(active_index, encoding="utf-8")
    (archive_dir / "index.md").write_text(archive_index, encoding="utf-8")

    MODULE.sync_indexes(tmp_path)

    todo_text = (tmp_path / "TODO.md").read_text(encoding="utf-8")
    milestone_text = (tmp_path / "MILESTONE.md").read_text(encoding="utf-8")
    status_text = (tmp_path / "docs" / "internal" / "status.md").read_text(encoding="utf-8")
    assert "Phase 2: 하네스 엔지니어링" in todo_text
    assert "레거시 계획" in todo_text
    assert "History Timeline" in milestone_text
    assert "docs/implementation/archive/2026/2026-04-01-legacy-plan/index.md" in milestone_text
    assert "문서 운영 구조 재편 및 계획 자동 저장 체계" in status_text
    assert "레거시 계획" in status_text


def test_validate_detects_duplicate_plan_ids(tmp_path: Path):
    bootstrap_repo(tmp_path)
    first_dir = tmp_path / "docs" / "implementation" / "active" / "2026-04-10-first-plan"
    second_dir = tmp_path / "docs" / "implementation" / "active" / "2026-04-10-second-plan"
    first_dir.mkdir(parents=True)
    second_dir.mkdir(parents=True)
    body = """---
plan_id: duplicate-plan
title: Duplicate
status: active
milestone: Backlog
source_agent: codex
created_at: 2026-04-10T09:00:00+09:00
updated_at: 2026-04-10T09:00:00+09:00
---
# Duplicate
"""
    (first_dir / "index.md").write_text(body, encoding="utf-8")
    (second_dir / "index.md").write_text(body, encoding="utf-8")
    MODULE.sync_indexes(tmp_path)

    with pytest.raises(ValueError, match="Duplicate plan_id"):
        MODULE.validate(tmp_path)


def test_collect_closeout_issues_reports_stale_status_surface(tmp_path: Path):
    bootstrap_repo(tmp_path)
    active_dir = tmp_path / "docs" / "implementation" / "active" / "2026-04-10-doc-system"
    active_dir.mkdir(parents=True)
    active_index = """---
plan_id: 2026-04-10-doc-system
title: 문서 운영 구조 재편 및 계획 자동 저장 체계
status: active
milestone: Phase 2: 하네스 엔지니어링
source_agent: codex
created_at: 2026-04-10T09:00:00+09:00
updated_at: 2026-04-10T10:00:00+09:00
---
# 문서 운영 구조 재편 및 계획 자동 저장 체계
"""
    (active_dir / "index.md").write_text(active_index, encoding="utf-8")

    issues = MODULE.collect_closeout_issues(tmp_path, "2026-04-10-doc-system")

    assert "TODO.md managed block stale (IMPLEMENTATION_INDEX)" in issues
    assert "MILESTONE.md managed block stale (MILESTONE_INDEX)" in issues
    assert "docs/internal/status.md managed block stale (STATUS_DONE/STATUS_NEXT_ACTIONS)" in issues
