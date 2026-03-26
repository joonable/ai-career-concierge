from __future__ import annotations

from agent.nodes.deliver_node import DeliverNode
from agent.nodes.ingest_node import IngestNode
from agent.nodes.llm_eval_node import LLMEvalNode
from agent.nodes.rule_filter_node import RuleFilterNode
from agent.pipeline_state import AgentState
from langgraph.graph import END, START, StateGraph


def build_pipeline_graph(
    ingest_node: IngestNode,
    rule_filter_node: RuleFilterNode,
    llm_eval_node: LLMEvalNode,
    deliver_node: DeliverNode,
):
    graph = StateGraph(AgentState)
    graph.add_node("IngestNode", ingest_node.run)
    graph.add_node("RuleFilterNode", rule_filter_node.run)
    graph.add_node("LLMEvalNode", llm_eval_node.run)
    graph.add_node("DeliverNode", deliver_node.run)

    graph.add_edge(START, "IngestNode")
    graph.add_edge("IngestNode", "RuleFilterNode")
    graph.add_edge("RuleFilterNode", "LLMEvalNode")
    graph.add_edge("LLMEvalNode", "DeliverNode")
    graph.add_edge("DeliverNode", END)

    return graph.compile()
