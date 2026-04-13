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
ACTIVE_PLANS=$(
  rg -l '^status: active$' "$ROOT/docs/implementation/active" -g 'index.md' 2>/dev/null \
    | xargs -n1 dirname 2>/dev/null \
    | xargs -n1 basename 2>/dev/null || true
)
if [ -n "$ACTIVE_PLANS" ]; then
  echo ""
  echo "⚠️  [StopHook] 완료되지 않은 active plan이 있습니다:"
  echo "$ACTIVE_PLANS" | sed 's/^/  - /'
  echo ""
  echo "  closeout readiness 점검:"
  while IFS= read -r plan_dir; do
    [ -n "$plan_dir" ] || continue
    echo "  [check] $plan_dir"
    python3 "$ROOT/scripts/implementation_docs.py" \
      --repo-root "$ROOT" \
      closeout-check \
      "$plan_dir" 2>&1 | sed 's/^/    /'
  done <<< "$ACTIVE_PLANS"
  echo "  작업이 완료됐다면 다음을 실행하세요:"
  echo "  python3 scripts/implementation_docs.py closeout-plan <plan_id>"
fi
