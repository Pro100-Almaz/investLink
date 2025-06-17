import asyncio
import datetime
import json
from typing import Any, List

import loguru
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from src.config.manager import settings
from src.models.db.market import MarketData
from src.repository.crud.market import MarketDataCRUDRepository
from src.repository.polygon_client import fetch_aggregates
from src.repository.redis import redis_client


async def process_market_data(data: List[dict], ticker: str) -> List[MarketData]:
    market_data_list = []
    for item in data:
        market_data = MarketData(
            ticker=ticker,
            timestamp=datetime.datetime.fromtimestamp(item['t'] / 1000, tz=datetime.timezone.utc),
            open_price=item['o'],
            high_price=item['h'],
            low_price=item['l'],
            close_price=item['c'],
            volume=item['v']
        )
        market_data_list.append(market_data)
    return market_data_list


async def update_market_data(async_session: AsyncSession) -> None:
    try:
        now = datetime.datetime.now()
        to_date = now.strftime("%Y-%m-%d")
        from_date = (now - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "META"]

        market_repo = MarketDataCRUDRepository(async_session)

        for ticker in tickers:
            try:
                data = await fetch_aggregates(
                    ticker=ticker,
                    multiplier=1,
                    timespan="hour",
                    _from=from_date,
                    to=to_date
                )

                market_data_list = await process_market_data(data, ticker)
                await market_repo.create_market_data_bulk(market_data_list)

                cache_key = f"frequent_ticker:{ticker}"
                if await redis_client.exists(cache_key):
                    latest_data = await market_repo.get_latest_market_data(ticker)
                    if latest_data:
                        await redis_client.set(
                            key=f"market_data:{ticker}",
                            value=json.dumps({
                                "ticker": latest_data.ticker,
                                "timestamp": latest_data.timestamp.isoformat(),
                                "open_price": latest_data.open_price,
                                "high_price": latest_data.high_price,
                                "low_price": latest_data.low_price,
                                "close_price": latest_data.close_price,
                                "volume": latest_data.volume
                            }),
                            expire=300
                        )

                loguru.logger.info(f"Successfully fetched and stored data for {ticker}")

            except Exception as e:
                loguru.logger.error(f"Error fetching data for {ticker}: {str(e)}")
                continue

    except Exception as e:
        loguru.logger.error(f"Error in update_market_data task: {str(e)}")


async def run_scheduler() -> None:
    from src.repository.database import async_db

    engine = create_async_engine(
        str(async_db.postgres_uri).replace("postgresql://", "postgresql+asyncpg://"),
        echo=settings.IS_DB_ECHO_LOG,
        pool_size=settings.DB_POOL_SIZE,
        max_overflow=settings.DB_POOL_OVERFLOW,
    )
    async_session_factory = async_sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False
    )

    while True:
        try:
            async with async_session_factory() as session:
                await update_market_data(session)
            await asyncio.sleep(settings.UPDATE_INTERVAL_MINUTES * 60)
        except Exception as e:
            loguru.logger.error(f"Error in scheduler: {str(e)}")
            await asyncio.sleep(300)