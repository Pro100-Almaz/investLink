import datetime
import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from src.api.routes.market import router
from src.models.db.market import MarketData
from src.repository.redis import RedisClient


@pytest.fixture
def mock_redis_client():
    client = AsyncMock(spec=RedisClient)
    client.get = AsyncMock(return_value=None)
    client.set = AsyncMock()
    client.convert_decimals = MagicMock(return_value=[{
        "ticker": "AAPL",
        "timestamp": "2024-03-20T10:00:00",
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 148.0,
        "close_price": 153.0,
        "volume": 1000000
    }])
    return client


@pytest.fixture
def mock_session():
    session = AsyncMock()
    return session


@pytest.fixture
def test_client(mock_session, mock_redis_client):
    from fastapi import FastAPI
    from src.api.dependencies.session import get_async_session, get_redis_client

    app = FastAPI()
    app.include_router(router)

    async def override_get_session():
        return mock_session

    async def override_get_redis():
        return mock_redis_client

    app.dependency_overrides[get_async_session] = override_get_session
    app.dependency_overrides[get_redis_client] = override_get_redis

    return TestClient(app)


def test_get_market_data(test_client, mock_session, mock_redis_client):
    ticker = "AAPL"
    mock_data = [
        MarketData(
            ticker=ticker,
            timestamp=datetime.datetime.now(),
            open_price=150.0,
            high_price=155.0,
            low_price=148.0,
            close_price=153.0,
            volume=1000000
        )
    ]
    mock_session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=mock_data)))))

    response = test_client.get(f"/market/{ticker}")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["ticker"] == ticker


def test_get_market_data_not_found(test_client, mock_session):
    ticker = "INVALID"
    mock_session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))

    response = test_client.get(f"/market/{ticker}")

    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert f"No market data available for {ticker}" in data["detail"]


def test_get_daily_market_data(test_client, mock_session, mock_redis_client):
    ticker = "AAPL"
    mock_data = [{
        "bucket": datetime.datetime.now(),
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 148.0,
        "close_price": 153.0,
        "volume": 1000000
    }]
    mock_result = MagicMock()
    mock_result.mappings.return_value.all.return_value = mock_data

    mock_session.execute = AsyncMock(return_value=mock_result)

    response = test_client.get(f"/market/{ticker}/daily")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["ticker"] == ticker


def test_get_hourly_market_data(test_client, mock_session, mock_redis_client):
    ticker = "AAPL"
    mock_data = [{
        "bucket": datetime.datetime.now(),
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 148.0,
        "close_price": 153.0,
        "volume": 1000000
    }]
    mock_session.execute = AsyncMock(return_value=MagicMock(fetchall=MagicMock(return_value=[MagicMock(_mapping=data) for data in mock_data])))

    response = test_client.get(f"/market/{ticker}/hourly")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert len(data["data"]) == 1
    assert data["data"][0]["ticker"] == ticker


def test_get_all_market_data(test_client, mock_session, mock_redis_client):
    mock_data = {
        "ticker": "AAPL",
        "timestamp": datetime.datetime.now(),
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 148.0,
        "close_price": 153.0,
        "volume": 1000000
    }
    mock_session.execute = AsyncMock(return_value=MagicMock(first=MagicMock(return_value=MagicMock(_mapping=mock_data))))

    response = test_client.get("/market")

    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert "AAPL" in data["data"] 