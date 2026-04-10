#!/usr/bin/env bash
# PreToolUse: ExitPlanMode
# 계획 완료 후 plan mode를 종료하기 전에 Codex 리뷰를 실행한다.
# - docs/implementation/active/ 에서 최신 plan을 찾는다.
# - plan이 없으면 exit 2 로 블록하고 먼저 저장하도록 안내한다.
# - plan이 있으면 codex exec 로 리뷰를 요청하고 결과를 출력한다.

set -euo pipefail

ROOT="${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
ACTIVE_DIR="$ROOT/docs/implementation/active"

# 가장 최근에 수정된 index.md 찾기
LATEST_INDEX=$(find "$ACTIVE_DIR" -name "index.md" 2>/dev/null \
  | xargs ls -t 2>/dev/null \
  | head -1 || true)

if [ -z "$LATEST_INDEX" ]; then
  echo "[codex-plan-review] ⚠️  docs/implementation/active/ 에 저장된 plan이 없습니다."
  echo ""
  echo "ExitPlanMode 전에 반드시 plan을 저장하세요:"
  echo ""
  echo "  python3 scripts/implementation_docs.py save-plan \\"
  echo "    --agent claude --milestone <milestone> --title \"<제목>\""
  echo ""
  echo "저장 후 다시 ExitPlanMode를 호출하면 Codex 리뷰를 실행합니다."
  exit 2
fi

PLAN_DIR=$(dirname "$LATEST_INDEX")
PLAN_SLUG=$(basename "$PLAN_DIR")

echo "[codex-plan-review] 📋 Plan: $PLAN_SLUG"
echo "[codex-plan-review] 🤖 Codex 리뷰 요청 중..."
echo "---"

# plan 디렉토리의 모든 마크다운을 합쳐 codex exec 에 전달
PLAN_FILES=$(find "$PLAN_DIR" -name "*.md" | sort | tr '\n' ' ')

codex exec \
  --ephemeral \
  -s read-only \
  -C "$ROOT" \
  "다음 구현 계획을 리뷰하고 아래 4가지 관점에서 간결하게 피드백하세요 (총 200단어 이내):
1. 아키텍처 리스크 (기존 파이프라인/스키마와 충돌 가능성)
2. 테스트 누락 (testing.md 기준으로 TDD 요건 충족 여부)
3. 범위 초과 (PoC 단계에서 불필요한 기능/추상화)
4. 브레이킹 체인지 미표기 (API 계약, 스키마, 인증 등)

리뷰 대상 파일: $PLAN_FILES" 2>&1 \
  || echo "[codex-plan-review] ⚠️  Codex 실행 실패 — 직접 plan을 리뷰하고 진행하세요."

echo "---"
echo "[codex-plan-review] ✅ 리뷰 완료. 피드백을 반영한 후 ExitPlanMode를 실행하세요."
