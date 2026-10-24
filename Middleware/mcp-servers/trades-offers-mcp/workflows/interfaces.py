from abc import ABC, abstractmethod

from pydantic import BaseModel

from common.dtos.req_resp_dtos import (
    ListCustomersRequest,
    ListCustomersResponse,
    ListRatingsRequest,
    ListRatingsResponse,
    PriceOfferRequest,
    PriceOfferResponse,
)


class WfTask(ABC):
    @abstractmethod
    def execute(self, context: BaseModel) -> BaseModel:
        raise NotImplementedError


class ListCustomersWf(ABC):
    @abstractmethod
    def invoke(self, request: ListCustomersRequest) -> ListCustomersResponse:
        raise NotImplementedError


class ListRatingsWf(ABC):
    @abstractmethod
    def invoke(self, request: ListRatingsRequest) -> ListRatingsResponse:
        raise NotImplementedError


class QuoteOfferWf(ABC):
    @abstractmethod
    def invoke(self, request: PriceOfferRequest) -> PriceOfferResponse:
        raise NotImplementedError
