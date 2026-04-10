# Implementation Docs Guide

`docs/implementation/`은 구현 메모, 에이전트 계획, 후속 실행 맥락을 plan package 단위로 관리하는 canonical 공간입니다.

## Lifecycle

1. 새 계획 또는 구현 메모는 `docs/implementation/active/YYYY-MM-DD-<slug>/` 아래에 저장합니다.
2. package의 기준 파일은 항상 `index.md`이며, 기계가 읽는 frontmatter를 포함합니다.
3. 문서가 길어지면 같은 디렉토리 안에 `01-summary.md`, `02-implementation.md`, `03-test-plan.md`처럼 분할합니다.
4. 구현이 완료된 뒤에만 `python3 scripts/implementation_docs.py archive-plan <plan_id>`로 `archive/<YYYY>/` 아래로 이동합니다.
5. `TODO.md`와 `MILESTONE.md`는 이 디렉토리를 스캔해 자동 생성된 인덱스를 노출합니다.

## Directory Layout

- `docs/implementation/active/`
  - 현재 진행 중인 계획과 구현 메모
- `docs/implementation/archive/<YYYY>/`
  - 완료되어 이력으로 보존하는 plan package

## Naming Rules

- package 디렉토리명은 `YYYY-MM-DD-<slug>` 형식을 사용합니다.
- `<slug>`는 작업 의도를 드러내는 짧은 문자열을 사용합니다.
- `index.md` frontmatter는 다음 필드를 모두 포함해야 합니다.
  - `plan_id`
  - `title`
  - `status`
  - `milestone`
  - `source_agent`
  - `created_at`
  - `updated_at`

## Commands

```bash
python3 scripts/implementation_docs.py save-plan --agent codex --milestone "Phase 2: 하네스 엔지니어링" --stdin-markdown
python3 scripts/implementation_docs.py archive-plan 2026-04-10-example-plan
python3 scripts/implementation_docs.py sync-indexes
python3 scripts/implementation_docs.py validate
```

## Collaboration Rules

- 상세 계획의 source of truth는 `docs/implementation/active/`입니다.
- `TODO.md`와 `MILESTONE.md`에는 긴 체크리스트를 직접 적지 않고 package 링크만 유지합니다.
- hook이 없는 에이전트는 `save-plan`을 직접 호출해야 합니다.
- archive는 명시적 명령으로만 수행합니다. 코드 diff만 보고 자동 archive 하지 않습니다.
