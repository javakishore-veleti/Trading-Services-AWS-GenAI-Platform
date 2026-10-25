from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from desk.assurance import ChecklistJudge
from desk.decision import choose, rank_products, recommendation
from desk.findings import (
    behavior_finding,
    hedging_finding,
    history_finding,
    market_finding,
    regulatory_finding,
    settlement_finding,
)


class DeskState(TypedDict, total=False):
    customer: dict
    orders: list
    eligibility: list
    references: list
    quote: dict
    behavior: dict
    history: dict
    settlement: dict
    market: dict
    hedging: dict
    regulatory: dict
    decision: dict
    assurance: dict


def _behavior(state: DeskState) -> dict:
    return {"behavior": behavior_finding(state["customer"])}


def _history(state: DeskState) -> dict:
    return {"history": history_finding(state["customer"], state["orders"])}


def _settlement(state: DeskState) -> dict:
    return {"settlement": settlement_finding(state["customer"])}


def _market(state: DeskState) -> dict:
    return {"market": market_finding(state["quote"])}


def _regulatory(state: DeskState) -> dict:
    return {"regulatory": regulatory_finding(state["eligibility"], state["references"])}


def _hedging(state: DeskState) -> dict:
    scores = rank_products(state["customer"], state["orders"], state["eligibility"], state["quote"])
    winner = choose(scores)
    return {"hedging": hedging_finding(state["customer"], winner)}


def _decision(state: DeskState) -> dict:
    findings = [state["behavior"], state["history"], state["settlement"], state["market"], state["hedging"], state["regulatory"]]
    return {"decision": recommendation(state["customer"], state["orders"], state["eligibility"], state["quote"], findings)}


def _assurance(state: DeskState) -> dict:
    return {"assurance": ChecklistJudge().review(state["customer"], state["decision"], state["quote"])}


def build_graph():
    graph = StateGraph(DeskState)
    graph.add_node("customer_behavior", _behavior)
    graph.add_node("historical_transaction", _history)
    graph.add_node("settlement_requirements", _settlement)
    graph.add_node("market_intelligence", _market)
    graph.add_node("regulatory_analysis", _regulatory)
    graph.add_node("hedging_strategy", _hedging)
    graph.add_node("decision_intelligence", _decision)
    graph.add_node("ai_assurance", _assurance)
    graph.add_edge(START, "customer_behavior")
    graph.add_edge("customer_behavior", "historical_transaction")
    graph.add_edge("historical_transaction", "settlement_requirements")
    graph.add_edge("settlement_requirements", "market_intelligence")
    graph.add_edge("market_intelligence", "regulatory_analysis")
    graph.add_edge("regulatory_analysis", "hedging_strategy")
    graph.add_edge("hedging_strategy", "decision_intelligence")
    graph.add_edge("decision_intelligence", "ai_assurance")
    graph.add_edge("ai_assurance", END)
    return graph.compile()
