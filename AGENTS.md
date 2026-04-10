# AGENTS.md

## 목적 (Purpose)

이 저장소는 노이즈가 많은 채용 공고를 필터링하고 적합도가 높은 기회만 추천하는 AI 기반 채용 매칭 시스템인 **AI Career Concierge**를 구축합니다.

현재 단계는 **단일 사용자 PoC(개념 증명)**입니다. 모든 구현 결정은 범위를 확장하기 전에 한 명의 주요 사용자를 위해 엔드투엔드 루프가 안정적으로 작동하도록 하는 것을 최우선으로 해야 합니다.

## 단일 진실 공급원 (Source Of Truth)

이 저장소에서 작업할 때는 다음 순서로 문서를 참조하세요:

1. [`docs/CONTEXT.md`](docs/CONTEXT.md)
2. [`docs/TRD.md`](docs/TRD.md)
3. [`docs/PRD.md`](docs/PRD.md)
4. [`docs/internal/operations_panel.md`](docs/internal/operations_panel.md)
5. [`docs/internal/status.md`](docs/internal/status.md)

충돌이 발생하는 경우 추측하지 말고 작업을 멈추고 명시적으로 해결하세요.

## 현재 제품 범위 (Current Product Scope)

PoC는 다음 루프를 지원해야 합니다:

1. 사용자가 Google로 로그인하여 프로필을 구성합니다.
2. 시스템이 대상 플랫폼에서 채용 공고를 수집(ingest)합니다.
3. 공고는 2단계 평가 파이프라인을 거칩니다 (규칙 기반 필터링 → LLM 기반 심층 평가).
4. 높은 점수를 받은 공고는 Slack을 통해 전달됩니다.
5. 사용자는 좋아요/싫어요 피드백을 제공합니다.
6. 최근의 싫어요 피드백은 단기 기억으로 저장되어 이후 평가에 재사용됩니다.

## 제품 우선순위 (Product Priorities)

- 재현율(recall)보다 정밀도(precision) 최적화.
- 모델 호출 전 공격적인 필터링으로 LLM 비용 절감.
- 향후 추천을 개선하는 깔끔한 피드백 루프 유지.
- 섣부른 SaaS 일반화보다 엔드투엔드 서비스 작동 우선.

## 확정된 기술 스택 (Confirmed Technical Stack)

- 프론트엔드: Next.js / TypeScript
- 백엔드: FastAPI / Python
- 워크플로우: LangGraph
- LLM: Google Gemini Flash (구조화된 JSON 출력)
- 스크래핑: Playwright (async)
- 데이터베이스 및 인증: Supabase PostgreSQL + Google OAuth
- 런타임 영속성: Supabase Data API (service role)
- 레거시 스키마 참조: SQLModel
- 스케줄링: GitHub Actions cron
- 추적(Tracing): LangSmith

명확한 이유와 사용자의 명시적 승인 없이 이를 교체하지 마세요.

## 도메인별 상세 규칙

상세한 구현 규칙은 `.claude/rules/` 디렉토리의 개별 파일을 참조하세요:

- [아키텍처 및 폴더 구조](.claude/rules/architecture.md)
- [파이프라인 계약 및 데이터 모델](.claude/rules/pipeline.md)
- [스크래퍼 규칙](.claude/rules/scraper.md)
- [PromptOps 규칙](.claude/rules/promptops.md)
- [프론트엔드 규칙](.claude/rules/frontend.md)
- [테스트 규칙 및 완료 조건](.claude/rules/testing.md)
- [API 계약 및 인증 경계](.claude/rules/api-contracts.md)
- [설정 및 환경 변수 규칙](.claude/rules/config-env.md)
- [Implementation 문서 규칙](.claude/rules/implementation-docs.md)

## 범위 가드레일 (Scope Guardrails)

PoC 루프가 작동하기 전에 다음 작업에 시간을 낭비하지 마세요:

- 다중 테넌트(multi-tenant) SaaS 복잡성
- 이력서 업로드 및 RAG 온보딩
- 추천 검토 및 피드백을 넘어선 고급 대시보드 기능
- 핵심 루프에 필요하지 않는 한, 많은 채용 플랫폼에 대한 광범위한 최적화

