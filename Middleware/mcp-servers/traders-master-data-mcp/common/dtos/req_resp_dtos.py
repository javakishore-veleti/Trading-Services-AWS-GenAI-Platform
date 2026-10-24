from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str


class CountryDto(BaseModel):
    code: str
    name: str
    region: str
    compass: str


class DeskDto(BaseModel):
    desk_id: str
    name: str


class InstallationDto(BaseModel):
    desk_id: str
    country_code: str
    channels: list[str]


class BookDto(BaseModel):
    book_id: str
    name: str
    desk_id: str
    base_currency: str


class BookDefaultDto(BaseModel):
    book_id: str
    default_channel: str
    default_tenor: str
    default_notional: int
    default_pair: str


class BookChannelDto(BaseModel):
    book_id: str
    channels: list[str]


class TraderDto(BaseModel):
    trader_id: str
    name: str
    desk_id: str
    book_id: str
    location: str


class EmptyRequest(BaseModel):
    pass


class ListCountriesRequest(BaseModel):
    region: str | None = None


class ListInstallationsRequest(BaseModel):
    desk_id: str | None = None
    country_code: str | None = None


class ListTradersRequest(BaseModel):
    desk_id: str | None = None


class ChannelsResponse(BaseModel):
    channels: list[str]
    error: ErrorDto | None = None


class CountriesResponse(BaseModel):
    countries: list[CountryDto]
    error: ErrorDto | None = None


class DesksResponse(BaseModel):
    desks: list[DeskDto]
    error: ErrorDto | None = None


class InstallationsResponse(BaseModel):
    installations: list[InstallationDto]
    error: ErrorDto | None = None


class BooksResponse(BaseModel):
    books: list[BookDto]
    error: ErrorDto | None = None


class BookDefaultsResponse(BaseModel):
    defaults: list[BookDefaultDto]
    error: ErrorDto | None = None


class BookChannelsResponse(BaseModel):
    book_channels: list[BookChannelDto]
    error: ErrorDto | None = None


class TradersResponse(BaseModel):
    traders: list[TraderDto]
    error: ErrorDto | None = None


class ChannelRowsDto(BaseModel):
    channels: list[str]


class CountryRowsDto(BaseModel):
    countries: list[CountryDto]


class DeskRowsDto(BaseModel):
    desks: list[DeskDto]


class InstallationRowsDto(BaseModel):
    installations: list[InstallationDto]


class BookRowsDto(BaseModel):
    books: list[BookDto]


class BookDefaultRowsDto(BaseModel):
    defaults: list[BookDefaultDto]


class BookChannelRowsDto(BaseModel):
    book_channels: list[BookChannelDto]


class TraderRowsDto(BaseModel):
    traders: list[TraderDto]


class RegionResolutionDto(BaseModel):
    request: ListCountriesRequest
    error: ErrorDto | None = None


class ChannelsContext(BaseModel):
    request: EmptyRequest
    response: ChannelsResponse | None = None
    error: ErrorDto | None = None


class CountriesContext(BaseModel):
    request: ListCountriesRequest
    response: CountriesResponse | None = None
    error: ErrorDto | None = None


class DesksContext(BaseModel):
    request: EmptyRequest
    response: DesksResponse | None = None
    error: ErrorDto | None = None


class InstallationsContext(BaseModel):
    request: ListInstallationsRequest
    response: InstallationsResponse | None = None
    error: ErrorDto | None = None


class BooksContext(BaseModel):
    request: EmptyRequest
    response: BooksResponse | None = None
    error: ErrorDto | None = None


class BookDefaultsContext(BaseModel):
    request: EmptyRequest
    response: BookDefaultsResponse | None = None
    error: ErrorDto | None = None


class BookChannelsContext(BaseModel):
    request: EmptyRequest
    response: BookChannelsResponse | None = None
    error: ErrorDto | None = None


class TradersContext(BaseModel):
    request: ListTradersRequest
    response: TradersResponse | None = None
    error: ErrorDto | None = None
