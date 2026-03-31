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
- `docs/internal_status.md`
- `docs/agent_workboard.md`
- `docs/PROMPTOPS.md`
- `docs/promptops_status.md`

## 최소 노출 기능

- 핵심 문서 레지스트리
  - 문서 제목, 역할, 왜 중요한지, 마지막 업데이트 맥락을 함께 보여줍니다.
- 최근 작업 요약
  - 최근 완료 작업, 현재 작업 상태, 다음 action, backlog를 보여줍니다.
- 검증 경로
  - 각 작업이 어디서 확인 가능한지 `UI 확인 위치` 또는 관련 링크를 함께 노출합니다.
- 운영 링크
  - PromptOps, iteration 기록, backlog 문서 같은 운영 링크를 카드 또는 섹션으로 묶어 보여줍니다.

## 편집 기능 방향

- 운영 패널은 장기적으로 다음 문서의 수정 동선을 제공하는 것을 목표로 합니다:
  - `docs/internal_status.md`
  - `docs/agent_workboard.md`
  - 운영자가 자주 갱신하는 상태성 문서
- 핵심 제품/아키텍처 문서(`AGENTS.md`, `docs/CONTEXT.md`, `docs/TRD.md`, `docs/PRD.md`)는 보기와 수정 진입점을 지원하되, 변경 시 계약 변경임을 명확히 보여줘야 합니다.
- 편집 기능이 아직 준비되지 않은 경우에도, 운영 패널은 최소한 열람과 원문 이동 경로를 제공해야 합니다.

## `docs/agent_workboard.md` 계약

- 이 문서는 운영 패널이 우선적으로 읽는 현재 상태판입니다.
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
