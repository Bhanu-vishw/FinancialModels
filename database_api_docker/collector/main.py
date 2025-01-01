from datetime import datetime
import json
import logging
import os
import requests
import time
from typing import Iterable

from alpaca.data import StockHistoricalDataClient, StockBarsRequest, DataFeed, TimeFrame
import pandas as pd
import schedule
from questdb.ingress import Sender

QUESTDB_HOST = os.environ.get("QUESTDB_HOST", "localhost")
CONF = f"http::addr={QUESTDB_HOST}:9000;username=admin;password=quest;"
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def init_schema(table_name) -> None:
    """Initializes schema"""

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
    """.replace(
        "\n", ""
    )
    result = requests.get(f"http://{QUESTDB_HOST}:9000/exec", params={"query": sql})
    result.raise_for_status()


def collect(symbols: Iterable[str], table_name: str, lookback: int):
    """Inserts symbols into QuestDB for the particular table name starting from
    the lookback period.

    Args:
        symbols (Iterable[str]): the symbols to collect
        table_name (str): the name of the table
        lookback (int): lookback business days
    """
    now = datetime.now()
    start = now - pd.tseries.offsets.BDay(lookback)
    logger.info(f"Running collection from {start} to {now}")

    # Your implementation

    ########################################################################
    # Get API Keys
    
    # Load environment variables from the .env file

    # Original directory -> ../.env

    try:
        with open('.env') as file:
            for line in file:
                # Strip whitespace from the line
                line = line.strip()
                # Skip empty lines and comments
                if line and not line.startswith('#'):
                    # Split at the first '=' sign
                    key, value = line.split('=', 1)
                    key = key.strip()  # Remove any extra spaces around the key
                    value = value.strip().strip('"').strip("'")  # Remove spaces and surrounding quotes
                    os.environ[key] = value
    except FileNotFoundError:
        raise FileNotFoundError("The .env file was not found. Please ensure it is in the correct directory.")

    # Retrieve environment variables

    alpaca_api_key = os.getenv("ALPACA_API_KEY")
    alpaca_secret_key = os.getenv("ALPACA_API_SECRET")


    print(alpaca_api_key)
    print(alpaca_secret_key)



    if not alpaca_api_key or not alpaca_secret_key:
        raise ValueError("API keys not found in the environment.")
    

    ##########################################################################
    # Get Data then Add to Quest DB

    client = StockHistoricalDataClient(alpaca_api_key, alpaca_secret_key)
    # Define the parameters for the data request
  
    timeframe = TimeFrame.Day  # Timeframe for the stock bars (e.g., Day, Minute)
    lookback_days = lookback  # Number of business days to look back
    # Calculate the date range
    now = datetime.now()
    start_date = now - pd.tseries.offsets.BDay(lookback_days)  # Lookback period
    # Fetch data for each symbol
    for symbol in symbols:
        # Create a request for stock bars
        request_params = StockBarsRequest(
            symbol_or_symbols=symbol,
            timeframe=timeframe,
            start=start_date.to_pydatetime(),
            end=now,
            feed=DataFeed.IEX  # Use SIP feed for accurate market data
        )
        # Get stock bars
        bars = client.get_stock_bars(request_params)
        data = pd.DataFrame(bars.df)

        #################################################################################
        # Start Adding to the Quest DB

        for i in range(len(data)):

            with Sender.from_conf(CONF) as sender:
                sender.row(
                    table_name,
                    columns = {
                        'symbol':  data.index[0][0],
                        'open': float(data.iloc[i]["open"]),
                        'high': float(data.iloc[i]["high"]),
                        'low' : float(data.iloc[i]["low"]),
                        'close': float(data.iloc[i]["close"]),
                        'volume': float(data.iloc[i]["volume"]),
                        'trade_count': float(data.iloc[i]["trade_count"]),
                        'vwap': float(data.iloc[i]["vwap"]), 
                    },
                    at = data.index[i][1]
                )
                sender.flush()


def main():
    """Entrypoint"""

    # Your implementation
    # ---
    # Here you should be loading cfg.json and populating table_name, symbols and
    # lookback

    with open('cfg.json', 'r') as file:
        data = json.load(file)

    table_name = data['table_name']
    symbols = data['symbols']
    lookback = data['lookback_days'] 

    print(data)

    # ---

    init_schema(table_name)
    collect(symbols=symbols, table_name=table_name, lookback=lookback)

    schedule.every().day.do(
        collect, symbols=symbols, table_name=table_name, lookback=lookback
    )

    
    while True:
        schedule.run_pending()
        time.sleep(1)


if __name__ == "__main__":
    main()