from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel


class ConfirmBody(BaseModel):
    customer_id: str
    product_id: str
    amount: float
    currency: str
    turn_id: str = ""


class OrdersApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/orders", self.confirm, methods=["POST"])
        self.router.add_api_route("/orders", self.list_for, methods=["GET"])

    def confirm(self, body: ConfirmBody, authorization: str = Header(default="")) -> dict:
        from services.impl.orderssvc import OrdersError
        from services.object_factory import ServiceObjectFactory

        try:
            return ServiceObjectFactory.orders_service().confirm(authorization, body.model_dump())
        except OrdersError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc

    def list_for(self, authorization: str = Header(default="")) -> dict:
        from services.impl.orderssvc import OrdersError
        from services.object_factory import ServiceObjectFactory

        try:
            return ServiceObjectFactory.orders_service().list_for(authorization)
        except OrdersError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc
