import datetime
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.db.market import MarketData
from src.repository.redis import RedisClient


@pytest.mark.asyncio
async def test_market_data_flow(test_client: TestClient, async_session: AsyncSession, redis_client: RedisClient):
    market_data = MarketData(
        ticker="AAPL",
        timestamp=datetime.datetime.now(),
        open_price=150.0,
        high_price=155.0,
        low_price=148.0,
        close_price=153.0,
        volume=1000000
    )
    async_session.add(market_data)
    await async_session.commit()

    response = test_client.get("/market/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["ticker"] == "AAPL"

    response = test_client.get("/market/AAPL/daily")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["ticker"] == "AAPL"

    response = test_client.get("/market/AAPL/hourly")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    assert data["data"][0]["ticker"] == "AAPL"

    response = test_client.get("/market/AAPL")
    assert response.status_code == 200

    cached_data = await redis_client.get("market_data:AAPL")
    assert cached_data is not None

    response = test_client.get("/market")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "AAPL" in data["data"]


@pytest.mark.asyncio
async def test_market_data_time_range(test_client: TestClient, async_session: AsyncSession):
    now = datetime.datetime.now()
    yesterday = now - datetime.timedelta(days=1)
    last_week = now - datetime.timedelta(days=7)

    market_data = [
        MarketData(
            ticker="AAPL",
            timestamp=now,
            open_price=150.0,
            high_price=155.0,
            low_price=148.0,
            close_price=153.0,
            volume=1000000
        ),
        MarketData(
            ticker="AAPL",
            timestamp=yesterday,
            open_price=145.0,
            high_price=149.0,
            low_price=144.0,
            close_price=148.0,
            volume=900000
        ),
        MarketData(
            ticker="AAPL",
            timestamp=last_week,
            open_price=140.0,
            high_price=144.0,
            low_price=139.0,
            close_price=143.0,
            volume=800000
        )
    ]
    async_session.add_all(market_data)
    await async_session.commit()

    response = test_client.get(
        f"/market/AAPL?start_time={yesterday.isoformat()}&end_time={now.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 2


@pytest.mark.asyncio
async def test_market_data_aggregates(test_client: TestClient, async_session: AsyncSession):
    now = datetime.datetime.now()
    market_data = [
        MarketData(
            ticker="AAPL",
            timestamp=now - datetime.timedelta(hours=i),
            open_price=150.0 + i,
            high_price=155.0 + i,
            low_price=148.0 + i,
            close_price=153.0 + i,
            volume=1000000 + i * 1000
        )
        for i in range(24)
    ]
    async_session.add_all(market_data)
    await async_session.commit()

    response = test_client.get("/market/AAPL/daily")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    daily_data = data["data"][0]
    assert "open_price" in daily_data
    assert "high_price" in daily_data
    assert "low_price" in daily_data
    assert "close_price" in daily_data
    assert "volume" in daily_data

    response = test_client.get("/market/AAPL/hourly")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) > 0
    hourly_data = data["data"][0]
    assert "open_price" in hourly_data
    assert "high_price" in hourly_data
    assert "low_price" in hourly_data
    assert "close_price" in hourly_data
    assert "volume" in hourly_data 