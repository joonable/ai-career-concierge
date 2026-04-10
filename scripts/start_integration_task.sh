#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./worktree_common.sh
source "${SCRIPT_DIR}/worktree_common.sh"

usage() {
  cat <<'EOF'
Usage:
  scripts/start_integration_task.sh --task <task-slug> [--base main]
EOF
}

task_slug=""
base_branch="main"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --task)
      task_slug="${2:-}"
      shift 2
      ;;
    --base)
      base_branch="${2:-}"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Error: unknown argument: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
done

ensure_git_repo
validate_task_slug "${task_slug}"
ensure_branch_exists "${base_branch}"
warn_if_dirty

branch_name="$(branch_name_for_integration "${task_slug}")"
worktree_path="$(worktree_path_for_kind "integration" "${task_slug}")"

create_or_reuse_worktree "${branch_name}" "${worktree_path}" "${base_branch}"
