from abc import ABC, abstractmethod


class OffersService(ABC):
    @abstractmethod
    def quote(self, base: str, term: str, direction: str) -> dict:
        raise NotImplementedError
