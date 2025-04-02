import logging
import os
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
import requests
import time

# Load environment variables for API keys
API_KEY = os.getenv("ALPACA_API_KEY")
API_SECRET = os.getenv("ALPACA_API_SECRET")
PAPER = True  # Set to False for live trading

# Initialize Alpaca Trading Client
trading_client = TradingClient(API_KEY, API_SECRET, paper=PAPER)

# QuestDB Connection Configuration (from your provided details)
QUESTDB_HOST = os.getenv("QUESTDB_HOST", "localhost")
BASE_URL = f"http://{QUESTDB_HOST}:9000/exec"

# Table name in QuestDB
TRADE_DATA_TABLE = "trading_data"

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_trade_table():
    """Creates the 'trading_data' table in QuestDB (if not exists)."""
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {TRADE_DATA_TABLE} (
        client_order_id STRING,
        symbol STRING,
        status STRING,
        side STRING,
        created_at TIMESTAMP,
        quantity DOUBLE,
        last_filled_qty DOUBLE,
        last_fill_price DOUBLE,
        total_filled_qty DOUBLE,
        average_fill_price DOUBLE,
        filled_at TIMESTAMP
    ) TIMESTAMP(created_at) PARTITION BY DAY;
    """
    
    try:
        # Send the query using requests.get() to QuestDB's HTTP API
        response = requests.get(BASE_URL, params={"query": create_table_query})
        response.raise_for_status()  # Raises an error for bad HTTP responses
        logger.info(f"Table '{TRADE_DATA_TABLE}' is ready in QuestDB.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error creating table: {e}")

def log_trade_data(order_data: dict):
    """Logs trade execution details into QuestDB."""
    insert_query = f"""
    INSERT INTO {TRADE_DATA_TABLE} (
        client_order_id, symbol, status, side, created_at, 
        quantity, last_filled_qty, last_fill_price, total_filled_qty, 
        average_fill_price, filled_at
    ) VALUES (
        '{order_data["client_order_id"]}', '{order_data["symbol"]}', '{order_data["status"]}', 
        '{order_data["side"]}', '{order_data["created_at"]}', 
        {order_data["quantity"]}, {order_data["last_filled_qty"]}, {order_data["last_fill_price"]}, 
        {order_data["total_filled_qty"]}, {order_data["average_fill_price"]}, 
        '{order_data["filled_at"]}'
    );
    """
    
    try:
        # Send the insert query using requests.get() to QuestDB's HTTP API
        response = requests.get(BASE_URL, params={"query": insert_query})
        response.raise_for_status()  # Raises an error for bad HTTP responses
        logger.info(f"Logged trade data for order: {order_data['client_order_id']} into '{TRADE_DATA_TABLE}'.")
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ Error logging trade data: {e}")

# Callback function for order updates
async def on_order_update(order):  # <-- Add 'async'
    """Async callback for order updates."""
    order_data = {
        "client_order_id": order.client_order_id,
        "symbol": order.symbol,
        "status": order.status,
        "side": order.side,
        "created_at": order.submitted_at.isoformat(),
        "quantity": float(order.qty),  # Ensure numeric types
        "last_filled_qty": float(order.filled_qty),
        "last_fill_price": float(order.filled_avg_price),
        "total_filled_qty": float(order.filled_qty),
        "average_fill_price": float(order.filled_avg_price),
        "filled_at": order.filled_at.isoformat() if order.filled_at else None,
    }
    log_trade_data(order_data)

def start_listening_for_order_updates():
    try:
        conn = TradingStream(API_KEY, API_SECRET)
        conn.subscribe_trade_updates(on_order_update)  # Now async
        
        # Run in an async context
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(conn.run())
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


# Main function to keep the script running
def main():
    # Ensure table is created when the script starts
    create_trade_table()
    
    # Start listening for Alpaca order updates
    start_listening_for_order_updates()

    # Keep the script running indefinitely
    while True:
        time.sleep(60)  # Sleep for 60 seconds before checking for updates again

if __name__ == "__main__":
    main()

# # Ensure table exists at startup
# create_trade_table()