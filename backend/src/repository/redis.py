from decimal import Decimal

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from src.config.manager import settings


class RedisClient:
    def __init__(self):
        self.pool = ConnectionPool(
            host=settings.REDIS_HOST,
            port=settings.REDIS_PORT,
            db=settings.REDIS_DB,
            max_connections=settings.REDIS_POOL_SIZE,
            socket_timeout=settings.REDIS_POOL_TIMEOUT,
            decode_responses=True
        )
        self.client = redis.Redis(connection_pool=self.pool)

    @classmethod
    def convert_decimals(cls, obj):
        if isinstance(obj, list):
            return [cls.convert_decimals(i) for i in obj]
        elif isinstance(obj, dict):
            return {k: cls.convert_decimals(v) for k, v in obj.items()}
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj

    async def get(self, key: str) -> str | None:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: int | None = None) -> bool:
        return await self.client.set(key, value, ex=expire)

    async def delete(self, key: str) -> int:
        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        return bool(await self.client.exists(key))

    async def expire(self, key: str, seconds: int) -> bool:
        return bool(await self.client.expire(key, seconds))

    async def ttl(self, key: str) -> int:
        return await self.client.ttl(key)

    async def close(self) -> None:
        await self.client.aclose()

# For tests, bcz it breaks down by creating separate instance
redis_client = RedisClient()