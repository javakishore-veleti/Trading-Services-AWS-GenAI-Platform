from abc import ABC, abstractmethod


class CatalogDao(ABC):
    @abstractmethod
    def products(self) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def product(self, product_id: str) -> dict | None:
        raise NotImplementedError

    @abstractmethod
    def eligibility(self, customer_id: str) -> list[dict]:
        raise NotImplementedError

    @abstractmethod
    def references(self) -> list[dict]:
        raise NotImplementedError
