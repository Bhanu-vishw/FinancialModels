from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, field_validator
import psycopg2
import os
from alpaca.trading.client import TradingClient
from psycopg2 import sql
from datetime import datetime

# Environment variables for database and Alpaca API
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_API_SECRET")

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Initialize Alpaca TradingClient for checking market status
TRADING_CLIENT = TradingClient(API_KEY, SECRET_KEY, paper=True)

# Pydantic model for the Trade data with more robust validation
class Trade(BaseModel):
    strategy: str = Field(..., min_length=1, max_length=100)
    symbol: str = Field(..., min_length=1, max_length=10)
    action: str 
    price: float = Field(..., gt=0)
    quantity: int = Field(..., gt=0)
    timestamp: str = Field(..., description="ISO formatted timestamp")

    @field_validator('action')
    @classmethod
    def validate_action(cls, v):
        if v.lower() not in ['buy', 'sell']:
            raise ValueError('Action must be either "buy" or "sell"')
        return v.lower()

@app.post("/trades/")
async def add_trade(trade: Trade):
    """Add a trade to the database with improved error handling."""
    conn = None
    try:
        # Validate timestamp
        datetime.fromisoformat(trade.timestamp)
        
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            query = sql.SQL(
                "INSERT INTO trades (strategy, symbol, action, price, quantity, timestamp) "
                "VALUES (%s, %s, %s, %s, %s, %s);"
            )
            cursor.execute(query, (
                trade.strategy, 
                trade.symbol, 
                trade.action, 
                trade.price, 
                trade.quantity, 
                trade.timestamp
            ))
            conn.commit()
        return {"message": "Trade logged successfully."}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=f"Invalid timestamp format: {ve}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inserting trade: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/")
async def get_health():
    """Health check endpoint."""
    return {"status": "healthy", "message": "API is running"}

@app.get("/pnl/")
async def get_pnl():
    """Retrieve PnL grouped by strategy with more robust error handling."""
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    strategy, 
                    SUM(CASE WHEN action = 'buy' THEN -price * quantity 
                              ELSE price * quantity END) AS pnl 
                FROM trades 
                GROUP BY strategy;
            """)
            results = cursor.fetchall()
        
        # Convert results to a more readable format
        pnl_dict = [
            {"strategy": row[0], "pnl": float(row[1])} 
            for row in results
        ]
        return {"pnl": pnl_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving PnL: {e}")
    finally:
        if conn:
            conn.close()

@app.get("/market_status/")
async def market_status():
    """Check if the market is open and provide next open/close times."""
    try:
        clock = TRADING_CLIENT.get_clock()
        return {
            "market_open": clock.is_open,
            "next_open": clock.next_open.isoformat(),
            "next_close": clock.next_close.isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching market status: {e}")
        

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

