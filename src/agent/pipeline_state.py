from __future__ import annotations

from typing import Any, Dict, List, TypedDict

from agent.schemas.evaluation_result import LLMEvaluationResult
from agent.schemas.pipeline_job import PipelineJob


class AgentState(TypedDict, total=False):
    """
    LangGraph 파이프라인이 실행되는 동안 유지 및 전달되는 전역 상태(State) 객체입니다.
    """

    current_jobs: List[PipelineJob]  # 이번 파이프라인 주기에서 처리해야 할 공고 대기열
    user_context: Dict[str, Any]  # User DB에서 로드된 사용자의 프로필, 필터 요건 (Must-haves, Deal-breakers 등)
    recent_memory: str  # 과거 사용자의 '별로예요(Dislike)' 피드백을 요약한 단기 기억 (시스템 프롬프트 주입용)
    evaluation_results: List[LLMEvaluationResult]  # 처리가 모두 완료된 평가 결과들 집합
    run_id: str  # 파이프라인 모니터링/추적을 위한 실행 고유 ID (Observability)
    source_errors: List[str]  # 지정된 데이터 소스에서 공고 수집 중 발생한 오류 (Graceful Degradation 처리용)
