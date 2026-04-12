# 운영 패널 문서 계약

날짜: 2026-03-31 (Asia/Seoul)

이 문서는 `/internal` 운영 패널이 어떤 문서를 읽고, 무엇을 보여주고, 어떤 종류의 수정 동선을 제공해야 하는지 정의하는 기준서입니다.

## 목표

- 운영 패널이 단순 링크 모음이 아니라 현재 제품과 운영 상태를 한눈에 보여주는 내부 cockpit 역할을 하게 합니다.
- 핵심 문서와 실제 작업 상태를 UI에서 바로 확인할 수 있게 합니다.
- 에이전트가 작업을 많이 하더라도 운영자가 “무엇이 바뀌었는지”를 직접 느낄 수 있게 만듭니다.

## 운영 패널이 다뤄야 하는 핵심 문서

- `AGENTS.md`
- `docs/CONTEXT.md`
- `docs/TRD.md`
- `docs/PRD.md`
- `docs/internal/status.md`
- `docs/promptops/README.md`
- `docs/promptops/status.md`

## 최소 노출 기능

- 핵심 문서 레지스트리
  - 문서 제목, 역할, 왜 중요한지, 마지막 업데이트 맥락을 함께 보여줍니다.
- 최근 작업 요약
  - 최근 완료 작업, 현재 작업 상태, 다음 action, backlog를 보여줍니다.
- 검증 경로
  - 각 작업이 어디서 확인 가능한지 `UI 확인 위치` 또는 관련 링크를 함께 노출합니다.
- 운영 링크
  - PromptOps, iteration 기록, backlog 문서 같은 운영 링크를 카드 또는 섹션으로 묶어 보여줍니다.

## 멀티 에이전트 개발 진입 정책

- `scripts/start_agent_task.sh`와 `scripts/start_integration_task.sh`를 worktree 시작의 공통 진입점으로 사용합니다.
- Codex, Claude, Gemini, integration worktree는 모두 동일한 bootstrap 규칙을 따라 `apps/web/.env.development.local`을 자동 생성해야 합니다.
- bootstrap 산출물은 최소한 다음 값을 포함해야 합니다:
  - worktree 전용 `PORT`
  - `NEXT_PUBLIC_API_BASE_URL`
  - `NEXT_PUBLIC_SUPABASE_URL`
  - `NEXT_PUBLIC_SUPABASE_ANON_KEY`
  - `PROMPTOPS_ADMIN_EMAILS`
  - `PROMPTOPS_DEV_BYPASS`
- 로컬 `npm run dev`는 env에 기록된 `PORT`를 실제 Next.js dev server 포트로 사용해야 합니다.
- 공개 env가 비어 있으면 fallback 값으로 조용히 진행하지 말고, 개발자가 즉시 원인을 알 수 있게 fail-fast 해야 합니다.

## PromptOps dev bypass 규칙

- `PROMPTOPS_DEV_BYPASS`는 로컬 개발에서 운영 UI 구조를 확인하기 위한 dev-only 예외입니다.
- 이 bypass는 `NODE_ENV != production`일 때만 허용합니다.
- bypass가 켜져 있어도 production 인증 경로를 대체해서는 안 됩니다.
- bypass가 켜진 상태에서 세션이 없으면 `/internal`, `/internal/prompts`는 문서 + fixture 기반 mock snapshot으로 렌더할 수 있습니다.
- mock snapshot은 운영 화면 확인 용도이며, 실제 compare/review/backlog 링크와 runtime snapshot 해석을 대신하지 않습니다.

## 편집 기능 방향

- 운영 패널은 장기적으로 다음 문서의 수정 동선을 제공하는 것을 목표로 합니다:
  - `docs/internal/status.md`
  - 운영자가 자주 갱신하는 상태성 문서
- 핵심 제품/아키텍처 문서(`AGENTS.md`, `docs/CONTEXT.md`, `docs/TRD.md`, `docs/PRD.md`)는 보기와 수정 진입점을 지원하되, 변경 시 계약 변경임을 명확히 보여줘야 합니다.
- 편집 기능이 아직 준비되지 않은 경우에도, 운영 패널은 최소한 열람과 원문 이동 경로를 제공해야 합니다.

## `docs/internal/status.md` 계약

- 이 문서는 운영 패널이 우선적으로 읽는 상태판(workboard + status) 문서입니다.
- 의미 있는 작업이 끝나면 에이전트는 가능할 때마다 이 문서를 갱신합니다.
- 최소 섹션:
  - `최근 완료 작업`
  - `현재 작업 상태`
  - `다음 action`
  - `backlog`
  - `UI 확인 위치`
  - `참고 문서`

## 운영 패널 정보 구조 제안

- 상단:
  - 오늘의 요약
  - 최근 바뀐 것
  - 지금 해야 할 것
- 중단:
  - 핵심 문서 레지스트리
  - workboard
  - PromptOps 상태
- 하단:
  - backlog
  - 검증 링크
  - 시스템 확장 카드 (scraper / pipeline / delivery)

## 추가 아이디어

- 문서별 마지막 수정 시각, 변경 이유, 관련 작업 링크 노출
- 작업 카드마다 `왜 바꿨는지`, `무엇이 달라졌는지`, `어디서 확인하는지`를 고정 포맷으로 표기
- recent pipeline run 요약과 system log summary를 운영 패널 카드로 합류
- 운영 패널에서 “문서 기준 상태”와 “runtime snapshot”을 나란히 보여 차이를 바로 확인
- 작업 완료 후 agent summary를 축적해 lightweight changelog로 재활용
