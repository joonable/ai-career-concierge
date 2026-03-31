# Docs Guide

문서를 빠르게 찾을 수 있도록 `docs/`를 역할별로 정리합니다.

## 읽는 순서

1. [CONTEXT.md](./CONTEXT.md)
2. [TRD.md](./TRD.md)
3. [PRD.md](./PRD.md)
4. 운영 관련 작업이면 [internal/status.md](./internal/status.md)
5. PromptOps 관련 작업이면 [promptops/README.md](./promptops/README.md)

## 디렉토리 구조

- `docs/`
  - 제품과 아키텍처의 canonical 문서만 둡니다.
  - `CONTEXT.md`, `TRD.md`, `PRD.md`
- `docs/internal/`
  - `/internal` 운영 패널이 읽는 운영 문서
  - 상태판, 작업 보드, 운영 패널 계약
- `docs/promptops/`
  - PromptOps 기준서, 상태판, iteration 기록, 연구 메모
- `docs/implementation/`
  - 특정 구현/리팩터링 메모

## 문서 배치 원칙

- 최상위 `docs/`에는 source of truth 성격의 핵심 문서만 둡니다.
- 운영 상태성 문서는 `docs/internal/`로 모읍니다.
- PromptOps 관련 문서는 `docs/promptops/`로 모읍니다.
- 일회성 구현 메모나 리팩터링 문서는 `docs/implementation/`으로 분리합니다.
- 새 문서를 추가할 때는 기존 문서와 역할이 겹치면 새 파일을 늘리기보다 같은 디렉토리 안에서 합치거나 확장하는 것을 먼저 검토합니다.
