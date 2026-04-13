---
plan_id: 2026-04-13-multi-source-ingest-regression
title: Multi-source ingest regression
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Multi-source ingest regression

목적: Incruit와 Jobkorea가 함께 등록된 상태에서 ingest 노드가 회귀 없이 동작하는지 검증한다.
- 명확한 산출물: 멀티소스 ingest 회귀 테스트와 통과 결과
- 이번 세션의 변경 범위: multi-source integration test, 부분 실패 허용 케이스, 회귀 확인
- 사용자가 직접 확인할 검증 방법: 관련 integration test가 통과하고 두 source 조합 결과를 확인
- 이번 세션에서 하지 않는 것: 새 scraper 기능 추가, PromptOps 운영 화면, metric 설명
