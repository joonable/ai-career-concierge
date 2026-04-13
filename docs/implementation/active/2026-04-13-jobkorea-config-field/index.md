---
plan_id: 2026-04-13-jobkorea-config-field
title: Jobkorea config field
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Jobkorea config field

목적: Jobkorea scraper가 사용할 base URL 등 필수 설정 항목을 configuration 레이어에 추가한다.
- 명확한 산출물: Jobkorea 관련 config 필드와 validation 규칙
- 이번 세션의 변경 범위: 설정 필드 정의, 기본값 또는 환경 변수 wiring, validation test
- 사용자가 직접 확인할 검증 방법: config validation test가 통과하고 잘못된 설정이 거부되는지 확인
- 이번 세션에서 하지 않는 것: 실제 scraper 실행, registry 등록, ingest 통합 테스트
