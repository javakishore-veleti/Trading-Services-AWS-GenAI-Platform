from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import (
    CreateOrderRequest,
    CreateOrderResponse,
    GetOrderRequest,
    GetOrderResponse,
    ListOrdersRequest,
    ListOrdersResponse,
)


class OrderSvc(ABC):
    @abstractmethod
    def list_orders(self, request: ListOrdersRequest) -> ListOrdersResponse:
        raise NotImplementedError

    @abstractmethod
    def get_order(self, request: GetOrderRequest) -> GetOrderResponse:
        raise NotImplementedError

    @abstractmethod
    def create_order(self, request: CreateOrderRequest) -> CreateOrderResponse:
        raise NotImplementedError
