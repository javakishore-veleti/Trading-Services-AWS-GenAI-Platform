from abc import ABC, abstractmethod


class CustomerService(ABC):
    @abstractmethod
    def statuses(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def status(self, dataset_key: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def populate_customers(self, authorization: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def populate_orders(self, authorization: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def customers(self, page: int, page_size: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def customer(self, customer_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def orders_for(self, customer_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def orders(self, page: int, page_size: int) -> dict:
        raise NotImplementedError

    @abstractmethod
    def many(self, customer_ids: list[str]) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_customer(self, authorization: str, row: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_order(self, authorization: str, row: dict) -> dict:
        raise NotImplementedError
