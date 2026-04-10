---
plan_id: 2026-04-10-documentation-operations-rework
title: 문서 운영 구조 재편 및 계획 자동 저장 체계
status: active
milestone: Phase 2: 하네스 엔지니어링
source_agent: codex
created_at: 2026-04-10T12:45:00+09:00
updated_at: 2026-04-10T12:45:00+09:00
---
# 문서 운영 구조 재편 및 계획 자동 저장 체계

이 package는 TODO/MILESTONE 경량화, implementation plan package 구조 정착, Claude/Gemini 자동 저장 훅, Codex 검증 fallback을 한 묶음으로 정리한 작업 기록입니다.

## Summary

- `docs/implementation/active/`와 `archive/`를 canonical 구조로 고정한다.
- `TODO.md`, `MILESTONE.md`는 managed block 기반의 가벼운 인덱스로 유지한다.
- `scripts/implementation_docs.py`로 save/archive/sync/validate를 공용 진입점으로 통합한다.

## Implementation Changes

- 기존 flat implementation 문서를 package 구조로 이동한다.
- `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.claude/rules/implementation-docs.md`에 협업 규칙을 반영한다.
- `.claude/settings.json`과 `.gemini/settings.json`에 plan 저장 자동화를 연결한다.
- Codex fallback으로 validate를 커밋 전/CI에서 실행한다.

## Test Plan

- unit/integration test로 save-plan, archive-plan, sync-indexes, validate를 검증한다.
- hook payload smoke test로 Claude Stop, Gemini AfterAgent 입력을 확인한다.
- CI와 로컬 pre-commit 경로에서 `python3 scripts/implementation_docs.py validate`를 강제한다.

## Assumptions

- archive는 명시적 명령으로만 수행한다.
- implementation 상세 문서의 source of truth는 plan package이며, 인덱스 문서는 직접 길게 편집하지 않는다.
