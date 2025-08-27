# 📈 Algorithmic Trading System  

An end-to-end **algorithmic trading platform** built in Python with live trading, backtesting, and analytics.  (version4 of version14)

Description below is for the final version.

---

## 🚀 Features  

### 🔹 Live Trading Engine  
- Multiple strategies:  
  - ⚡ **Momentum (short-term)**  
  - 📉 **Mean Reversion (VWAP-based)**  
  - 📊 **Opening Range Breakout (ORB)**  
  - 🕒 **Buy-Close-Sell-Post-Close**  
  - 🔀 **SMA Crossover (new)**  
- **Pairs trading** with cointegration & z-score triggers  
- Real-time execution via **Alpaca API**  
- Automatic risk management:  
  - PnL-based exits  
  - Forced end-of-day exits  
  - Daily halt/reset logic  

---

### 🔹 Stock Selector (`selector.py`)  
- Sentiment-aware stock screening  
- Uses **Yahoo Finance + Alpaca** data  
- Selects **top 5 tickers per strategy daily**  

---

### 🔹 Backtesting Module  
- Historical data from **Alpaca** or **CSV**  
- Supports all core strategies  
- Built-in analytics:  
  - 📈 PnL charts  
  - 📊 Trade insights  
  - 📚 Combined performance reports  

---

### 🔹 Data & Logging  
- Trade executions stored in **QuestDB** (`trade_data_exec`)  
- User authentication & logging via **FastAPI + QuestDB**  

---

### 🔹 Dashboard & Alerts  
- **Streamlit dashboard** for:  
  - Live monitoring  
  - Trade analytics  
  - Strategy performance  
- Automated **email alerts** for:  
  - Hourly PnL updates  
  - Daily trade summary  

---

## 🛠️ Tech Stack  
- **Python**: pandas, NumPy, statsmodels, scikit-learn, Streamlit, FastAPI  
- **Trading API**: Alpaca  
- **Database**: QuestDB (time-series logging)  
- **Frontend**: Streamlit  
