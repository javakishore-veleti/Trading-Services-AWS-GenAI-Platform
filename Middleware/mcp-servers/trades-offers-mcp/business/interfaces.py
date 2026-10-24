from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import PriceOfferRequest, PriceOfferResponse, QuoteFactsDto, ValidationDto


class OfferBiz(ABC):
    @abstractmethod
    def validate(self, request: PriceOfferRequest) -> ValidationDto:
        raise NotImplementedError

    @abstractmethod
    def price(self, facts: QuoteFactsDto) -> PriceOfferResponse:
        raise NotImplementedError
