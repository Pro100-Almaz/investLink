import typing

from fastapi import Request
from sqlalchemy.ext.asyncio import (
    async_sessionmaker as sqlalchemy_async_sessionmaker,
    AsyncSession as SQLAlchemyAsyncSession,
    AsyncSessionTransaction as SQLAlchemyAsyncSessionTransaction,
)

from src.repository.database import async_db

from src.repository.redis import RedisClient


async def get_async_session() -> typing.AsyncGenerator[SQLAlchemyAsyncSession, None]:
    async_session = async_db.async_session
    try:
        yield async_session
    except Exception as e:
        await async_session.rollback()
        raise e
    finally:
        await async_session.close()


def get_redis_client(request: Request) -> RedisClient:
    return request.app.state.redis
