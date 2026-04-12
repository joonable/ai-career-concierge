#!/usr/bin/env bash

set -euo pipefail

usage_common() {
  cat <<'EOF'
Common helper for main-based agent/integration worktree setup.
EOF
}

ensure_git_repo() {
  if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
    echo "Error: current directory is not inside a git repository." >&2
    exit 1
  fi
}

repo_root() {
  git rev-parse --show-toplevel
}

repo_name() {
  basename "$(repo_root)"
}

ensure_branch_exists() {
  local branch="$1"
  if ! git show-ref --verify --quiet "refs/heads/${branch}"; then
    echo "Error: base branch '${branch}' does not exist locally." >&2
    echo "Hint: fetch or create the branch locally, then retry." >&2
    exit 1
  fi
}

warn_if_dirty() {
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "Warning: current worktree has uncommitted changes. Continue carefully." >&2
  fi
}

validate_task_slug() {
  local task_slug="$1"
  if [[ -z "${task_slug}" ]]; then
    echo "Error: --task is required." >&2
    exit 1
  fi

  case "${task_slug}" in
    *[!A-Za-z0-9._-]*)
      echo "Error: task slug must match [A-Za-z0-9._-]." >&2
      exit 1
      ;;
  esac
}

validate_agent() {
  local agent="$1"
  case "${agent}" in
    codex|claude|gemini) ;;
    *)
      echo "Error: --agent must be one of: codex, claude, gemini." >&2
      exit 1
      ;;
  esac
}

branch_name_for_agent() {
  local agent="$1"
  local task_slug="$2"
  printf '%s/%s\n' "${agent}" "${task_slug}"
}

branch_name_for_integration() {
  local task_slug="$1"
  printf 'integration/%s\n' "${task_slug}"
}

worktree_path_for_kind() {
  local kind="$1"
  local task_slug="$2"
  local root
  root="$(repo_root)"
  printf '%s/%s-worktrees/%s/%s\n' "$(dirname "${root}")" "$(repo_name)" "${kind}" "${task_slug}"
}

existing_worktree_for_branch() {
  local branch="$1"
  git worktree list --porcelain | awk -v target="refs/heads/${branch}" '
    $1 == "worktree" { current=$2 }
    $1 == "branch" && $2 == target { print current; exit }
  '
}

print_result() {
  local base_branch="$1"
  local target_branch="$2"
  local worktree_path="$3"
  local root
  root="$(repo_root)"

  cat <<EOF
base_branch=${base_branch}
target_branch=${target_branch}
worktree_path=${worktree_path}
next_command=cd ${worktree_path}
EOF

  cat >&2 <<EOF
notice=execution_worktree_ready
coordination_root=${root}
canonical_docs_policy=edit_docs_in_root_repo
EOF
}

ensure_parent_dir() {
  local worktree_path="$1"
  mkdir -p "$(dirname "${worktree_path}")"
}

create_or_reuse_worktree() {
  local branch="$1"
  local worktree_path="$2"
  local base_branch="$3"

  local existing_worktree
  existing_worktree="$(existing_worktree_for_branch "${branch}")"
  if [[ -n "${existing_worktree}" ]]; then
    print_result "${base_branch}" "${branch}" "${existing_worktree}"
    return 0
  fi

  if [[ -e "${worktree_path}" && ! -d "${worktree_path}" ]]; then
    echo "Error: target worktree path exists and is not a directory: ${worktree_path}" >&2
    exit 1
  fi

  ensure_parent_dir "${worktree_path}"

  if git show-ref --verify --quiet "refs/heads/${branch}"; then
    git worktree add "${worktree_path}" "${branch}" >/dev/null
  else
    git worktree add -b "${branch}" "${worktree_path}" "${base_branch}" >/dev/null
  fi

  print_result "${base_branch}" "${branch}" "${worktree_path}"
}
