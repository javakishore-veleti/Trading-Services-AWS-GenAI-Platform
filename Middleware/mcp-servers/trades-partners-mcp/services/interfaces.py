from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import GetPartnerRequest, GetPartnerResponse, ListPartnersRequest, ListPartnersResponse


class PartnerSvc(ABC):
    @abstractmethod
    def list_partners(self, request: ListPartnersRequest) -> ListPartnersResponse:
        raise NotImplementedError

    @abstractmethod
    def get_partner(self, request: GetPartnerRequest) -> GetPartnerResponse:
        raise NotImplementedError
