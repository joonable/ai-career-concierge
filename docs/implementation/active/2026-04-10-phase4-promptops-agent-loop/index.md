---
plan_id: 2026-04-10-phase4-promptops-agent-loop
title: Phase 4: PromptOps 에이전트 분석 루프
status: active
milestone: Phase 3: PromptOps 자동화 및 에이전트 운영 확장
source_agent: claude
created_at: 2026-04-10T00:00:00+09:00
updated_at: 2026-04-10T00:00:00+09:00
---

# Phase 4: PromptOps 에이전트 분석 루프

## 목표

에이전트(Claude)가 iteration 리포트를 읽고 구조화된 분석 JSON을 출력하는 CLI 도구를 만든다.
이 도구가 있으면 에이전트가 실험 실행 → 리포트 분석 → 다음 액션 결정을 자율 루프로 실행할 수 있다.

> **참고**: 에이전트 워크플로우 규칙(4-1)은 `.claude/rules/promptops.md`에 이미 완료됨. 이 plan은 4-2 구현에 집중.

## 에이전트 실행 프로토콜

| 단계 | 에이전트 | 작업 | 검증 기준 |
|------|---------|------|----------|
| 1 | **[Human]** | `scripts/start_agent_task.sh --agent claude --task promptops-agent-loop` | worktree 생성 확인 |
| 2 | **[Claude]** | Red: `tests/unit/test_analyze_iteration.py` 먼저 작성 | `pytest tests/unit/test_analyze_iteration.py -v` → FAILED |
| 3 | **[Claude]** | Green: `src/promptops/cli/analyze_iteration.py` 작성 | 테스트 통과 + smoke test |
| 4 | **[Claude]** | PR: `claude/promptops-agent-loop` → `main` | Codex plan review hook 통과 |
| 5 | **[Human]** | 분석 결과 JSON 검토 후 backlog 반영 결정 | |

## A. 테스트 먼저 작성 (Claude: Red 단계)

### `tests/unit/test_analyze_iteration.py`

- `test_parse_failure_patterns_groups_repeated_rules` — 동일 규칙 3회 이상 → `failure_patterns`에 포함
- `test_parse_borderline_candidates_detects_fit_score_range` — fit_score 40-79 케이스 추출
- `test_parse_prompt_change_candidates_from_failed_rules` — backlog 후보 키 매핑
- `test_generate_trend_summary_with_multiple_reports` — 리포트 2개 입력 → trend_summary 생성
- `test_analyze_returns_empty_collections_on_no_failures` — 실패 없음 케이스 방어

## B. 구현 파일 (Claude: Green 단계)

### `src/promptops/cli/analyze_iteration.py`

```python
# 입력: iteration 리포트 마크다운 경로 (1개 이상)
# 출력: JSON
{
  "failure_patterns": [
    {"rule": "keyword_match", "count": 5, "scenarios": [...]}
  ],
  "borderline_candidates": [
    {"scenario": "...", "fit_score": 65, "role_alignment": "MEDIUM"}
  ],
  "prompt_change_candidates": ["prompt:role-alignment", "prompt:must-have-coverage"],
  "trend_summary": "iteration 001→002: keyword_match 실패 증가 (2→5회). 한/영 불일치 패턴 지속."
}
```

**파싱 대상** (`docs/promptops/iterations/iteration_*.md`의 실제 구조):
- Failure analysis 테이블: `| scenario | job title | failed rules | reasoning |`
- fit_score 및 role_alignment 추출
- 규칙 이름 → `FAILURE_TAXONOMY` 키 매핑 (`src/promptops/core/failures.py` 참조)

## C. 검증 커맨드 (Claude 자율 실행)

```bash
# Red 단계
pytest tests/unit/test_analyze_iteration.py -v

# Green 단계
pytest tests/unit/test_analyze_iteration.py -v
# Smoke test: 기존 리포트로 실행
python3 -m promptops.cli.analyze_iteration \
  docs/promptops/iterations/iteration_001.md \
  docs/promptops/iterations/iteration_002-final.md

# 전체 회귀
pytest
```

## 참조 파일

- `src/promptops/core/failures.py` — `FAILURE_TAXONOMY`, `is_borderline_case()`, `is_failure_case()`
- `src/promptops/core/models.py` — `FailureRecord`, `ReviewItem` 등 데이터 모델
- `src/promptops/run_iteration.py` — 리포트 생성 방식 참조
- `docs/promptops/iterations/` — 실제 리포트 구조 확인용 (iteration_001.md, iteration_002-final.md)
- `.claude/rules/promptops.md` — 에이전트 워크플로우 규칙 (구현 지침)

## 에이전트 루프 완성 후 워크플로우

```
실험 실행 (run_iteration.py)
  → iteration 리포트 생성 (docs/promptops/iterations/)
  → 에이전트가 analyze_iteration.py 호출
  → JSON 분석 결과 출력
  → 에이전트가 다음 액션 결정:
      failure_patterns 3회 이상 → taxonomy 업데이트 제안
      borderline_candidates 있음 → 데이터셋 큐레이션 제안
      prompt_change_candidates 있음 → 프롬프트 수정 제안
```
