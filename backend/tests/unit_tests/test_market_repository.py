import datetime
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.models.db.market import MarketData
from src.repository.crud.market import MarketDataCRUDRepository


@pytest.fixture
def mock_session():
    session = AsyncMock(spec=AsyncSession)
    return session


@pytest.fixture
def market_repo(mock_session):
    return MarketDataCRUDRepository(mock_session)


@pytest.mark.asyncio
async def test_create_market_data(market_repo, mock_session):
    market_data = MarketData(
        ticker="AAPL",
        timestamp=datetime.datetime.now(),
        open_price=150.0,
        high_price=155.0,
        low_price=148.0,
        close_price=153.0,
        volume=1000000
    )
    mock_session.add = AsyncMock()
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()

    result = await market_repo.create_market_data(market_data)

    assert result == market_data
    mock_session.add.assert_called_once_with(market_data)
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once_with(market_data)


@pytest.mark.asyncio
async def test_get_market_data(market_repo, mock_session):
    ticker = "AAPL"
    start_time = datetime.datetime.now() - datetime.timedelta(days=1)
    end_time = datetime.datetime.now()
    limit = 10

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

    result = await market_repo.get_market_data(ticker, start_time, end_time, limit)

    assert result == mock_data
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_latest_market_data(market_repo, mock_session):
    ticker = "AAPL"
    mock_data = {
        "ticker": ticker,
        "timestamp": datetime.datetime.now(),
        "open_price": 150.0,
        "high_price": 155.0,
        "low_price": 148.0,
        "close_price": 153.0,
        "volume": 1000000
    }
    mock_session.execute = AsyncMock(return_value=MagicMock(first=MagicMock(return_value=MagicMock(_mapping=mock_data))))

    result = await market_repo.get_latest_market_data(ticker)

    assert result is not None
    assert result.ticker == ticker
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_daily_aggregates(market_repo, mock_session):
    ticker = "AAPL"
    start_time = datetime.datetime.now() - datetime.timedelta(days=7)
    end_time = datetime.datetime.now()

    mock_data = [
        {
            "bucket": datetime.datetime.now(),
            "open_price": 150.0,
            "high_price": 155.0,
            "low_price": 148.0,
            "close_price": 153.0,
            "volume": 1000000
        }
    ]
    mock_session.execute = AsyncMock(return_value=MagicMock(fetchall=MagicMock(return_value=[MagicMock(_mapping=data) for data in mock_data])))

    result = await market_repo.get_daily_aggregates(ticker, start_time, end_time)

    assert len(result) == 1
    assert result[0]["open_price"] == 150.0
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_hourly_aggregates(market_repo, mock_session):
    ticker = "AAPL"
    start_time = datetime.datetime.now() - datetime.timedelta(hours=24)
    end_time = datetime.datetime.now()

    mock_data = [
        {
            "bucket": datetime.datetime.now(),
            "open_price": 150.0,
            "high_price": 155.0,
            "low_price": 148.0,
            "close_price": 153.0,
            "volume": 1000000
        }
    ]
    mock_session.execute = AsyncMock(return_value=MagicMock(fetchall=MagicMock(return_value=[MagicMock(_mapping=data) for data in mock_data])))

    result = await market_repo.get_hourly_aggregates(ticker, start_time, end_time)

    assert len(result) == 1
    assert result[0]["open_price"] == 150.0
    mock_session.execute.assert_called_once() 