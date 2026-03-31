# 에이전트 작업 보드

날짜: 2026-03-31 (Asia/Seoul)

이 문서는 `/internal` 운영 패널에서 최근 작업과 현재 상태를 보여주기 위한 canonical workboard입니다.

## 최근 완료 작업

- 에이전트 작업 후 가능하면 UI에서 직접 검증 가능한 형태로 마무리하라는 규칙을 `AGENTS.md`에 반영
- 운영 패널이 핵심 문서와 작업 상태를 적극적으로 활용해야 한다는 방향을 `AGENTS.md`, `docs/CONTEXT.md`, `docs/TRD.md`, `docs/PRD.md`에 반영
- 운영 패널 전용 문서 계약인 `docs/operations_panel.md`를 추가

## 현재 작업 상태

- 현재는 운영 패널 문서 계약과 작업 보드 문서를 정의한 상태
- `/internal`에서 바로 활용할 수 있도록 관련 링크를 `docs/internal_status.md`에 연결한 상태
- 문서 계약은 먼저 정리됐고, 실제 UI 확장은 다음 구현 작업으로 이어질 수 있는 상태

## 다음 action

- `/internal` 운영 허브가 `docs/agent_workboard.md`를 읽어 최근 작업/다음 action/backlog를 별도 카드로 보여주도록 연결
- 핵심 문서 레지스트리 카드에서 `AGENTS.md`, `docs/CONTEXT.md`, `docs/TRD.md`, `docs/PRD.md`를 직접 노출
- 가능하면 운영 패널에서 상태성 markdown 문서를 수정하거나 바로 이동할 수 있는 동선 추가

## backlog

- 문서별 owner, last updated, change reason 메타데이터를 운영 패널에서 읽을 수 있게 문서 계약 확장
- recent pipeline run, scraper health, delivery status를 운영 패널 카드로 합류
- 작업별 `UI 확인 위치`를 구조화된 포맷으로 유지하도록 템플릿화

## UI 확인 위치

- `/internal`
  - 운영 상태 문서의 참고 링크에서 `운영 패널 문서 계약`, `에이전트 작업 보드` 링크 확인 가능
- 문서 원문
  - `docs/internal_status.md`
  - `docs/operations_panel.md`
  - `docs/agent_workboard.md`

## 참고 문서

- [AGENTS.md](../AGENTS.md)
- [프로젝트 컨텍스트](./CONTEXT.md)
- [TRD](./TRD.md)
- [PRD](./PRD.md)
- [운영 패널 문서 계약](./operations_panel.md)
- [Internal 운영 상태](./internal_status.md)
