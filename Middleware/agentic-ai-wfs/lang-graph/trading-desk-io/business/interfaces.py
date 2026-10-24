from abc import ABC, abstractmethod


class DeskAgentBiz(ABC):
    @abstractmethod
    def sub_agent(self, tool: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def reject(self, tool: str) -> str | None:
        raise NotImplementedError

    @abstractmethod
    def select(self, tool: str, payload: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def compress(self, sub_agent: str, payload: dict) -> tuple[str, dict]:
        raise NotImplementedError

    @abstractmethod
    def server_for(self, tool: str) -> str | None:
        raise NotImplementedError
