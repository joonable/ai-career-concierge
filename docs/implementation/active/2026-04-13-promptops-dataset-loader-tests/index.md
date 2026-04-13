---
plan_id: 2026-04-13-promptops-dataset-loader-tests
title: PromptOps prompt dataset loader tests
status: active
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: codex
created_at: 2026-04-13T14:48:46+09:00
updated_at: 2026-04-13T14:48:46+09:00
---
# PromptOps prompt dataset loader tests

목적: golden dataset 로더가 운영 기준에 맞는 입력과 실패 케이스를 처리하는지 테스트로 고정한다.
- 명확한 산출물: dataset 로더용 unit 또는 integration 테스트 세트
- 이번 세션의 변경 범위: 정상 로드, 데이터 구조, 실패/누락 케이스 검증
- 사용자가 직접 확인할 검증 방법: 관련 pytest가 통과하는지 확인
- 이번 세션에서 하지 않는 것: 새로운 UI 추가, metric 용어 정리, agent loop 구현
