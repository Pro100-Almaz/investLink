import asgi_lifespan
import fastapi
import httpx
import pytest
import asyncio
from typing import AsyncGenerator, Generator
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy import text

from src.main import initialize_backend_application
from src.api.dependencies.session import get_async_session
from src.repository.redis import RedisClient
from src.repository.table import Base
from src.main import backend_app


@pytest.fixture(name="backend_test_app")
def backend_test_app() -> fastapi.FastAPI:
    return initialize_backend_application()


@pytest.fixture(name="initialize_backend_test_application")
async def initialize_backend_test_application(backend_test_app: fastapi.FastAPI) -> fastapi.FastAPI:  # type: ignore
    async with asgi_lifespan.LifespanManager(backend_test_app):
        yield backend_test_app


@pytest.fixture(name="async_client")
async def async_client(initialize_backend_test_application: fastapi.FastAPI) -> httpx.AsyncClient:  # type: ignore
    async with httpx.AsyncClient(
        app=initialize_backend_test_application,
        base_url="http://testserver",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client


TEST_DATABASE_URL = "postgresql+asyncpg://testuser:testpass@localhost:5433/testdb"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=StaticPool,
    echo=True,
)

TestingSessionLocal = sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def drop_all_objects(conn):
    await conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
    await conn.execute(text("CREATE SCHEMA public"))
    await conn.execute(text("GRANT ALL ON SCHEMA public TO testuser"))
    await conn.execute(text("GRANT ALL ON SCHEMA public TO public"))


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with test_engine.begin() as conn:
        await drop_all_objects(conn)
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await drop_all_objects(conn)


@pytest.fixture
async def test_client(async_session: AsyncSession) -> Generator:
    async def override_get_session():
        yield async_session

    backend_app.dependency_overrides[get_async_session] = override_get_session
    with TestClient(backend_app) as client:
        yield client
    backend_app.dependency_overrides.clear()


@pytest.fixture
async def redis_client() -> AsyncGenerator[RedisClient, None]:
    client = RedisClient()
    yield client
    await client.close()
