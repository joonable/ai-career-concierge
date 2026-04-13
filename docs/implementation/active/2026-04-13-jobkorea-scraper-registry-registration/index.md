---
plan_id: 2026-04-13-jobkorea-scraper-registry-registration
title: Jobkorea scraper registry registration
status: active
milestone: Phase 5: 스크래퍼/데이터 계층 보강
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# Jobkorea scraper registry registration

목적: Jobkorea scraper를 runtime registry에 연결해 멀티소스 구조 안에서 인식되도록 만든다.
- 명확한 산출물: runtime registry에 Jobkorea source가 포함된 상태
- 이번 세션의 변경 범위: scraper 인스턴스화, registry 등록, 최소 wiring 확인
- 사용자가 직접 확인할 검증 방법: runtime 관련 테스트나 확인 코드에서 Jobkorea source가 등록되는지 확인
- 이번 세션에서 하지 않는 것: 상세 파서 재구현, multi-source 회귀 전체 검증, UI 작업
