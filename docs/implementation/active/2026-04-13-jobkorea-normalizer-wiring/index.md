---
plan_id: 2026-04-13-jobkorea-normalizer-wiring
title: Jobkorea normalizer wiring
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Jobkorea normalizer wiring

목적: Jobkorea 파싱 결과가 기존 정규화 계층과 올바르게 연결되도록 wiring을 고정한다.
- 명확한 산출물: 절대 URL 정규화, 짧은 JD 거부 등 normalizer 연동 결과
- 이번 세션의 변경 범위: normalizer 연결, 파싱 결과 매핑, 관련 테스트
- 사용자가 직접 확인할 검증 방법: 테스트에서 URL 정규화와 유효성 거부 조건이 통과하는지 확인
- 이번 세션에서 하지 않는 것: runtime registry, ingest 회귀, 프론트엔드 작업
