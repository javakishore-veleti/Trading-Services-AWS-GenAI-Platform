from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import (
    CustomerRowsDto,
    ListCustomersRequest,
    ListRatingsRequest,
    PriceOfferRequest,
    QuoteLookupDto,
    RatingRowsDto,
)


class OfferDao(ABC):
    @abstractmethod
    def find_customers(self, request: ListCustomersRequest) -> CustomerRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_ratings(self, request: ListRatingsRequest) -> RatingRowsDto:
        raise NotImplementedError

    @abstractmethod
    def lookup_quote(self, request: PriceOfferRequest) -> QuoteLookupDto:
        raise NotImplementedError
