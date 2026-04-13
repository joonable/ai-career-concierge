# 내부 대시보드 상태판

이 문서는 개발팀과 운영팀이 실시간으로 공유하는 상황판(Single Source of Truth)입니다.
웹 대시보드의 `/internal` 패널에서 이 파일을 파싱하여 렌더링하므로 형식을 준수해야 합니다.

## 날짜: 2026-04-12 (Asia/Seoul)

## 핵심 문서 및 참고 링크

- [AGENTS.md](../../AGENTS.md)
- [프로젝트 컨텍스트](../CONTEXT.md)
- [초기 제품 요구사항 (PRD)](../PRD.md)
- [기술 요구사항 결정 (TRD)](../TRD.md)
- [운영 패널 컴포넌트 정리](./operations_panel.md)
- [Implementation 문서 가이드](../implementation/README.md)

## 시스템 및 에이전트 관점 (Operations & Agent)

- PromptOps lineage / compare / review / iteration 동선 정리
- 운영 패널에서 핵심 문서와 작업 보드를 직접 활용하는 방향으로 문서 계약 확장
- LangGraph 워크플로우를 Agentic 구조로 모듈화 리팩터링 진행
- assistant-neutral control plane, context router, capability pack, runner 구조로의 migration plan을 `docs/implementation/active/2026-04-10-agentic-engineering-migration-plan/`에 활성 계획으로 정리
- 현재 active plan의 우선순위는 기능 확장보다 harness + agent 전환을 먼저 두며, `Phase 4: PromptOps 에이전트 분석 루프`를 `Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)`보다 선행 과제로 해석
- PromptOps 운영 가시성 정비를 위해 한국어 실험 기준 전환, 운영 패널 정보구조 개선, 평가 지표 가이드 노출을 별도 active plan 3개로 분리 저장
- `/internal/prompts`를 현재 상태, 실험/비교 추적, 후속 액션 추적, golden dataset 기준 흐름으로 재구성해 운영 판단 동선을 명확히 정리
- canonical 문서(`docs/`, `TODO.md`, `MILESTONE.md`, `docs/internal/status.md`, `docs/implementation/active/`)는 루트 저장소에서 관리하고 agent worktree는 실행 전용으로 구분하는 정책을 문서와 스크립트에 반영
- 채용 플랫폼 사이트별 Scraper 로깅 한계 파악 및 에러 복구 제어 연구
- Codex / Claude / Gemini 협업을 위한 `main` 기준 멀티 worktree 운영 표준 도입
- implementation plan package 구조와 자동 저장 훅 기반 문서 운영 체계 도입

## 현재 협업 readiness

- 현재 판정: `partially ready`
- 준비된 것
  - `main` 기준 agent / integration worktree 스크립트 존재
  - `python3 scripts/implementation_docs.py validate` 통과 가능
  - plan package와 상태판 기반 운영 문서 흐름 존재
  - `git worktree list` 기준 Codex / Claude / Gemini / integration 예시가 실제로 구성 가능
- 남은 갭
  - Codex 전용 자동 hook / guard는 Claude, Gemini보다 약함
  - 운영 문서 링크와 canonical 문서 목록은 계속 정리 필요
  - 로컬 산출물 경계와 root worktree 역할을 운영 문서로 계속 명확히 해야 함
  - 실전 멀티 에이전트 태스크 운영 기록이 더 필요함

## 유저 및 제품 관점 (User & Product UX)

- 로그인, 인증 콜백, 프로필 정보, 대시보드 구조에 대한 `apps/web` 수직 슬라이스 완성도 높이기
- 유저 모델의 구직 요건(희망 직무, 지역, 기타) 입력 플로우 구체화
- UI/UX Asymmetric Dashboard 뷰 리디자인에 맞춘 세부 카드 스타일 개선

## 최근 완료 작업 (Done)

<!-- BEGIN MANAGED:STATUS_DONE -->
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
<!-- END MANAGED:STATUS_DONE -->

## 다음 action

