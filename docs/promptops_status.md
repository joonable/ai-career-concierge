# PromptOps Current Status

날짜: 2026-03-31 (Asia/Seoul)

이 문서는 개발자와 비개발자 모두가 PromptOps의 현재 상태를 같은 위치에서 확인하기 위한 공용 상태판입니다.

웹 운영 패널에서는 `/internal/promptops`에서 같은 상태를 카드 형태로 확인할 수 있습니다.

## `job-evaluation`

### Current stage snapshot

- current production tag: `job-evaluation:latest`
- current staging tag: `job-evaluation:staging`
- current candidate prompt: `job-evaluation`
- current candidate local reference: `local-v4`
- latest decision: `candidate 유지`

### LangSmith / 문서 / Notion 링크

- production prompt: `job-evaluation:latest`
- staging prompt: `job-evaluation:staging`
- candidate prompt: `job-evaluation` candidate lineage
- baseline vs candidate compare: [compare link](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59&selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda)
- latest iteration report: [`job_evaluation_iteration_001.md`](./promptops_iterations/job_evaluation_iteration_001.md)
- human review queue: `job-evaluation-review`
- Notion backlog: [PromptOps Backlog](https://www.notion.so/c5fb7393ece54107b445e90bdabab642)

### Latest experiment summary

- `fit_score_band`는 개선됨: `0.6667 -> 0.8000`
- `classification_match`도 개선됨: `0.8667 -> 0.9333`
- 하지만 `role_alignment_match`, `must_have_coverage_match`, `transferable_skill_credit`는 하락

### Current interpretation

- 이번 candidate는 score band 보정에는 도움이 있었음
- 다만 adjacent infra 역할 해석이 다소 과하게 눌리면서 structured sub-judgment 일관성이 낮아짐
- 따라서 바로 승격하지 않고 human review 확인 후 다음 수정이 필요함

### Next backlog top 3

- `prompt:role-alignment`
- `prompt:must-have-coverage`
- `prompt:transferable-skill-credit`

## 역할별 사용법

### 개발자

1. current stage snapshot을 확인한다.
2. compare 링크를 열어 baseline/candidate 차이를 본다.
3. iteration report에서 해석과 blocker를 읽는다.
4. review queue와 Notion backlog를 확인한다.

### PM / 운영자

1. latest decision과 current interpretation을 확인한다.
2. compare 링크와 review queue를 필요 시 연다.
3. iteration report에서 왜 보류/유지되었는지 읽는다.
4. Notion backlog에서 다음 작업 상태를 확인한다.

## 참고 문서

- 상위 기준서: [`PROMPTOPS.md`](./PROMPTOPS.md)
