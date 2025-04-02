import time
import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import datetime
import os
import pytz

# Streamlit app title
st.title("📈 Live Stock Analytics Dashboard")

# API Endpoints
API_BASE_URL = "http://api:8000"
SYMBOLS_URL = f"{API_BASE_URL}/symbols"
DAILY_DATA_URL = f"{API_BASE_URL}/bar"
REALTIME_DATA_URL = f"{API_BASE_URL}/latest_bar"
EXECUTION_REPORT_URL = f"{API_BASE_URL}/trade-data"

# New York Time Zone
ny_tz = pytz.timezone('America/New_York')

# Helper function to convert UTC timestamps to New York Time
def convert_to_ny_timezone(utc_timestamp):
    """
    Converts UTC timestamp string to New York Time (Eastern Time).
    Assumes the UTC timestamp is in ISO 8601 format ('YYYY-MM-DDTHH:MM:SS.ssssssZ').
    """
    # Convert UTC timestamp string to datetime object
    utc_time = datetime.datetime.strptime(utc_timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
    
    # Localize to UTC and convert to New York Time
    utc_time = pytz.utc.localize(utc_time)
    ny_time = utc_time.astimezone(ny_tz)
    
    return ny_time

# Get available symbols
symbols_response = requests.get(SYMBOLS_URL)
available_symbols = symbols_response.json().get("items", []) if symbols_response.status_code == 200 else []
symbol = st.selectbox("Select Stock Symbol", available_symbols)

# Set date range for historical data
HISTORICAL_DAYS = int(os.getenv("HISTORICAL_DAYS", 200))
now = datetime.datetime.utcnow()
from_date = (now - datetime.timedelta(days=HISTORICAL_DAYS)).strftime("%Y-%m-%d")
to_date = now.strftime("%Y-%m-%d")

# 📈 **1. Real-Time Price Updates (Minute-by-Minute)**
st.subheader(f"⏳ {symbol} Real-Time Updates (Today)")

# Fetch latest bar
realtime_response = requests.get(REALTIME_DATA_URL, params={"symbol": symbol})

if realtime_response.status_code == 200:
    data = realtime_response.json()
    if isinstance(data, list) and len(data) > 0:  # Check if it's a list of multiple time points
        df_realtime = pd.DataFrame(data)  # Convert full intraday data to DataFrame
        df_realtime["timestamp"] = pd.to_datetime(df_realtime["timestamp"])  # Ensure datetime format
        
        # Convert timestamps to New York time for display
        df_realtime["ny_time"] = df_realtime["timestamp"].dt.tz_convert('America/New_York')

        # Format for displaying time in "YYYY-MM-DD HH:MM:SS" format
        df_realtime["formatted_ny_time"] = df_realtime["ny_time"].dt.strftime('%Y-%m-%d %H:%M:%S')

        st.subheader(f"📈 {symbol} Intraday Price Movement (Minute-by-Minute)")
        fig_realtime = px.line(df_realtime, x="formatted_ny_time", y="close", title=f"{symbol} Intraday Price")
        st.plotly_chart(fig_realtime)
    else:
        st.warning("No intraday market data available.")
else:
    st.error("Failed to fetch real-time data.")

# 📊 **2. Fetch and Display Daily Closing Prices**
params = {"from_date": from_date, "to_date": to_date, "symbol": symbol}
response = requests.get(DAILY_DATA_URL, params=params)

if response.status_code == 200:
    data = response.json()
    if data:
        df = pd.DataFrame(data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df["date"] = df["timestamp"].dt.date  # Extract only the date

        # Convert timestamps to New York time for display
        df["ny_date"] = df["timestamp"].dt.tz_convert('America/New_York').dt.strftime('%Y-%m-%d')

        # Keep only the last entry per day (EOD price)
        df = df.groupby("ny_date").last().reset_index()

        st.subheader(f"📅 {symbol} Daily Closing Prices (Last {HISTORICAL_DAYS} Days)")
        fig = px.line(df, x="ny_date", y="close", title=f"{symbol} Daily Closing Price")
        st.plotly_chart(fig)

        # 📊 **3. Advanced Analytics**
        st.subheader("📊 Advanced Analytics")

        # Calculate Moving Averages & Volatility
        df["SMA_10"] = df["close"].rolling(window=10).mean()
        df["SMA_50"] = df["close"].rolling(window=50).mean()
        df["Volatility"] = df["close"].pct_change().rolling(window=10).std()

        # Validate available columns for Avg_Price calculation
        available_cols = [col for col in ["open", "high", "low", "close"] if col in df.columns]
        if available_cols:  # Ensure at least one valid column exists
            df["Avg_Price"] = df[available_cols].mean(axis=1)
        else:
            st.warning("No price columns available to calculate Avg_Price")

        # Plot Moving Averages
        fig_ma = px.line(df, x="ny_date", y=["close", "SMA_10", "SMA_50"], 
                        title=f"{symbol} Moving Averages", labels={"value": "Price", "variable": "Legend"})
        st.plotly_chart(fig_ma)

        # Plot Volatility
        fig_vol = px.line(df, x="ny_date", y="Volatility", title=f"{symbol} Volatility (10-day Rolling Std)")
        st.plotly_chart(fig_vol)
    else:
        st.warning("No historical data found.")
else:
    st.error("Failed to fetch daily data.")

# 📉 4. Display Order Execution & PnL
st.subheader("📉 Strategy Performance Dashboard")

# Get strategy configuration from environment
def get_strategy_config():
    config = {}
    for env_var in os.environ:
        if env_var.startswith("SYMBOL_"):
            strategy = env_var.replace("SYMBOL_", "")
            symbol = os.getenv(env_var)
            shares_var = f"SHARES_{strategy}"
            shares = int(os.getenv(shares_var, 0))
            config[strategy] = (symbol, shares)
    return config

STRATEGY_CONFIG = get_strategy_config()

@st.cache_data(ttl=60)
def fetch_execution_data():
    try:
        response = requests.get(EXECUTION_REPORT_URL, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Failed to fetch trade data: {str(e)}")
        return []

# Fetch and process data
execution_data = fetch_execution_data()

if execution_data:
    df = pd.DataFrame(execution_data)
    df['filled_at'] = pd.to_datetime(df['filled_at'])
    df['date'] = df['filled_at'].dt.date
    
    # Strategy detection based on symbol and quantity
    def detect_strategy(row):
        for strategy, (symbol, shares) in STRATEGY_CONFIG.items():
            if row['symbol'] == symbol and abs(row['last_filled_qty']) == shares:
                return strategy
        return "UNKNOWN"
    
    df['strategy'] = df.apply(detect_strategy, axis=1)
    
    # --- PnL Calculation ---
    positions = {}
    pnl_records = []
    
    for _, row in df.sort_values('filled_at').iterrows():
        if row['strategy'] == "UNKNOWN":
            continue
            
        key = (row['strategy'], row['symbol'])
        
        if row['side'] == 'BUY':
            if key not in positions:
                positions[key] = {
                    'qty': float(row['last_filled_qty']),
                    'avg_price': float(row['last_fill_price']),
                    'buy_time': row['filled_at']
                }
            else:
                total_qty = positions[key]['qty'] + float(row['last_filled_qty'])
                positions[key]['avg_price'] = (
                    (positions[key]['avg_price'] * positions[key]['qty']) + 
                    float(row['last_fill_price']) * float(row['last_filled_qty'])
                ) / total_qty
                positions[key]['qty'] = total_qty
                
        elif row['side'] == 'SELL':
            if key in positions:
                pnl = (float(row['last_fill_price']) - positions[key]['avg_price']) * float(row['last_filled_qty'])
                holding_period = (row['filled_at'] - positions[key]['buy_time']).total_seconds()/3600
                
                pnl_records.append({
                    'strategy': row['strategy'],
                    'symbol': row['symbol'],
                    'pnl': pnl,
                    'return_pct': (float(row['last_fill_price'])/positions[key]['avg_price'] - 1) * 100,
                    'holding_hours': holding_period,
                    'exit_time': row['filled_at']
                })
                
                positions[key]['qty'] -= float(row['last_filled_qty'])
                if positions[key]['qty'] <= 0:
                    del positions[key]
    
    # --- Dashboard Visualization ---
    st.sidebar.subheader("Strategy Configuration")
    for strategy, (symbol, shares) in STRATEGY_CONFIG.items():
        st.sidebar.metric(
            label=f"{strategy}",
            value=f"{symbol} ({shares} shares)"
        )
    
    if pnl_records:
        pnl_df = pd.DataFrame(pnl_records)
        
        # Strategy Summary
        st.subheader("Strategy Performance Summary")
        summary = pnl_df.groupby('strategy').agg({
            'pnl': ['sum', 'count', 'mean'],
            'return_pct': 'mean',
            'holding_hours': 'mean'
        }).reset_index()
        
        summary.columns = ['Strategy', 'Total PnL', 'Trades', 'Avg PnL', 'Avg Return %', 'Avg Holding Hours']
        st.dataframe(
            summary.style
            .format({
                'Total PnL': '${:.2f}',
                'Avg PnL': '${:.2f}',
                'Avg Return %': '{:.2f}%',
                'Avg Holding Hours': '{:.1f}'
            })
            .bar(color='#5fba7d')
        )
        
        # Detailed Trade View
        st.subheader("Trade Execution Details")
        st.dataframe(df[['strategy', 'symbol', 'side', 'last_filled_qty', 'last_fill_price', 'filled_at']])
        
        # Time Series Chart
        st.subheader("PnL Over Time")
        cumulative_pnl = pnl_df.groupby(['exit_time', 'strategy'])['pnl'].sum().unstack().cumsum()
        st.line_chart(cumulative_pnl.fillna(method='ffill'))
        
        # Current Positions
        if positions:
            st.subheader("Current Open Positions")
            positions_df = pd.DataFrame([
                {
                    'Strategy': k[0],
                    'Symbol': k[1],
                    'Quantity': v['qty'],
                    'Avg Price': v['avg_price'],
                    'Held Since': v['buy_time'],
                    'Current PnL': (df[df['symbol'] == k[1]]['last_fill_price'].iloc[-1] - v['avg_price']) * v['qty'] 
                                   if not df[df['symbol'] == k[1]].empty else 0
                }
                for k, v in positions.items()
            ])
            st.dataframe(positions_df.style.format({
                'Current PnL': '${:.2f}',
                'Avg Price': '${:.2f}'
            }))
    else:
        st.warning("No completed trades found for PnL calculation.")
else:
    st.warning("No trade execution data available.")

# Auto-refresh 
st.rerun()