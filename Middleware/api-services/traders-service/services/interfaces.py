from abc import ABC, abstractmethod


class TradersService(ABC):
    @abstractmethod
    def statuses(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def status(self, dataset_key: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def populate_books(self, authorization: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def populate_traders(self, authorization: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def populate_mappings(self, authorization: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def books(self, page: int, page_size: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def traders(self, page: int, page_size: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def mappings(self, page: int, page_size: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def trader(self, trader_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def customers_for(self, trader_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def books_for(self, trader_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_book(self, authorization: str, row: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_trader(self, authorization: str, row: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_mapping(self, authorization: str, row: dict) -> dict:
        raise NotImplementedError
