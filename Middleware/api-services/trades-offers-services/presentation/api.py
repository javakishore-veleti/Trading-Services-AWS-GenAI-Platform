from fastapi import APIRouter, HTTPException

from services.impl.offerssvc import OffersError
from services.object_factory import ServiceObjectFactory


class OffersApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/quotes", self.quote, methods=["GET"])

    def quote(self, base: str, term: str, direction: str = "sell_base") -> dict:
        try:
            return ServiceObjectFactory.offers_service().quote(base, term, direction)
        except OffersError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc
