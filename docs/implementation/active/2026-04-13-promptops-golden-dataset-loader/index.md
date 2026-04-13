---
plan_id: 2026-04-13-promptops-golden-dataset-loader
title: PromptOps golden dataset loader
status: active
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: codex
created_at: 2026-04-13T14:48:46+09:00
updated_at: 2026-04-13T14:48:46+09:00
---
# PromptOps golden dataset loader

목적: PromptOps 운영 화면과 후속 테스트가 공통으로 사용할 golden dataset 로더를 정의한다.
- 명확한 산출물: local golden dataset 파일을 읽어 구조화된 데이터로 반환하는 로더 계약
- 이번 세션의 변경 범위: dataset 파일 접근, 로더 함수/모듈, 최소 오류 처리
- 사용자가 직접 확인할 검증 방법: 테스트 또는 CLI/서버 호출로 dataset 로딩 결과 구조를 확인
- 이번 세션에서 하지 않는 것: 화면 렌더링, metric 설명, iteration 분석
