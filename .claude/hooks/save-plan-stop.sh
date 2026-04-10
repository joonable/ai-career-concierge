#!/usr/bin/env bash

set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"

python3 "$ROOT/scripts/implementation_docs.py" \
  --repo-root "$ROOT" \
  save-plan \
  --agent claude \
  --milestone "Backlog" \
  --hook-event Stop \
  --stdin-json \
  --quiet
