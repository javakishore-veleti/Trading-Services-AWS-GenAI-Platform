from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import GetProductRequest, GetProductResponse, ListProductsRequest, ListProductsResponse


class CatalogSvc(ABC):
    @abstractmethod
    def list_products(self, request: ListProductsRequest) -> ListProductsResponse:
        raise NotImplementedError

    @abstractmethod
    def get_product(self, request: GetProductRequest) -> GetProductResponse:
        raise NotImplementedError
