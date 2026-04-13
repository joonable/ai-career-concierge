---
plan_id: 2026-04-13-promptops-internal-prompts-route-shell
title: PromptOps /internal/prompts route shell
status: archived
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: codex
created_at: 2026-04-13T14:48:46+09:00
updated_at: 2026-04-13T15:33:22+09:00
---
# PromptOps /internal/prompts route shell

목적: 운영자가 `/internal/prompts` 경로로 진입했을 때 PromptOps 전용 화면 골격을 확인할 수 있는 최소 라우트와 페이지 shell을 만든다.
- 명확한 산출물: `/internal/prompts` 라우트와 기본 레이아웃/placeholder 상태
- 이번 세션의 변경 범위: 라우트 연결, 페이지 shell, 최소한의 운영자 안내 문구
- 사용자가 직접 확인할 검증 방법: 브라우저에서 `/internal/prompts` 경로가 열리고 기본 화면 구조가 보이는지 확인
- 이번 세션에서 하지 않는 것: dataset 로딩, metric 노출, 실제 리스트 렌더링
