from abc import ABC, abstractmethod


class OrdersService(ABC):
    @abstractmethod
    def confirm(self, authorization: str, body: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def list_for(self, authorization: str) -> dict:
        raise NotImplementedError
