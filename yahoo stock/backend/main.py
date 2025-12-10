"""
FastAPI backend for stock market data.
Provides REST API endpoints for searching assets and fetching historical data.
Endpoints: /health, /assets/search, /assets/history
"""

import sys
from pathlib import Path

current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import os
from dotenv import load_dotenv

load_dotenv()

# Import modules with fallback for different import paths
try:
    from backend.symbol_resolver import resolve_symbol, extract_symbols_from_query
    from backend.data_fetch import fetch_historical_data, calculate_technical_indicators
    from backend.cache import market_cache
    from backend.utils import (
        get_all_stocks, get_all_indices, get_all_commodities,
        search_stocks, search_indices, search_commodities,
        get_market_stats, get_market_status, validate_symbol
    )
except ImportError:
    from symbol_resolver import resolve_symbol, extract_symbols_from_query
    from data_fetch import fetch_historical_data, calculate_technical_indicators
    from cache import market_cache
    from utils import (
        get_all_stocks, get_all_indices, get_all_commodities,
        search_stocks, search_indices, search_commodities,
        get_market_stats, get_market_status, validate_symbol
    )

# Initialize FastAPI app
app = FastAPI(
    title="Stock Market Data API",
    version="1.0.0",
    description="Fetch market data for stocks, commodities, and indices",
)

origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3001"),
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:8080",
]

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response models for type validation
class AssetSearchResponse(BaseModel):
    symbol: str
    name: str
    type: str
    confidence: str

class HistoryDataPoint(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int

class AssetHistoryResponse(BaseModel):
    symbol: str
    name: str
    data: List[HistoryDataPoint]
    current_price: float
    change_pct: float
    high_52w: float
    low_52w: float
    currency: str
    metadata: Dict


class StockInfo(BaseModel):
    symbol: str
    name: str
    sector: Optional[str] = None
    industry: Optional[str] = None


class MarketStatsResponse(BaseModel):
    total_stocks: int
    total_indices: int
    total_commodities: int
    markets: Dict
    timestamp: str

# Endpoints
@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "ok"}

@app.get("/assets/search", response_model=AssetSearchResponse)
def search_asset(q: str = Query(..., min_length=1, description="Ticker or asset name")):
    """Search for stock/commodity/index by symbol or name."""
    result = resolve_symbol(q)
    return result

@app.get("/assets/history", response_model=AssetHistoryResponse)
def get_asset_history(
    symbol: str = Query(..., description="Asset ticker"),
    period: str = Query("1y", description="Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, max)"),
    interval: str = Query("1d", description="Data interval (1m, 5m, 15m, 30m, 60m, 1d, 1wk, 1mo)"),
):
    """Get historical price data and metrics for an asset."""
    # Check cache first
    cache_key = f"{symbol}_{period}_{interval}"
    cached_data = market_cache.get(cache_key)
    if cached_data:
        return cached_data
    
    data = fetch_historical_data(symbol, period=period, interval=interval)
    
    if data is None:
        raise HTTPException(status_code=404, detail=f"No data found for symbol: {symbol}")
    
    # Cache the result
    market_cache.set(cache_key, data)
    return data


@app.get("/stocks")
def get_all_stocks_endpoint() -> List[Dict]:
    """Get list of all available stocks."""
    stocks = get_all_stocks()
    return stocks


@app.get("/indices")
def get_all_indices_endpoint() -> Dict:
    """Get list of all available indices."""
    indices = get_all_indices()
    return {"indices": indices}


@app.get("/commodities")
def get_all_commodities_endpoint() -> Dict:
    """Get list of all available commodities."""
    commodities = get_all_commodities()
    return {"commodities": commodities}


@app.get("/search")
def search_markets(
    q: str = Query(..., min_length=1, description="Search query for stocks, indices, or commodities")
) -> Dict:
    """Search across all markets (stocks, indices, commodities)."""
    stocks = search_stocks(q)
    indices = search_indices(q)
    commodities = search_commodities(q)
    
    return {
        "stocks": stocks,
        "indices": indices,
        "commodities": commodities,
        "total_results": len(stocks) + len(indices) + len(commodities)
    }


@app.get("/market/stats")
def market_stats() -> Dict:
    """Get market statistics and metadata."""
    return get_market_stats()


@app.get("/market/status")
def market_status() -> Dict:
    """Get market status information."""
    return get_market_status()


@app.get("/cache/stats")
def cache_stats() -> Dict:
    """Get cache statistics."""
    return market_cache.get_stats()


@app.post("/cache/clear")
def clear_cache() -> Dict:
    """Clear the market data cache."""
    market_cache.clear()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("BACKEND_PORT", 8000))
    
    uvicorn.run(app, host=host, port=port)
