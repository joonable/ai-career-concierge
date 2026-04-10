# CLAUDE.md

## 프로젝트 개요

AI Career Concierge — AI 기반 채용 매칭 PoC 시스템.
노이즈가 많은 채용 공고를 필터링하고 적합도가 높은 기회만 추천한다.

현재 단계: **단일 사용자 PoC**. 모든 결정은 엔드투엔드 루프 안정화를 최우선으로 한다.

## 필수 참조 문서 (우선순위 순)

1. `docs/CONTEXT.md` — 구현 컨텍스트 (상당한 수정 전 먼저 읽기)
2. `docs/TRD.md` — 아키텍처 및 기술 계약
3. `docs/PRD.md` — 제품 의도 및 비즈니스 목표
4. `AGENTS.md` — 운영 계약 (사람과 에이전트 공용)
5. `docs/internal/operations_panel.md` — 운영 패널 컴포넌트 정리
6. `docs/internal/status.md` — 현재 운영 상태판

## 도메인별 규칙

.claude/rules/architecture.md
.claude/rules/pipeline.md
.claude/rules/scraper.md
.claude/rules/promptops.md
.claude/rules/frontend.md
.claude/rules/testing.md
.claude/rules/api-contracts.md
.claude/rules/config-env.md
.claude/rules/implementation-docs.md

## 기술 스택

- **백엔드**: Python 3.9+ / Poetry / FastAPI / LangGraph / Gemini Flash / Playwright
- **프론트엔드**: Next.js 15 / TypeScript / Supabase Auth (SSR)
- **데이터**: Supabase PostgreSQL / SQLModel (레거시)
- **운영**: LangSmith (트레이싱) / GitHub Actions (스케줄링)

## 작업 완료 체크리스트

- [ ] 관련 테스트 포함
- [ ] `docs/internal/status.md` 업데이트 (운영 상태 변경 시)
- [ ] API 계약 변경 시 스키마/문서/테스트 동시 업데이트
- [ ] `.env.example` 업데이트 (환경 변수 추가/변경 시)
- [ ] implementation 문서 구조 변경 시 `python3 scripts/implementation_docs.py validate`
- [ ] 브레이킹 체인지는 명시적으로 언급

## 에이전트 작업 규범

- 상당한 수정 전 `docs/CONTEXT.md`를 읽는다.
- 사용자 요청 없이 현재 스택/아키텍처를 변경하지 않는다.
- 불확실할 때는 엔드투엔드 PoC 작동, 낮은 LLM 비용, 추천 품질을 우선한다.
- 의미 있는 작업 후 `docs/internal/status.md`를 업데이트한다.
- 상세 계획은 `docs/implementation/active/`의 plan package에 저장한다.
- `TODO.md`, `MILESTONE.md`에는 긴 상세 계획을 직접 누적하지 않는다.
- hook이 저장하지 못한 경우 `python3 scripts/implementation_docs.py save-plan ...`을 직접 실행한다.

## 멀티 에이전트 Git / Worktree 규칙

- 기본 base branch는 항상 `main`이다.
- `main`에서 직접 기능 작업을 시작하거나 커밋하지 않는다.
- 새 작업은 저장소 루트에서 스크립트로 시작한다.

```bash
scripts/start_agent_task.sh --agent claude --task <task-slug>
scripts/start_integration_task.sh --task <task-slug>
```

- Claude branch는 항상 `claude/<task-slug>` 규칙을 따른다.
- worktree 경로는 `../ai-career-concierge-worktrees/claude/<task-slug>` 규칙을 따른다.
- Codex, Gemini와 협업하는 작업은 각자 전용 branch/worktree에서 진행하고, 결과는 먼저 `integration/<task-slug>`에서 통합 검증한다.
- 충돌 가능성이 높은 파일은 작업 전에 담당 범위를 나눈다.
