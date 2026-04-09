<!-- AGENTS.md 추출: 핵심 워크플로우 계약, 데이터 모델 예상 사항, 마이그레이션 규칙 -->

# 파이프라인 계약

## LangGraph 노드 흐름

```
START → IngestNode → RuleFilterNode → LLMEvalNode → DeliverNode → END
```

규칙 필터링을 우회하고 스크래핑된 원시 공고를 LLM 평가로 직접 보내지 않는다.

## 공유 파이프라인 상태 (AgentState)

- `current_jobs` -- List[PipelineJob]
- `user_context` -- Dict (유저 프로필 + 필터)
- `recent_memory` -- str (싫어요 피드백 요약)
- `evaluation_results` -- List[LLMEvaluationResult]
- `run_id` -- str (추적용)
- `source_errors` -- List[str] (우아한 저하)

## 데이터 모델

핵심 엔티티: `User`, `Job`, `Evaluation`, `System_Log`

### 평가 수명 주기
```
PENDING → RULE_REJECTED (규칙 거부)
       → LLM_EVALUATED (LLM 평가 완료)
```

### 피드백 상태
- `LIKE`, `DISLIKE`

### 불변성 (Invariants)
- `Job.external_job_id`는 소스별로 고유해야 한다 (중복 수집 방지).
- 규칙 기반 거부도 평가 상태로 유지(persist)되어야 한다.
- 싫어요 피드백은 이유와 함께 저장할 수 있어야 한다.

## 마이그레이션 규칙

- 스키마 변경을 로컬 리팩터링이 아닌 계약 변경으로 취급한다.
- 순방향 마이그레이션 경로와 롤백/호환성 계획을 포함한다.
- PoC 런타임에서는 Supabase SQL/MCP를 선호한다.
- 레거시 SQLModel 참조, DB 스키마, 상태 enum, API 가정을 동기화 유지한다.
- 스키마 변경이 API 응답/평가 수명주기/피드백에 영향을 미치면 같은 변경에서 테스트와 문서를 업데이트한다.

## 안정성 요구 사항

- 한 플랫폼의 스크래핑 실패가 전체 파이프라인을 중단시키지 않는다.
- 실패한 소스는 건너뛰고 기록되며 운영상 보고된다.
- 중요한 실패는 `System_Log`에 기록한다.

## 옵저버빌리티

- 파이프라인 실행마다 `run_id` 또는 `trace_id`를 방출하고 하위 작업 전반에 재사용한다.
- 구조화된 로그에 `run_id`, `user_id`, `job_id`, `platform`, `status`, `error_type`을 포함한다.
- 시크릿, 액세스 토큰, PII를 기록하지 않는다.

## 현재 단일 사용자 가정

이 파이프라인은 현재 단일 사용자 PoC 기반이다. 멀티유저 확장 시 파이프라인 스케줄링, 유저별 설정 주입 등 리팩토링이 필요하다.
