from business.interfaces import PartnerBiz
from common.dtos.req_resp_dtos import ErrorDto, GetPartnerRequest, ValidationDto


class PartnerBizImpl(PartnerBiz):
    def validate_get(self, request: GetPartnerRequest) -> ValidationDto:
        if not request.partner_id.strip():
            return ValidationDto(error=ErrorDto(code="invalid", message="partner_id is required"))
        return ValidationDto()
