from abc import ABC, abstractmethod

from pydantic import BaseModel

from common.dtos.req_resp_dtos import (
    GetProductRequest,
    GetProductResponse,
    ListProductsRequest,
    ListProductsResponse,
)


class WfTask(ABC):
    @abstractmethod
    def execute(self, context: BaseModel) -> BaseModel:
        raise NotImplementedError


class ListProductsWf(ABC):
    @abstractmethod
    def invoke(self, request: ListProductsRequest) -> ListProductsResponse:
        raise NotImplementedError


class GetProductWf(ABC):
    @abstractmethod
    def invoke(self, request: GetProductRequest) -> GetProductResponse:
        raise NotImplementedError
