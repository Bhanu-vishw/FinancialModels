from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from enum import Enum

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

class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderStatus(str, Enum):
    FILLED = "filled"
    PENDING = "pending"
    CANCELLED = "cancelled"

class ExecutionReport(BaseModel):
    """Tracks status of an order"""
    
    client_order_id: str
    symbol: str
    status: OrderStatus  # Now restricted to 'filled', 'pending', 'cancelled'
    side: OrderSide  # Now restricted to 'BUY' or 'SELL'
    created_at: datetime
    quantity: Optional[float] = None
    last_filled_qty: Optional[float] = None
    last_fill_price: Optional[float] = None
    total_filled_qty: Optional[float] = None
    average_fill_price: Optional[float] = None
    filled_at: Optional[datetime] = None
