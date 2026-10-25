import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone

from dao.interfaces import OrdersDao
from services.interfaces import OrdersService


class OrdersError(Exception):
    def __init__(self, status: int, message: str) -> None:
        self.status = status
        self.message = message
        super().__init__(message)


class OrdersServiceImpl(OrdersService):
    def __init__(self, dao: OrdersDao) -> None:
        self._dao = dao
        self._sequence = 0

    def confirm(self, authorization: str, body: dict) -> dict:
        session = _trader(authorization)
        self._sequence += 1
        order = {
            "order_id": f"CNF-{self._sequence:06d}",
            "trader_id": session["trader_id"],
            "customer_id": body["customer_id"],
            "product_id": body["product_id"],
            "amount": body["amount"],
            "currency": body["currency"],
            "turn_id": body.get("turn_id", ""),
            "status": "trader_confirmed",
            "confirmed_at": datetime.now(timezone.utc).isoformat(),
        }
        return self._dao.add(order)

    def list_for(self, authorization: str) -> dict:
        session = _trader(authorization)
        return {"orders": self._dao.for_trader(session["trader_id"])}


def _trader(authorization: str) -> dict:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise OrdersError(401, "Sign in again.")
    base = os.environ.get("AUTH_BASE_URL", "http://127.0.0.1:8501").rstrip("/")
    request = urllib.request.Request(f"{base}/session", headers={"Authorization": authorization})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            session = json.loads(response.read().decode())
    except urllib.error.HTTPError as exc:
        raise OrdersError(exc.code, "Sign in again.") from exc
    except urllib.error.URLError as exc:
        raise OrdersError(503, f"Auth service is down: {exc.reason}") from exc
    if session.get("role") != "trader":
        raise OrdersError(403, "A trader session is required.")
    return session
