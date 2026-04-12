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

부분 완료 (docs only — 코드 구현 미완료, 별도 보완 plan 진행 중):

- `Phase 4-1: PromptOps 한국어 실험 기준 전환`
  - 완료: fixture 기대 신호 문서, evaluator 해석 문서, PromptOps 상태/연구 문서 한국어 정렬
  - 미완료: `job_eval_gold.json` 샘플 교체, evaluator expectation 코드 정렬 → `Phase 4-1 보완` plan으로 재개

1. `Phase 4-1 보완: job_eval_gold.json 한국어 공고 기준 정렬`
   - 이유: docs 전환은 완료되었으나 실제 fixture 샘플과 evaluator expectation이 한국어 JD와 정렬되지 않아, 실험 실패 해석 시 영어 mismatch가 여전히 발생하기 때문입니다.
2. `Phase 4-2 재개: /internal/prompts UI 구현 및 golden dataset 로더`
   - 이유: 이전 archive 시도는 docs 수정만 완료되었고 프론트엔드 코드 변경, golden dataset 로더, 테스트가 모두 미구현 상태이기 때문입니다.
3. `worktree port policy 버그 수정 및 main 머지`
   - 이유: `codex/unify-worktree-bootstrap-policy` 브랜치에 FastAPI 포트 충돌, api_base_url 구성 오류, launch.json 구식 등 버그 3개가 미수정 + 미머지 상태로, 멀티 worktree 운영 안정성이 보장되지 않기 때문입니다.
4. `Phase 4-3: PromptOps 평가 지표 가이드 및 현재 사용 지표 노출`
   - 이유: metric 의미와 현재 사용 지표를 함께 설명해야 운영자가 결과를 해석하고 backlog 우선순위를 판단할 수 있기 때문입니다.
5. `Phase 4: PromptOps 에이전트 분석 루프`
   - 이유: 위 plan들로 운영 해석층을 정비한 뒤, iteration report → structured JSON → next action 결정 루프를 안정적으로 확장할 수 있기 때문입니다.
6. `Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)`
   - 이유: PromptOps control plane과 운영 가시성이 정리된 뒤 scraper 도메인에 harness + agent 패턴을 적용하는 것이 검증 비용을 줄이기 때문입니다.

제품 기능 확장 자체보다 "하네스와 에이전트가 한국어 서비스 맥락에서 다음 행동을 정하고, 운영자가 그 결과를 이해하고 검증할 수 있는 구조"를 먼저 굳히는 것을 기본 원칙으로 둡니다.

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
## Active Plans

- [worktree port policy 버그 수정 및 main 머지](docs/implementation/active/2026-04-12-worktree-port-policy-fix-and-merge/index.md) — milestone: `Phase 2: 하네스 엔지니어링`, agent: `claude`, updated: `2026-04-12T18:00:00+09:00`
- [Phase 4-1 보완: job_eval_gold.json 한국어 공고 기준 정렬](docs/implementation/active/2026-04-12-phase4-1-fixture-evaluator-alignment/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `claude`, updated: `2026-04-12T18:00:00+09:00`
- [Phase 4-2 재개: /internal/prompts UI 구현 및 golden dataset 로더](docs/implementation/active/2026-04-12-phase4-2-promptops-ops-ui-implementation/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `claude`, updated: `2026-04-12T18:00:00+09:00`
- [Phase 4-3: PromptOps 평가 지표 가이드 및 현재 사용 지표 노출](docs/implementation/active/2026-04-12-phase4-3-promptops-metric-glossary/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `codex`, updated: `2026-04-12T12:16:37+09:00`
- [Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)](docs/implementation/active/2026-04-10-phase5-1-jobkorea-scraper-agentic/index.md) — milestone: `Phase 5: 스크래퍼/데이터 계층 보강`, agent: `claude`, updated: `2026-04-10T00:00:00+09:00`
- [Phase 4: PromptOps 에이전트 분석 루프](docs/implementation/active/2026-04-10-phase4-promptops-agent-loop/index.md) — milestone: `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`, agent: `claude`, updated: `2026-04-10T00:00:00+09:00`

## Priority Snapshot

- `Phase 2: 하네스 엔지니어링`: active 1건
- `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`: active 4건
- `Phase 5: 스크래퍼/데이터 계층 보강`: active 1건

## Recent Archive

- [Phase 4-2: PromptOps 운영 패널 정보구조 개선](docs/implementation/archive/2026/2026-04-12-phase4-2-promptops-ops-ui-clarity/index.md) — `2026-04-12T14:30:30+09:00`
- [Phase 4-1: PromptOps 한국어 실험 기준 전환](docs/implementation/archive/2026/2026-04-12-phase4-1-promptops-korean-experiment-migration/index.md) — `2026-04-12T13:52:33+09:00`
- [Phase 4: PromptOps 에이전트 통합 자동화](docs/implementation/archive/2026/2026-04-10-phase4-promptops-automation/index.md) — `2026-04-10T16:04:31+09:00`
- [Phase 5-1: Jobkorea 멀티소스 스크래퍼 확장](docs/implementation/archive/2026/2026-04-10-phase5-1-jobkorea-scraper/index.md) — `2026-04-10T16:04:31+09:00`
- [하네스 엔지니어링 전환 보완 계획](docs/implementation/archive/2026/2026-04-10-harness-engineering-transition-gap-plan/index.md) — `2026-04-10T15:28:52+09:00`
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
