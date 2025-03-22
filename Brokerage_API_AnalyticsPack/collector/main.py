from datetime import datetime
import json
import logging
import os
import time
from typing import Iterable

import pandas as pd
import requests
import schedule
from alpaca.data import StockHistoricalDataClient, StockBarsRequest, DataFeed, TimeFrame
from questdb.ingress import Sender

# Configuration
QUESTDB_HOST = os.getenv("QUESTDB_HOST", "localhost")
CONF = f"http::addr={QUESTDB_HOST}:9000;username=admin;password=quest;"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_schema(table_name: str) -> None:
    """Initializes the schema in QuestDB."""
    sql = f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            symbol SYMBOL,
            open DOUBLE,
            high DOUBLE,
            low DOUBLE,
            close DOUBLE,
            volume DOUBLE,
            trade_count DOUBLE,
            vwap DOUBLE,
            timestamp TIMESTAMP
        ) TIMESTAMP(timestamp) PARTITION BY DAY WAL
        DEDUP UPSERT KEYS(timestamp, symbol);
    """.replace("\n", "")
    
    response = requests.get(f"http://{QUESTDB_HOST}:9000/exec", params={"query": sql})
    response.raise_for_status()
    logger.info(f"Initialized schema for table: {table_name}")

def collect(symbols: Iterable[str], table_name: str, lookback: int) -> None:
    """Fetches stock data from Alpaca and inserts into QuestDB."""
    now = datetime.now()
    start_date = now - pd.tseries.offsets.BDay(lookback)
    logger.info(f"Fetching data from {start_date} to {now}")

    # Retrieve API credentials
    alpaca_api_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret_key = os.getenv("ALPACA_API_SECRET")
    if not alpaca_api_key or not alpaca_secret_key:
        raise ValueError("Alpaca API keys not found in environment variables.")

    # Initialize Alpaca client
    client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)

    # Request stock data for all symbols at once
    request_params = StockBarsRequest(
        symbol_or_symbols=list(symbols),
        timeframe=TimeFrame.Day,
        start=start_date.to_pydatetime(),
        end=now,
        feed=DataFeed.IEX  # Use IEX for accurate data
    )

    try:
        bars = client.get_stock_bars(request_params)
        data = bars.df.reset_index()  # Convert to DataFrame
        if data.empty:
            logger.warning("No data retrieved from Alpaca.")
            return
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return

    # Insert data into QuestDB
    with Sender.from_conf(CONF) as sender:
        for _, row in data.iterrows():
            sender.row(
                table_name,
                columns={
                    "symbol": row["symbol"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                    "trade_count": row["trade_count"],
                    "vwap": row["vwap"],
                },
                at=row["timestamp"]
            )
        sender.flush()
    logger.info(f"Inserted {len(data)} records into {table_name}")

def main():
    """Entrypoint for the data collection script."""
    with open("cfg.json", "r") as file:
        config = json.load(file)

    table_name = config["table_name"]
    symbols = config["symbols"]
    lookback = config["lookback_days"]

    init_schema(table_name)
    collect(symbols=symbols, table_name=table_name, lookback=lookback)

    # Schedule daily data collection
    schedule.every().day.do(collect, symbols=symbols, table_name=table_name, lookback=lookback)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Reduce CPU usage

if __name__ == "__main__":
    main()
