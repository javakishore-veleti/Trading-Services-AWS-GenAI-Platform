from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from common.dtos.req_resp_dtos import (
    ErrorDto,
    ListCustomersRequest,
    ListCustomersResponse,
    ListRatingsRequest,
    ListRatingsResponse,
    PriceOfferRequest,
    PriceOfferResponse,
)
from workflows.interfaces import ListCustomersWf, ListRatingsWf, QuoteOfferWf
from workflows.object_factory import WorkflowObjectFactory


class OfferApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/customers", self.list_customers, methods=["GET"], response_model=ListCustomersResponse)
        self.router.add_api_route("/ratings", self.list_ratings, methods=["GET"], response_model=ListRatingsResponse)
        self.router.add_api_route("/offers/price", self.price, methods=["POST"], response_model=PriceOfferResponse)

    def list_customers(self, request: Annotated[ListCustomersRequest, Depends()]) -> ListCustomersResponse:
        workflow: ListCustomersWf = WorkflowObjectFactory.list_customers()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def list_ratings(self, request: Annotated[ListRatingsRequest, Depends()]) -> ListRatingsResponse:
        workflow: ListRatingsWf = WorkflowObjectFactory.list_ratings()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def price(self, request: PriceOfferRequest) -> PriceOfferResponse:
        workflow: QuoteOfferWf = WorkflowObjectFactory.quote_offer()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def _raise_for_error(self, error: ErrorDto | None) -> None:
        if error is None:
            return
        status = 404 if error.code == "not_found" else 400
        raise HTTPException(status_code=status, detail=error.message)
