from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import CreateOrderRequest, GetOrderRequest, ValidationDto


class OrderBiz(ABC):
    @abstractmethod
    def validate_get(self, request: GetOrderRequest) -> ValidationDto:
        raise NotImplementedError

    @abstractmethod
    def validate_create(self, request: CreateOrderRequest) -> ValidationDto:
        raise NotImplementedError
