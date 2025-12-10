# Stock Market Yahoo Finance API - Complete Backend

## Overview
This is a comprehensive FastAPI backend for fetching real-time and historical stock market data from Yahoo Finance. It supports US stocks, Indian stocks, indices, commodities, and includes intelligent caching.

## Features
✅ **Real-time Stock Data** - Fetch live prices, OHLCV data  
✅ **Historical Data** - Daily, weekly, monthly price history  
✅ **Multi-Market Support** - US (NASDAQ, NYSE), India (NSE, BSE), Commodities  
✅ **Smart Caching** - 15-minute TTL to reduce API calls  
✅ **Technical Indicators** - SMA, volatility, trend detection  
✅ **Market Metadata** - 40+ stocks, 6+ indices, 7+ commodities  
✅ **CORS Enabled** - Cross-origin requests from frontend  
✅ **Comprehensive Search** - Search stocks, indices, commodities  

## API Endpoints

### Core Endpoints

#### 1. **Health Check**
```
GET /health
```
**Response:**
```json
{"status": "ok"}
```

---

#### 2. **Search Asset**
```
GET /assets/search?q=apple
```
**Query Parameters:**
- `q` (required): Ticker symbol or company name

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple",
  "type": "stock",
  "confidence": "high"
}
```

---

#### 3. **Get Historical Data**
```
GET /assets/history?symbol=AAPL&period=3mo&interval=1d
```
**Query Parameters:**
- `symbol` (required): Ticker symbol (e.g., "AAPL", "TCS.NS", "^NSEI")
- `period` (optional): "1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "max" (default: "1y")
- `interval` (optional): "1m", "5m", "15m", "30m", "60m", "1d", "1wk", "1mo" (default: "1d")

**Response:**
```json
{
  "symbol": "AAPL",
  "name": "Apple Inc.",
  "data": [
    {
      "date": "2025-09-10",
      "open": 231.97,
      "high": 232.19,
      "low": 225.73,
      "close": 226.57,
      "volume": 83440800
    }
  ],
  "current_price": 277.18,
  "change_pct": 22.34,
  "high_52w": 288.62,
  "low_52w": 168.63,
  "currency": "USD",
  "metadata": {
    "description": "",
    "sector": "Technology",
    "industry": "Consumer Electronics"
  }
}
```

---

### Market Data Endpoints

#### 4. **Get All Stocks**
```
GET /stocks
```
**Response:**
```json
[
  {
    "symbol": "AAPL",
    "name": "Apple Inc.",
    "sector": "Technology",
    "industry": "Consumer Electronics"
  }
]
```

---

#### 5. **Get All Indices**
```
GET /indices
```
**Response:**
```json
{
  "indices": [
    {
      "symbol": "^GSPC",
      "name": "S&P 500",
      "description": "Large-cap US stocks"
    }
  ]
}
```

---

#### 6. **Get All Commodities**
```
GET /commodities
```
**Response:**
```json
{
  "commodities": [
    {
      "symbol": "GC=F",
      "name": "Gold Futures",
      "type": "Metal"
    }
  ]
}
```

---

#### 7. **Search Across All Markets**
```
GET /search?q=gold
```
**Query Parameters:**
- `q` (required): Search term

**Response:**
```json
{
  "stocks": [],
  "indices": [],
  "commodities": [
    {
      "symbol": "GC=F",
      "name": "Gold Futures",
      "type": "Metal"
    }
  ],
  "total_results": 1
}
```

---

#### 8. **Get Market Statistics**
```
GET /market/stats
```
**Response:**
```json
{
  "total_stocks": 20,
  "total_indices": 5,
  "total_commodities": 7,
  "markets": {
    "us": 10,
    "india": 10
  },
  "timestamp": "dynamic"
}
```

---

#### 9. **Get Market Status**
```
GET /market/status
```
**Response:**
```json
{
  "us_market": "NASDAQ, NYSE",
  "india_market": "NSE, BSE",
  "commodities": "NYMEX, ICE",
  "trading_days": "Monday-Friday (with holidays)",
  "last_updated": "real-time via yfinance"
}
```

---

### Cache Management

#### 10. **Get Cache Statistics**
```
GET /cache/stats
```
**Response:**
```json
{
  "total_entries": 5,
  "ttl_minutes": 15
}
```

---

#### 11. **Clear Cache**
```
POST /cache/clear
```
**Response:**
```json
{"message": "Cache cleared successfully"}
```

---

## Example Usage

### Fetch Apple Stock Data
```bash
curl "http://localhost:5000/assets/history?symbol=AAPL&period=3mo&interval=1d"
```

### Search for Gold Commodity
```bash
curl "http://localhost:5000/search?q=gold"
```

### Get Indian Stocks
```bash
curl "http://localhost:5000/stocks" | grep -i "NS"
```

### Get S&P 500 Data
```bash
curl "http://localhost:5000/assets/history?symbol=%5EGSPC&period=1mo&interval=1d"
```

---

## Supported Symbols

### US Stocks
- **Tech:** AAPL, MSFT, GOOGL, NVDA, META
- **Finance:** JPM, V, BAC, GS
- **Healthcare:** JNJ, PFE, LLY
- **Energy:** XOM, CVX
- **Retail:** AMZN, WMT

### Indian Stocks
- **IT:** TCS.NS, INFY.NS, WIPRO.NS, HCLTECH.NS
- **Finance:** HDFCBANK.NS, ICICIBANK.NS, AXISBANK.NS, SBIN.NS
- **Energy:** RELIANCE.NS
- **Auto:** MARUTI.NS
- **Pharma:** SUNPHARMA.NS, ABBV.NS

### US Indices
- `^GSPC` - S&P 500
- `^DJI` - Dow Jones Industrial Average
- `^IXIC` - NASDAQ Composite

### Indian Indices
- `^NSEI` - NIFTY 50
- `^BSESN` - BSE Sensex

### Commodities
- `GC=F` - Gold Futures
- `SI=F` - Silver Futures
- `CL=F` - Crude Oil (WTI)
- `BZ=F` - Brent Crude Oil
- `NG=F` - Natural Gas Futures
- `ZW=F` - Wheat Futures
- `ZC=F` - Corn Futures

---

## Installation & Running

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
Create a `.env` file:
```
BACKEND_HOST=127.0.0.1
BACKEND_PORT=5000
FRONTEND_URL=http://localhost:3001
```

### 3. Run the Backend
```bash
python -m uvicorn backend.main:app --host 127.0.0.1 --port 5000
```

### 4. Access API Documentation
- **Swagger UI:** http://localhost:5000/docs
- **ReDoc:** http://localhost:5000/redoc

---

## Performance Optimization

### Caching Strategy
- **TTL:** 15 minutes (configurable in `market_config.json`)
- **Key Format:** `{symbol}_{period}_{interval}`
- **Storage:** In-memory (fast, suitable for production with multiple instances using Redis)

### Best Practices
1. Use `/cache/stats` to monitor cache usage
2. Call `/cache/clear` before major data refreshes
3. Cache individual symbol requests, not bulk searches
4. For real-time data, use shorter interval parameters

---

## Error Handling

### Common Errors

**404 - Symbol Not Found**
```json
{"detail": "No data found for symbol: INVALID"}
```

**400 - Invalid Query**
```json
{"detail": "Symbol must be a non-empty string"}
```

**500 - Server Error**
Check backend logs for yfinance API errors or network issues.

---

## Architecture

### Files
- `main.py` - FastAPI application & endpoints
- `data_fetch.py` - Yahoo Finance data retrieval
- `symbol_resolver.py` - Symbol normalization & resolution
- `cache.py` - In-memory caching with TTL
- `utils.py` - Market metadata, search, formatting
- `market_config.json` - Market data configuration

### Data Flow
```
Frontend Request
    ↓
