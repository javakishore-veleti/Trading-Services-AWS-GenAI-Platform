import json
import os
import urllib.error
import urllib.parse
import urllib.request


class DeskClientError(Exception):
    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def base_url(env_name: str, default: str) -> str:
    return os.environ.get(env_name, default).rstrip("/")


def get_json(url: str, headers: dict | None = None) -> dict:
    request = urllib.request.Request(url, headers=headers or {})
    return _read(request)


def post_json(url: str, payload: dict, headers: dict | None = None) -> dict:
    body = json.dumps(payload).encode()
    merged = {"Content-Type": "application/json"}
    if headers:
        merged.update(headers)
    request = urllib.request.Request(url, data=body, headers=merged, method="POST")
    return _read(request)


def _read(request: urllib.request.Request) -> dict:
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode()
        raise DeskClientError(_detail(raw) or f"{request.full_url} returned {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise DeskClientError(f"Cannot reach {request.full_url}: {exc.reason}") from exc


def _detail(raw: str) -> str:
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return raw
    detail = parsed.get("detail", raw)
    return detail if isinstance(detail, str) else raw


def customer_record(customer_id: str) -> dict:
    root = base_url("CUSTOMER_BASE_URL", "http://127.0.0.1:8503")
    return get_json(f"{root}/customers/{urllib.parse.quote(customer_id)}")


def customer_orders(customer_id: str) -> list[dict]:
    root = base_url("CUSTOMER_BASE_URL", "http://127.0.0.1:8503")
    payload = get_json(f"{root}/customers/{urllib.parse.quote(customer_id)}/orders")
    return payload["orders"]


def customer_names(customer_ids: list[str]) -> list[dict]:
    root = base_url("CUSTOMER_BASE_URL", "http://127.0.0.1:8503")
    payload = post_json(f"{root}/customers/lookup", {"customer_ids": customer_ids})
    return payload["customers"]


def trader_customers(trader_id: str) -> list[str]:
    root = base_url("TRADERS_BASE_URL", "http://127.0.0.1:8502")
    payload = get_json(f"{root}/traders/{urllib.parse.quote(trader_id)}/customers")
    return payload["customer_ids"]


def eligibility(customer_id: str) -> list[dict]:
    root = base_url("CATALOG_BASE_URL", "http://127.0.0.1:8504")
    payload = get_json(f"{root}/eligibility?customer_id={urllib.parse.quote(customer_id)}")
    return payload["products"]


def references() -> list[dict]:
    root = base_url("CATALOG_BASE_URL", "http://127.0.0.1:8504")
    return get_json(f"{root}/regulatory-references")["references"]


def quote(base: str, term: str) -> dict:
    root = base_url("OFFERS_BASE_URL", "http://127.0.0.1:8505")
    query = urllib.parse.urlencode({"base": base, "term": term, "direction": "sell_base"})
    return get_json(f"{root}/quotes?{query}")


def session(authorization: str) -> dict:
    root = base_url("AUTH_BASE_URL", "http://127.0.0.1:8501")
    return get_json(f"{root}/session", headers={"Authorization": authorization})
