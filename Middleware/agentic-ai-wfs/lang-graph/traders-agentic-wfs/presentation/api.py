import uuid

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

from desk.cache import CacheFactory
from desk.client import DeskClientError, session, trader_customers
from desk.runtimes import frameworks, runtime_for


class TurnBody(BaseModel):
    customer_id: str
    message: str
    framework: str | None = None


class DeskApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/frameworks", self.list_frameworks, methods=["GET"])
        self.router.add_api_route("/turns", self.ask, methods=["POST"])
        self.router.add_api_route("/turns", self.list_turns, methods=["GET"])

    def list_frameworks(self) -> dict:
        return frameworks()

    def ask(self, body: TurnBody, authorization: str = Header(default="")) -> dict:
        trader = _trader(authorization)
        _allowed(trader["trader_id"], body.customer_id)
        text = body.message.strip()
        if not text:
            raise HTTPException(status_code=400, detail="Enter a question.")
        try:
            runtime = runtime_for(body.framework)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        turn = runtime.answer(text, body.customer_id)
        turn["turn_id"] = uuid.uuid4().hex
        turn["trader_id"] = trader["trader_id"]
        turn["customer_id"] = body.customer_id
        cache = CacheFactory.cache()
        cache.add(trader["trader_id"], body.customer_id, turn)
        return cache.page(trader["trader_id"], body.customer_id, 1, 5)

    def list_turns(self, customer_id: str, page: int = 1, page_size: int = 5, authorization: str = Header(default="")) -> dict:
        trader = _trader(authorization)
        _allowed(trader["trader_id"], customer_id)
        return CacheFactory.cache().page(trader["trader_id"], customer_id, page, page_size)


def _trader(authorization: str) -> dict:
    prefix = "Bearer "
    if not authorization.startswith(prefix):
        raise HTTPException(status_code=401, detail="Sign in again.")
    try:
        found = session(authorization)
    except DeskClientError as exc:
        raise HTTPException(status_code=401, detail=exc.message) from exc
    if found.get("role") != "trader":
        raise HTTPException(status_code=403, detail="A trader session is required.")
    return found


def _allowed(trader_id: str, customer_id: str) -> None:
    try:
        customers = trader_customers(trader_id)
    except DeskClientError as exc:
        raise HTTPException(status_code=409, detail=exc.message) from exc
    if customer_id not in customers:
        raise HTTPException(status_code=403, detail="That customer is not assigned to this trader.")
