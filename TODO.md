# TODO.md

이 문서는 현재 진행 중인 implementation plan package의 가벼운 인덱스입니다.
상세 계획의 canonical source는 [`docs/implementation/active/`](docs/implementation/active/)이며, 구조 규칙은 [`docs/implementation/README.md`](docs/implementation/README.md)를 따릅니다.

## 운영 원칙

- 새 계획 저장: `python3 scripts/implementation_docs.py save-plan --agent <agent> --milestone "<milestone>" --stdin-markdown`
- 완료 후 archive: `python3 scripts/implementation_docs.py archive-plan <plan_id>`
- 인덱스 재동기화: `python3 scripts/implementation_docs.py sync-indexes`
- 정합성 검증: `python3 scripts/implementation_docs.py validate`
- `TODO.md`에는 `status: active`인 실행 plan만 노출합니다.
- 상위 방향 정렬용 문서는 `docs/implementation/active/` 아래에 두더라도 `status: reference`로 관리하고 managed index에는 노출하지 않습니다.

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
## Active Plans

- [Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)](docs/implementation/active/2026-04-10-phase5-1-jobkorea-scraper-agentic/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `claude`, updated: `2026-04-10T00:00:00+09:00`
- [Phase 4: PromptOps 에이전트 분석 루프](docs/implementation/active/2026-04-10-phase4-promptops-agent-loop/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `claude`, updated: `2026-04-10T00:00:00+09:00`

## Priority Snapshot

- `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`: active 1건
- `Phase 5: 스크래퍼/데이터 계층 보강`: active 1건

## Recent Archive

- [Phase 4: PromptOps 에이전트 통합 자동화](docs/implementation/archive/2026/2026-04-10-phase4-promptops-automation/index.md) — `2026-04-10T16:04:31+09:00`
- [Phase 5-1: Jobkorea 멀티소스 스크래퍼 확장](docs/implementation/archive/2026/2026-04-10-phase5-1-jobkorea-scraper/index.md) — `2026-04-10T16:04:31+09:00`
- [하네스 엔지니어링 전환 보완 계획](docs/implementation/archive/2026/2026-04-10-harness-engineering-transition-gap-plan/index.md) — `2026-04-10T15:28:52+09:00`
- [문서 운영 구조 재편 및 계획 자동 저장 체계](docs/implementation/archive/2026/2026-04-10-documentation-operations-rework/index.md) — `2026-04-10T15:12:15+09:00`
- [Onboarding Profile Schema Refactor](docs/implementation/archive/2026/2026-04-10-onboarding-profile-schema-refactor/index.md) — `2026-04-10T15:11:59+09:00`
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
