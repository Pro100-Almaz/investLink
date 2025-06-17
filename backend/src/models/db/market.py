import datetime

import sqlalchemy
from sqlalchemy.orm import Mapped as SQLAlchemyMapped, mapped_column as sqlalchemy_mapped_column
from sqlalchemy.sql import functions as sqlalchemy_functions

from src.repository.table import Base


class MarketData(Base):
    __tablename__ = "market_data"

    id: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(primary_key=True, autoincrement="auto")
    ticker: SQLAlchemyMapped[str] = sqlalchemy_mapped_column(sqlalchemy.String(length=10), nullable=False)
    timestamp: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False
    )
    open_price: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    high_price: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    low_price: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    close_price: SQLAlchemyMapped[float] = sqlalchemy_mapped_column(sqlalchemy.Float, nullable=False)
    volume: SQLAlchemyMapped[int] = sqlalchemy_mapped_column(sqlalchemy.BigInteger, nullable=False)
    created_at: SQLAlchemyMapped[datetime.datetime] = sqlalchemy_mapped_column(
        sqlalchemy.DateTime(timezone=True), nullable=False, server_default=sqlalchemy_functions.now()
    )

    __table_args__ = (
        sqlalchemy.Index('idx_market_data_ticker_timestamp', 'ticker', 'timestamp'),
        # TimescaleDB hypertable configuration
        {'timescaledb_hypertable': {
            'time_column_name': 'timestamp',
            'chunk_time_interval': '1 day',
            'if_not_exists': True
        }}
    ) 