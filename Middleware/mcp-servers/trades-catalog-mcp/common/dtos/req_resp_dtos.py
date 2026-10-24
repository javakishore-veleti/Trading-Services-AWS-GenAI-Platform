from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str


class ProductDto(BaseModel):
    product_id: str
    name: str
    product_type: str
    pair: str
    base: str
    quote: str
    tenor: str
    settlement: str
    min_notional_usd: int
    max_notional_usd: int
    customer_segments: list[str]


class ListProductsRequest(BaseModel):
    product_type: str | None = None
    segment: str | None = None


class ListProductsResponse(BaseModel):
    products: list[ProductDto]
    error: ErrorDto | None = None


class GetProductRequest(BaseModel):
    product_id: str


class GetProductResponse(BaseModel):
    product: ProductDto | None = None
    error: ErrorDto | None = None


class ProductRowsDto(BaseModel):
    products: list[ProductDto]


class ProductRowDto(BaseModel):
    product: ProductDto | None = None


class ValidationDto(BaseModel):
    error: ErrorDto | None = None


class ListProductsContext(BaseModel):
    request: ListProductsRequest
    response: ListProductsResponse | None = None
    error: ErrorDto | None = None


class GetProductContext(BaseModel):
    request: GetProductRequest
    response: GetProductResponse | None = None
    error: ErrorDto | None = None
