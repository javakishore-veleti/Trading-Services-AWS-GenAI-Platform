from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from services.impl.customersvc import CustomerError
from services.object_factory import ServiceObjectFactory


class ManyBody(BaseModel):
    customer_ids: list[str] = Field(default_factory=list)


class CustomerBody(BaseModel):
    customer_id: str = ""
    name: str = ""
    country: str = ""
    resident: bool = True
    preferred_product: str = ""
    amount: float = 0
    currency: str = ""
    base_currency: str = ""
    term_currency: str = ""
    usd_available_now: bool = False
    dates: list[str] = Field(default_factory=list)


class OrderBody(BaseModel):
    order_id: str = ""
    customer_id: str = ""
    book_id: str = ""
    product_id: str = ""
    base_currency: str = ""
    term_currency: str = ""
    amount: float = 0
    currency: str = ""
    order_date: str = ""
    value_date: str = ""
    rate: float = 0


class CustomerApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/ingestion", self.statuses, methods=["GET"])
        self.router.add_api_route("/ingestion/{dataset_key}", self.status, methods=["GET"])
        self.router.add_api_route("/customers/populate", self.populate_customers, methods=["POST"])
        self.router.add_api_route("/customers", self.customers, methods=["GET"])
        self.router.add_api_route("/customers", self.add_customer, methods=["POST"])
        self.router.add_api_route("/customers/lookup", self.many, methods=["POST"])
        self.router.add_api_route("/customers/{customer_id}", self.customer, methods=["GET"])
        self.router.add_api_route("/customers/{customer_id}/orders", self.orders_for, methods=["GET"])
        self.router.add_api_route("/customer-trades-history/populate", self.populate_orders, methods=["POST"])
        self.router.add_api_route("/customer-trades-history", self.orders, methods=["GET"])
        self.router.add_api_route("/orders", self.add_order, methods=["POST"])

    def statuses(self) -> dict:
        return ServiceObjectFactory.customer_service().statuses()

    def status(self, dataset_key: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().status(dataset_key))

    def populate_customers(self, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().populate_customers(authorization))

    def populate_orders(self, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().populate_orders(authorization))

    def add_customer(self, body: CustomerBody, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().add_customer(authorization, body.model_dump()))

    def add_order(self, body: OrderBody, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().add_order(authorization, body.model_dump()))

    def customers(self, page: int = 1, page_size: int = 20) -> dict:
        return ServiceObjectFactory.customer_service().customers(page, page_size)

    def customer(self, customer_id: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().customer(customer_id))

    def orders_for(self, customer_id: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.customer_service().orders_for(customer_id))

    def orders(self, page: int = 1, page_size: int = 20) -> dict:
        return ServiceObjectFactory.customer_service().orders(page, page_size)

    def many(self, body: ManyBody) -> dict:
        return ServiceObjectFactory.customer_service().many(body.customer_ids)

    def _call(self, action):
        try:
            return action()
        except CustomerError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
