from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, Field

from services.impl.traderssvc import TradersError
from services.object_factory import ServiceObjectFactory


class BookBody(BaseModel):
    book_id: str = ""
    name: str = ""
    base_currency: str = ""
    term_currency: str = ""
    products: list[str] = Field(default_factory=list)


class TraderBody(BaseModel):
    trader_id: str = ""
    username: str = ""
    display_name: str = ""
    desk: str = ""
    customer_ids: list[str] = Field(default_factory=list)


class MappingBody(BaseModel):
    trader_id: str = ""
    book_id: str = ""


class TradersApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/ingestion", self.statuses, methods=["GET"])
        self.router.add_api_route("/ingestion/{dataset_key}", self.status, methods=["GET"])
        self.router.add_api_route("/books/populate", self.populate_books, methods=["POST"])
        self.router.add_api_route("/books", self.books, methods=["GET"])
        self.router.add_api_route("/books", self.add_book, methods=["POST"])
        self.router.add_api_route("/traders/populate", self.populate_traders, methods=["POST"])
        self.router.add_api_route("/traders", self.traders, methods=["GET"])
        self.router.add_api_route("/traders", self.add_trader, methods=["POST"])
        self.router.add_api_route("/traders/{trader_id}", self.trader, methods=["GET"])
        self.router.add_api_route("/traders/{trader_id}/customers", self.customers_for, methods=["GET"])
        self.router.add_api_route("/traders/{trader_id}/books", self.books_for, methods=["GET"])
        self.router.add_api_route("/trader-book-mappings/populate", self.populate_mappings, methods=["POST"])
        self.router.add_api_route("/trader-book-mappings", self.mappings, methods=["GET"])
        self.router.add_api_route("/trader-book-mappings", self.add_mapping, methods=["POST"])

    def statuses(self) -> dict:
        return ServiceObjectFactory.traders_service().statuses()

    def status(self, dataset_key: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().status(dataset_key))

    def populate_books(self, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().populate_books(authorization))

    def populate_traders(self, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().populate_traders(authorization))

    def populate_mappings(self, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().populate_mappings(authorization))

    def add_book(self, body: BookBody, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().add_book(authorization, body.model_dump()))

    def add_trader(self, body: TraderBody, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().add_trader(authorization, body.model_dump()))

    def add_mapping(self, body: MappingBody, authorization: str = Header(default="")) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().add_mapping(authorization, body.model_dump()))

    def books(self, page: int = 1, page_size: int = 20) -> dict:
        return ServiceObjectFactory.traders_service().books(page, page_size)

    def traders(self, page: int = 1, page_size: int = 20) -> dict:
        return ServiceObjectFactory.traders_service().traders(page, page_size)

    def mappings(self, page: int = 1, page_size: int = 20) -> dict:
        return ServiceObjectFactory.traders_service().mappings(page, page_size)

    def trader(self, trader_id: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().trader(trader_id))

    def customers_for(self, trader_id: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().customers_for(trader_id))

    def books_for(self, trader_id: str) -> dict:
        return self._call(lambda: ServiceObjectFactory.traders_service().books_for(trader_id))

    def _call(self, action):
        try:
            return action()
        except TradersError as exc:
            raise HTTPException(status_code=exc.status, detail=exc.message) from exc
        except FileNotFoundError as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
        except RuntimeError as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except Exception as exc:
            raise HTTPException(status_code=500, detail=str(exc)) from exc
