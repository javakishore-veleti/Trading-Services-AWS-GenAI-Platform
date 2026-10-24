from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import ListCountriesRequest, RegionResolutionDto


class MasterDataBiz(ABC):
    @abstractmethod
    def resolve_region(self, request: ListCountriesRequest) -> RegionResolutionDto:
        raise NotImplementedError
