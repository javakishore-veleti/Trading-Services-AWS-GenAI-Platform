from abc import ABC, abstractmethod

from common.dtos import InvokeRequest, StoredSlice


class AgentSvc(ABC):
    @abstractmethod
    async def externalize(self, agent: str, request: InvokeRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    async def isolate(self, agent: str, context_id: str, sub_agent: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def load_skill(self, agent: str, context_id: str, sub_agent: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def select_and_call(self, agent: str, context_id: str, sub_agent: str, tool: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def compress(self, agent: str, context_id: str, sub_agent: str, tool: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    async def read_parent(self, agent: str, context_id: str) -> StoredSlice | None:
        raise NotImplementedError

    @abstractmethod
    async def retrieve(self, agent: str, context_id: str, sub_agent: str) -> dict | None:
        raise NotImplementedError