<!-- BEGIN MANAGED:STATUS_NEXT_ACTIONS -->
- [PromptOps analyze_iteration CLI output](docs/implementation/active/2026-04-13-promptops-analyze-iteration-cli-output/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea listing parser](docs/implementation/active/2026-04-13-jobkorea-listing-parser/index.md) — `2026-04-13T14:48:47+09:00`
- [PromptOps analyze_iteration smoke run](docs/implementation/active/2026-04-13-promptops-analyze-iteration-smoke-run/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea config field](docs/implementation/active/2026-04-13-jobkorea-config-field/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea normalizer wiring](docs/implementation/active/2026-04-13-jobkorea-normalizer-wiring/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea detail parser](docs/implementation/active/2026-04-13-jobkorea-detail-parser/index.md) — `2026-04-13T14:48:47+09:00`
- [PromptOps analyze_iteration tests](docs/implementation/active/2026-04-13-promptops-analyze-iteration-tests/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea ingest integration](docs/implementation/active/2026-04-13-jobkorea-ingest-integration/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea fixture pack](docs/implementation/active/2026-04-13-jobkorea-fixture-pack/index.md) — `2026-04-13T14:48:47+09:00`
- [Jobkorea scraper registry registration](docs/implementation/active/2026-04-13-jobkorea-scraper-registry-registration/index.md) — `2026-04-13T14:48:47+09:00`
- [Multi-source ingest regression](docs/implementation/active/2026-04-13-multi-source-ingest-regression/index.md) — `2026-04-13T14:48:47+09:00`
- [PromptOps metric glossary document](docs/implementation/active/2026-04-13-promptops-metric-glossary-document/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps prompt dataset loader tests](docs/implementation/active/2026-04-13-promptops-dataset-loader-tests/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps metric terminology alignment](docs/implementation/active/2026-04-13-promptops-metric-terminology-alignment/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps prompt dataset list rendering](docs/implementation/active/2026-04-13-promptops-dataset-list-rendering/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps current metrics UI exposure](docs/implementation/active/2026-04-13-promptops-current-metrics-ui-exposure/index.md) — `2026-04-13T14:48:46+09:00`
- [PromptOps iteration report parsing contract](docs/implementation/active/2026-04-13-promptops-iteration-report-parsing-contract/index.md) — `2026-04-13T14:48:46+09:00`
<!-- END MANAGED:STATUS_NEXT_ACTIONS -->

## backlog

- **시스템/운영**: `/internal` 대시보드 내 시스템 로그(API 응답/오류 로그, 채용 공고 수집 실패 등) 및 Playwright 기반 Scraper 상태를 모니터링할 전용 인디케이터 시각화 추가
- **개선**: 피드백 수집 및 단기 기억(short-term memory) 로직을 Next.js API와 엮어보기
- **기술 부채**: UI 레벨에서 `error.tsx`, `loading.tsx` 스켈레톤 로딩 보강

## 프로젝트 milestone 및 진행상황

- `Phase 1`: 단일 유저 수직 횡단(Vertical Slice) 아키텍처 및 Supabase 인증 PoC (진행 중)
- `Phase 2`: 핵심 LangGraph 평가 파이프라인 연동 확인
- `Phase 3`: Slack 알림 봇 딜리버리 및 긍정/부정(Like/Dislike) 피드백 루프 구축

## 운영 메모

- Next.js 로컬 구동 중 빌드 커맨드가 돌어갈 경우 `.next` 캐시가 날아가 스타일이 꺠질 수 있으니 재시작을 권장함.
- 현재 영속성은 `SUPABASE_SERVICE_ROLE_KEY`를 주로 사용하고 있으며 추후 RLS 정책 반영을 미룸.
- 멀티 에이전트 협업 시작은 저장소 루트에서 `scripts/start_agent_task.sh` 또는 `scripts/start_integration_task.sh`로 통일함.
- 루트 worktree는 관리/리뷰/문서 정리 중심으로 사용하고, 기능 구현은 agent worktree에서 시작하는 것을 기본값으로 둠.
- `.claude/worktrees/`, `.claude/sessions/`, `.gemini/plans/`는 로컬 에이전트 산출물 경로이며 제품 코드의 canonical source가 아님.

## UI 확인 위치

- `/internal`
  - 운영 허브 대시보드 (리디자인 됨)
  - 프롬프트 운영 패널 (`/internal/prompts`) - 상태/실험/액션/golden dataset 기준 흐름 반영
  - [NEW] 마크다운 문서 뷰어 서브라우트 (`/internal/docs`)
- 문서 원문
  - `docs/internal/status.md`
  - `docs/internal/operations_panel.md`
  - `docs/promptops/metric_glossary.md`
