<!-- implementation plan package 운영 규칙 -->

# Implementation Docs 규칙

## 기본 원칙

- 상세 계획, 구현 메모, 대형 리팩터링 맥락 문서는 `docs/implementation/` 아래의 plan package로 관리한다.
- `TODO.md`와 `MILESTONE.md`는 상세 작업 목록이 아니라 요약 인덱스 문서로 취급한다.
- active 계획의 canonical source는 `docs/implementation/active/`이다.

## 저장 규칙

- 새 계획은 `docs/implementation/active/YYYY-MM-DD-<slug>/index.md` 형식으로 저장한다.
- `index.md`에는 frontmatter가 있어야 하며 `plan_id`, `title`, `status`, `milestone`, `source_agent`, `created_at`, `updated_at`를 모두 포함한다.
- 문서가 길면 동일 디렉토리에 `01-summary.md`, `02-implementation.md`, `03-test-plan.md`처럼 분할한다.
- hook이 없는 에이전트나 수동 작업은 `python3 scripts/implementation_docs.py save-plan ...`을 직접 호출해 저장한다.

## 아카이브 규칙

- 구현 완료 뒤에만 `python3 scripts/implementation_docs.py archive-plan <plan_id>`로 archive 한다.
- archive는 `docs/implementation/archive/<YYYY>/` 아래로 이동한다.
- archive 여부를 코드 diff나 추정 상태만으로 자동 결정하지 않는다.

## 검증 규칙

- 문서 구조 변경 후 `python3 scripts/implementation_docs.py validate`를 통과시킨다.
- `TODO.md`와 `MILESTONE.md`의 managed block은 수동 편집하지 않고 `sync-indexes`로 갱신한다.
