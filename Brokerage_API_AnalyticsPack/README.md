# Stock Analytics Dashboard

### Overview

The Stock Analytics Dashboard is an interactive web application built with Streamlit that allows users to analyze stock market data with various visualization tools. It provides real-time updates, historical trends, correlation analysis, and key statistical insights.

### Features

✅ Stock Symbol Selection - Choose from multiple stock symbols to analyze individual or multiple stocks.

✅ Auto-Refreshing Data - The dashboard refreshes every 60 seconds to display the latest stock data.

✅ Time-Series Analysis - Visualize stock prices over time with moving averages (10-day & 50-day).

✅ Correlation Matrix - Compare multiple stocks to analyze relationships using a heatmap.

✅ Volatility Analysis - Track rolling volatility to measure market fluctuations.

✅ Cumulative Returns - Observe long-term performance of stocks using cumulative return charts.

✅ Volume vs. Price Analysis - Compare trade volume with stock price movements.

✅ RSI (Relative Strength Index) Indicator - Evaluate overbought or oversold conditions in the stock.

### Technologies Used

Python - Core programming language.

Streamlit - Web framework for building the dashboard.

FastAPI - Backend API for fetching stock data.

Pandas - Data manipulation and analysis.

Plotly - Interactive visualizations.

Matplotlib & Seaborn - Statistical plotting and correlation analysis.

Alpaca API - Fetching real-time and historical stock market data.

### Installation & Setup

#### Prerequisites

Ensure you have Python 3.8+ installed on your system.

#### Clone the Repository

https://github.com/yourusername/stock-analytics-dashboard.git
cd stock-analytics-dashboard

#### Install Dependencies

pip install -r requirements.txt

#### Run the FastAPI Backend

uvicorn api:app --host 0.0.0.0 --port 8000

#### Run the Streamlit Dashboard

streamlit run app.py

### Usage

Select a stock symbol from the dropdown menu.

Analyze the stock trends, volatility, and technical indicators.

Use the correlation matrix to compare multiple stocks.

Monitor real-time updates every 60 seconds.

Screenshots



### Contributing

Feel free to contribute by submitting a pull request or opening an issue.
