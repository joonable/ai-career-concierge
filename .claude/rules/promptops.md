<!-- AGENTS.md 추출: 프롬프트 관리 규칙 + docs/promptops/README.md 참조 -->

# PromptOps 규칙

## 프롬프트 관리

- 프롬프트를 라우트/서비스/테스트에 인라인으로 흩어놓지 않고 전용 모듈에 보관한다.
- 목적에 따라 프롬프트 이름을 지정한다 (추적 가능하도록).
- 프롬프트 지침, 구조화된 출력 스키마, 파싱 로직, 검증 테스트를 같은 변경에서 정렬한다.
- 스키마 변경 시 프롬프트 텍스트, 파서/검증기, 테스트를 함께 업데이트한다.

## 거버넌스 원칙 (docs/promptops/README.md 참조)

1. 프롬프트는 계약의 일부 (출력 스키마, 정책, 컨텍스트 정규화, 평가기, 리뷰 루브릭 포함)
2. 작은 변경만 수행 (baseline → small diff → 실험 → 비교 → 리뷰 → backlog)
3. 원시 컨텍스트를 직접 주입하지 않는다 (정규화된 컨텍스트 사용)
4. 외부 백엔드는 어댑터 뒤에 둔다 (LangSmith가 첫 어댑터)
5. 실패는 다음 액션으로 이어진다 (분류: prompt/policy/context/dataset/feature gap)

## 프롬프트 패밀리

- `job-evaluation` (v3, schema_version=3) -- 채용 공고 평가
- `memory-summary` (v1, schema_version=1) -- 피드백 요약

## 주요 파일 경로

- 코어: `src/promptops/core/` (models, experiments, failures, reviews, registry)
- 어댑터: `src/promptops/adapters/langsmith.py`
- 프로젝트: `src/promptops/projects/ai_career_concierge/` (context, prompts, review_rubric, backlog_rules)
- 러너: `src/promptops/run_iteration.py`
- 평가기: `src/agent/evals/rule_based_evaluators.py` (6개 규칙 기반 평가기)

## CLI 명령어

- 데이터셋 동기화: `APP_ENV=development poetry run eval-jobs sync-dataset`
- 실험 실행: `APP_ENV=development .venv/bin/python3 -m promptops.run_iteration <ID>`
- iteration 리포트: `docs/promptops/iterations/iteration_<ID>.md`

## 에이전트 워크플로우 규칙

- 실험 실행 후 반드시 iteration 리포트를 읽고 분석을 제안한다.
- 실패 패턴이 3회 이상 반복되면 taxonomy 업데이트를 제안한다.
- borderline 케이스(fit_score 40-79, role_alignment MEDIUM) 발견 시 데이터셋 큐레이션을 제안한다.
- 프롬프트 변경 제안 시 반드시 현재 baseline과 비교 근거를 제시한다.
- 규칙 필터 거부 패턴을 분석하여 임계값 조정을 제안한다.

## 실패 분류 체계 (FAILURE_TAXONOMY)

10개 카테고리: `src/promptops/core/failures.py` 참조.
borderline 판별: `is_borderline_case()`, failure 판별: `is_failure_case()`
