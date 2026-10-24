from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import AnalyticRowsDto, GrainRowsDto, ListGrainsRequest, ReadAnalyticsRequest


class AnalyticsDao(ABC):
    @abstractmethod
    def find_grains(self, request: ListGrainsRequest) -> GrainRowsDto:
        raise NotImplementedError

    @abstractmethod
    def find_rows(self, request: ReadAnalyticsRequest) -> AnalyticRowsDto:
        raise NotImplementedError
