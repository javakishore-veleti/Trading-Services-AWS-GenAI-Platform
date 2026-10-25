from abc import ABC, abstractmethod
from collections import defaultdict


class TurnCache(ABC):
    @abstractmethod
    def add(self, trader_id: str, customer_id: str, turn: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    def page(self, trader_id: str, customer_id: str, page: int, page_size: int) -> dict:
        raise NotImplementedError


class MemoryTurnCache(TurnCache):
    """Newest turn first, one list per trader and customer."""

    def __init__(self) -> None:
        self._turns: dict[tuple[str, str], list[dict]] = defaultdict(list)

    def add(self, trader_id: str, customer_id: str, turn: dict) -> None:
        self._turns[(trader_id, customer_id)].insert(0, turn)

    def page(self, trader_id: str, customer_id: str, page: int, page_size: int) -> dict:
        rows = self._turns[(trader_id, customer_id)]
        safe_page = max(page, 1)
        safe_size = min(max(page_size, 1), 20)
        start = (safe_page - 1) * safe_size
        return {
            "page": safe_page,
            "page_size": safe_size,
            "total": len(rows),
            "turns": rows[start:start + safe_size],
        }


class CacheFactory:
    _cache: TurnCache | None = None

    @classmethod
    def cache(cls) -> TurnCache:
        if cls._cache is None:
            cls._cache = MemoryTurnCache()
        return cls._cache
