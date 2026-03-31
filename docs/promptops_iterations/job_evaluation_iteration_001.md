# Job Evaluation 반복 개선 기록 001

Date: 2026-03-31 (Asia/Seoul)

## 1. 반복 개선 개요

`job-evaluation` prompt family를 대상으로 작은 prompt 변경 1건을 적용하고, 선별된 실험 데이터셋 재실행, LLM judge 비교, human review queue 전달까지 포함한 첫 번째 end-to-end PromptOps 반복 개선입니다.

### Prompt Family

- family: `job-evaluation`
- baseline prompt tag: `job-evaluation:staging`
- candidate prompt tag: `job-evaluation`
- local baseline reference: `local-v3`
- local candidate reference: `local-v4`
- lifecycle stage under test: `candidate`

## 2. 기준선(Baseline)

- dataset: `job-eval-gold-dev`
- fixture: `src/agent/evals/fixtures/job_eval_gold.json`
- baseline experiment: `promptops-baseline-local-v3-a59d3c59`
- baseline session id: `54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59`
- baseline compare link: [baseline compare](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59)
- dataset sync result: `created=0`, `updated=15`, `skipped=0`

## 3. 후보안(Candidate) 변경

후보 revision `local-v4`는 인접 직무 점수 정책 섹션에 더 좁은 범위의 지시문 한 줄을 추가했습니다.

- experimentation infra, data platform, analytics infra 역할은 직접적인 model training, serving, deployment ownership이 약하면 기본적으로 `40~59`를 준다
- 매우 강한 추가 근거가 있을 때만 `60+`로 올린다

이번 변경은 큰 prompt rewrite가 아니라, 의도적으로 정책 문구 한 줄만 바꾸는 방식으로 제한했습니다.

## 4. 후보안(Candidate) 실험

