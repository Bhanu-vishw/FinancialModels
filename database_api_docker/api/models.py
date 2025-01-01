from datetime import datetime

from pydantic import BaseModel


class Symbols(BaseModel):
    items: list[str]


class DailyBar(BaseModel):
    symbol: str
    open: float
    high: float
    close: float
    volume: float
    trade_count: float
    vwap: float
    timestamp: datetime
