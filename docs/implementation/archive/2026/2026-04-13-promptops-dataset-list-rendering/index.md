---
plan_id: 2026-04-13-promptops-dataset-list-rendering
title: PromptOps prompt dataset list rendering
status: archived
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: codex
created_at: 2026-04-13T14:48:46+09:00
updated_at: 2026-04-13T15:48:49+09:00
---
# PromptOps prompt dataset list rendering

목적: golden dataset 로더 결과를 `/internal/prompts` 화면에서 운영자가 볼 수 있는 목록으로 연결한다.
- 명확한 산출물: dataset 항목 목록과 상태를 보여주는 첫 UI 렌더링
- 이번 세션의 변경 범위: 화면 바인딩, 목록/상태 표시, 빈 상태 또는 에러 상태 처리
- 사용자가 직접 확인할 검증 방법: 브라우저에서 `/internal/prompts` 화면에 dataset 목록과 상태가 표시되는지 확인
- 이번 세션에서 하지 않는 것: metric glossary, analyze_iteration CLI, scraper 작업
