import pydantic
from sqlalchemy.ext.asyncio import (
    async_sessionmaker as sqlalchemy_async_sessionmaker,
    AsyncEngine as SQLAlchemyAsyncEngine,
    AsyncSession as SQLAlchemyAsyncSession,
    create_async_engine as create_sqlalchemy_async_engine,
)
from sqlalchemy.pool import Pool as SQLAlchemyPool, QueuePool as SQLAlchemyQueuePool

from src.config.manager import settings


class AsyncDatabase:
    def __init__(self):
        self.postgres_uri: pydantic.PostgresDsn = pydantic.PostgresDsn(
            url=settings.POSTGRES_URI
        )
        self.async_engine: SQLAlchemyAsyncEngine = create_sqlalchemy_async_engine(
            url=self.set_async_db_uri,
            echo=settings.IS_DB_ECHO_LOG,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_POOL_OVERFLOW,
            poolclass=SQLAlchemyQueuePool,
            connect_args={"server_settings": {"application_name": "investlink_timescale"}}
        )
        self.async_session: SQLAlchemyAsyncSession = SQLAlchemyAsyncSession(bind=self.async_engine)
        self.pool: SQLAlchemyPool = self.async_engine.pool

    @property
    def set_async_db_uri(self) -> str:
        uri = str(self.postgres_uri)
        return uri.replace("postgresql://", "postgresql+asyncpg://")


async_db: AsyncDatabase = AsyncDatabase()
