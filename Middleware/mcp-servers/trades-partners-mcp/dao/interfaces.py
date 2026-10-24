from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import GetPartnerRequest, ListPartnersRequest, PartnerRowDto, PartnerRowsDto


class PartnerDao(ABC):
    @abstractmethod
    def find_partners(self, request: ListPartnersRequest) -> PartnerRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_partner(self, request: GetPartnerRequest) -> PartnerRowDto:
        raise NotImplementedError
