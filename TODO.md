# TODO.md

이 문서는 현재 진행 중인 implementation plan package의 가벼운 인덱스입니다.
상세 계획의 canonical source는 [`docs/implementation/active/`](docs/implementation/active/)이며, 구조 규칙은 [`docs/implementation/README.md`](docs/implementation/README.md)를 따릅니다.

## 운영 원칙

- 새 계획 저장: `python3 scripts/implementation_docs.py save-plan --agent <agent> --milestone "<milestone>" --stdin-markdown`
- closeout 점검: `python3 scripts/implementation_docs.py closeout-check <plan_id>`
- 완료 후 기본 closeout: `python3 scripts/implementation_docs.py closeout-plan <plan_id>`
- 인덱스 재동기화: `python3 scripts/implementation_docs.py sync-indexes`
- 정합성 검증: `python3 scripts/implementation_docs.py validate`
- `TODO.md`는 active한 세션 단위 task 인덱스만 노출합니다.
- 읽는 계층은 `Milestone -> Track/Workstream -> Task`이지만, 실제 착수와 handoff 기준은 항상 task입니다.
- 각 task는 세션 1개가 책임지는 범위와 명확한 산출물을 가져야 합니다.
- 각 task는 사용자가 직접 확인할 수 있는 UI/CLI/테스트 검증 경로를 포함해야 합니다.
- 상위 방향 정렬용 문서는 `docs/implementation/active/` 아래에 두더라도 `status: reference`로 관리하고 managed index에는 노출하지 않습니다.

## 현재 실행 우선순위

harness + agent 전환을 현재 최상위 목표로 두되, broad phase가 아니라 사람이 바로 읽고 판단할 수 있는 `Milestone -> Track -> Task` 계층으로 남은 작업을 관리합니다.

### Phase 3: PromptOps 자동화 및 에이전트 운영 확장

- Track A. `/internal/prompts` 운영 화면
  - Task: [PromptOps /internal/prompts route shell](docs/implementation/active/2026-04-13-promptops-internal-prompts-route-shell/index.md)
    - 산출물: `/internal/prompts` 진입 라우트와 기본 화면 골격
    - 검증: 브라우저에서 해당 경로가 정상적으로 열리는지 확인
  - Task: [PromptOps golden dataset loader](docs/implementation/active/2026-04-13-promptops-golden-dataset-loader/index.md)
    - 산출물: 운영 화면이 읽을 수 있는 golden dataset 로더
    - 검증: 테스트 또는 CLI/서버 호출로 dataset 구조 확인
  - Task: [PromptOps prompt dataset list rendering](docs/implementation/active/2026-04-13-promptops-dataset-list-rendering/index.md)
    - 산출물: dataset 목록/상태를 보여주는 첫 UI 연결
    - 검증: `/internal/prompts`에서 목록과 상태가 보이는지 확인
  - Task: [PromptOps prompt dataset loader tests](docs/implementation/active/2026-04-13-promptops-dataset-loader-tests/index.md)
    - 산출물: dataset 로더 회귀 테스트
    - 검증: 관련 `pytest` 통과

- Track B. PromptOps metric 해석
  - Task: [PromptOps metric glossary document](docs/implementation/active/2026-04-13-promptops-metric-glossary-document/index.md)
    - 산출물: metric 의미와 해석 기준 문서
    - 검증: 문서만 읽고 현재 metric 의미를 이해할 수 있는지 확인
  - Task: [PromptOps current metrics UI exposure](docs/implementation/active/2026-04-13-promptops-current-metrics-ui-exposure/index.md)
    - 산출물: 운영 화면의 현재 metric 노출 섹션
    - 검증: 운영 화면에서 현재 사용 지표가 보이는지 확인
  - Task: [PromptOps metric terminology alignment](docs/implementation/active/2026-04-13-promptops-metric-terminology-alignment/index.md)
    - 산출물: 문서와 UI 간 metric 용어 정렬
    - 검증: 문서와 화면을 나란히 봤을 때 용어가 일치하는지 확인

- Track C. PromptOps agent analysis loop
  - Task: [PromptOps iteration report parsing contract](docs/implementation/active/2026-04-13-promptops-iteration-report-parsing-contract/index.md)
    - 산출물: iteration report parsing 계약
    - 검증: fixture 또는 문서로 파싱 필드를 이해할 수 있는지 확인
  - Task: [PromptOps analyze_iteration CLI output](docs/implementation/active/2026-04-13-promptops-analyze-iteration-cli-output/index.md)
    - 산출물: 구조화 JSON을 출력하는 CLI 엔트리포인트
    - 검증: CLI 실행 시 JSON 출력 생성 확인
  - Task: [PromptOps analyze_iteration tests](docs/implementation/active/2026-04-13-promptops-analyze-iteration-tests/index.md)
    - 산출물: analyze_iteration 회귀 테스트
    - 검증: 관련 `pytest` 통과
  - Task: [PromptOps analyze_iteration smoke run](docs/implementation/active/2026-04-13-promptops-analyze-iteration-smoke-run/index.md)
    - 산출물: 기존 iteration 문서 기반 smoke 검증 결과
    - 검증: 실제 iteration 문서 입력으로 CLI 실행 성공

