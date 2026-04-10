#!/usr/bin/env bash

set -euo pipefail

ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"

python3 "$ROOT/scripts/implementation_docs.py" \
  --repo-root "$ROOT" \
  save-plan \
  --agent gemini \
  --milestone "Backlog" \
  --hook-event AfterAgent \
  --stdin-json \
  --quiet

echo "{}"
