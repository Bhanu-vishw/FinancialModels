import os
import time
import logging
import pytz
from datetime import datetime
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from alpaca.data.historical.stock import StockHistoricalDataClient
from alpaca.data.requests import StockLatestTradeRequest
from concurrent.futures import ThreadPoolExecutor
from strategy import TradingStrategies

# Configure logging
logging.basicConfig(level=logging.INFO)

# Alpaca API credentials from environment variables
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

# Initialize Alpaca clients
REST_CLIENT = StockHistoricalDataClient(API_KEY, SECRET_KEY)
TRADING_CLIENT = TradingClient(API_KEY, SECRET_KEY, paper=True)

NY_TZ = pytz.timezone("America/New_York")

def is_market_open():
    return TRADING_CLIENT.get_clock().is_open

def get_last_price(symbol):
    try:
        data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
        request_params = StockLatestTradeRequest(symbol_or_symbols=[symbol])
        latest_trade = data_client.get_latest_trade(request_params)
        return latest_trade[symbol].price
    except Exception as e:
        logging.error(f"Error fetching last price for {symbol}: {e}")
        return None

def submit_order(symbol, qty, side, strategy_name):
    """Submit an order via Alpaca"""
    try:
        order_request = MarketOrderRequest(symbol=symbol, qty=qty, side=side, time_in_force=TimeInForce.GTC)
        order = TRADING_CLIENT.submit_order(order_data=order_request)
        logging.info(f"{strategy_name}: {side.capitalize()} order for {qty} {symbol} shares")
        return order
    except Exception as e:
        logging.error(f"Order submission error for {symbol}: {e}")
        return None

def main():
    strategies = TradingStrategies(TRADING_CLIENT, REST_CLIENT, submit_order, get_last_price)

    # Load symbols and allocations from environment variables
    symbols = {
        "buy_close_sell_open": os.getenv("SYMBOL_BUY_CLOSE_SELL_OPEN"),
        "short_term_momentum": os.getenv("SYMBOL_SHORT_TERM_MOMENTUM"),
        "ORB_strategy": os.getenv("SYMBOL_ORB_STRATEGY"),
    }
    
    shares_allocation = {
        "buy_close_sell_open": int(os.getenv("SHARES_BUY_CLOSE_SELL_OPEN", 10)),
        "short_term_momentum": int(os.getenv("SHARES_SHORT_TERM_MOMENTUM", 5)),
        "ORB_strategy": int(os.getenv("SHARES_ORB_STRATEGY", 8)),
    }

    while True:
        if is_market_open():
            with ThreadPoolExecutor(max_workers=3) as executor:
                executor.submit(strategies.buy_close_sell_open, symbols["buy_close_sell_open"], shares_allocation["buy_close_sell_open"])
                executor.submit(strategies.short_term_momentum, symbols["short_term_momentum"], shares_allocation["short_term_momentum"])
                executor.submit(strategies.opening_range_breakout, symbols["ORB_strategy"], shares_allocation["ORB_strategy"])
        
        time.sleep(60)

if __name__ == "__main__":
    main()
