# MILESTONE.md

프로젝트의 phase별 진행 맥락과 implementation 이력을 추적하는 인덱스입니다.
세부 계획은 `TODO.md`가 아니라 `docs/implementation/active/` 아래 plan package를 source of truth로 사용합니다.

## Phase Overview

- `Phase 0`: 프로젝트 초기화와 기술 스택 확정
- `Phase 1`: 단일 사용자 수직 슬라이스 PoC 구현
- `Phase 2`: 하네스 엔지니어링과 멀티 에이전트 운영 표준화
- `Phase 3`: PromptOps 자동화 및 에이전트 운영 확장
- `Phase 4`: PromptOps 운영 루프와 평가 해석 계층 고도화
- `Phase 5`: 스크래퍼/데이터 계층/멀티유저 기반 보강

<!-- BEGIN MANAGED:MILESTONE_INDEX -->
## Active By Milestone

### Phase 3: PromptOps 자동화 및 에이전트 운영 확장

- [PromptOps analyze_iteration CLI output](docs/implementation/active/2026-04-13-promptops-analyze-iteration-cli-output/index.md) — `2026-04-13T14:48:47+09:00`
- [PromptOps analyze_iteration smoke run](docs/implementation/active/2026-04-13-promptops-analyze-iteration-smoke-run/index.md) — `2026-04-13T14:48:47+09:00`
- [PromptOps analyze_iteration tests](docs/implementation/active/2026-04-13-promptops-analyze-iteration-tests/index.md) — `2026-04-13T14:48:47+09:00`
- [PromptOps metric glossary document](docs/implementation/active/2026-04-13-promptops-metric-glossary-document/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps prompt dataset loader tests](docs/implementation/active/2026-04-13-promptops-dataset-loader-tests/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps metric terminology alignment](docs/implementation/active/2026-04-13-promptops-metric-terminology-alignment/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps prompt dataset list rendering](docs/implementation/active/2026-04-13-promptops-dataset-list-rendering/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps current metrics UI exposure](docs/implementation/active/2026-04-13-promptops-current-metrics-ui-exposure/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps iteration report parsing contract](docs/implementation/active/2026-04-13-promptops-iteration-report-parsing-contract/index.md) — `2026-04-13T14:48:46+09:00`

### Phase 5: 스크래퍼/데이터 계층 보강

- [Jobkorea listing parser](docs/implementation/active/2026-04-13-jobkorea-listing-parser/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea config field](docs/implementation/active/2026-04-13-jobkorea-config-field/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea normalizer wiring](docs/implementation/active/2026-04-13-jobkorea-normalizer-wiring/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea detail parser](docs/implementation/active/2026-04-13-jobkorea-detail-parser/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea ingest integration](docs/implementation/active/2026-04-13-jobkorea-ingest-integration/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea fixture pack](docs/implementation/active/2026-04-13-jobkorea-fixture-pack/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea scraper registry registration](docs/implementation/active/2026-04-13-jobkorea-scraper-registry-registration/index.md) — `2026-04-13T14:48:47+09:00`
- [Multi-source ingest regression](docs/implementation/active/2026-04-13-multi-source-ingest-regression/index.md) — `2026-04-13T14:48:47+09:00`

## History Timeline

### 2026

- [PromptOps golden dataset loader](docs/implementation/archive/2026/2026-04-13-promptops-golden-dataset-loader/index.md) — `Phase 3: PromptOps 자동화 및 에이전트 운영 확장` / `2026-04-13T15:39:15+09:00`
- [PromptOps /internal/prompts route shell](docs/implementation/archive/2026/2026-04-13-promptops-internal-prompts-route-shell/index.md) — `Phase 3: PromptOps 자동화 및 에이전트 운영 확장` / `2026-04-13T15:33:22+09:00`
- [Phase 4-1 보완: job_eval_gold.json 한국어 공고 기준 정렬](docs/implementation/archive/2026/2026-04-12-phase4-1-fixture-evaluator-alignment/index.md) — `Phase 3: PromptOps 자동화 및 에이전트 운영 확장` / `2026-04-13T14:12:49+09:00`
- [worktree port policy 버그 수정 및 main 머지](docs/implementation/archive/2026/2026-04-12-worktree-port-policy-fix-and-merge/index.md) — `Phase 2: 하네스 엔지니어링` / `2026-04-12T16:50:16+09:00`
- [Phase 4-2: PromptOps 운영 패널 정보구조 개선](docs/implementation/archive/2026/2026-04-12-phase4-2-promptops-ops-ui-clarity/index.md) — `Phase 3: PromptOps 자동화 및 에이전트 운영 확장` / `2026-04-12T14:30:30+09:00`
- [Phase 4-1: PromptOps 한국어 실험 기준 전환](docs/implementation/archive/2026/2026-04-12-phase4-1-promptops-korean-experiment-migration/index.md) — `Phase 3: PromptOps 자동화 및 에이전트 운영 확장` / `2026-04-12T13:52:33+09:00`
- [Phase 4: PromptOps 에이전트 통합 자동화](docs/implementation/archive/2026/2026-04-10-phase4-promptops-automation/index.md) — `Phase 3: PromptOps 자동화 및 에이전트 운영 확장` / `2026-04-10T16:04:31+09:00`
- [Phase 5-1: Jobkorea 멀티소스 스크래퍼 확장](docs/implementation/archive/2026/2026-04-10-phase5-1-jobkorea-scraper/index.md) — `Phase 5: 스크래퍼/데이터 계층 보강` / `2026-04-10T16:04:31+09:00`
- [하네스 엔지니어링 전환 보완 계획](docs/implementation/archive/2026/2026-04-10-harness-engineering-transition-gap-plan/index.md) — `Phase 2: 하네스 엔지니어링` / `2026-04-10T15:28:52+09:00`
- [문서 운영 구조 재편 및 계획 자동 저장 체계](docs/implementation/archive/2026/2026-04-10-documentation-operations-rework/index.md) — `Phase 2: 하네스 엔지니어링` / `2026-04-10T15:12:15+09:00`
- [Onboarding Profile Schema Refactor](docs/implementation/archive/2026/2026-04-10-onboarding-profile-schema-refactor/index.md) — `Backlog` / `2026-04-10T15:11:59+09:00`
<!-- END MANAGED:MILESTONE_INDEX -->
