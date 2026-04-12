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

- `/internal` 대시보드를 비대칭형 레이아웃으로 전면 리디자인 완료
- 문서 뷰어 라우트 신설 및 404 오류 제거
- 로컬 웹서버 Next.js 캐싱 깨짐 이슈 안내 및 복구 완료
- 로그인 / 온보딩 / 대시보드 기초 공사 완료
- PromptOps 운영 패널 초안 구축 및 문서 단일화 정리 완료
- Phase 4-1 PromptOps 한국어 실험 기준 전환 (docs only): 상태/연구 문서, iteration TEMPLATE을 한국어 서비스 기준으로 정렬 (fixture/evaluator 코드 보완은 별도 plan으로 재개)
- `main` 기준 멀티 에이전트 branch / worktree 규칙 문서화
- 에이전트별 작업 시작 스크립트 및 integration worktree 시작 스크립트 추가
- Claude 로컬 설정에 worktree 시작 규칙 안내 및 branch 가드 보강
- `docs/implementation/active|archive` 기반 plan package 구조, `TODO.md`/`MILESTONE.md` 자동 인덱스, Claude/Gemini plan 저장 훅 도입
- 루트 README, AGENTS, implementation guide를 기준으로 repo 구조와 멀티 에이전트 운영 절차 재정렬
- `docs/internal/status.md` 링크 정합성 및 readiness 체크리스트 정리
- Poetry package 목록에 `promptops` 누락 여부 반영
- 문서 정합성 복구: onboarding schema refactor(설계 완료) 및 documentation-operations-rework(구현 완료) plan package archive 처리
- Phase 4 / Phase 5-1 plan을 Agentic Engineering 관점으로 재구성하고 기존 계획 2개를 archive 처리
- Existing Harness to Agentic Engineering migration 초안을 active plan package로 승격하고 TODO 인덱스 반영 준비
- PromptOps 운영 가시성 정비 계획을 `Phase 4-1/4-2/4-3` active plan으로 분리 저장
- root coordination worktree와 agent execution worktree의 역할 분리를 AGENTS / docs guide / implementation rule / worktree bootstrap 출력에 반영
- 멀티 에이전트 공통 worktree bootstrap 정책 정리: agent/integration 시작 스크립트 모두 web env 자동 생성과 전용 포트 할당을 수행하도록 보강
- PromptOps dev bypass를 로컬 개발 전용 예외로 정의하고 운영 패널 문서 계약 및 컨텍스트 문서에 명시

## 다음 action

- `Phase 4-1 보완`: `job_eval_gold.json` 한국어 공고 기준 정렬 및 evaluator expectation 코드 정렬
- `Phase 4-2 재개`: `/internal/prompts` UI 4개 섹션 재구성 및 golden dataset 로더 구현
- `worktree port policy 버그 수정`: FastAPI 포트 충돌, api_base_url 버그, launch.json 구식 수정 후 main 머지
- `Phase 4-3: PromptOps 평가 지표 가이드 및 현재 사용 지표 노출`로 metric 의미와 현재 사용 지표를 관리자 화면에서 이해 가능하게 만들기
- 위 정비 이후 `Phase 4: PromptOps 에이전트 분석 루프`를 확장해 iteration report → structured JSON → next action 결정 루프를 운영 가능한 수준으로 고도화하기
- PromptOps 운영 해석층 정비 이후 `Phase 5-1: Jobkorea 스크래퍼 (Agentic TDD)`를 통해 scraper 도메인에 harness + agent 실행 흐름을 적용하고 회귀 패턴을 검증하기
- 실제 협업 태스크에서 `codex/*`, `claude/*`, `gemini/*`, `integration/*` 흐름을 운영에 적용하고 충돌 사례를 보정하기
- Codex 쪽 자동 guard / hook 보강이 필요한지 PromptOps/스크래퍼 실전 적용 경험을 바탕으로 판단하기
- Claude/Gemini/integration 경로까지 포함한 bootstrap 정책이 실제 실전 태스크에서 안정적으로 동작하는지 추가 검증하기
- `.agents/` canonical control plane, capability registry, context bundle 도입을 별도 실행 plan으로 분해하기
- docs 기반의 상태판 구조를 파싱하여 예쁘게 렌더링하는 Markdown 뷰어와 `react-markdown` 컴포넌트 작업 완료하기
- Supabase Service Role 정책 적용을 백엔드 통합과 어떻게 분리할지 결정
- LangSmith 추적 (Tracing) 구조 및 ID 설정

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
