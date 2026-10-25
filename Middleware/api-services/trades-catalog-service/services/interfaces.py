from abc import ABC, abstractmethod


class CatalogService(ABC):
    @abstractmethod
    def products(self) -> dict:
        raise NotImplementedError

    @abstractmethod
    def product(self, product_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def eligibility(self, customer_id: str) -> dict:
        raise NotImplementedError

    @abstractmethod
    def references(self) -> dict:
        raise NotImplementedError
