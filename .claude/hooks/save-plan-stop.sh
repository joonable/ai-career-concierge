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

# active plan 잔존 경고
ACTIVE_PLANS=$(ls "$ROOT/docs/implementation/active/" 2>/dev/null | grep -v '^$' || true)
if [ -n "$ACTIVE_PLANS" ]; then
  echo ""
  echo "⚠️  [StopHook] 완료되지 않은 active plan이 있습니다:"
  echo "$ACTIVE_PLANS" | sed 's/^/  - /'
  echo "  작업이 완료됐다면 다음을 실행하세요:"
  echo "  python3 scripts/implementation_docs.py archive-plan <plan_id>"
  echo "  python3 scripts/implementation_docs.py sync-indexes"
fi
