import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import os

MAX_DAYS = int(os.getenv("MAX_DAYS", "200")) # Equal to lookback_days defined in json

# Streamlit app title
st.title("📈 Stock Analytics Dashboard")

API_BASE_URL = "http://api:8000"
SYMBOLS_URL = f"{API_BASE_URL}/symbols"
DATA_URL = f"{API_BASE_URL}/daily_bar"

# Fetch available symbols for dropdown
symbols_response = requests.get(SYMBOLS_URL)
available_symbols = symbols_response.json().get("items", []) if symbols_response.status_code == 200 else []
available_symbols.insert(0, "All")  # Add "All" for multiple stock graphs

# Rolling window selection
today = datetime.date.today()
start_limit = today - datetime.timedelta(days=MAX_DAYS)
from_date = st.date_input("Start Date", min_value=start_limit, max_value=today, value=start_limit)
to_date = st.date_input("End Date", min_value=from_date, max_value=today, value=today)

# Dropdown for symbol selection
symbol = st.selectbox("Select Stock Symbol", available_symbols)

# Fetch data when button is clicked
if st.button("Fetch Data"):
    params = {"from_date": from_date, "to_date": to_date}
    if symbol != "All":
        params["symbol"] = symbol
    
    response = requests.get(DATA_URL, params=params)

    if response.status_code == 200:
        data = response.json()
        if data:
            df = pd.DataFrame(data)
            df["timestamp"] = pd.to_datetime(df["timestamp"]).dt.date
            df = df.sort_values(by="timestamp")

            if symbol == "All":
                st.subheader("📈 Stock Price Trends for Multiple Stocks")
                fig_multi = px.line(df, x="timestamp", y="close", color="symbol", title="Stock Price Trends")
                st.plotly_chart(fig_multi)

                # Correlation Matrix
                st.subheader("📌 Correlation Matrix Between Stocks")
                pivot_table = df.pivot_table(index="timestamp", columns="symbol", values="close")
                fig_corr, ax = plt.subplots()
                sns.heatmap(pivot_table.corr(), annot=True, cmap="coolwarm", ax=ax)
                st.pyplot(fig_corr)
            else:
                st.subheader(f"Analysis for {symbol}")
                st.dataframe(df)

                # Summary Statistics
                st.subheader("📊 Summary Statistics")
                st.metric("Latest Closing Price", f"${df['close'].iloc[-1]:.2f}")
                st.metric("Highest Closing Price", f"${df['close'].max():.2f}")
                st.metric("Lowest Closing Price", f"${df['close'].min():.2f}")
                st.metric("Average Closing Price", f"${df['close'].mean():.2f}")
                st.metric("Total Volume Traded", f"{df['volume'].sum():,.0f}")

                # Stock Price with Moving Averages
                st.subheader("📈 Stock Price with Moving Averages")
                df["MA_10"] = df["close"].rolling(window=10).mean()
                df["MA_50"] = df["close"].rolling(window=50).mean()
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["timestamp"], y=df["close"], mode='lines', name='Close Price'))
                fig.add_trace(go.Scatter(x=df["timestamp"], y=df["MA_10"], mode='lines', name='10-Day MA'))
                fig.add_trace(go.Scatter(x=df["timestamp"], y=df["MA_50"], mode='lines', name='50-Day MA'))
                st.plotly_chart(fig)

                # Volatility Analysis
                st.subheader("📉 Volatility Analysis")
                df["daily_return"] = df["close"].pct_change() * 100
                df["volatility"] = df["daily_return"].rolling(window=7).std()
                st.plotly_chart(px.line(df, x="timestamp", y="volatility", title="Rolling Volatility (7-day)"))

                # Cumulative Returns
                st.subheader("📈 Cumulative Returns")
                df['cumulative_return'] = (1 + df['daily_return'] / 100).cumprod()
                st.plotly_chart(px.line(df, x="timestamp", y="cumulative_return", title="Cumulative Returns"))

                # Volume vs. Price
                st.subheader("📊 Volume vs. Price")
                fig_vol_price = go.Figure()
                fig_vol_price.add_trace(go.Bar(x=df["timestamp"], y=df["volume"], name="Volume"))
                fig_vol_price.add_trace(go.Scatter(x=df["timestamp"], y=df["close"], name="Closing Price", yaxis='y2'))
                fig_vol_price.update_layout(yaxis2=dict(overlaying='y', side='right'))
                st.plotly_chart(fig_vol_price)

                # RSI Calculation
                st.subheader("📊 RSI (Relative Strength Index)")
                df['change'] = df['close'].diff()
                df['gain'] = df['change'].apply(lambda x: x if x > 0 else 0)
                df['loss'] = df['change'].apply(lambda x: -x if x < 0 else 0)
                df['avg_gain'] = df['gain'].rolling(window=14).mean()
                df['avg_loss'] = df['loss'].rolling(window=14).mean()
                df['rs'] = df['avg_gain'] / df['avg_loss']
                df['rsi'] = 100 - (100 / (1 + df['rs']))
                st.plotly_chart(px.line(df, x="timestamp", y="rsi", title="RSI Indicator"))
        else:
            st.warning("No data found for the selected date range.")
    else:
        st.error("Failed to fetch data. Check FastAPI server.")
