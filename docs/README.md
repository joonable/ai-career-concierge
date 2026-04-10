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
  - plan package 단위의 구현 계획, 리팩터링 메모, archive 이력

## 문서 배치 원칙

- 최상위 `docs/`에는 source of truth 성격의 핵심 문서만 둡니다.
- 운영 상태성 문서는 `docs/internal/`로 모읍니다.
- PromptOps 관련 문서는 `docs/promptops/`로 모읍니다.
- 구현 계획과 리팩터링 메모는 `docs/implementation/active/YYYY-MM-DD-<slug>/` package로 저장합니다.
- 완료된 plan package는 `docs/implementation/archive/<YYYY>/`로 이동합니다.
- `TODO.md`와 `MILESTONE.md`는 `docs/implementation/`을 가리키는 요약 인덱스로만 유지합니다.
- 새 문서를 추가할 때는 기존 문서와 역할이 겹치면 새 파일을 늘리기보다 같은 디렉토리 안에서 합치거나 확장하는 것을 먼저 검토합니다.
