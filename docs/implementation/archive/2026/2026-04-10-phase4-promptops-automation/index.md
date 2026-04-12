---
plan_id: 2026-04-10-phase4-promptops-automation
title: Phase 4: PromptOps 에이전트 통합 자동화
status: archived
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: claude
created_at: 2026-04-10T00:00:00+09:00
updated_at: 2026-04-10T16:04:31+09:00
---
# Phase 4: PromptOps 에이전트 통합 자동화

## 목표

실험 후 분석 자동화, 실패 패턴 감지, borderline 케이스 큐레이션 워크플로우 구축

## 작업 목록

### 4-1. 에이전트 워크플로우 규칙
- [ ] `.claude/rules/promptops.md`에 에이전트 워크플로우 섹션 추가

### 4-2. 통합 포인트 구현
- [ ] 실험 후 분석 워크플로우 (iteration 리포트 → 실패 패턴 그룹화 → 트렌드 감지)
- [ ] 실패 패턴 트렌드 리포트 생성
- [ ] Borderline 케이스 데이터셋 큐레이션 워크플로우
- [ ] 프롬프트 최적화 제안 자동화
- [ ] 규칙 필터 개선 분석

## 우선순위 메모

PoC 핵심 루프를 막고 있는 문제라기보다 운영 고도화 backlog에 가깝다.
테스트/계약 안정화와 멀티소스 ingest 확장(Phase 5-1)보다 ROI가 낮으므로 후순위.
