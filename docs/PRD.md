# 📄 PRD: Scalable AI Job-Matching Agent System (v3.1 - PoC Focus)

## 1. Product Overview (프로젝트 개요)

- **Product Name:** (TBD) AI Career Concierge
- **Mission:** 매일 쏟아지는 채용 공고 노이즈(Noise)를 제거하고, 개별 사용자의 정교한 커리어 니즈에 100% 부합하는 고품질 공고만을 큐레이션하는 지능형 자동화 서비스.
- **Target Audience:** * [Phase 1 / PoC] 개발자 본인 (5~6년 차 MLE)
    - [Phase 2 / SaaS] 맞춤형 이직 기회를 수동으로 찾기 번거로워하는 모든 IT/Tech 직군 종사자

## 2. Core Features & Business Logic (핵심 기능 및 비즈니스 로직)

### 2.1 Authentication & Profile Management (사용자 인증 및 프로필 관리)

사용자는 마찰 없는 로그인과 직관적인 웹 인터페이스(Web UI)를 통해 에이전트를 설정합니다.

- **소셜 로그인 (OAuth 2.0):** Google 로그인을 기본 인증 방식으로 사용하여 1초 만에 회원가입/로그인 처리. (수집 범위: `email`, `profile` 기본 정보)
- **초기 온보딩 (Onboarding Flow):** 첫 로그인 시 에이전트가 사용자에게 인사이드 가이드를 제공하며, 직무/연차/기술 스택/Must-haves/Deal-breakers를 입력받는 단계별 폼(Step-by-step Form) 제공.
- **입력 방식 진화 (Roadmap):** * **[Current Phase]:** 텍스트 폼(Form) 직접 입력.
    - **[Future Phase]:** 이력서(PDF) 업로드 시 RAG(Retrieval-Augmented Generation) 파이프라인을 통한 자동 완성(Auto-fill).
- **수신 설정:** 알림 채널(Slack 등), 수신 주기(매일 오전 9시 등), 최소 매칭 점수(예: 80점 이상) 설정.
- **대시보드 뷰:** 추천 공고 리스트 확인 및 상태 관리용 칸반(Kanban) 뷰.

### 2.2 Multi-stage Evaluation Pipeline (다단 평가 파이프라인)

비용 최적화(Cost Optimisation)를 위해 에이전트 평가는 2단계로 실행됩니다.

- **[Stage 1] Rule-based Filtering:**
    - LLM 호출 전 DB 쿼리 및 단순 텍스트 매칭으로 1차 필터링.
    - 로직: 기평가 공고 제외(De-duplication) → 직무명 확인 → 연차 조건 부합 여부 확인.
- **[Stage 2] Agentic Deep Evaluation:**
    - 1차 통과 공고에 한해 LLM 에이전트 투입.
    - 로직: Deal-breaker 문맥 분석 → Must-haves 충족 여부 추론 → 매칭 점수(1~100) 산정 → 2줄 추천 사유(Reasoning) 도출.

### 2.3 Continuous Learning & Feedback Loop (지속 학습 및 피드백 루프)

사용자의 반응을 에이전트의 '단기 기억(Memory)'으로 전환하여 추천 품질을 향상시킵니다.

- **Explicit Feedback:** 대시보드에서 공고에 대해 👍(좋아요) / 👎(별로예요) 평가.
- **Memory Update:** '별로예요' 선택 시 거절 사유(예: "연봉 낮음")를 입력받아 DB 저장.
- **Dynamic Prompting:** 다음 날 평가 시 최근 누적 피드백을 시스템 프롬프트에 주입(Injection)하여 실수를 줄임.

### 2.4 Multi-channel Delivery (다중 채널 알림)

- **메시지 전송:** 설정된 주기에 맞춰 최상위 공고들을 Slack으로 전송.
- **알림 템플릿:** 직무명, 회사명, 매칭 점수, 2줄 추천 사유, Web 대시보드 딥링크(Deep Link) 포함.

## 3. User Journey (사용자 여정)

1. **[Login & Onboarding]** 사용자가 Web UI에 접속하여 Google 계정으로 로그인한 뒤, 초기 온보딩 폼을 통해 프로필과 제약 조건(Deal-breakers), 알림 채널을 설정합니다.
2. **[Agent Action]** 백그라운드에서 매일 타겟 플랫폼의 신규 공고를 수집하고, Rule-based 필터링과 LLM 심층 평가를 거쳐 공고를 선별합니다.
3. **[Notification]** 사용자는 지정된 시간에 Slack으로 요약 리포트를 받습니다.
4. **[Feedback]** 링크를 통해 Web UI 상세 페이지를 확인하고, 공고에 대해 👍/👎 피드백을 남겨 내일의 에이전트 평가 기준을 미세 조정합니다.

## 4. Success Metrics (성공 지표)

- **Precision (정확도):** 에이전트가 추천한 공고 중 사용자가 '지원' 또는 '👍'를 누른 비율.
- **Cost Optimisation:** Rule-based 필터링 도입을 통한 1인당 일일 API 호출 비용 최소화 달성률.