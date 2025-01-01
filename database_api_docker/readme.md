# Building a Containerized Market Data System

## **Overview**

### **Objectives**
1. **Create a Market Data System**:
   - Build a database for market data storage.
   - Implement a scraper service to populate the database with market data from Alpaca’s API.
   - Develop an API for querying the data efficiently.

2. **Containerize Services**:
   - Use Docker and its Compose plugin to manage services as background processes.
   - Ensure seamless interaction between services.

3. **Learn Key Tools**:
   - **QuestDB** for high-performance time-series data storage.
   - **FastAPI** for developing a RESTful API.
   - **Docker** for container orchestration.

### **Why Create Your Own Market Data Database?**
Maintaining a local market data database has several advantages:
- **Organization**: Normalize data across sources and consolidate it in one place.
- **Speed**: Querying data locally is faster than over the internet.
- **Cost-Effectiveness**: Collect free or affordable granular data over time, avoiding high costs for long histories.
