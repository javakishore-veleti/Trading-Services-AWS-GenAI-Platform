from abc import ABC, abstractmethod


class McpToolDao(ABC):
    @abstractmethod
    async def call_tool(self, server: str, tool: str, arguments: dict) -> dict:
        raise NotImplementedError


class SkillDao(ABC):
    @abstractmethod
    def load(self, name: str) -> str | None:
        raise NotImplementedError


class ContextDao(ABC):
    @abstractmethod
    async def save(self, key: str, payload: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def load(self, key: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: str) -> None:
        raise NotImplementedError
