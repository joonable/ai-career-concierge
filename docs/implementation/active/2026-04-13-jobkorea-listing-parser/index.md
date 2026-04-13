---
plan_id: 2026-04-13-jobkorea-listing-parser
title: Jobkorea listing parser
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Jobkorea listing parser

목적: Jobkorea 목록 페이지에서 공고 카드와 링크 단서를 추출하는 파서를 구현한다.
- 명확한 산출물: 목록 페이지 카드 추출 로직과 관련 테스트 통과
- 이번 세션의 변경 범위: 목록 parser, selector/hint, 기본 파싱 테스트
- 사용자가 직접 확인할 검증 방법: unit test가 통과하고 fixture 기준으로 카드 정보가 추출되는지 확인
- 이번 세션에서 하지 않는 것: 상세 JD 파싱, registry 연결, multi-source ingest 검증
