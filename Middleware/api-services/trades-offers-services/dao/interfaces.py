from abc import ABC, abstractmethod


class OffersDao(ABC):
    @abstractmethod
    def quote(self, base: str, term: str, direction: str) -> dict | None:
        raise NotImplementedError
