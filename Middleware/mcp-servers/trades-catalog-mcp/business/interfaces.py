from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import GetProductRequest, ValidationDto


class CatalogBiz(ABC):
    @abstractmethod
    def validate_get(self, request: GetProductRequest) -> ValidationDto:
        raise NotImplementedError
