import json
import os

from redis.asyncio import Redis

from dao.interfaces import ContextDao


class RedisContextDao(ContextDao):
    """The only class that reads or writes agent context. The body lives in Redis, not in the graph."""

    def __init__(self) -> None:
        self._redis = Redis(
            host="127.0.0.1",
            port=int(os.environ.get("REDIS_PORT", "6379")),
            password=os.environ.get("REDIS_PASSWORD", "redis"),
            decode_responses=True,
        )

    async def save(self, key: str, payload: dict) -> None:
        await self._redis.set(key, json.dumps(payload))

    async def load(self, key: str) -> dict | None:
        raw = await self._redis.get(key)
        if raw is None:
            return None
        loaded = json.loads(raw)
        if isinstance(loaded, dict):
            return loaded
        return None

    async def delete(self, key: str) -> None:
        await self._redis.delete(key)
