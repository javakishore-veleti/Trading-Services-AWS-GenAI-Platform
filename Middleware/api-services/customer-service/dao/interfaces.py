from abc import ABC, abstractmethod


class CustomerDao(ABC):
    @abstractmethod
    def statuses(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def status(self, dataset_key: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def load_customers(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def customers(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def customer(self, customer_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def load_orders(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def orders_for(self, customer_id: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def orders(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def add_customer(self, row: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def add_order(self, order: dict) -> dict:
        raise NotImplementedError
