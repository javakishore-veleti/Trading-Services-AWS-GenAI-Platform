from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import (
    ListCustomersRequest,
    ListCustomersResponse,
    ListRatingsRequest,
    ListRatingsResponse,
    PriceOfferRequest,
    QuoteFactsDto,
)


class OfferSvc(ABC):
    @abstractmethod
    def list_customers(self, request: ListCustomersRequest) -> ListCustomersResponse:
        raise NotImplementedError

    @abstractmethod
    def list_ratings(self, request: ListRatingsRequest) -> ListRatingsResponse:
        raise NotImplementedError

    @abstractmethod
    def load_quote(self, request: PriceOfferRequest) -> QuoteFactsDto:
        raise NotImplementedError