- candidate experiment: `promptops-candidate-local-v4-bcba8f4f`
- candidate session id: `4906f684-12db-4c1a-88d0-782d25f5bbda`
- candidate compare link: [candidate compare](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda)
- combined compare link: [baseline vs candidate](https://smith.langchain.com/o/a5f5f699-f384-58ec-9be0-2a39bb96969e/datasets/277c4ae5-c460-4be4-8895-732911768cd7/compare?selectedSessions=54971cd3-fcee-4dc1-bb7c-ca7f9abb6c59&selectedSessions=4906f684-12db-4c1a-88d0-782d25f5bbda)
- dataset sync result: `created=0`, `updated=15`, `skipped=0`

## 5. 핵심 결과

| 지표 | 기준선 (`local-v3`) | 후보안 (`local-v4`) | 변화량 |
| --- | ---: | ---: | ---: |
| `fit_score_band` | 0.6667 | 0.8000 | +0.1333 |
| `classification_match` | 0.8667 | 0.9333 | +0.0666 |
| `must_have_expectation` | 0.9333 | 0.8667 | -0.0666 |
| `deal_breaker_expectation` | 1.0000 | 0.9333 | -0.0667 |
| `role_alignment_match` | 0.7333 | 0.6000 | -0.1333 |
| `must_have_coverage_match` | 0.8667 | 0.8000 | -0.0667 |
| `deal_breaker_severity_match` | 0.9333 | 0.9333 | 0.0000 |
| `transferable_skill_credit` | 0.8667 | 0.8000 | -0.0667 |
| `hard_reject_penalty` | 1.0000 | 1.0000 | 0.0000 |
| `confidence_alignment` | 0.5333 | 0.5333 | 0.0000 |

### 결과 해석

- 후보 prompt는 핵심 목표 지표인 `fit_score_band`를 `0.6667`에서 `0.8000`으로 개선했습니다.
- `classification_match`도 함께 개선되어, 더 좁은 infra-role 지시문이 상위 추천 class를 흔들지는 않았음을 시사합니다.
- 주요 회귀는 `role_alignment_match`, `must_have_coverage_match`, `must_have_expectation`, `transferable_skill_credit`에서 나타났습니다.
- 즉 새 문구는 score band 선택에는 도움이 되었지만, 일부 인접 직무 reasoning을 과하게 눌러 structured sub-judgment 일관성을 낮췄을 가능성이 있습니다.

## 6. Human Review

- queue name: `job-evaluation-review`
- queue id: `a1438ae9-2449-4798-94f1-0243ab9b1e18`
- backend: LangSmith annotation queue
- runs added: `15`

이 queue에는 아래 규칙으로 선별한 borderline 사례와 후보안 실패 run이 들어 있습니다.

- `fit_score` between `40` and `79`
- or `role_alignment = MEDIUM`
- or any tracked evaluator score below `1.0`

### Human Review로 보낸 run

- `a20df58e-b997-4a21-9c59-8c62284520c7` `Senior Machine Learning Engineer`
- `0a6be6e6-a9d0-46af-8ae4-7af130504715` `Frontend Engineer`
- `13665ea6-8805-43a0-a69d-b0d061c86a81` `Applied Scientist`
- `a99b24c6-f5a2-4b77-8556-b1b0d03d7e13` `ML Platform Engineer`
- `8b35e988-db33-4fe8-b44a-e6945c51af42` `Data Engineer for ML Platform`
- `9994ea75-4769-401a-baee-bc8165f1b4d6` `Senior Data Engineer, Experimentation Platform`
- `cdc7faaa-5145-49ad-9ef4-b62f284623f5` `Senior Backend Engineer, Model Serving`
- `564eff8d-770d-4445-a369-8030bad6cf66` `Backend Platform Engineer, AI Runtime`
- `78826cac-73da-4004-b14c-c5f6222d2c37` `Applied Scientist, Ranking`
- `8ed6dede-2168-4bae-bfde-47f70077976a` `Research Scientist, Personalization`
- `e7441209-81df-4059-9729-95692bc60750` `Software Engineer, Experimentation Infrastructure`
- `efbca094-c3e2-4b19-95b4-978e03882153` `MLOps Engineer`
- `480b76fe-6b11-4abb-9fd9-be7f44804d48` `AI Platform Engineer`
- `7b082634-6f18-4c84-a88d-3c17ea1a5f29` `Software Engineer, AI Developer Experience`
- `147e32f5-0264-4413-83fb-8374a3ce36d8` `Machine Learning Infra Engineer`

## 8. 다음 Backlog

아래 항목들은 다음 PromptOps 반복 개선에서 가장 먼저 다룰 후보입니다.

### `prompt:role-alignment`

- 우선순위: `P1`
- 이유: `role_alignment_match`가 `0.7333`에서 `0.6000`으로 하락함
- 액션: score band 개선 효과를 유지하면서, adjacent infra role이 `LOW`와 `MEDIUM` alignment로 매핑되는 방식을 더 정교하게 조정한다

### `prompt:must-have-coverage`

- 우선순위: `P1`
- 이유: `must_have_coverage_match`와 `must_have_expectation`이 모두 하락함
- 액션: transferable skill overlap과 must-have 결손이 분리되어 드러나도록 지시문을 더 명확히 한다

### `prompt:transferable-skill-credit`

- 우선순위: `P1`
- 이유: infra-role banding은 개선됐지만 `transferable_skill_credit`은 하락함
- 액션: score band를 보수적으로 유지하더라도 transferable skill credit은 분명히 드러나도록 설명을 보강한다

### `prompt:summary-usefulness`

- 우선순위: `P1`
- 이유: 일부 후보 run이 여전히 `strength_keywords_match` 또는 `concern_keywords_match`를 놓침
- 액션: role-alignment와 must-have 동작이 다시 안정화된 뒤 explanation wording을 개선한다

## 7. 결정(Decision)

Iteration 001은 아래 전체 루프를 모두 완료했기 때문에 성공한 PromptOps 사이클입니다.

1. baseline snapshot recorded
2. one small prompt diff applied
3. curated experiment rerun
4. LLM-judge comparison captured
5. human review queue created
6. next backlog items registered

현재 후보 revision은 `candidate` 단계에 유지하는 것이 맞습니다. 핵심 score-band 목표는 개선했지만, role-alignment와 must-have 관련 회귀가 수용 가능한지 human review로 확인하기 전에는 승격하지 않아야 합니다.
