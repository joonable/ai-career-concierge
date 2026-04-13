---
plan_id: 2026-04-13-jobkorea-ingest-integration
title: Jobkorea ingest integration
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Jobkorea ingest integration

목적: Jobkorea source가 ingest 흐름 안에서 데이터를 올바르게 upsert 또는 discard 하는지 검증한다.
- 명확한 산출물: Jobkorea ingest integration test와 통과 결과
- 이번 세션의 변경 범위: ingest 흐름 연결, fixture scraper 활용, integration test 작성/수정
- 사용자가 직접 확인할 검증 방법: 관련 integration test가 통과하는지 확인
- 이번 세션에서 하지 않는 것: multi-source 회귀 전체, PromptOps UI, metric glossary
