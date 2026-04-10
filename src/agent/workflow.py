from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from agent.nodes.deliver_node import DeliverNode
from agent.nodes.ingest_node import IngestNode
from agent.nodes.llm_eval_node import LLMEvalNode
from agent.nodes.rule_filter_node import RuleFilterNode
from agent.pipeline_state import AgentState


def build_pipeline_graph(
    ingest_node: IngestNode,
    rule_filter_node: RuleFilterNode,
    llm_eval_node: LLMEvalNode,
    deliver_node: DeliverNode,
):
    """
    LangGraph를 사용하여 채용 공고 평가 파이프라인의 핵심 워크플로우를 정의하고 연결합니다.
    단계를 순차적으로 실행하는 DAG(Directed Acyclic Graph) 구조입니다.

    흐름 (Flow):
    1. IngestNode: 채용 플랫폼(예: 인크루트)에서 공고를 비동기로 수집합니다.
    2. RuleFilterNode: 연차, 직무 키워드 등 DB 쿼리 기반 첫 번째 필터링을 수행합니다. (LLM 비용 절감)
    3. LLMEvalNode: 필터링을 통과한 공고만 LLM(Gemini)에 넘겨 정밀 평가를 진행합니다.
    4. DeliverNode: 기준 점수 이상의 공고를 포맷팅하여 Slack 등으로 사용자에게 전달합니다.
    """
    graph = StateGraph(AgentState)

    # 1. 그래프에 노드(컴포넌트) 추가
    graph.add_node("IngestNode", ingest_node.run)
    graph.add_node("RuleFilterNode", rule_filter_node.run)
    graph.add_node("LLMEvalNode", llm_eval_node.run)
    graph.add_node("DeliverNode", deliver_node.run)

    # 2. 노드 간의 실행 순서(Edge) 정의
    graph.add_edge(START, "IngestNode")
    graph.add_edge("IngestNode", "RuleFilterNode")
    graph.add_edge("RuleFilterNode", "LLMEvalNode")
    graph.add_edge("LLMEvalNode", "DeliverNode")
    graph.add_edge("DeliverNode", END)

    # 정의된 그래프를 컴파일하여 실행 가능한 형태로 반환
    return graph.compile()
