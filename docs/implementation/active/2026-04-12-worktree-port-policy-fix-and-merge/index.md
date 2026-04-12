---
plan_id: 2026-04-12-worktree-port-policy-fix-and-merge
title: worktree port policy 버그 수정 및 main 머지
status: active
milestone: Phase 2: 하네스 엔지니어링
source_agent: claude
created_at: 2026-04-12T18:00:00+09:00
updated_at: 2026-04-12T18:00:00+09:00
---
# worktree port policy 버그 수정 및 main 머지

`codex/unify-worktree-bootstrap-policy` 브랜치에 Next.js 포트 분리, `PROMPTOPS_DEV_BYPASS`, `env.ts` fail-fast 개선이 구현되어 있으나 미커밋 + 미머지 상태이며 버그 3개가 남아 있다.

**현재 위치**: `../ai-career-concierge-worktrees/codex/unify-worktree-bootstrap-policy`

## 문서 구성

- [목표](01-목표.md)
- [범위](02-범위.md)
- [중요 계약](03-중요-계약.md)
- [검증](04-검증.md)
- [실행 메모](05-실행-메모.md)
