# 내부 대시보드 상태판

이 문서는 개발팀과 운영팀이 실시간으로 공유하는 상황판(Single Source of Truth)입니다.
웹 대시보드의 `/internal` 패널에서 이 파일을 파싱하여 렌더링하므로 형식을 준수해야 합니다.

## 날짜: 2026-04-10 (Asia/Seoul)

## 핵심 문서 및 참고 링크

- [AGENTS.md](../AGENTS.md)
- [프로젝트 컨텍스트](./CONTEXT.md)
- [초기 제품 요구사항 (PRD)](./PRD.md)
- [기술 요구사항 결정 (TRD)](./TRD.md)
- [운영 패널 컴포넌트 정리](./operations_panel.md)

## 시스템 및 에이전트 관점 (Operations & Agent)

- PromptOps lineage / compare / review / iteration 동선 정리
- 운영 패널에서 핵심 문서와 작업 보드를 직접 활용하는 방향으로 문서 계약 확장
- LangGraph 워크플로우를 Agentic 구조로 모듈화 리팩터링 진행
- 채용 플랫폼 사이트별 Scraper 로깅 한계 파악 및 에러 복구 제어 연구
- Codex / Claude / Gemini 협업을 위한 `main` 기준 멀티 worktree 운영 표준 도입

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
- `main` 기준 멀티 에이전트 branch / worktree 규칙 문서화
- 에이전트별 작업 시작 스크립트 및 integration worktree 시작 스크립트 추가
- Claude 로컬 설정에 worktree 시작 규칙 안내 및 branch 가드 보강

## 다음 action

- docs 기반의 상태판 구조를 파싱하여 예쁘게 렌더링하는 Markdown 뷰어와 `react-markdown` 컴포넌트 작업 완료하기
- Supabase Service Role 정책 적용을 백엔드 통합과 어떻게 분리할지 결정
- LangSmith 추적 (Tracing) 구조 및 ID 설정
- 실제 협업 태스크에서 `codex/*`, `claude/*`, `gemini/*`, `integration/*` 흐름을 운영에 적용하고 충돌 사례를 보정하기

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

## UI 확인 위치

- `/internal`
  - 운영 허브 대시보드 (리디자인 됨)
  - 프롬프트 운영 패널 (`/internal/prompts`)
  - [NEW] 마크다운 문서 뷰어 서브라우트 (`/internal/docs`)
- 문서 원문
  - `docs/internal/status.md`
  - `docs/internal/operations_panel.md`
