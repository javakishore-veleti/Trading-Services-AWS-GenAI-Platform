from pydantic import BaseModel


class ErrorDto(BaseModel):
    code: str
    message: str


class PartnerDto(BaseModel):
    partner_id: str
    name: str
    bic: str
    role: str
    status: str
    home: str
    supported_pairs: list[str]
    cutoff_utc: str


class ListPartnersRequest(BaseModel):
    role: str | None = None
    pair: str | None = None


class ListPartnersResponse(BaseModel):
    partners: list[PartnerDto]
    error: ErrorDto | None = None


class GetPartnerRequest(BaseModel):
    partner_id: str


class GetPartnerResponse(BaseModel):
    partner: PartnerDto | None = None
    error: ErrorDto | None = None


class PartnerRowsDto(BaseModel):
    partners: list[PartnerDto]


class PartnerRowDto(BaseModel):
    partner: PartnerDto | None = None


class ValidationDto(BaseModel):
    error: ErrorDto | None = None


class ListPartnersContext(BaseModel):
    request: ListPartnersRequest
    response: ListPartnersResponse | None = None
    error: ErrorDto | None = None


class GetPartnerContext(BaseModel):
    request: GetPartnerRequest
    response: GetPartnerResponse | None = None
    error: ErrorDto | None = None
