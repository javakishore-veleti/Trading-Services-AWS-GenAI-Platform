from common.dtos.req_resp_dtos import ErrorDto, GetPartnerRequest, GetPartnerResponse, ListPartnersRequest, ListPartnersResponse
from dao.object_factory import DaoObjectFactory
from services.interfaces import PartnerSvc


class PartnerSvcImpl(PartnerSvc):
    def list_partners(self, request: ListPartnersRequest) -> ListPartnersResponse:
        rows = DaoObjectFactory.partner_dao().find_partners(request)
        return ListPartnersResponse(partners=rows.partners)

    def get_partner(self, request: GetPartnerRequest) -> GetPartnerResponse:
        row = DaoObjectFactory.partner_dao().find_partner(request)
        if row.partner is None:
            return GetPartnerResponse(error=ErrorDto(code="not_found", message=f"Unknown partner {request.partner_id}"))
        return GetPartnerResponse(partner=row.partner)
