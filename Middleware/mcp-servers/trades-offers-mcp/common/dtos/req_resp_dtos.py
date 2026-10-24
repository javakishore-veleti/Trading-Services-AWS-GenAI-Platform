from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str


class CustomerDto(BaseModel):
    customer_id: str
    name: str
    rating: str
    home: str
    segment: str


class RatingDto(BaseModel):
    rating: str
    discount_bps: float
    description: str


class ListCustomersRequest(BaseModel):
    pass


class ListCustomersResponse(BaseModel):
    customers: list[CustomerDto]
    error: ErrorDto | None = None


class ListRatingsRequest(BaseModel):
    pass


class ListRatingsResponse(BaseModel):
    ratings: list[RatingDto]
    error: ErrorDto | None = None


class PriceOfferRequest(BaseModel):
    customer_id: str
    pair: str
    product_type: str
    notional: float
    side: str


class PriceOfferResponse(BaseModel):
    customer_id: str | None = None
    customer_name: str | None = None
    rating: str | None = None
    pair: str | None = None
    product_type: str | None = None
    side: str | None = None
    notional: float | None = None
    mid: float | None = None
    spread_bps: float | None = None
    discount_bps: float | None = None
    net_spread_bps: float | None = None
    all_in_rate: float | None = None
    total_quote_amount: float | None = None
    error: ErrorDto | None = None


class CustomerRowsDto(BaseModel):
    customers: list[CustomerDto]


class RatingRowsDto(BaseModel):
    ratings: list[RatingDto]


class QuoteLookupDto(BaseModel):
    customer: CustomerDto | None = None
    rating: RatingDto | None = None
    mid: float | None = None
    spread_bps: float | None = None


class QuoteFactsDto(BaseModel):
    request: PriceOfferRequest
    customer: CustomerDto | None = None
    rating: RatingDto | None = None
    mid: float | None = None
    spread_bps: float | None = None
    error: ErrorDto | None = None


class ValidationDto(BaseModel):
    error: ErrorDto | None = None


class ListCustomersContext(BaseModel):
    request: ListCustomersRequest
    response: ListCustomersResponse | None = None
    error: ErrorDto | None = None


class ListRatingsContext(BaseModel):
    request: ListRatingsRequest
    response: ListRatingsResponse | None = None
    error: ErrorDto | None = None


class QuoteContext(BaseModel):
    request: PriceOfferRequest
    facts: QuoteFactsDto | None = None
    response: PriceOfferResponse | None = None
    error: ErrorDto | None = None
