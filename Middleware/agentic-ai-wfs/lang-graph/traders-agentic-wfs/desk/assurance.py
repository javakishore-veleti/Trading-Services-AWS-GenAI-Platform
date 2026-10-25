from abc import ABC, abstractmethod

from desk.client import DeskClientError, quote as fetch_quote


class Judge(ABC):
    @abstractmethod
    def review(self, customer: dict, recommendation: dict, used_quote: dict) -> dict:
        raise NotImplementedError


class ChecklistJudge(Judge):
    """Checks the card and re-reads the quote. It does not call a model and it does not approve the trade."""

    def review(self, customer: dict, recommendation: dict, used_quote: dict) -> dict:
        requirement = customer["settlement_requirement"]
        try:
            fresh = fetch_quote(requirement["base_currency"], requirement["term_currency"])
        except DeskClientError as exc:
            return {"passed": False, "confirm_allowed": False, "checks": [{"name": "quote", "passed": False, "detail": exc.message}]}
        checks = [
            _same("indicative", used_quote["indicative"], fresh["indicative"]),
            _same("window outright", used_quote["window_forward"]["outright"], fresh["window_forward"]["outright"]),
            _same("futures price", used_quote["currency_futures"]["price"], fresh["currency_futures"]["price"]),
            _text("rationale", recommendation.get("rationale", "")),
            _text("evidence", recommendation.get("evidence", [])),
            _text("alternatives", recommendation.get("alternatives", [])),
            _text("risks", recommendation.get("risks", [])),
            {"name": "trader decides", "passed": recommendation.get("trader_decides") is True, "detail": "The trader remains the decision maker."},
        ]
        passed = all(item["passed"] for item in checks) and bool(recommendation.get("product_id"))
        return {"passed": passed, "confirm_allowed": passed, "checks": checks, "quote_id": fresh["quote_id"]}


def _same(name: str, used: float, fresh: float) -> dict:
    passed = abs(float(used) - float(fresh)) < 0.001
    return {"name": name, "passed": passed, "detail": f"used {used} and the offers service now shows {fresh}"}


def _text(name: str, value) -> dict:
    return {"name": name, "passed": bool(value), "detail": "present" if value else "missing"}
