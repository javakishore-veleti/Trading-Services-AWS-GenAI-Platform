from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str


class AnalyticDto(BaseModel):
    grain: str
    as_of: str
    book_id: str
    desk_id: str
    channel: str
    country_code: str
    trade_count: int
    volume_usd: int
    pnl_usd: int


class ListGrainsRequest(BaseModel):
    pass


class ListGrainsResponse(BaseModel):
    grains: list[str]
    error: ErrorDto | None = None


class ReadAnalyticsRequest(BaseModel):
    grain: str = "eod"
    book_id: str | None = None
    channel: str | None = None
    country_code: str | None = None


class ReadAnalyticsResponse(BaseModel):
    rows: list[AnalyticDto]
    error: ErrorDto | None = None


class GrainRowsDto(BaseModel):
    grains: list[str]


class AnalyticRowsDto(BaseModel):
    rows: list[AnalyticDto]


class ValidationDto(BaseModel):
    error: ErrorDto | None = None


class ListGrainsContext(BaseModel):
    request: ListGrainsRequest
    response: ListGrainsResponse | None = None
    error: ErrorDto | None = None


class ReadAnalyticsContext(BaseModel):
    request: ReadAnalyticsRequest
    response: ReadAnalyticsResponse | None = None
    error: ErrorDto | None = None
