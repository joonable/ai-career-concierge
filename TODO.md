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

## 현재 실행 우선순위

harness + agent 전환을 현재 최상위 목표로 두되, PromptOps를 실제 운영 가능한 상태로 정리하는 것을 우선합니다.

1. `Phase 4-1: PromptOps 한국어 실험 기준 전환`
   - 이유: 한국어 서비스 기준으로 실험 데이터와 해석을 먼저 맞춰야 review와 비교 결과가 실제 운영 판단에 의미를 갖기 때문입니다.
2. `Phase 4-2: PromptOps 운영 패널 정보구조 개선`
   - 이유: 실험/비교 추적과 후속 액션 추적을 관리자 화면에서 명확히 분리해 보여줘야 PromptOps 흐름이 운영 관점에서 이해 가능해지기 때문입니다.
3. `Phase 4-3: PromptOps 평가 지표 가이드 및 현재 사용 지표 노출`
   - 이유: metric 의미와 현재 사용 지표를 함께 설명해야 운영자가 결과를 해석하고 backlog 우선순위를 판단할 수 있기 때문입니다.
4. `Phase 4: PromptOps 에이전트 분석 루프`
   - 이유: 위 세 plan으로 운영 해석층을 정비한 뒤, iteration report → structured JSON → next action 결정 루프를 안정적으로 확장할 수 있기 때문입니다.
5. `Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)`
   - 이유: PromptOps control plane과 운영 가시성이 정리된 뒤 scraper 도메인에 harness + agent 패턴을 적용하는 것이 검증 비용을 줄이기 때문입니다.

제품 기능 확장 자체보다 "하네스와 에이전트가 한국어 서비스 맥락에서 다음 행동을 정하고, 운영자가 그 결과를 이해하고 검증할 수 있는 구조"를 먼저 굳히는 것을 기본 원칙으로 둡니다.

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
## Active Plans

- [Phase 4-1: PromptOps 한국어 실험 기준 전환](docs/implementation/active/2026-04-12-phase4-1-promptops-korean-experiment-migration/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-12T12:16:37+09:00`
- [Phase 4-2: PromptOps 운영 패널 정보구조 개선](docs/implementation/active/2026-04-12-phase4-2-promptops-ops-ui-clarity/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-12T12:16:37+09:00`
- [Phase 4-3: PromptOps 평가 지표 가이드 및 현재 사용 지표 노출](docs/implementation/active/2026-04-12-phase4-3-promptops-metric-glossary/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-12T12:16:37+09:00`
- [Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)](docs/implementation/active/2026-04-10-phase5-1-jobkorea-scraper-agentic/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `claude`, updated: `2026-04-10T00:00:00+09:00`
- [Phase 4: PromptOps 에이전트 분석 루프](docs/implementation/active/2026-04-10-phase4-promptops-agent-loop/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `claude`, updated: `2026-04-10T00:00:00+09:00`

## Priority Snapshot

- `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`: active 4건
- `Phase 5: 스크래퍼/데이터 계층 보강`: active 1건

## Recent Archive

- [Phase 4: PromptOps 에이전트 통합 자동화](docs/implementation/archive/2026/2026-04-10-phase4-promptops-automation/index.md) — `2026-04-10T16:04:31+09:00`
- [Phase 5-1: Jobkorea 멀티소스 스크래퍼 확장](docs/implementation/archive/2026/2026-04-10-phase5-1-jobkorea-scraper/index.md) — `2026-04-10T16:04:31+09:00`
- [하네스 엔지니어링 전환 보완 계획](docs/implementation/archive/2026/2026-04-10-harness-engineering-transition-gap-plan/index.md) — `2026-04-10T15:28:52+09:00`
- [문서 운영 구조 재편 및 계획 자동 저장 체계](docs/implementation/archive/2026/2026-04-10-documentation-operations-rework/index.md) — `2026-04-10T15:12:15+09:00`
- [Onboarding Profile Schema Refactor](docs/implementation/archive/2026/2026-04-10-onboarding-profile-schema-refactor/index.md) — `2026-04-10T15:11:59+09:00`
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
