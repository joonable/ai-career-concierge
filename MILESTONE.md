# MILESTONE.md

프로젝트 진화 이력을 추적하는 마일스톤 문서입니다.
세부 실행 작업은 `TODO.md`를 참조하세요.

---

## Phase 0: 프로젝트 초기화 (2026-03)

- [x] 저장소 구조 및 기술 스택 확정 (Next.js + FastAPI + LangGraph + Gemini + Supabase)
- [x] AGENTS.md 초판 작성 (운영 계약 문서)
- [x] docs/CONTEXT.md, TRD.md, PRD.md 초판 작성
- [x] 환경 분리 원칙 확립 (dev/prod Supabase 프로젝트 분리)

---

## Phase 1: 수직 슬라이스 PoC (2026-03 ~ 2026-04)

- [x] Supabase Google OAuth 인증 연동
- [x] 온보딩 및 프로필 플로우 구현
- [x] 인크루트(Incruit) 스크래퍼 구현 (Playwright 기반)
- [x] LangGraph 4-노드 파이프라인 구현 (Ingest → RuleFilter → LLMEval → Deliver)
- [x] Slack 알림 및 피드백 웹훅 연동
- [x] /internal 운영 대시보드 (비대칭 그리드 레이아웃)
- [x] PromptOps 프레임워크 스캐폴드 (LangSmith 어댑터 포함)
- [x] 자동화 iteration 러너 및 리포트 생성 (`run_iteration.py`)
- [ ] 엔드투엔드 파이프라인 안정화
- [ ] 피드백 기반 단기 기억 연동

---

## Phase 2: 하네스 엔지니어링 (2026-04) ← 현재

- [x] CLAUDE.md 생성 (경로 참조 스타일 하네스 설정)
- [x] AGENTS.md 슬림화 (378줄 → 89줄)
- [x] `.claude/rules/` 8개 도메인 규칙 파일 생성
- [x] `.claude/settings.json` 훅 및 권한 설정
- [x] `.claude/launch.json` dev 서버 설정
- [x] `TODO.md` 단계별 작업 목록 생성
- [ ] MILESTONE.md 생성 ← 현재 작업
- [ ] `.claude/sessions/` 세션 히스토리 체계
- [ ] CI/CD 파이프라인 (GitHub Actions)
- [ ] ruff 린터 설정

---

## Phase 3: PromptOps 에이전트 통합 (계획)

- [ ] 실험 후 자동 분석 워크플로우
- [ ] 실패 패턴 트렌드 감지 및 리포트
- [ ] Borderline 케이스 데이터셋 큐레이션 워크플로우
- [ ] 프롬프트 최적화 제안 자동화
- [ ] 규칙 필터 개선 분석

---

## Phase 4: 인프라 보강 (계획)

- [ ] 2번째 스크래퍼 소스 구현 (잡코리아 등) — 레지스트리 패턴 검증
- [ ] Supabase Data API vs SQLModel 이중 구조 정리
- [ ] 프론트엔드 경량화 (Three.js / Framer Motion 제거 검토)
- [ ] 다중 사용자 확장 기반 설계 문서
