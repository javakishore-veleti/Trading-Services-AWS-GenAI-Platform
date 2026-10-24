from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import ListGrainsRequest, ListGrainsResponse, ReadAnalyticsRequest, ReadAnalyticsResponse


class AnalyticsSvc(ABC):
    @abstractmethod
    def list_grains(self, request: ListGrainsRequest) -> ListGrainsResponse:
        raise NotImplementedError

    @abstractmethod
    def read_analytics(self, request: ReadAnalyticsRequest) -> ReadAnalyticsResponse:
        raise NotImplementedError
