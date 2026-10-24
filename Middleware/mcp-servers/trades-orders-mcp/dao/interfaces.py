from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import CreateOrderRequest, GetOrderRequest, ListOrdersRequest, OrderDto, OrderRowDto, OrderRowsDto


class OrderDao(ABC):
    @abstractmethod
    def find_orders(self, request: ListOrdersRequest) -> OrderRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_order(self, request: GetOrderRequest) -> OrderRowDto:
        raise NotImplementedError

    @abstractmethod
    def insert_order(self, request: CreateOrderRequest) -> OrderDto:
        raise NotImplementedError
