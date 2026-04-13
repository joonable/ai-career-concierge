---
plan_id: 2026-04-13-promptops-iteration-report-parsing-contract
title: PromptOps iteration report parsing contract
status: active
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: codex
created_at: 2026-04-13T14:48:46+09:00
updated_at: 2026-04-13T14:48:46+09:00
---
# PromptOps iteration report parsing contract

목적: 실제 iteration 리포트를 어떤 입력 계약으로 파싱할지 테스트 가능하게 고정한다.
- 명확한 산출물: iteration report 입력 shape와 파싱 기대 결과를 설명하는 계약
- 이번 세션의 변경 범위: fixture 또는 parsing expectation 정의, 실제 리포트 구조 확인
- 사용자가 직접 확인할 검증 방법: 테스트 fixture 또는 문서를 보고 어떤 필드를 파싱하는지 이해할 수 있는지 확인
- 이번 세션에서 하지 않는 것: CLI 출력 구현, 다음 액션 결정 로직 구현, UI 연결
