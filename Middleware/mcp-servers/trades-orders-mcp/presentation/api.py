from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from common.dtos.req_resp_dtos import (
    CreateOrderRequest,
    CreateOrderResponse,
    ErrorDto,
    GetOrderRequest,
    GetOrderResponse,
    ListOrdersRequest,
    ListOrdersResponse,
)
from workflows.interfaces import CreateOrderWf, GetOrderWf, ListOrdersWf
from workflows.object_factory import WorkflowObjectFactory


class OrderApi:
    def __init__(self) -> None:
        self.router = APIRouter()
        self.router.add_api_route("/orders", self.list_orders, methods=["GET"], response_model=ListOrdersResponse)
        self.router.add_api_route("/orders", self.create_order, methods=["POST"], response_model=CreateOrderResponse)
        self.router.add_api_route("/orders/{order_id}", self.get_order, methods=["GET"], response_model=GetOrderResponse)

    def list_orders(self, request: Annotated[ListOrdersRequest, Depends()]) -> ListOrdersResponse:
        workflow: ListOrdersWf = WorkflowObjectFactory.list_orders()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def get_order(self, order_id: str) -> GetOrderResponse:
        workflow: GetOrderWf = WorkflowObjectFactory.get_order()
        response = workflow.invoke(GetOrderRequest(order_id=order_id))
        self._raise_for_error(response.error)
        return response

    def create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        workflow: CreateOrderWf = WorkflowObjectFactory.create_order()
        response = workflow.invoke(request)
        self._raise_for_error(response.error)
        return response

    def _raise_for_error(self, error: ErrorDto | None) -> None:
        if error is None:
            return
        status = 404 if error.code == "not_found" else 400
        raise HTTPException(status_code=status, detail=error.message)
