from abc import ABC, abstractmethod

from common.dtos.req_resp_dtos import ReadAnalyticsRequest, ValidationDto


class AnalyticsBiz(ABC):
    @abstractmethod
    def validate_read(self, request: ReadAnalyticsRequest) -> ValidationDto:
        raise NotImplementedError