### Phase 5: 스크래퍼/데이터 계층 보강

- Track A. Jobkorea parser foundation
  - Task: [Jobkorea fixture pack](docs/implementation/active/2026-04-13-jobkorea-fixture-pack/index.md)
    - 산출물: 목록/상세 HTML fixture 세트
    - 검증: fixture 파일과 샘플 구조 확인
  - Task: [Jobkorea listing parser](docs/implementation/active/2026-04-13-jobkorea-listing-parser/index.md)
    - 산출물: 목록 카드 추출 로직
    - 검증: 관련 unit test 통과
  - Task: [Jobkorea detail parser](docs/implementation/active/2026-04-13-jobkorea-detail-parser/index.md)
    - 산출물: 상세 JD/식별자 파싱 로직
    - 검증: 관련 unit test 통과
  - Task: [Jobkorea normalizer wiring](docs/implementation/active/2026-04-13-jobkorea-normalizer-wiring/index.md)
    - 산출물: 정규화 계층 연결 결과
    - 검증: URL 정규화/짧은 JD 거부 테스트 통과

- Track B. Runtime wiring
  - Task: [Jobkorea config field](docs/implementation/active/2026-04-13-jobkorea-config-field/index.md)
    - 산출물: Jobkorea 관련 config 필드와 validation 규칙
    - 검증: config validation test 통과
  - Task: [Jobkorea scraper registry registration](docs/implementation/active/2026-04-13-jobkorea-scraper-registry-registration/index.md)
    - 산출물: runtime registry 내 Jobkorea source 등록
    - 검증: runtime 관련 테스트나 확인 코드로 source 등록 확인

- Track C. Ingest verification
  - Task: [Jobkorea ingest integration](docs/implementation/active/2026-04-13-jobkorea-ingest-integration/index.md)
    - 산출물: Jobkorea ingest integration test
    - 검증: 관련 integration test 통과
  - Task: [Multi-source ingest regression](docs/implementation/active/2026-04-13-multi-source-ingest-regression/index.md)
    - 산출물: Incruit + Jobkorea 회귀 테스트
    - 검증: 관련 integration test 통과

### 첫 착수 순서

1. `PromptOps /internal/prompts route shell`
2. `PromptOps golden dataset loader`
3. `PromptOps prompt dataset list rendering`

제품 기능 확장 자체보다 "하네스와 에이전트가 한국어 서비스 맥락에서 다음 행동을 정하고, 운영자가 그 결과를 직접 이해하고 검증할 수 있는 구조"를 먼저 굳히는 것을 기본 원칙으로 둡니다.

<!-- BEGIN MANAGED:IMPLEMENTATION_INDEX -->
## Priority Snapshot

- `Phase 3: PromptOps 자동화 및 에이전트 운영 확장`: active 9건
- `Phase 5: 스크래퍼/데이터 계층 보강`: active 8건

## Recent Archive

- [PromptOps golden dataset loader](docs/implementation/archive/2026/2026-04-13-promptops-golden-dataset-loader/index.md) — `2026-04-13T15:39:15+09:00`
- [PromptOps /internal/prompts route shell](docs/implementation/archive/2026/2026-04-13-promptops-internal-prompts-route-shell/index.md) — `2026-04-13T15:33:22+09:00`
- [Phase 4-1 보완: job_eval_gold.json 한국어 공고 기준 정렬](docs/implementation/archive/2026/2026-04-12-phase4-1-fixture-evaluator-alignment/index.md) — `2026-04-13T14:12:49+09:00`
- [worktree port policy 버그 수정 및 main 머지](docs/implementation/archive/2026/2026-04-12-worktree-port-policy-fix-and-merge/index.md) — `2026-04-12T16:50:16+09:00`
- [Phase 4-2: PromptOps 운영 패널 정보구조 개선](docs/implementation/archive/2026/2026-04-12-phase4-2-promptops-ops-ui-clarity/index.md) — `2026-04-12T14:30:30+09:00`
<!-- END MANAGED:IMPLEMENTATION_INDEX -->
