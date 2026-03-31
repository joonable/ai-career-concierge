# Internal 운영 상태

날짜: 2026-03-31 (Asia/Seoul)

이 문서는 `/internal` 운영 허브에서 보여주는 canonical 상태 요약입니다.

## 현재 작업 중

- `/internal` 운영 허브와 `/internal/prompts` 전용 작업대 분리
- docs 기반 상태판 구조 정리와 카드형 정보 계층 고정
- PromptOps lineage / compare / review / iteration 동선 정리
- 운영 패널에서 핵심 문서와 작업 보드를 직접 활용하는 방향으로 문서 계약 확장

## 프로젝트 milestone 및 진행상황

- 로그인 / 온보딩 / 대시보드 수직 슬라이스: 완료
- PromptOps 운영 패널 초안: 완료
- Internal 운영 허브 정보 구조 정리: 진행 중
- docs 기반 운영 기록 정착: 진행 중
- 운영 패널 문서 레지스트리 및 작업 보드 계약 정리: 완료

## 지금 해야 할 action

- 운영 허브에서 지금 해야 할 action이 먼저 보이도록 섹션 우선순위 유지
- milestone과 backlog를 문서 기준으로 계속 갱신
- Prompt workspace에서 최신 iteration과 review queue 동선을 바로 열 수 있게 유지
- 운영 패널이 `AGENTS.md`, `CONTEXT`, `TRD`, `PRD`, workboard를 자연스럽게 노출하도록 문서/로더/UI를 잇는 작업 진행

## 앞으로의 backlog

- prompt family가 늘어나도 `/internal/prompts` 카드 구조를 그대로 재사용할 수 있게 확장
- internal 운영 허브에 more systems view가 필요해지면 scraper / pipeline / delivery 상태도 합류
- docs 항목별 owner / due / 상태 표현이 필요해지면 additive한 문서 계약으로 확장
- 문서 보기뿐 아니라 inline editing 또는 저장 동선을 운영 패널에 추가
- recent changes, current status, next action, backlog, verification path를 카드로 분리해 가시성 강화

## 운영 메모

- 운영 상태의 canonical source는 docs 문서로 유지
- runtime truth가 필요한 lineage / compare / review 링크는 API 스냅샷을 사용
- Prompt 관련 상세 내용은 `/internal/prompts`에 모아서 관리
- 일반 운영 허브는 docs 레지스트리 + workboard + verification links를 먼저 보여주는 방향을 유지

## 참고 링크

- [PromptOps 기준서](../promptops/README.md)
- [PromptOps 현재 상태](../promptops/status.md)
- [Iteration 001 기록](../promptops/iterations/job_evaluation_iteration_001.md)
- [운영 패널 문서 계약](./operations_panel.md)
- [에이전트 작업 보드](./agent_workboard.md)
