from datetime import datetime
import json
import logging
import os
import time
import asyncio
import schedule
import pandas as pd
import threading
import requests
from alpaca.data import StockHistoricalDataClient, StockBarsRequest, DataFeed, TimeFrame
from questdb.ingress import Sender

# Configuration
QUESTDB_HOST = os.getenv("QUESTDB_HOST", "localhost")
CONF = f"http::addr={QUESTDB_HOST}:9000;username=admin;password=quest;"
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", 200))  # Default to 200 days
EOD_TABLE = "eod_data"
INTRADAY_TABLE = "intraday_data"
# TRADE_DATA_TABLE = "trading_data"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_schema():
    """Initializes schemas in QuestDB."""
    for table_name in [EOD_TABLE, INTRADAY_TABLE]: # Trade tabel removed
        sql = ""
        
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

def collect_eod(symbols: list):
    """Fetches historical EOD data from Alpaca and inserts into QuestDB."""
    now = datetime.now()
    start_date = now - pd.Timedelta(days=HISTORICAL_DAYS)
    logger.info(f"Fetching EOD data from {start_date.date()} to {now.date()}")

    alpaca_api_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret_key = os.getenv("ALPACA_API_SECRET")
    if not alpaca_api_key or not alpaca_secret_key:
        raise ValueError("Alpaca API keys not found in environment variables.")

    client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    request_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Day,
        start=start_date,
        end=now,
        feed=DataFeed.IEX
    )

    try:
        bars = client.get_stock_bars(request_params)
        data = bars.df.reset_index()
        if data.empty:
            logger.warning("No data retrieved from Alpaca.")
            return
    except Exception as e:
        logger.error(f"Error fetching data: {e}")
        return

    with Sender.from_conf(CONF) as sender:
        for _, row in data.iterrows():
            sender.row(
                EOD_TABLE,
                columns={
                    "symbol": row["symbol"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                    "trade_count": row.get("trade_count", 0),
                    "vwap": row.get("vwap", row["close"]),
                },
                at=row["timestamp"]
            )
        sender.flush()
    logger.info(f"Inserted {len(data)} records into {EOD_TABLE}")

def collect_intraday(symbols):
    """Fetches the latest 1-minute bar for the given symbols and inserts into QuestDB."""
    alpaca_api_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret_key = os.getenv("ALPACA_API_SECRET")
    
    if not alpaca_api_key or not alpaca_secret_key:
        raise ValueError("Alpaca API keys not found in environment variables.")

    client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    now = datetime.utcnow()
    start_time = now - pd.Timedelta(minutes=2)
    
    request_params = StockBarsRequest(
        symbol_or_symbols=symbols,
        timeframe=TimeFrame.Minute,
        start=start_time,
        end=now,
        feed=DataFeed.IEX
    )

    try:
        bars = client.get_stock_bars(request_params)
        data = bars.df.reset_index()
        if data.empty:
            logger.warning("No intraday data retrieved from Alpaca.")
            return
    except Exception as e:
        logger.error(f"Error fetching intraday data: {e}")
        return

    with Sender.from_conf(CONF) as sender:
        for _, row in data.iterrows():
            sender.row(
                INTRADAY_TABLE,
                columns={
                    "symbol": row["symbol"],
                    "open": row["open"],
                    "high": row["high"],
                    "low": row["low"],
                    "close": row["close"],
                    "volume": row["volume"],
                    "trade_count": row.get("trade_count", 0),
                    "vwap": row.get("vwap", row["close"]),
                },
                at=row["timestamp"]
            )
        sender.flush()
    logger.info(f"Inserted {len(data)} records into {INTRADAY_TABLE}")
    

def main():
    """Entrypoint for the data collection script."""
    with open("cfg.json", "r") as file:
        config = json.load(file)
    symbols = config["symbols"]

    init_schema()
    collect_eod(symbols)

    # Schedule intraday data collection every minute
    schedule.every(1).minute.do(collect_intraday, symbols=symbols)

    # Schedule EOD data collection at 22:00 UTC
    schedule.every().day.at("22:00").do(collect_eod, symbols=symbols)

    try:
        while True:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")

if __name__ == "__main__":
    main()
