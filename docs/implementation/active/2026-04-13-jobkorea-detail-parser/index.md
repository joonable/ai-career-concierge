---
plan_id: 2026-04-13-jobkorea-detail-parser
title: Jobkorea detail parser
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Jobkorea detail parser

목적: Jobkorea 상세 페이지에서 JD 본문과 식별자를 추출하는 파서를 구현한다.
- 명확한 산출물: 상세 페이지 JD/식별자 파싱 로직과 관련 테스트 통과
- 이번 세션의 변경 범위: 상세 parser, JSON-LD 또는 본문 추출, external id 파싱
- 사용자가 직접 확인할 검증 방법: unit test가 통과하고 fixture 기준으로 JD와 식별자가 추출되는지 확인
- 이번 세션에서 하지 않는 것: registry 등록, multi-source ingest, 운영 화면 작업
