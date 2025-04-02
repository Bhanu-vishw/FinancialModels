from datetime import datetime, timedelta
import os
import requests
import logging
import sys
from typing import Optional
from fastapi import FastAPI, HTTPException
from models import Symbols, DailyBar, ExecutionReport

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# Environment variables
QUESTDB_HOST = os.getenv("QUESTDB_HOST", "localhost")
QUESTDB_ENDPOINT = f"http://{QUESTDB_HOST}:9000/exec"
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", 200))  # Default to 200 days

# Table names
# Extract table names and symbols from config
EOD_TABLE = "eod_data"
INTRADAY_TABLE = "intraday_data"
TRADE_DATA_TABLE = "trading_data"

# Initialize FastAPI app
app = FastAPI()


def parse_datetime(dt_str: str) -> Optional[datetime]:
    """Helper to parse various datetime string formats"""
    if not dt_str:
        return None
    try:
        # Handle ISO format
        if 'T' in dt_str:
            return datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        # Handle other formats as needed
        return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except (ValueError, TypeError) as e:
        logger.warning(f"Failed to parse datetime '{dt_str}': {e}")
        return None
    


def fetch_trade_data() -> list[dict]:
    """Self-contained QuestDB query function"""
    query = f"SELECT * FROM {TRADE_DATA_TABLE} ORDER BY created_at DESC;"
    try:
        response = requests.get(
            QUESTDB_ENDPOINT, 
            params={"query": query},
            timeout=5  # Always set timeouts for production
        )
        response.raise_for_status()
        return response.json().get('dataset', [])  # Adapt based on QuestDB's response format
    except Exception as e:
        logger.error(f"QuestDB query failed: {str(e)}")
        return []



@app.get("/symbols")
def symbols() -> Symbols:
    """Fetch all available stock symbols from the database."""
    query = f"SELECT DISTINCT symbol FROM {EOD_TABLE}"
    try:
        response = requests.get(QUESTDB_ENDPOINT, params={"query": query})
        response.raise_for_status()
        data = response.json()
        if "dataset" not in data:
            raise HTTPException(status_code=500, detail="Invalid response from database")
        return Symbols(items=[i[0] for i in data["dataset"]])
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Database request failed: {str(e)}")

@app.get("/bar")
def bar(
    from_date: Optional[str] = None,
    to_date: Optional[str] = None,
    symbol: Optional[str] = None,
    intraday: Optional[bool] = False 
) -> list[DailyBar]:
    """Fetch stock bars for given symbols within a date range."""
    if not to_date:
        to_date = datetime.utcnow().strftime("%Y-%m-%d")
    if not from_date:
        from_date = (datetime.utcnow() - timedelta(days=HISTORICAL_DAYS)).strftime("%Y-%m-%d")
    
    # Validate date format
    try:
        datetime.strptime(from_date, "%Y-%m-%d")
        datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")
    
    table = INTRADAY_TABLE if intraday else EOD_TABLE
    query = f"""
        SELECT symbol, open, high, close, volume, trade_count, vwap, timestamp 
        FROM {table} 
        WHERE timestamp >= '{from_date}T00:00:00.000000Z' 
        AND timestamp <= '{to_date}T23:59:59.999999Z'
    """
    if symbol:
        query += f" AND symbol = '{symbol}'"
    
    try:
        response = requests.get(QUESTDB_ENDPOINT, params={"query": query})
        response.raise_for_status()
        data = response.json()

        if "dataset" not in data or not data["dataset"]:
            return []  # Return empty list if no data

        daily_bars = []
        for i in data["dataset"]:
            timestamp = i[7]
            
            # Handle different timestamp formats
            if isinstance(timestamp, (int, float)):
                if timestamp > 1e12:
                    timestamp = datetime.utcfromtimestamp(timestamp / 1e9).isoformat() + "Z"
                elif timestamp > 1e9:
                    timestamp = datetime.utcfromtimestamp(timestamp / 1e6).isoformat() + "Z"
                else:
                    timestamp = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"

            daily_bars.append(
                DailyBar(
                    symbol=i[0], open=i[1], high=i[2], close=i[3], volume=i[4], 
                    trade_count=i[5], vwap=i[6], timestamp=timestamp,
                )
            )
        return daily_bars

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Database request failed: {str(e)}")

