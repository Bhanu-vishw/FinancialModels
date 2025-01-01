import time
import pytz
import os
import logging
from datetime import datetime, timedelta
from alpaca_trade_api.rest import REST, TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
#from alpaca.trading.client import PositionClient
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
import uuid


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('trading_log.txt'),
        logging.StreamHandler()
    ]
)

# Alpaca API credentials
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_API_SECRET")
BASE_URL = "https://paper-api.alpaca.markets"

# Initialize REST client for market data and TradingClient for placing orders
REST_CLIENT = REST(API_KEY, SECRET_KEY, BASE_URL)
TRADING_CLIENT = TradingClient(API_KEY, SECRET_KEY, paper=True)
#POSITION_CLIENT = PositionClient(API_KEY, SECRET_KEY, paper=True)

# Configuration
#TRADING_DAYS = 5
TRADING_DAYS = int(os.getenv("TRADE_DAYS"))

CAPITAL_ALLOCATION = {
    "buy_close_sell_open": int(os.getenv("CAPITAL_ALLOCATION_BUY_CLOSE_SELL_OPEN")),
    "short_term_momentum": int(os.getenv("CAPITAL_ALLOCATION_SHORT_TERM_MOMENTUM")),
    "custom_strategy": int(os.getenv("CAPITAL_ALLOCATION_CUSTOM_STRATEGY")),
}

SYMBOLS = {
    "buy_close_sell_open": os.getenv("SYMBOL_BUY_CLOSE_SELL_OPEN"),
    "short_term_momentum": os.getenv("SYMBOL_SHORT_TERM_MOMENTUM"),
    "custom_strategy": os.getenv("SYMBOL_CUSTOM_STRATEGY"),
}


strategy_status = {strategy: False for strategy in SYMBOLS}
market_check = False
NY_TZ = pytz.timezone('America/New_York')

def is_market_open():
    """Check if the market is currently open."""
    try:
        return TRADING_CLIENT.get_clock().is_open
    except Exception as e:
        logging.error(f"Error checking market status: {e}")
        return False

def get_last_price(symbol):
    """Fetch the last trade price for the given symbol."""
    try:
        latest_trade = REST_CLIENT.get_latest_trade(symbol)
        return latest_trade.price
    except Exception as e:
        logging.error(f"Error fetching last price for {symbol}: {e}")
        return None

def submit_order(symbol, qty, side, strategy_name):
    """Submit a market order with enhanced logging."""
    try:
        order_request = MarketOrderRequest(
            
            symbol=symbol,
            qty=qty,
            side=side,
            type="market",
            time_in_force="gtc",
            client_order_id=strategy_name
        )
        order = TRADING_CLIENT.submit_order(order_request)
        logging.info(f"{strategy_name}: {side.capitalize()} order for {qty} {symbol} shares")
        return order
    except Exception as e:
        logging.error(f"Order submission error for {symbol}: {e}")
        return None

