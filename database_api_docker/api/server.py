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

    # Your implementation

    # Your implementation
    query = "SELECT DISTINCT symbol FROM daily_history"

    # Make the request with the query parameter
    response = requests.get(QUESTDB_ENDPOINT, params={"query": query})

    data = response.json()

    ticks = [i[0] for i in data['dataset']]

    return Symbols(items=ticks)



@app.get("/daily_bar")
def daily_bar(date: str, symbol: Optional[str] = None) -> list[DailyBar]:
    """Get a daily bar for all or a subset of symbols at a particular date

    Args:
        date (str): The specified date of the bar
        symbol (Optional[str], optional): An optional symbol, if not provided will return all bars

    Returns:
        list[DailyBar]: Daily bars at specified date (optionally per symbol)
    """

    # Your implementation
    query = f"SELECT * FROM daily_history WHERE timestamp >= '{date}T00:00:00.000000Z' AND timestamp < '{date}T23:59:59.999999Z'"
    if symbol:
        query += f" AND symbol = '{symbol}'"
    
    response = requests.get(QUESTDB_ENDPOINT, params={"query": query})

    data = response.json()

    daily = []

    for i in data["dataset"]:
        
        daily.append(
            DailyBar(
                    symbol= i[0],
                    open=i[1],
                    high=i[2],
                    close=i[4],
                    volume=i[5],
                    trade_count=i[6],
                    vwap=i[7],
                    timestamp=i[8],
            )
        )

    return(daily)




