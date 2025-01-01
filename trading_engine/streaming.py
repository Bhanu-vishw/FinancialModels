import os
import requests
import time
from datetime import datetime, timedelta
import pytz
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Timezone for consistency
NY_TZ = pytz.timezone('America/New_York')

BASE_URL = "https://paper-api.alpaca.markets/v2/orders"
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_API_SECRET")
API_URL = os.getenv("API_URL")  # Points to the FastAPI server
#API_URL = "http://127.0.0.1:8000"

HEADERS = {
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": SECRET_KEY,
}

# Track the last processed order to prevent duplicates
last_order_time = datetime.now(NY_TZ) - timedelta(days=1)
processed_order_ids = set()  # Prevent duplicate processing


def is_market_open():
    """Check if the market is currently open using FastAPI endpoint."""
    try:
        response = requests.get(f"{API_URL}/market_status/")
        response.raise_for_status()
        market_status = response.json()
        logging.info(f"Market open status: {market_status['market_open']}.")
        return market_status["market_open"]
    except requests.exceptions.RequestException as e:
        logging.error(f"Error checking market status via API: {e}")
        return False

# def fetch_order_updates():
#     """Fetch recent order updates."""
#     global last_order_time
#     try:
#         params = {"after": last_order_time.isoformat()}
#         #params = { "status": "all", "limit": 50}
#         response = requests.get(BASE_URL, headers=HEADERS, params=params)
#         response.raise_for_status()
#         orders = response.json()

#         # Update the last processed order time if new orders are found
#         if orders:
#             last_order_time = datetime.now(NY_TZ)
#         else :
#             logging.info("no orders to show from last 24 hrs")
#         return orders
    
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error fetching orders: {e}")
#         if hasattr(e, 'response') and e.response is not None:
#             logging.error(f"Response content: {e.response.content}")
#         return []

# def post_trade_update(order):
#     """Post trade updates to the database via FastAPI."""
#     try:
#         data = {
#             "strategy": order["client_order_id"],
#             "symbol": order["symbol"],
#             "action": order["side"],
#             "price": float(order["filled_avg_price"]),
#             "quantity": int(order["filled_qty"]),
#             "timestamp": datetime.fromisoformat(order["filled_at"]).astimezone(NY_TZ).isoformat(),
#         }
#         logging.info(f"Posting trade update: {data}")
#         response = requests.post(f"{API_URL}/trades/", json=data)
#         response.raise_for_status()
#         logging.info(f"Trade update posted for {order['symbol']}: {order['side']} {order['filled_qty']} shares at {order['filled_avg_price']}")
#     except requests.exceptions.RequestException as e:
#         logging.error(f"Error posting trade update: {e}")
#         if hasattr(e, 'response') and e.response is not None:
#             logging.error(f"Response content: {e.response.content}")


def stream_events():
    """Poll for order updates and stream them."""
    last_market_check = datetime.now(NY_TZ) - timedelta(minutes=1)  # To control market checks
    market_open = False

    while True:
        # Periodically refresh market status (every 1 minute)
        if datetime.now(NY_TZ) - last_market_check >= timedelta(minutes=1):
            market_open = is_market_open()
            last_market_check = datetime.now(NY_TZ)

        # if market_open:
        #     orders = fetch_order_updates()
        #     for order in orders:
        #         if order["status"] == "filled" and order["id"] not in processed_order_ids:
        #             post_trade_update(order)
        #             processed_order_ids.add(order["id"])  # Mark the order as processed
        else:
            logging.info("Market is closed. Waiting for market to open...")

        # Adaptive sleep: Check more frequently when market is about to open
        sleep_duration = 3600 if not market_open else 60
        time.sleep(sleep_duration)

if __name__ == "__main__":
    stream_events()


