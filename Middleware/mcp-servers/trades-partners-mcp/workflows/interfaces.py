from abc import ABC, abstractmethod

from pydantic import BaseModel

from common.dtos.req_resp_dtos import GetPartnerRequest, GetPartnerResponse, ListPartnersRequest, ListPartnersResponse


class WfTask(ABC):
    @abstractmethod
    def execute(self, context: BaseModel) -> BaseModel:
        raise NotImplementedError


class ListPartnersWf(ABC):
    @abstractmethod
    def invoke(self, request: ListPartnersRequest) -> ListPartnersResponse:
        raise NotImplementedError


class GetPartnerWf(ABC):
    @abstractmethod
    def invoke(self, request: GetPartnerRequest) -> GetPartnerResponse:
        raise NotImplementedError