## 에이전트 작업 규범 (Working Norms For Agents)

- 상당한 수정을 하기 전에 `docs/CONTEXT.md`를 읽으세요.
- 사용자가 변경을 요청하지 않는 한 현재 스택과 아키텍처를 유지하세요.
- 새 모듈을 추가할 때 이름을 명시적이고 제품 개념과 일치하도록 유지하세요.
- 작업을 마친 뒤 사용자가 UI에서 직접 결과를 확인할 수 있도록 검증 경로까지 정리하세요.
- 의미 있는 작업을 마치면 `docs/internal/status.md`를 업데이트하세요.
- 불확실할 때에는 엔드투엔드 PoC 작동, 낮은 LLM 비용, 추천 품질을 가장 잘 지원하는 경로를 선택하세요.

## 멀티 에이전트 Git / Worktree 운영 규칙

Codex, Claude, Gemini가 같은 로컬 저장소를 병렬로 사용할 수 있으므로, Git 작업은 아래 규칙을 기본값으로 고정합니다.

- 기본 기준 브랜치(base branch)는 항상 `main`입니다.
- 새 작업은 현재 체크아웃된 브랜치에서 바로 시작하지 않고, 항상 `main` 기준으로 새 branch + 새 worktree를 준비한 뒤 시작합니다.
- `main`에서는 직접 기능 작업 커밋을 만들지 않습니다.
- 에이전트 전용 branch prefix는 다음으로 고정합니다.
  - Codex: `codex/<task-slug>`
  - Claude: `claude/<task-slug>`
  - Gemini: `gemini/<task-slug>`
- 통합 branch prefix는 `integration/<task-slug>`로 고정합니다.
- 에이전트별 worktree 경로는 `../ai-career-concierge-worktrees/<agent>/<task-slug>` 규칙을 사용합니다.
- 여러 에이전트 결과는 바로 `main`으로 합치지 않고, 먼저 `integration/<task-slug>`에서 merge 또는 cherry-pick으로 통합한 뒤 검증합니다.
- 같은 작업에서 파일 충돌 가능성이 높으면 착수 전에 담당 범위를 명시적으로 분리합니다.
- integration 검증 전에는 에이전트 branch끼리 임의 merge를 하지 않습니다.

### 표준 시작 절차

저장소 루트에서 아래 스크립트를 사용해 작업 공간을 준비합니다.

```bash
scripts/start_agent_task.sh --agent codex --task dashboard-filter
scripts/start_agent_task.sh --agent claude --task dashboard-filter
scripts/start_agent_task.sh --agent gemini --task dashboard-filter
scripts/start_integration_task.sh --task dashboard-filter
```

- 동일한 `task-slug`를 다시 실행하면 기존 branch/worktree를 우선 재사용합니다.
- `--base`를 명시하지 않으면 항상 `main`을 사용합니다.
- 통합 검증이 끝난 뒤에만 `main` 대상 PR 또는 최종 merge를 진행합니다.

## 문서화 규칙 (Documentation Rules)

- 참조 문서와 운영 문서는 기본적으로 한국어를 우선 사용합니다.
- 영어 표현이 꼭 필요할 때만 괄호로 병기합니다.
- 구현으로 인해 아키텍처, API 계약, 핵심 데이터 모델 또는 워크플로우 가정이 변경되는 경우 관련 문서를 업데이트하세요 (`docs/CONTEXT.md`, `docs/TRD.md`, `docs/internal/status.md`).
- 상세 계획의 source of truth는 `docs/implementation/active/`의 plan package입니다.
- `TODO.md`와 `MILESTONE.md`는 자동 동기화되는 요약 인덱스이므로 긴 상세 계획을 직접 적지 마세요.
- hook이 없는 에이전트는 `python3 scripts/implementation_docs.py save-plan ...`으로 계획을 직접 저장해야 합니다.
- 구현 완료 후에는 `python3 scripts/implementation_docs.py archive-plan <plan_id>`로 archive하고, `python3 scripts/implementation_docs.py validate`를 통과시켜야 합니다.
