from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "implementation_docs.py"

TODO_TEMPLATE = """# TODO.md

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
placeholder
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
"""

MILESTONE_TEMPLATE = """# MILESTONE.md

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


def run_cli(tmp_path: Path, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), "--repo-root", str(tmp_path), *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=True,
    )


def test_archive_plan_moves_package_and_updates_indexes(tmp_path: Path):
    bootstrap_repo(tmp_path)
    markdown = """# Hook Saved Plan

## Summary

summary

## Implementation Changes

implementation
"""

    run_cli(
        tmp_path,
        "save-plan",
        "--agent",
        "codex",
        "--milestone",
        "Phase 2: 하네스 엔지니어링",
        "--created-at",
        "2026-04-10T09:00:00+09:00",
        "--updated-at",
        "2026-04-10T09:00:00+09:00",
        "--stdin-markdown",
        stdin=markdown,
    )

    run_cli(
        tmp_path,
        "archive-plan",
        "2026-04-10-hook-saved-plan",
        "--updated-at",
        "2026-04-11T09:00:00+09:00",
    )

    archived_index = (
        tmp_path / "docs" / "implementation" / "archive" / "2026" / "2026-04-10-hook-saved-plan" / "index.md"
    )
    assert archived_index.exists()
    archived_text = archived_index.read_text(encoding="utf-8")
    assert "status: archived" in archived_text

    todo_text = (tmp_path / "TODO.md").read_text(encoding="utf-8")
    milestone_text = (tmp_path / "MILESTONE.md").read_text(encoding="utf-8")
    status_text = (tmp_path / "docs" / "internal" / "status.md").read_text(encoding="utf-8")
    assert "active plan 없음" in todo_text
    assert "docs/implementation/archive/2026/2026-04-10-hook-saved-plan/index.md" in milestone_text
    assert "Hook Saved Plan" in status_text


def test_hook_smoke_save_plan_from_stdin_json(tmp_path: Path):
    bootstrap_repo(tmp_path)
    payload = {
        "hook_event_name": "Stop",
        "last_assistant_message": "<proposed_plan>\n# Smoke Plan\n\n## Summary\n\nok\n</proposed_plan>",
    }

    run_cli(
        tmp_path,
        "save-plan",
        "--agent",
        "claude",
        "--milestone",
        "Backlog",
        "--hook-event",
        "Stop",
        "--stdin-json",
        "--created-at",
        "2026-04-10T09:00:00+09:00",
        "--updated-at",
        "2026-04-10T09:00:00+09:00",
        stdin=json.dumps(payload),
    )

    index_path = tmp_path / "docs" / "implementation" / "active" / "2026-04-10-smoke-plan" / "index.md"
    assert index_path.exists()


def test_closeout_check_reports_stale_tracking_surfaces(tmp_path: Path):
    bootstrap_repo(tmp_path)
    markdown = """# Closeout Plan

## Summary

summary
"""

    run_cli(
        tmp_path,
        "save-plan",
        "--agent",
        "codex",
        "--milestone",
        "Backlog",
        "--created-at",
        "2026-04-10T09:00:00+09:00",
        "--updated-at",
        "2026-04-10T09:00:00+09:00",
        "--stdin-markdown",
        stdin=markdown,
    )

    # Force a stale status surface without changing plan packages.
    (tmp_path / "docs" / "internal" / "status.md").write_text(STATUS_TEMPLATE, encoding="utf-8")

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT_PATH),
            "--repo-root",
            str(tmp_path),
            "closeout-check",
            "2026-04-10-closeout-plan",
        ],
        text=True,
        capture_output=True,
    )

    assert result.returncode == 1
    assert "docs/internal/status.md managed block stale" in result.stderr


def test_closeout_plan_archives_without_double_sync_and_validates(tmp_path: Path):
    bootstrap_repo(tmp_path)
    markdown = """# Closeout Target

## Summary

summary
"""

    run_cli(
        tmp_path,
        "save-plan",
        "--agent",
        "codex",
        "--milestone",
        "Backlog",
        "--created-at",
        "2026-04-10T09:00:00+09:00",
        "--updated-at",
        "2026-04-10T09:00:00+09:00",
        "--stdin-markdown",
        stdin=markdown,
    )

    result = run_cli(
        tmp_path,
        "closeout-plan",
        "2026-04-10-closeout-target",
        "--updated-at",
        "2026-04-11T09:00:00+09:00",
    )

    archived_index = (
        tmp_path / "docs" / "implementation" / "archive" / "2026" / "2026-04-10-closeout-target" / "index.md"
    )
    assert archived_index.exists()
    assert "2026-04-10-closeout-target" in result.stdout
    validate_result = run_cli(tmp_path, "validate")
    assert validate_result.stdout.strip() == "ok"
