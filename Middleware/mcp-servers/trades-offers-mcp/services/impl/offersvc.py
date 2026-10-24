from common.dtos.req_resp_dtos import (
    ErrorDto,
    ListCustomersRequest,
    ListCustomersResponse,
    ListRatingsRequest,
    ListRatingsResponse,
    PriceOfferRequest,
    QuoteFactsDto,
)
from dao.object_factory import DaoObjectFactory
from services.interfaces import OfferSvc


class OfferSvcImpl(OfferSvc):
    def list_customers(self, request: ListCustomersRequest) -> ListCustomersResponse:
        rows = DaoObjectFactory.offer_dao().find_customers(request)
        return ListCustomersResponse(customers=rows.customers)

    def list_ratings(self, request: ListRatingsRequest) -> ListRatingsResponse:
        rows = DaoObjectFactory.offer_dao().find_ratings(request)
        return ListRatingsResponse(ratings=rows.ratings)

    def load_quote(self, request: PriceOfferRequest) -> QuoteFactsDto:
        found = DaoObjectFactory.offer_dao().lookup_quote(request)
        if found.customer is None:
            return QuoteFactsDto(request=request, error=ErrorDto(code="not_found", message=f"Unknown customer {request.customer_id}"))
        if found.mid is None:
            return QuoteFactsDto(request=request, error=ErrorDto(code="not_found", message=f"No mid rate for {request.pair}"))
        if found.spread_bps is None:
            return QuoteFactsDto(request=request, error=ErrorDto(code="invalid", message=f"Unknown product type {request.product_type}"))
        if found.rating is None:
            return QuoteFactsDto(request=request, error=ErrorDto(code="not_found", message=f"No rating {found.customer.rating}"))
        return QuoteFactsDto(request=request, customer=found.customer, rating=found.rating, mid=found.mid, spread_bps=found.spread_bps)
