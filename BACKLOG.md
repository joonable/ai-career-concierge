# BACKLOG.md

이 문서는 현재 바로 실행하지는 않지만, 후속 검토와 분해가 필요한 작업을 모아두는 backlog입니다.
상세 실행 단위는 추후 `docs/implementation/active/`의 plan package로 분리합니다.

## 운영 원칙

- backlog 항목은 아직 decision-complete execution task가 아닙니다.
- 실제 착수 전에는 별도 active plan package로 쪼개고 검증 경로를 명시합니다.
- canonical source는 이 문서와 이후 생성될 plan package입니다.

## Closeout Contract 후속 항목

- `.agents/capabilities/implementation-closeout/` 신설
  - 목적: assistant-neutral capability 경로를 도입해 Claude/Gemini/Codex가 같은 closeout contract를 더 직접적으로 참조하게 만들기
  - 보류 이유: Phase 1에서는 공용 CLI만으로도 목적 달성이 가능한지 먼저 검증

- assistant-neutral manifest/contract 파일 추가
  - 목적: closeout 대상 surface, 명령, validation 규칙을 machine-readable contract로 고정
  - 보류 이유: 현재는 `scripts/implementation_docs.py`와 문서 계약만으로도 충분히 운영 가능

- plan body anchor 파싱 기반 richer summary
  - 목적: `docs/internal/status.md`의 done/next action 요약에 산출물과 검증 힌트까지 자동 노출
  - 보류 이유: active plan body 형식 일관성이 더 확보된 뒤 도입하는 편이 안전

- hook smoke test 자동화
  - 목적: Claude/Gemini hook가 공용 closeout command를 기대한 방식으로 호출하는지 자동 검증
  - 보류 이유: 현재는 수동 smoke로도 충분하며 hook 테스트 harness 구축 비용이 큼

- Codex/Gemini 강제 hook 도입
  - 목적: closeout 누락 방지를 문서 규칙이 아니라 실행 가드 수준으로 끌어올리기
  - 보류 이유: Codex/Gemini 쪽 운영 friction과 실제 반복 누락 패턴을 더 본 뒤 우선순위 판단

- managed block 직접 수정 흔적 탐지
  - 목적: sync 누락뿐 아니라 managed block 직접 편집까지 탐지
  - 보류 이유: Phase 1에서는 재렌더 결과 비교만으로도 drift 감지가 가능

- active plan 우선순위 자동 계산 또는 N개만 노출하는 필터링
  - 목적: `STATUS_NEXT_ACTIONS`의 정보 밀도를 높이고 운영자 가독성 개선
  - 보류 이유: 먼저 active set 정리와 현재 최소 snapshot 방식이 운영에 충분한지 확인 필요

## Closeout Contract 재평가 기준

- `closeout-plan`만으로 closeout 누락이 충분히 줄었는지
- `STATUS_NEXT_ACTIONS`의 최소 정보가 운영에 충분한지
- Codex/Gemini에서 강제력 부족이 실제 운영 문제로 반복되는지
- `.agents/` 계층이 실제 adapter 수렴점으로 기능할 필요가 생겼는지

## 제품 / 운영 backlog

- 최초 로그인 시 2번 로그인해야 하는 문제
  - 목적: 첫 로그인 플로우를 한 번의 인증으로 끝나게 복구
  - 관찰 포인트: OAuth callback, 세션 저장, redirect 타이밍, onboarding/dashboard 진입 조건
  - 기대 산출물: 재현 조건 정리, 원인 분석, fix plan, 사용자 확인 경로

- 실제 공고 내용으로 테스트셋 구성
  - 목적: synthetic fixture 중심 검증을 넘어 실제 한국어 채용 공고 본문 기반 회귀셋 확보
  - 관찰 포인트: 데이터 수집 기준, 민감정보/저작권 취급 원칙, evaluator expectation 형식, platform coverage
  - 기대 산출물: golden/fixture 후보군, 샘플링 규칙, 익명화/정규화 기준, PromptOps/스크래퍼 공용 검증셋 계획
