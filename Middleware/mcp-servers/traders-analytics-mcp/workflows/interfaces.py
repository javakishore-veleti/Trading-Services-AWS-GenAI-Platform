from abc import ABC, abstractmethod

from pydantic import BaseModel

from common.dtos.req_resp_dtos import ListGrainsRequest, ListGrainsResponse, ReadAnalyticsRequest, ReadAnalyticsResponse


class WfTask(ABC):
    @abstractmethod
    def execute(self, context: BaseModel) -> BaseModel:
        raise NotImplementedError


class ListGrainsWf(ABC):
    @abstractmethod
    def invoke(self, request: ListGrainsRequest) -> ListGrainsResponse:
        raise NotImplementedError


class ReadAnalyticsWf(ABC):
    @abstractmethod
    def invoke(self, request: ReadAnalyticsRequest) -> ReadAnalyticsResponse:
        raise NotImplementedError
