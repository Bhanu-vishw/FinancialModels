import logging
import pytz
import os
import uuid
from datetime import datetime, timedelta
from alpaca.trading.enums import OrderSide
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("logs/trading_log.txt"),
        logging.StreamHandler(),
    ],
)

# Load strategy parameters from environment variables
ORB_WINDOW = int(os.getenv("ORB_WINDOW", 15))  # Opening range in minutes
ORB_BREAKOUT_PCT = float(os.getenv("ORB_BREAKOUT_PCT", 0.003))  # 0.3% breakout
ORB_STOP_LOSS_PCT = float(os.getenv("ORB_STOP_LOSS_PCT", 0.005))  # 0.5% stop loss
ORB_TARGET_PCT = float(os.getenv("ORB_TARGET_PCT", 0.01))  # 1% profit target

MOMENTUM_WINDOW = int(os.getenv("MOMENTUM_WINDOW", 10))  # Default: 10 minutes
MOMENTUM_THRESHOLD = float(os.getenv("MOMENTUM_THRESHOLD", 0.005))  # Default: 0.5%
STOP_LOSS_PCT = float(os.getenv("STOP_LOSS_PCT", 0.003))  # Default: 0.3%

NY_TZ = pytz.timezone("America/New_York")
strategy_status = {}

class TradingStrategies:
    def __init__(self, trading_client, rest_client, submit_order, get_last_price):
        self.trading_client = trading_client
        self.rest_client = rest_client
        self.submit_order = submit_order
        self.get_last_price = get_last_price

    # def buy_close_sell_open(self, symbol, shares):
    #     """Executes a buy at close and sells at open strategy."""
    #     try:
    #         clock = self.trading_client.get_clock()
    #         now_nyc = datetime.now(NY_TZ)
    #         market_close = clock.next_close.astimezone(NY_TZ)
    #         next_market_open = clock.next_open.astimezone(NY_TZ)
    #         seconds_to_close = (market_close - now_nyc).total_seconds()
    #         seconds_to_open = (next_market_open - now_nyc).total_seconds()

    #         # Check for open position
    #         try:
    #             position = self.trading_client.get_open_position(symbol)
    #             has_position = int(position.qty) > 0
    #         except Exception:
    #             has_position = False

    #         # Sell at market open
    #         if clock.is_open and has_position:
    #             sell_order = self.submit_order(symbol, shares, OrderSide.SELL, f"sell_{symbol}_{uuid.uuid4().hex[:8]}")
    #             if sell_order:
    #                 logging.info(f"Buy Close Sell: Sell order placed for {symbol} at open.")
    #             else:
    #                 logging.error(f"Failed to place sell order for {symbol} at open.")
    #         else:
    #             logging.warning("Buy Close Sell: Market not open or no position to sell. Skipping sell order.")

    #         # Buy before market close
    #         if seconds_to_close <= 600:
    #             buy_order = self.submit_order(symbol, shares, OrderSide.BUY, f"buy_{symbol}_{uuid.uuid4().hex[:8]}")
    #             if buy_order:
    #                 logging.info(f"Buy Close Sell: Buy order placed for {symbol} before market close.")
    #                 # time.sleep(max(0, seconds_to_open - 1800))
    #             else:
    #                 logging.error(f"Failed to place buy order for {symbol}.")
    #         else:
    #             logging.info("Buy Close Sell: Not close enough to market close. Skipping buy order.")

    #         strategy_status["buy_close_sell_open"] = True

    #     except Exception as e:
    #         logging.error(f"Error in buy_close_sell_open: {e}")

    def buy_close_sell_open(self, symbol, shares):
        """Executes a buy at close and sells at open strategy."""
        try:
            clock = self.trading_client.get_clock()
            now_nyc = datetime.now(NY_TZ)
            market_close = clock.next_close.astimezone(NY_TZ)
            next_market_open = clock.next_open.astimezone(NY_TZ)
            seconds_to_close = (market_close - now_nyc).total_seconds()
            seconds_to_open = (next_market_open - now_nyc).total_seconds()

            # Check if the market is already closed
            if seconds_to_close < 0:
                logging.warning(f"Market already closed. Cannot buy at close for {symbol}.")
                return

            # Check for open position before selling
            has_position = False
            try:
                position = self.trading_client.get_open_position(symbol)
                has_position = float(position.qty) > 0
            except Exception as e:
                logging.info(f"No open position for {symbol} (or API error: {e})")

            # Sell at market open
            if has_position and seconds_to_open <= 600:
                sell_order = self.submit_order(
                    symbol, shares, OrderSide.SELL, f"sell_{symbol}_{uuid.uuid4().hex[:8]}"
                )
                if sell_order:
                    logging.info(f"Sell order placed for {symbol} at open.")
                else:
                    logging.error(f"Failed to place sell order for {symbol} at open.")
            else:
                logging.info("Market not open yet or no position to sell. Skipping sell order.")

            # Buy before market close
            if seconds_to_close <= 600 and seconds_to_close > 0:
                buy_order = self.submit_order(
                    symbol, shares, OrderSide.BUY, f"buy_{symbol}_{uuid.uuid4().hex[:8]}"
                )
                if buy_order:
                    logging.info(f"Buy order placed for {symbol} before market close.")
                else:
                    logging.error(f"Failed to place buy order for {symbol}.")
            else:
                logging.info("Not within 10 minutes of market close. Skipping buy order.")

            strategy_status["buy_close_sell_open"] = True

        except Exception:
            logging.error(f"Error in buy_close_sell_open strategy for {symbol}")

    # def short_term_momentum(self, symbol, shares):
    #     """Executes a short-term momentum strategy."""
    #     try:
    #         # bars = self.rest_client.get_stock_bars(symbol, "minute", limit=30)
    #         # bars = list(bars)
    #         bar_request = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Minute)

    #         bars = self.rest_client.get_stock_bars(bar_request).df
    #         if symbol not in bars.index:
    #             logging.warning(f"No data for {symbol}. Skipping strategy.")
    #             return

    #         bars = bars.loc[symbol].tail(30)

    #         if bars.empty:
    #             logging.warning(f"No bars returned for {symbol}.")
    #             return

    #         open_price = bars.iloc[0]["open"]
    #         current_price = bars.iloc[-1]["close"]

    #         try:
    #             position = self.trading_client.get_open_position(symbol)
    #             current_position = int(position.qty)
    #         except Exception:
    #             logging.warning(f"Momentum: No open position for {symbol}. Defaulting to 0.")
    #             current_position = 0

    #         # Buy condition
    #         if current_price >= open_price * 1.005 and current_position <= 0:
    #             buy_order = self.submit_order(symbol, shares, OrderSide.BUY, f"momentum_buy_{symbol}_{uuid.uuid4().hex[:8]}")
    #             if buy_order:
    #                 logging.info(f"Momentum buy order placed for {symbol}.")
    #             else:
    #                 logging.error(f"Failed to place buy order for {symbol}.")

    #         # Sell condition
    #         elif current_price <= open_price * 0.999 and current_position > 0:
    #             sell_order = self.submit_order(symbol, min(shares, current_position), OrderSide.SELL, f"momentum_sell_{symbol}_{uuid.uuid4().hex[:8]}")
    #             if sell_order:
    #                 logging.info(f"Momentum sell order placed for {symbol}.")
    #             else:
    #                 logging.error(f"Failed to place sell order for {symbol}.")

    #         strategy_status["short_term_momentum"] = True

    #     except Exception as e:
    #         logging.error(f"Error in short_term_momentum: {e}")

    def short_term_momentum(self, symbol, shares):
        """Executes a short-term momentum strategy using environment variables for configuration."""
        try:
            # Fetch latest stock bars
            bar_request = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Minute)
            bars = self.rest_client.get_stock_bars(bar_request).df
            
            if symbol not in bars.index:
                logging.warning(f"Momentum: No data for {symbol}. Skipping strategy.")
                return

            # Select the last `MOMENTUM_WINDOW` minutes
            bars = bars.loc[symbol].tail(MOMENTUM_WINDOW)

            if bars.empty:
                logging.warning(f"Momentum: No bars returned for {symbol}.")
                return

            open_price = bars.iloc[0]["open"]
            current_price = bars.iloc[-1]["close"]

            try:
                position = self.trading_client.get_open_position(symbol)
                current_position = int(position.qty)
            except Exception:
                logging.warning(f"Momentum: No open position for {symbol}. Defaulting to 0.")
                current_position = 0

            # Buy condition (price up by `MOMENTUM_THRESHOLD` %)
            if current_price >= open_price * (1 + MOMENTUM_THRESHOLD) and current_position <= 0:
                buy_order = self.submit_order(symbol, shares, OrderSide.BUY, f"momentum_buy_{symbol}_{uuid.uuid4().hex[:8]}")
                if buy_order:
                    logging.info(f"Momentum: Buy order placed for {symbol} at {current_price}.")
                else:
                    logging.error(f"Momentum: Failed to place buy order for {symbol}.")

            # Sell condition (stop-loss OR price drop by `MOMENTUM_THRESHOLD` %)
            elif (current_price <= open_price * (1 - MOMENTUM_THRESHOLD) and current_position > 0) or \
                (current_price <= open_price * (1 - STOP_LOSS_PCT) and current_position > 0):
                sell_order = self.submit_order(symbol, min(shares, current_position), OrderSide.SELL, f"momentum_sell_{symbol}_{uuid.uuid4().hex[:8]}")
                if sell_order:
                    logging.info(f"Momentum: Sell order placed for {symbol} at {current_price}.")
                else:
                    logging.error(f"Momentum: Failed to place sell order for {symbol}.")

            # Short selling condition (if price drops below `MOMENTUM_THRESHOLD` %)
            elif current_price <= open_price * (1 - MOMENTUM_THRESHOLD) and current_position >= 0:
                short_sell_order = self.submit_order(symbol, shares, OrderSide.SELL, f"momentum_short_{symbol}_{uuid.uuid4().hex[:8]}")
                if short_sell_order:
                    logging.info(f"Momentum: Short sell order placed for {symbol} at {current_price}.")
                else:
                    logging.error(f"Momentum: Failed to place short sell order for {symbol}.")

            # Cover short position (if price rebounds above threshold)
            elif current_price >= open_price * (1 + MOMENTUM_THRESHOLD) and current_position < 0:
                cover_order = self.submit_order(symbol, abs(current_position), OrderSide.BUY, f"momentum_cover_{symbol}_{uuid.uuid4().hex[:8]}")
                if cover_order:
                    logging.info(f"Momentum: Cover short position for {symbol} at {current_price}.")
                else:
                    logging.error(f"Momentum: Failed to cover short position for {symbol}.")

            strategy_status["short_term_momentum"] = True

        except Exception as e:
            logging.error(f"Error in short_term_momentum: {e}")

    def opening_range_breakout(self, symbol, shares):
        """Executes the Opening Range Breakout (ORB) strategy."""
        try:
            now_nyc = datetime.now(NY_TZ)
            market_open = datetime(now_nyc.year, now_nyc.month, now_nyc.day, 9, 30, tzinfo=NY_TZ)

            # Ensure we are within the ORB window
            if now_nyc < market_open + timedelta(minutes=ORB_WINDOW):
                logging.info(f"ORB: Still within the opening range for {symbol}. Waiting.")
                return

            # Fetch stock bars for the ORB window
            bar_request = StockBarsRequest(symbol_or_symbols=[symbol], timeframe=TimeFrame.Minute)
            bars = self.rest_client.get_stock_bars(bar_request).df

            if symbol not in bars.index:
                logging.warning(f"ORB: No data for {symbol}. Skipping strategy.")
                return

            # Select the opening range
            bars = bars.loc[symbol].between_time("09:30", f"09:{30 + ORB_WINDOW}")

            if bars.empty:
                logging.warning(f"ORB: No bars returned for {symbol}.")
                return

            # Calculate ORB high & low
            orb_high = bars["high"].max()
            orb_low = bars["low"].min()
            current_price = bars.iloc[-1]["close"]

            try:
                position = self.trading_client.get_open_position(symbol)
                current_position = int(position.qty)
            except Exception:
                current_position = 0

            # Buy Condition: Breakout above ORB High
            if current_price >= orb_high * (1 + ORB_BREAKOUT_PCT) and current_position <= 0:
                buy_order = self.submit_order(symbol, shares, OrderSide.BUY, f"orb_buy_{symbol}_{uuid.uuid4().hex[:8]}")
                if buy_order:
                    logging.info(f"ORB: Buy order placed for {symbol} at {current_price}.")
                else:
                    logging.error(f"ORB: Failed to place buy order for {symbol}.")

            # Sell Condition: Drop below ORB Low
            elif current_price <= orb_low * (1 - ORB_BREAKOUT_PCT) and current_position >= 0:
                sell_order = self.submit_order(symbol, shares, OrderSide.SELL, f"orb_sell_{symbol}_{uuid.uuid4().hex[:8]}")
                if sell_order:
                    logging.info(f"ORB: Sell order placed for {symbol} at {current_price}.")
                else:
                    logging.error(f"ORB: Failed to place sell order for {symbol}.")

            # Stop Loss: If price drops below stop loss threshold
            elif current_position > 0 and current_price <= orb_high * (1 - ORB_STOP_LOSS_PCT):
                stop_loss_order = self.submit_order(symbol, shares, OrderSide.SELL, f"orb_stop_loss_{symbol}_{uuid.uuid4().hex[:8]}")
                if stop_loss_order:
                    logging.info(f"ORB: Stop-loss triggered for {symbol} at {current_price}.")
                else:
                    logging.error(f"ORB: Failed to execute stop-loss for {symbol}.")

            # Profit Target: If price reaches target
            elif current_position > 0 and current_price >= orb_high * (1 + ORB_TARGET_PCT):
                target_sell_order = self.submit_order(symbol, shares, OrderSide.SELL, f"orb_target_sell_{symbol}_{uuid.uuid4().hex[:8]}")
                if target_sell_order:
                    logging.info(f"ORB: Profit target hit for {symbol} at {current_price}.")
                else:
                    logging.error(f"ORB: Failed to take profit for {symbol}.")

            strategy_status["opening_range_breakout"] = True

        except Exception as e:
            logging.error(f"Error in ORB strategy: {e}")
