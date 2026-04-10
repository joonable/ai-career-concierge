# Implementation Docs Guide

`docs/implementation/`은 구현 메모, 에이전트 계획, 후속 실행 맥락을 plan package 단위로 관리하는 canonical 공간입니다.

이 디렉토리는 제품 코드가 아니라 협업 실행 맥락의 source of truth입니다. `TODO.md`, `MILESTONE.md`보다 상세 계획이 우선하며, 멀티 에이전트 작업에서는 각 worktree 결과를 통합하기 전에도 plan package를 통해 의도를 공유해야 합니다.

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
- Codex는 현재 Claude/Gemini처럼 자동 저장 hook이 강하게 연결되어 있지 않을 수 있으므로, plan package 저장 여부를 직접 확인합니다.
- 루트 저장소는 coordination 공간으로 보고, 실제 기능 구현은 `scripts/start_agent_task.sh --agent <agent> --task <slug>`로 만든 worktree에서 진행하는 것을 기본값으로 둡니다.
- worktree 구조의 canonical 예시는 다음과 같습니다.

```text
../ai-career-concierge-worktrees/codex/<task-slug>
../ai-career-concierge-worktrees/claude/<task-slug>
../ai-career-concierge-worktrees/gemini/<task-slug>
../ai-career-concierge-worktrees/integration/<task-slug>
```

- 에이전트 branch 결과는 먼저 `integration/<task-slug>`에서 merge 또는 cherry-pick으로 통합 검증하고, 그 뒤에만 `main` 대상 PR 또는 merge를 진행합니다.

## Readiness Checklist

멀티 에이전트 협업 시작 전 최소 체크:

- `scripts/start_agent_task.sh` / `scripts/start_integration_task.sh`가 기대한 branch와 worktree를 생성하는지 확인
- `python3 scripts/implementation_docs.py validate`가 통과하는지 확인
- 작업 결과에 UI 확인 위치 또는 검증 커맨드가 포함되는지 확인
- `docs/internal/status.md`에 현재 상태와 다음 action을 남길 수 있는지 확인
