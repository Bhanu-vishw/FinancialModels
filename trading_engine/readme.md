# Live Trading System

This project is focused on designing and implementing a minimally complete **live trading system**, integrating essential components such as a trading engine, a database, a trade event streaming service, and an API.
---

## **Overview**

### **Objective**
Build and run a live trading system, integrating:
1. **Trading Engine**: Executes intraday trading strategies.
2. **Database**: Stores trading data using QuestDB.
3. **Trade Event Streaming Service**: Tracks and posts trade updates.
4. **API**: Facilitates interaction with the database for trade management and result analysis.

### **Key Deliverables**
- **Live System Implementation**: Fully functional code for all system components.
- **Database Submission**: Export your database as a tarball file.
- **Summary Report**: Analyze results from 5 trading days in a Jupyter Notebook.

---

## **System Components**

### **1. Trading Engine**
The trading engine is the heart of the system, running intraday strategies for live trading. You will implement the following strategies:

#### **Strategies**
1. **Buy Close Sell Open**: 
   - Buy at the close of a trading day and sell at the open of the next day.
2. **Short-Term Momentum**: 
   - Buy if the stock is up by more than 1% in the first 30 minutes, otherwise short it.
   - Close all positions by the end of the trading day.
3. **Custom Strategy**:
   - Design your own strategy that generates at least one trade per day.
   - Example: Use the "Moody Trader" strategy based on time-of-day trading patterns.

#### **Behavior**
- Decide whether to run all strategies in a single engine or use separate instances.
- Ensure positions and trades are tracked by strategy for P&L calculations.
- Gracefully handle shutdowns by closing open positions when receiving a SIGTERM signal.
- Configure key parameters, such as:
  - Allocated capital
  - Symbol traded
  - Number of trading days
  - Alpaca API keys
  - Quantity of shares per trade

---

### **2. Trade Event Streaming Service**
A lightweight service that listens for trade updates from the broker and posts them to the database through the API.

---

### **3. API**
The API is the only component directly interacting with the database. It provides endpoints to:
- **Add or Update Records**: Use POST functions to insert new data.
- **Retrieve Data**: Use GET functions to fetch information for analysis.

#### **Behavior**
- Use `pydantic` models for data validation.
- Initialize tables asynchronously with an `asynccontextmanager`.
- Ensure all services interact with the database solely through the API.

---

### **4. Database**
Leverage QuestDB to store trading data. All interactions with the database must occur via the API. Use the `compose.yml` file to set up QuestDB with Docker.

---
