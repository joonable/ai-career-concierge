# GEMINI.md

## 프로젝트 개요

AI Career Concierge는 단일 사용자 PoC 단계의 AI 기반 채용 매칭 시스템입니다.
현재 우선순위는 엔드투엔드 추천 루프 안정화, 낮은 LLM 비용, 높은 추천 정밀도입니다.

## 필수 참조 문서

1. `docs/CONTEXT.md`
2. `docs/TRD.md`
3. `docs/PRD.md`
4. `AGENTS.md`
5. `docs/internal/status.md`

## 문서 운영 규칙

- 상세 계획의 canonical source는 `docs/implementation/active/`입니다.
- `TODO.md`와 `MILESTONE.md`는 요약 인덱스이며 긴 체크리스트를 직접 적지 않습니다.
- Plan Mode에서 정리한 계획은 `python3 scripts/implementation_docs.py save-plan ...` 또는 project hook으로 저장합니다.
- 구현 완료 후에는 `python3 scripts/implementation_docs.py archive-plan <plan_id>`로 archive 합니다.

## 멀티 에이전트 운영

- `main`에서 직접 기능 작업을 하지 않습니다.
- 작업 시작은 `scripts/start_agent_task.sh --agent gemini --task <task-slug>`를 사용합니다.
- integration 전에는 `gemini/*` branch를 다른 에이전트 branch와 직접 merge 하지 않습니다.