@app.get("/latest_bar")
def latest_bar(symbol: str, to_date: Optional[str] = None, intraday: Optional[bool] = True) -> Optional[list[DailyBar]]:
    """Fetch the most recent stock bars for a given symbol."""
    if not QUESTDB_ENDPOINT:
        raise HTTPException(status_code=500, detail="Database endpoint is missing")
    
    # Use today's date if no specific date is provided
    if not to_date:
        to_date = datetime.utcnow().strftime("%Y-%m-%d")

    table = INTRADAY_TABLE if intraday else EOD_TABLE
    query = f"""
        SELECT symbol, open, high, close, volume, trade_count, vwap, timestamp 
        FROM {table} 
        WHERE timestamp >= '{to_date}T00:00:00.000000Z' 
        AND timestamp <= '{to_date}T23:59:59.999999Z'
    """
    if symbol:
        query += f" AND symbol = '{symbol}'"
    try:
        response = requests.get(QUESTDB_ENDPOINT, params={"query": query})
        response.raise_for_status()
        data = response.json()

        if "dataset" not in data or not data["dataset"]:
            return []

        result = []
        for row in data["dataset"]:
            timestamp = row[7]

            # Handle timestamp conversion
            if isinstance(timestamp, (int, float)):
                if timestamp > 1e12:
                    timestamp = datetime.utcfromtimestamp(timestamp / 1e9).isoformat() + "Z"
                elif timestamp > 1e9:
                    timestamp = datetime.utcfromtimestamp(timestamp / 1e6).isoformat() + "Z"
                else:
                    timestamp = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"

            result.append(DailyBar(
                symbol=row[0], open=row[1], high=row[2], close=row[3], volume=row[4], 
                trade_count=row[5], vwap=row[6], timestamp=timestamp,
            ))

        return result

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Database request failed: {str(e)}")

    except (IndexError, KeyError, ValueError) as e:
        raise HTTPException(status_code=500, detail=f"Error processing data: {str(e)}")

@app.get("/trade-data", response_model=list[ExecutionReport])
async def get_trade_data():
    """
    Endpoint to get trade execution data from QuestDB.
    Returns:
        List[ExecutionReport]: List of trade execution records
    """
    try:
        # Fetch trade data from QuestDB
        trades = fetch_trade_data()
        
        if not trades:
            logger.info("No trade data available")
            return []
        
        # Transform and validate the data
        trade_list = []
        for trade in trades:
            try:
                # Ensure all required fields exist and are properly formatted
                trade_list.append(ExecutionReport(
                    client_order_id=str(trade.get('client_order_id', '')),
                    symbol=str(trade.get('symbol', '')),
                    status=str(trade.get('status', '')),
                    side=str(trade.get('side', '')),
                    created_at=parse_datetime(trade.get('created_at')),
                    quantity=float(trade.get('quantity', 0)),
                    last_filled_qty=float(trade.get('last_filled_qty', 0)),
                    last_fill_price=float(trade.get('last_fill_price', 0)),
                    total_filled_qty=float(trade.get('total_filled_qty', 0)),
                    average_fill_price=float(trade.get('average_fill_price', 0)),
                    filled_at=parse_datetime(trade.get('filled_at'))
                ))
            except (ValueError, TypeError) as e:
                logger.warning(f"Skipping malformed trade record: {trade}. Error: {e}")
                continue
        
        return trade_list
    
    except Exception as e:
        logger.error(f"Error fetching trade data: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching trade data: {str(e)}"
        )
