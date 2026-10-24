from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str


class OrderDto(BaseModel):
    order_id: str
    customer_id: str
    product_id: str
    pair: str
    side: str
    notional: float
    all_in_rate: float
    channel: str
    desk_location: str
    status: str


class ListOrdersRequest(BaseModel):
    customer_id: str | None = None
    status: str | None = None


class ListOrdersResponse(BaseModel):
    orders: list[OrderDto]
    error: ErrorDto | None = None


class GetOrderRequest(BaseModel):
    order_id: str


class GetOrderResponse(BaseModel):
    order: OrderDto | None = None
    error: ErrorDto | None = None


class CreateOrderRequest(BaseModel):
    customer_id: str
    product_id: str
    pair: str
    side: str
    notional: float
    all_in_rate: float
    channel: str
    desk_location: str


class CreateOrderResponse(BaseModel):
    order: OrderDto | None = None
    error: ErrorDto | None = None


class OrderRowsDto(BaseModel):
    orders: list[OrderDto]


class OrderRowDto(BaseModel):
    order: OrderDto | None = None


class ValidationDto(BaseModel):
    error: ErrorDto | None = None


class ListOrdersContext(BaseModel):
    request: ListOrdersRequest
    response: ListOrdersResponse | None = None
    error: ErrorDto | None = None


class GetOrderContext(BaseModel):
    request: GetOrderRequest
    response: GetOrderResponse | None = None
    error: ErrorDto | None = None


class CreateOrderContext(BaseModel):
    request: CreateOrderRequest
    response: CreateOrderResponse | None = None
    error: ErrorDto | None = None
