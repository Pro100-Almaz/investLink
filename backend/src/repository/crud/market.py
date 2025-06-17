import datetime
from typing import List, Optional, Dict, Any

from sqlalchemy import select, text, bindparam, String, DateTime

from src.models.db.market import MarketData
from src.repository.crud.base import BaseCRUDRepository


class MarketDataCRUDRepository(BaseCRUDRepository):
    async def create_market_data(self, market_data: MarketData) -> MarketData:
        self.async_session.add(market_data)
        await self.async_session.commit()
        await self.async_session.refresh(market_data)
        return market_data

    async def create_market_data_bulk(self, market_data_list: List[MarketData]) -> List[MarketData]:
        self.async_session.add_all(market_data_list)
        await self.async_session.commit()
        for market_data in market_data_list:
            await self.async_session.refresh(market_data)
        return market_data_list

    async def get_market_data(
        self,
        ticker: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None,
        limit: int = 100
    ) -> List[MarketData]:
        query = select(MarketData).where(MarketData.ticker == ticker)
        
        if start_time:
            query = query.where(MarketData.timestamp >= start_time)
        if end_time:
            query = query.where(MarketData.timestamp <= end_time)
            
        query = query.order_by(MarketData.timestamp.desc()).limit(limit)
        
        result = await self.async_session.execute(query)
        return result.scalars().all()

    async def get_latest_market_data(self, ticker: str) -> Optional[MarketData]:
        query = text("""
            SELECT * FROM market_data 
            WHERE ticker = :ticker 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        result = await self.async_session.execute(query, {"ticker": ticker})
        row = result.first()
        if row:
            return MarketData(**row._mapping)
        return None

    async def get_daily_aggregates(
        self,
        ticker: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                time_bucket('1 day', timestamp) as bucket,
                first(open_price, timestamp) as open_price,
                max(high_price) as high_price,
                min(low_price) as low_price,
                last(close_price, timestamp) as close_price,
                sum(volume) as volume
            FROM market_data
            WHERE ticker = :ticker
            AND (:start_time IS NULL OR timestamp >= :start_time)
            AND (:end_time IS NULL OR timestamp <= :end_time)
            GROUP BY bucket
            ORDER BY bucket DESC
        """).bindparams(
            bindparam("ticker", type_=String),
            bindparam("start_time", type_=DateTime),
            bindparam("end_time", type_=DateTime)
        )
        
        result = await self.async_session.execute(
            query,
            {
                "ticker": ticker,
                "start_time": start_time,
                "end_time": end_time
            }
        )
        return [dict(row._mapping) for row in result]

    async def get_hourly_aggregates(
        self,
        ticker: str,
        start_time: Optional[datetime.datetime] = None,
        end_time: Optional[datetime.datetime] = None
    ) -> List[Dict[str, Any]]:
        query = text("""
            SELECT 
                time_bucket('1 hour', timestamp) as bucket,
                first(open_price, timestamp) as open_price,
                max(high_price) as high_price,
                min(low_price) as low_price,
                last(close_price, timestamp) as close_price,
                sum(volume) as volume
            FROM market_data
            WHERE ticker = :ticker
            AND (:start_time IS NULL OR timestamp >= :start_time)
            AND (:end_time IS NULL OR timestamp <= :end_time)
            GROUP BY bucket
            ORDER BY bucket DESC
        """).bindparams(
            bindparam("ticker", type_=String),
            bindparam("start_time", type_=DateTime),
            bindparam("end_time", type_=DateTime)
        )
        
        result = await self.async_session.execute(
            query,
            {
                "ticker": ticker,
                "start_time": start_time,
                "end_time": end_time
            }
        )
        return [dict(row._mapping) for row in result]