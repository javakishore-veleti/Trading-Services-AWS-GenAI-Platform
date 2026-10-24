from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import GetProductRequest, ListProductsRequest, ProductRowDto, ProductRowsDto


class CatalogDao(ABC):
    @abstractmethod
    def find_products(self, request: ListProductsRequest) -> ProductRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_product(self, request: GetProductRequest) -> ProductRowDto:
        raise NotImplementedError
