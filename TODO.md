# TODO.md

이 문서는 현재 진행 중인 implementation plan package의 가벼운 인덱스입니다.
상세 계획의 canonical source는 [`docs/implementation/active/`](docs/implementation/active/)이며, 구조 규칙은 [`docs/implementation/README.md`](docs/implementation/README.md)를 따릅니다.

## 운영 원칙

- 새 계획 저장: `python3 scripts/implementation_docs.py save-plan --agent <agent> --milestone "<milestone>" --stdin-markdown`
- 완료 후 archive: `python3 scripts/implementation_docs.py archive-plan <plan_id>`
- 인덱스 재동기화: `python3 scripts/implementation_docs.py sync-indexes`
- 정합성 검증: `python3 scripts/implementation_docs.py validate`
- `TODO.md`는 active한 세션 단위 task 인덱스만 노출합니다.
- 읽는 계층은 `Milestone -> Track/Workstream -> Task`이지만, 실제 착수와 handoff 기준은 항상 task입니다.
- 각 task는 세션 1개가 책임지는 범위와 명확한 산출물을 가져야 합니다.
- 각 task는 사용자가 직접 확인할 수 있는 UI/CLI/테스트 검증 경로를 포함해야 합니다.
- 상위 방향 정렬용 문서는 `docs/implementation/active/` 아래에 두더라도 `status: reference`로 관리하고 managed index에는 노출하지 않습니다.

## 현재 실행 우선순위

harness + agent 전환을 현재 최상위 목표로 두되, broad phase가 아니라 검증 가능한 task를 먼저 쌓는 것을 우선합니다.

첫 실행 순서는 아래 3개로 고정합니다.

1. `/internal/prompts route shell`
   - 산출물: `/internal/prompts` 진입 라우트와 기본 화면 골격
   - 검증: 브라우저에서 해당 경로가 정상적으로 열리는지 확인
2. `golden dataset loader`
   - 산출물: 운영 화면이 읽을 수 있는 golden dataset 로더
   - 검증: 테스트 또는 CLI/서버 호출로 dataset 구조 확인
3. `prompt dataset list rendering`
   - 산출물: dataset 목록/상태를 보여주는 첫 UI 연결
   - 검증: `/internal/prompts`에서 목록과 상태가 보이는지 확인

제품 기능 확장 자체보다 "하네스와 에이전트가 한국어 서비스 맥락에서 다음 행동을 정하고, 운영자가 그 결과를 직접 이해하고 검증할 수 있는 구조"를 먼저 굳히는 것을 기본 원칙으로 둡니다.

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
## Active Plans

- [PromptOps analyze_iteration CLI output](docs/implementation/active/2026-04-13-promptops-analyze-iteration-cli-output/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea listing parser](docs/implementation/active/2026-04-13-jobkorea-listing-parser/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [PromptOps analyze_iteration smoke run](docs/implementation/active/2026-04-13-promptops-analyze-iteration-smoke-run/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea config field](docs/implementation/active/2026-04-13-jobkorea-config-field/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea normalizer wiring](docs/implementation/active/2026-04-13-jobkorea-normalizer-wiring/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea detail parser](docs/implementation/active/2026-04-13-jobkorea-detail-parser/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [PromptOps analyze_iteration tests](docs/implementation/active/2026-04-13-promptops-analyze-iteration-tests/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea ingest integration](docs/implementation/active/2026-04-13-jobkorea-ingest-integration/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea fixture pack](docs/implementation/active/2026-04-13-jobkorea-fixture-pack/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Jobkorea scraper registry registration](docs/implementation/active/2026-04-13-jobkorea-scraper-registry-registration/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [Multi-source ingest regression](docs/implementation/active/2026-04-13-multi-source-ingest-regression/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `codex`, updated: `2026-04-13T14:48:47+09:00`
- [PromptOps /internal/prompts route shell](docs/implementation/active/2026-04-13-promptops-internal-prompts-route-shell/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps metric glossary document](docs/implementation/active/2026-04-13-promptops-metric-glossary-document/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps prompt dataset loader tests](docs/implementation/active/2026-04-13-promptops-dataset-loader-tests/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps metric terminology alignment](docs/implementation/active/2026-04-13-promptops-metric-terminology-alignment/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps prompt dataset list rendering](docs/implementation/active/2026-04-13-promptops-dataset-list-rendering/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps golden dataset loader](docs/implementation/active/2026-04-13-promptops-golden-dataset-loader/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps current metrics UI exposure](docs/implementation/active/2026-04-13-promptops-current-metrics-ui-exposure/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`
- [PromptOps iteration report parsing contract](docs/implementation/active/2026-04-13-promptops-iteration-report-parsing-contract/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-13T14:48:46+09:00`

## Priority Snapshot

- `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`: active 11건
- `Phase 5: 스크래퍼/데이터 계층 보강`: active 8건

## Recent Archive

- [Phase 4-1 보완: job_eval_gold.json 한국어 공고 기준 정렬](docs/implementation/archive/2026/2026-04-12-phase4-1-fixture-evaluator-alignment/index.md) — `2026-04-13T14:12:49+09:00`
- [worktree port policy 버그 수정 및 main 머지](docs/implementation/archive/2026/2026-04-12-worktree-port-policy-fix-and-merge/index.md) — `2026-04-12T16:50:16+09:00`
- [Phase 4-2: PromptOps 운영 패널 정보구조 개선](docs/implementation/archive/2026/2026-04-12-phase4-2-promptops-ops-ui-clarity/index.md) — `2026-04-12T14:30:30+09:00`
- [Phase 4-1: PromptOps 한국어 실험 기준 전환](docs/implementation/archive/2026/2026-04-12-phase4-1-promptops-korean-experiment-migration/index.md) — `2026-04-12T13:52:33+09:00`
- [Phase 4: PromptOps 에이전트 통합 자동화](docs/implementation/archive/2026/2026-04-10-phase4-promptops-automation/index.md) — `2026-04-10T16:04:31+09:00`
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