/assets/search or /assets/history
    ↓
Check Cache (15-min TTL)
    ↓
If cached → Return immediately
If expired → Fetch from yfinance
    ↓
Cache Result → Return to Frontend
```

---

## Dependencies
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **yfinance** - Yahoo Finance API wrapper
- **pandas** - Data manipulation
- **pydantic** - Data validation
- **python-dotenv** - Environment variables

---

## Frontend Integration

The frontend (`frontend/index.html`) expects:
- **Backend URL:** `http://localhost:5000`
- **CORS:** Enabled for `http://localhost:3001`

### API Calls from Frontend
```javascript
const BACKEND_URL = 'http://localhost:5000';

// Search endpoint
fetch(`${BACKEND_URL}/assets/search?q=apple`)

// History endpoint
fetch(`${BACKEND_URL}/assets/history?symbol=AAPL&period=3mo&interval=1d`)

// List all stocks
fetch(`${BACKEND_URL}/stocks`)

// Search all markets
fetch(`${BACKEND_URL}/search?q=gold`)
```

---

## Future Enhancements
- [ ] Redis caching for distributed systems
- [ ] Real-time WebSocket updates
- [ ] Historical price comparisons
- [ ] Portfolio tracking
- [ ] Watchlist management
- [ ] Email alerts
- [ ] Technical analysis indicators (RSI, MACD, etc.)
- [ ] Multi-currency support
- [ ] Database persistence (PostgreSQL/MongoDB)

---

## License
MIT

## Support
For issues, refer to `HOW_TO_RUN.md` or check backend logs.
