from datetime import datetime
import os
import requests
from typing import Optional

from fastapi import FastAPI

from models import *

QUESTDB_HOST = os.environ.get("QUESTDB_HOST", "localhost")
QUESTDB_ENDPOINT = f"http://{QUESTDB_HOST}:9000/exec"

app = FastAPI()

@app.get("/symbols")
def symbols() -> Symbols:
    """Get a list of all symbols available for querying from the database

    Returns:
        Symbols: the available symbols
    """
    query = "SELECT DISTINCT symbol FROM daily_history"
    response = requests.get(QUESTDB_ENDPOINT, params={"query": query})
    data = response.json()

    ticks = [i[0] for i in data['dataset']]
    return Symbols(items=ticks)

@app.get("/daily_bar")
def daily_bar(
    from_date: str, 
    to_date: str, 
    symbol: Optional[str] = None
) -> list[DailyBar]:
    """Get daily bars for all or a subset of symbols within a date range."""

    try:
        datetime.strptime(from_date, "%Y-%m-%d")
        datetime.strptime(to_date, "%Y-%m-%d")
    except ValueError:
        return {"error": "Invalid date format. Use YYYY-MM-DD."}

    query = f"""
        SELECT symbol, open, high, close, volume, trade_count, vwap, timestamp 
        FROM daily_history 
        WHERE timestamp >= '{from_date}T00:00:00.000000Z' 
        AND timestamp <= '{to_date}T23:59:59.999999Z'
    """
    if symbol:
        query += f" AND symbol = '{symbol}'"

    response = requests.get(QUESTDB_ENDPOINT, params={"query": query})
    data = response.json()

    print("DEBUG: Raw response from QuestDB:", data)  # Debugging output

    daily = []
    for i in data["dataset"]:
        timestamp = i[7]

        # Correct handling for microseconds or nanoseconds
        if isinstance(timestamp, (int, float)):
            if timestamp > 1e12:  # Likely nanoseconds
                timestamp = datetime.utcfromtimestamp(timestamp / 1e9).isoformat() + "Z"
            elif timestamp > 1e9:  # Likely microseconds
                timestamp = datetime.utcfromtimestamp(timestamp / 1e6).isoformat() + "Z"
            else:  # Already in seconds
                timestamp = datetime.utcfromtimestamp(timestamp).isoformat() + "Z"

        daily.append(
            DailyBar(
                symbol=i[0],
                open=i[1],
                high=i[2],
                close=i[3],
                volume=i[4],
                trade_count=i[5],
                vwap=i[6],
                timestamp=timestamp,
            )
        )

    return daily