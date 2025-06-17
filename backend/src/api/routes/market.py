import datetime
import json
from typing import Any, List

import fastapi
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.session import get_async_session, get_redis_client
from src.repository.crud.market import MarketDataCRUDRepository
from src.repository.redis import RedisClient

router = APIRouter()


@router.get("/market/{ticker}")
async def get_market_data(
    ticker: str,
    start_time: datetime.datetime | None = Query(None, description="Start time in ISO format"),
    end_time: datetime.datetime | None = Query(None, description="End time in ISO format"),
    limit: int = Query(100, ge=1, le=1000, description="Number of records to return"),
    async_session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client)
) -> dict[str, Any]:
    cache_key = f"market_data:{ticker}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        await redis_client.set(f"frequent_ticker:{ticker}", "1", expire=3600)
        return {"data": json.loads(cached_data)}

    market_repo = MarketDataCRUDRepository(async_session)
    data = await market_repo.get_market_data(
        ticker=ticker,
        start_time=start_time,
        end_time=end_time,
        limit=limit
    )

    if not data:
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"No market data available for {ticker}"
        )

    result = [{
        "ticker": item.ticker,
        "timestamp": item.timestamp.isoformat(),
        "open_price": item.open_price,
        "high_price": item.high_price,
        "low_price": item.low_price,
        "close_price": item.close_price,
        "volume": item.volume
    } for item in data]

    return {"data": result}


@router.get("/market/{ticker}/daily")
async def get_daily_market_data(
    ticker: str,
    start_time: datetime.datetime | None = Query(None, description="Start time in ISO format"),
    end_time: datetime.datetime | None = Query(None, description="End time in ISO format"),
    async_session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client)
) -> dict[str, Any]:
    cache_key = f"market_data_daily:{ticker}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return {"data": json.loads(cached_data)}

    market_repo = MarketDataCRUDRepository(async_session)
    data = await market_repo.get_daily_aggregates(
        ticker=ticker,
        start_time=start_time,
        end_time=end_time
    )

    if not data:
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"No daily market data available for {ticker}"
        )

    result = [{
        "ticker": ticker,
        "date": item["bucket"].isoformat(),
        "open_price": item["open_price"],
        "high_price": item["high_price"],
        "low_price": item["low_price"],
        "close_price": item["close_price"],
        "volume": item["volume"]
    } for item in data]

    safe_result = redis_client.convert_decimals(result)
    await redis_client.set(cache_key, json.dumps(safe_result), expire=3600)
    return {"data": result}


@router.get("/market/{ticker}/hourly")
async def get_hourly_market_data(
    ticker: str,
    start_time: datetime.datetime | None = Query(None, description="Start time in ISO format"),
    end_time: datetime.datetime | None = Query(None, description="End time in ISO format"),
    async_session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client)
) -> dict[str, Any]:
    cache_key = f"market_data_hourly:{ticker}"
    cached_data = await redis_client.get(cache_key)

    if cached_data:
        return {"data": json.loads(cached_data)}

    market_repo = MarketDataCRUDRepository(async_session)
    data = await market_repo.get_hourly_aggregates(
        ticker=ticker,
        start_time=start_time,
        end_time=end_time
    )

    if not data:
        raise fastapi.HTTPException(
            status_code=404,
            detail=f"No hourly market data available for {ticker}"
        )

    result = [{
        "ticker": ticker,
        "hour": item["bucket"].isoformat(),
        "open_price": item["open_price"],
        "high_price": item["high_price"],
        "low_price": item["low_price"],
        "close_price": item["close_price"],
        "volume": item["volume"]
    } for item in data]

    safe_result = redis_client.convert_decimals(result)
    await redis_client.set(cache_key, json.dumps(safe_result), expire=3600)
    return {"data": result}


@router.get("/market")
async def get_all_market_data(
    async_session: AsyncSession = Depends(get_async_session),
    redis_client: RedisClient = Depends(get_redis_client)
) -> dict[str, Any]:
    tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]
    result = {}
    market_repo = MarketDataCRUDRepository(async_session)

    for ticker in tickers:
        cache_key = f"market_data:{ticker}"
        cached_data = await redis_client.get(cache_key)

        if cached_data:
            result[ticker] = json.loads(cached_data)
            continue

        latest_data = await market_repo.get_latest_market_data(ticker)
        if latest_data:
            result[ticker] = {
                "ticker": latest_data.ticker,
                "timestamp": latest_data.timestamp.isoformat(),
                "open_price": latest_data.open_price,
                "high_price": latest_data.high_price,
                "low_price": latest_data.low_price,
                "close_price": latest_data.close_price,
                "volume": latest_data.volume
            }

    if not result:
        raise fastapi.HTTPException(
            status_code=404,
            detail="No market data available"
        )

    return {"data": result} 