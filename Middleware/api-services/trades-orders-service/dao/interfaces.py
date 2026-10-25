from abc import ABC, abstractmethod


class OrdersDao(ABC):
    @abstractmethod
    def add(self, order: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def for_trader(self, trader_id: str) -> list[dict]:
        raise NotImplementedError
