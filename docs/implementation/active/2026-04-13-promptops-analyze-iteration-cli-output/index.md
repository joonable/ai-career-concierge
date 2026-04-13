---
plan_id: 2026-04-13-promptops-analyze-iteration-cli-output
title: PromptOps analyze_iteration CLI output
status: active
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: codex
created_at: 2026-04-13T14:48:47+09:00
updated_at: 2026-04-13T14:48:47+09:00
---
# PromptOps analyze_iteration CLI output

목적: iteration 리포트를 읽고 구조화된 JSON을 출력하는 analyze_iteration CLI의 최소 출력을 만든다.
- 명확한 산출물: 리포트 입력 시 구조화 JSON을 반환하는 CLI 엔트리포인트
- 이번 세션의 변경 범위: CLI 인자 처리, JSON 직렬화, 최소 파싱 연결
- 사용자가 직접 확인할 검증 방법: CLI를 실행해 JSON 출력이 생성되는지 확인
- 이번 세션에서 하지 않는 것: UI 노출, taxonomy 대규모 리팩터링, scraper 작업
