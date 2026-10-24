from abc import ABC, abstractmethod

from pydantic import BaseModel

from common.dtos.req_resp_dtos import (
    CreateOrderRequest,
    CreateOrderResponse,
    GetOrderRequest,
    GetOrderResponse,
    ListOrdersRequest,
    ListOrdersResponse,
)


class WfTask(ABC):
    @abstractmethod
    def execute(self, context: BaseModel) -> BaseModel:
        raise NotImplementedError


class ListOrdersWf(ABC):
    @abstractmethod
    def invoke(self, request: ListOrdersRequest) -> ListOrdersResponse:
        raise NotImplementedError


class GetOrderWf(ABC):
    @abstractmethod
    def invoke(self, request: GetOrderRequest) -> GetOrderResponse:
        raise NotImplementedError


class CreateOrderWf(ABC):
    @abstractmethod
    def invoke(self, request: CreateOrderRequest) -> CreateOrderResponse:
        raise NotImplementedError
