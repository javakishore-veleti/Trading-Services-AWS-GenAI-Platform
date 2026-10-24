from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import GetPartnerRequest, ValidationDto


class PartnerBiz(ABC):
    @abstractmethod
    def validate_get(self, request: GetPartnerRequest) -> ValidationDto:
        raise NotImplementedError
