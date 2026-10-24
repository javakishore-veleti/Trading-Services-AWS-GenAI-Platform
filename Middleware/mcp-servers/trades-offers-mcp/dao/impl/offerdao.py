from common.dtos.req_resp_dtos import (
    CustomerDto,
    CustomerRowsDto,
    ListCustomersRequest,
    ListRatingsRequest,
    PriceOfferRequest,
    QuoteLookupDto,
    RatingDto,
    RatingRowsDto,
)
from dao.interfaces import OfferDao


class OfferDaoImpl(OfferDao):
    _customers: list[CustomerDto] = [
        CustomerDto(customer_id="CUS-1001", name="Atlas Manufacturing", rating="AAA", home="US-East", segment="corporate"),
        CustomerDto(customer_id="CUS-1002", name="Nordic Timber", rating="AA", home="Norway", segment="corporate"),
        CustomerDto(customer_id="CUS-1003", name="Sakura Electronics", rating="A", home="Japan", segment="corporate"),
        CustomerDto(customer_id="CUS-1004", name="Iberia Foods", rating="BBB", home="Spain", segment="corporate"),
        CustomerDto(customer_id="CUS-1005", name="Gulf Logistics", rating="BB", home="United Arab Emirates", segment="corporate"),
        CustomerDto(customer_id="CUS-1006", name="Rhine Autos", rating="AA", home="France", segment="institutional"),
        CustomerDto(customer_id="CUS-1007", name="Pacific Retail", rating="A", home="Singapore", segment="corporate"),
        CustomerDto(customer_id="CUS-1008", name="Andes Mining", rating="BBB", home="US-West", segment="institutional"),
    ]
    _ratings: list[RatingDto] = [
        RatingDto(rating="AAA", discount_bps=8.0, description="Top-tier corporate or institutional, tightest all-in"),
        RatingDto(rating="AA", discount_bps=6.0, description="Strong credit, established flow"),
        RatingDto(rating="A", discount_bps=4.0, description="Standard corporate"),
        RatingDto(rating="BBB", discount_bps=2.5, description="Higher spread, still investment grade"),
        RatingDto(rating="BB", discount_bps=1.0, description="Non-investment grade, smallest discount"),
    ]
    _mids: dict[str, float] = {
        "EUR/USD": 1.0860,
        "GBP/USD": 1.2710,
        "USD/JPY": 151.20,
        "USD/CHF": 0.8820,
        "AUD/USD": 0.6540,
        "USD/CAD": 1.3620,
        "NZD/USD": 0.5980,
        "EUR/GBP": 0.8545,
        "EUR/JPY": 164.20,
        "USD/SGD": 1.3420,
        "USD/INR": 83.40,
        "USD/KRW": 1365.0,
    }
    _spreads: dict[str, float] = {
        "spot": 10.0,
        "forward": 14.0,
        "swap": 12.0,
        "ndf": 18.0,
        "vanilla-option": 22.0,
        "barrier-option": 26.0,
    }

    def find_customers(self, request: ListCustomersRequest) -> CustomerRowsDto:
        return CustomerRowsDto(customers=list(OfferDaoImpl._customers))

    def find_ratings(self, request: ListRatingsRequest) -> RatingRowsDto:
        return RatingRowsDto(ratings=list(OfferDaoImpl._ratings))

    def lookup_quote(self, request: PriceOfferRequest) -> QuoteLookupDto:
        customer = next((row for row in OfferDaoImpl._customers if row.customer_id == request.customer_id), None)
        rating = None
        if customer is not None:
            rating = next((row for row in OfferDaoImpl._ratings if row.rating == customer.rating), None)
        return QuoteLookupDto(
            customer=customer,
            rating=rating,
            mid=OfferDaoImpl._mids.get(request.pair),
            spread_bps=OfferDaoImpl._spreads.get(request.product_type),
        )
