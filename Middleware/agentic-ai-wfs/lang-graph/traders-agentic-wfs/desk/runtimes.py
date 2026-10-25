from abc import ABC, abstractmethod
from datetime import datetime, timezone

from desk.client import (
    DeskClientError,
    customer_orders,
    customer_record,
    eligibility,
    quote,
    references,
)
from desk.graph import build_graph


class QuestionRuntime(ABC):
    key = ""
    connected = False

    @abstractmethod
    def answer(self, question: str, customer_id: str) -> dict:
        raise NotImplementedError


class LangGraphRuntime(QuestionRuntime):
    key = "langgraph"
    connected = True

    def __init__(self) -> None:
        self._graph = build_graph()

    def answer(self, question: str, customer_id: str) -> dict:
        try:
            customer = customer_record(customer_id)
            orders = customer_orders(customer_id)
            product_rules = eligibility(customer_id)
            refs = references()
            requirement = customer["settlement_requirement"]
            board = quote(requirement["base_currency"], requirement["term_currency"])
        except DeskClientError as exc:
            return _turn("langgraph", True, question, [], None, {"passed": False, "confirm_allowed": False, "checks": []}, exc.message)
        state = self._graph.invoke({
            "customer": customer,
            "orders": orders,
            "eligibility": product_rules,
            "references": refs,
            "quote": board,
        })
        findings = [
            state["behavior"],
            state["history"],
            state["settlement"],
            state["market"],
            state["hedging"],
            state["regulatory"],
        ]
        assurance = state["assurance"]
        return _turn("langgraph", True, question, findings, state["decision"], assurance, "")


class UnconnectedRuntime(QuestionRuntime):
    def __init__(self, key: str, label: str) -> None:
        self.key = key
        self.connected = False
        self._label = label

    def answer(self, question: str, customer_id: str) -> dict:
        message = f"{self._label} is not connected. LangGraph is the runtime for this desk."
        return _turn(self.key, False, question, [], None, {"passed": False, "confirm_allowed": False, "checks": []}, message)


_LANGGRAPH: LangGraphRuntime | None = None


def runtime_for(framework: str | None) -> QuestionRuntime:
    global _LANGGRAPH
    key = (framework or "langgraph").strip().lower() or "langgraph"
    if key == "langgraph":
        if _LANGGRAPH is None:
            _LANGGRAPH = LangGraphRuntime()
        return _LANGGRAPH
    if key == "strands":
        return UnconnectedRuntime("strands", "Strands")
    if key == "agno":
        return UnconnectedRuntime("agno", "Agno")
    raise ValueError(f"Unknown framework {framework}.")


def frameworks() -> dict:
    return {
        "default": "langgraph",
        "frameworks": [
            {"id": "langgraph", "label": "LangGraph", "connected": True},
            {"id": "strands", "label": "Strands", "connected": False},
            {"id": "agno", "label": "Agno", "connected": False},
        ],
    }


def _turn(framework: str, connected: bool, question: str, findings: list, recommendation: dict | None, assurance: dict, message: str) -> dict:
    return {
        "framework": framework,
        "connected": connected,
        "question": question,
        "asked_at": datetime.now(timezone.utc).isoformat(),
        "agents": findings,
        "recommendation": recommendation,
        "assurance": assurance,
        "message": message,
        "confirm_allowed": bool(assurance.get("confirm_allowed")),
    }
