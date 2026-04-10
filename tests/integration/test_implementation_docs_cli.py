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


def bootstrap_repo(tmp_path: Path) -> None:
    (tmp_path / "docs" / "implementation" / "active").mkdir(parents=True)
    (tmp_path / "docs" / "implementation" / "archive").mkdir(parents=True)
    (tmp_path / "TODO.md").write_text(TODO_TEMPLATE, encoding="utf-8")
    (tmp_path / "MILESTONE.md").write_text(MILESTONE_TEMPLATE, encoding="utf-8")


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
    assert "현재 활성 plan package 없음" in todo_text
    assert "docs/implementation/archive/2026/2026-04-10-hook-saved-plan/index.md" in milestone_text


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