def calculate_shares(symbol, capital):
    """Calculate shares to trade based on capital."""
    price = get_last_price(symbol)
    if price is None:
        logging.warning(f"Cannot calculate shares for {symbol}")
        return 0
    return int(capital // price)

@lru_cache(maxsize=1, typed=False)
def get_market_hours():
    """Get market hours with caching to reduce API calls."""
    clock = TRADING_CLIENT.get_clock()
    return clock.is_open, clock.next_open.astimezone(NY_TZ), clock.next_close.astimezone(NY_TZ)


def buy_close_sell_open(symbol, shares):
    try:
        clock = TRADING_CLIENT.get_clock()
        now_nyc = datetime.now(pytz.timezone('America/New_York'))
        market_close = clock.next_close.astimezone(pytz.timezone('America/New_York'))
        next_market_open = clock.next_open.astimezone(pytz.timezone('America/New_York'))
        seconds_to_close = (market_close - now_nyc).total_seconds()
        seconds_to_open = (next_market_open - now_nyc).total_seconds()

        # Check if there is an open position to sell
        try:
            position = TRADING_CLIENT.get_open_position(symbol)
            current_position = int(position["qty"]) if isinstance(position, dict) else int(position.qty)
            if current_position > 0:
                has_position = True
            else:
                has_position = False
        except Exception:
            has_position = False

        # Sell at market open
        if clock.is_open and has_position:
            sell_client_order_id = f"sell_{symbol}_{uuid.uuid4().hex[:8]}"
            sell_order = submit_order(symbol, shares, OrderSide.SELL, sell_client_order_id)
            if sell_order:
                logging.info(f"Sell order placed for {symbol} at open.")
            else:
                logging.error(f"Failed to place sell order for {symbol} at open.")
        else:
            logging.warning("Market not open or no position to sell. Skipping sell order.")

        # Check if near market close to place buy order
        if seconds_to_close <= 600:
            buy_client_order_id = f"buy_{symbol}_{uuid.uuid4().hex[:8]}"
            buy_order = submit_order(symbol, shares, OrderSide.BUY, buy_client_order_id)
            if buy_order:
                logging.info(f"Buy order placed for {symbol} before market close.")
                market_check = True
                # Wait for next market open if necessary
                logging.info(f"Sleeping for {max(0, seconds_to_open)} seconds until market opens.")
                #strategy_status["buy_close_sell_open"] = True
                time.sleep(max(0, seconds_to_open - 1800))
            else:
                logging.error(f"Failed to place buy order for {symbol} before market close.")
        else:
            logging.info("Not close enough to market close. Skipping buy order.")

        strategy_status["buy_close_sell_open"] = True

    except Exception as e:
        logging.error(f"Error in buy_close_sell_open: {e}")


def short_term_momentum(symbol, shares):
    """Short-term momentum strategy."""
    try:
        if not is_market_open():
            logging.warning("Market closed. Skipping short_term_momentum.")
            return

        bars = REST_CLIENT.get_bars(symbol, TimeFrame.Minute, limit=30)
        bars = list(bars)

        if not bars:
            logging.warning(f"No bars returned for {symbol}.")
            return

        open_price = bars[0].o
        current_price = bars[-1].c

        # Check current position
        try:
            position = TRADING_CLIENT.get_open_position(symbol)
            # If the API call succeeds, process the position
            current_position = int(position["qty"]) if isinstance(position, dict) else int(position.qty)
            print(f"Current position for ALBT: {current_position}")
        except Exception as e:
            # Handle the specific "position does not exist" error
            if "position does not exist" in str(e):
                current_position = 0
                print("No position exists for ALBT.")
            else:
                # Log or handle other unexpected exceptions
                print(f"Unexpected error fetching position for ALBT: {e}")

        # Buy condition: momentum upward movement (no current long position)
        if current_price >= open_price * 1.005 and current_position <= 0:
            client_order_id = f"momentum_buy_{symbol}_{uuid.uuid4().hex[:8]}"
            buy_order = submit_order(symbol, shares, OrderSide.BUY, client_order_id)
            if buy_order:
                logging.info(f"Momentum buy order placed for {symbol}.")
                strategy_status["short_term_momentum"] = True
            else:
                logging.error(f"Failed to place buy order for {symbol}.")
        
        # Sell condition: downward momentum (close long if open)
        elif current_price <= open_price * 0.999 and current_position > 0:
            try:
                available_qty = int(position["qty"]) if isinstance(position, dict) else int(position.qty)
            except AttributeError as e:
                logging.error(f"Failed to fetch available quantity for {symbol}: {e}")
                available_qty = 0
            except Exception as e:
                logging.error(f"Unexpected error fetching available quantity for {symbol}: {e}")
                available_qty = 0

            # Determine the quantity to sell
            sell_qty = min(shares, available_qty)  # Sell only up to the available quantity

            if sell_qty > 0:  # Ensure there is a valid quantity to sell
                client_order_id = f"momentum_sell_{symbol}_{uuid.uuid4().hex[:8]}"
                sell_order = submit_order(symbol, sell_qty, OrderSide.SELL, client_order_id)
                if sell_order:
                    logging.info(f"Momentum sell order placed for {symbol}: {sell_qty} shares.")
                    strategy_status["short_term_momentum"] = True
                else:
                    logging.error(f"Failed to place sell order for {symbol}.")
            else:
                logging.warning(f"No shares available to sell for {symbol}.")
        else:
            logging.info(f"No action taken for {symbol} in short_term_momentum strategy.")

        # Clean up
        del bars

    except Exception as e:
        logging.error(f"Error in short_term_momentum: {e}")


def custom_strategy(symbol, shares):
    """Custom strategy based on time."""
    try:
        current_time = datetime.now(pytz.timezone('America/New_York'))
        current_hour = current_time.hour

        # Check if there's an open position
        try:
            position = TRADING_CLIENT.get_open_position(symbol)
            current_position = int(position["qty"]) if isinstance(position, dict) else int(position.qty)
        except Exception:
            current_position = 0

        # Morning: Enter short position if no current position
        if current_hour < 11 and current_position == 0:
            client_order_id = f"custom_sell_{symbol}_{uuid.uuid4().hex[:8]}"
            sell_order = submit_order(symbol, shares, OrderSide.SELL, client_order_id)
            if sell_order:
                logging.info(f"Custom strategy sell (short) order placed for {symbol} in the morning.")
            else:
                logging.error(f"Failed to place sell order for {symbol}.")
        
        # Afternoon: Cover short position if one exists
        elif current_hour >= 14 and current_position <0:
            client_order_id = f"custom_buy_{symbol}_{uuid.uuid4().hex[:8]}"
            buy_order = submit_order(symbol, shares, OrderSide.BUY, client_order_id)
            if buy_order:
                logging.info(f"Custom strategy buy (cover) order placed for {symbol} in the afternoon.")
                #strategy_status["custom_strategy"] = True
            else:
                logging.error(f"Failed to place buy order for {symbol}.")
        else:
            logging.info(f"No action taken for {symbol}. Hour: {current_hour}, Has position: {current_position}")
        
        strategy_status["custom_strategy"] = True

    except Exception as e:
        logging.error(f"Error in custom_strategy: {e}")


def main():
    global strategy_status, market_check
    logging.info("Trading system started")
    end_time = datetime.now(pytz.timezone('America/New_York')) + timedelta(days=TRADING_DAYS)

    while datetime.now(pytz.timezone('America/New_York')) < end_time:
        # Fetch market hours
        is_open, next_open, next_close = get_market_hours()

        # If the market is open, execute the strategies every minute
        if is_open:
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = []

                # Schedule strategies
                futures.append(executor.submit(buy_close_sell_open, SYMBOLS["buy_close_sell_open"], calculate_shares(SYMBOLS["buy_close_sell_open"], CAPITAL_ALLOCATION["buy_close_sell_open"])))
                futures.append(executor.submit(short_term_momentum, SYMBOLS["short_term_momentum"], calculate_shares(SYMBOLS["short_term_momentum"], CAPITAL_ALLOCATION["short_term_momentum"])))
                futures.append(executor.submit(custom_strategy, SYMBOLS["custom_strategy"], calculate_shares(SYMBOLS["custom_strategy"], CAPITAL_ALLOCATION["custom_strategy"])))

                # Wait for each strategy to complete
                for future in futures:
                    try:
                        future.result()
                    except Exception as e:
                        logging.error(f"Error executing strategy: {e}")

            # Log consolidated strategy status
            logging.info(f"Strategy Status: {strategy_status}")

        else:
            logging.warning("Market is closed. Waiting...")

            # Recheck market status
            is_open, _, _ = get_market_hours()
            if is_open:
                logging.info("Market just opened! Resuming execution.")
                continue
            else:
                logging.info("Market still closed. Rechecking;....")
                time.sleep(600)

        # Control loop frequency
        time.sleep(60)


if __name__ == "__main__":
    main()
