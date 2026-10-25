from abc import ABC, abstractmethod


class TradersDao(ABC):
    @abstractmethod
    def statuses(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def status(self, dataset_key: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def load_books(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def books(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def load_traders(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def traders(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def trader(self, trader_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def load_mappings(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def mappings(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def books_for(self, trader_id: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def add_book(self, row: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_trader(self, row: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_mapping(self, row: dict) -> dict:
        raise NotImplementedError
