from abc import ABC, abstractmethod

from common.dtos import InvokeRequest, InvokeResponse


class DeskAgentWf(ABC):
    @abstractmethod
    async def invoke(self, request: InvokeRequest) -> InvokeResponse:
        raise NotImplementedError

    @abstractmethod
    async def retrieve(self, context_id: str, sub_agent: str) -> dict | None:
        raise NotImplementedError
