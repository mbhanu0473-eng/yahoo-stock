"""
Utilities module for stock market operations.
Provides helper functions for data validation, formatting, and market info.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import re


def load_market_config() -> Dict:
    """Load market configuration from market_config.json."""
    config_path = Path(__file__).parent / "market_config.json"
    if config_path.exists():
        with open(config_path, "r") as f:
            return json.load(f)
    return {}


def get_all_stocks() -> List[Dict]:
    """Get all stocks from market config."""
    config = load_market_config()
    all_stocks = []
    
    for market_key, market in config.get("markets", {}).items():
        for stock in market.get("stocks", []):
            all_stocks.append(stock)
    
    return all_stocks


def get_all_indices() -> List[Dict]:
    """Get all indices from market config."""
    config = load_market_config()
    all_indices = []
    
    for market_key, market in config.get("markets", {}).items():
        for idx in market.get("indices", []):
            all_indices.append(idx)
    
    return all_indices


def get_all_commodities() -> List[Dict]:
    """Get all commodities from market config."""
    config = load_market_config()
    commodities = config.get("markets", {}).get("commodities", {}).get("commodities", [])
    return commodities


def get_stock_by_symbol(symbol: str) -> Optional[Dict]:
    """Find stock by symbol in market config."""
    symbol_upper = symbol.upper()
    for stock in get_all_stocks():
        if stock.get("symbol", "").upper() == symbol_upper:
            return stock
    return None


def get_index_by_symbol(symbol: str) -> Optional[Dict]:
    """Find index by symbol in market config."""
    for idx in get_all_indices():
        if idx.get("symbol", "").upper() == symbol.upper():
            return idx
    return None


def get_commodity_by_symbol(symbol: str) -> Optional[Dict]:
    """Find commodity by symbol in market config."""
    for commodity in get_all_commodities():
        if commodity.get("symbol", "").upper() == symbol.upper():
            return commodity
    return None


def format_currency(value: float, decimals: int = 2) -> str:
    """Format value as currency string."""
    return f"${value:,.{decimals}f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage string."""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.{decimals}f}%"


def get_market_type(symbol: str) -> str:
    """Determine market type from symbol."""
    symbol_upper = symbol.upper()
    
    # Check if it's an index
    if symbol_upper.startswith("^"):
        return "index"
    
    # Check if it's a commodity
    if any(c in symbol_upper for c in ["=F", "=X"]):
        return "commodity"
    
    # Check if it's Indian stock
    if symbol_upper.endswith((".NS", ".BO")):
        return "stock_india"
    
    # Default to US stock
    return "stock_us"


def validate_symbol(symbol: str) -> Tuple[bool, str]:
    """
    Validate if a symbol is in correct format.
    Returns (is_valid, message)
    """
    if not symbol or not isinstance(symbol, str):
        return False, "Symbol must be a non-empty string"
    
    symbol = symbol.strip()
    if len(symbol) > 10:
        return False, "Symbol too long (max 10 characters)"
    
    # Allow alphanumeric, dots, hyphens, equals, and caret
    if not re.match(r"^[A-Z0-9\.\-\=\^]+$", symbol.upper()):
        return False, "Symbol contains invalid characters"
    
    return True, "Valid symbol"


def get_market_status() -> Dict:
    """Get market status and info."""
    return {
        "us_market": "NASDAQ, NYSE",
        "india_market": "NSE, BSE",
        "commodities": "NYMEX, ICE",
        "trading_days": "Monday-Friday (with holidays)",
        "last_updated": "real-time via yfinance"
    }


def search_stocks(query: str) -> List[Dict]:
    """Search stocks by name or symbol."""
    query_lower = query.lower()
    results = []
    
    for stock in get_all_stocks():
        if (query_lower in stock.get("symbol", "").lower() or
            query_lower in stock.get("name", "").lower() or
            query_lower in stock.get("sector", "").lower() or
            query_lower in stock.get("industry", "").lower()):
            results.append(stock)
    
    return results[:10]  # Return top 10 results


def search_indices(query: str) -> List[Dict]:
    """Search indices by name or symbol."""
    query_lower = query.lower()
    results = []
    
    for idx in get_all_indices():
        if (query_lower in idx.get("symbol", "").lower() or
            query_lower in idx.get("name", "").lower() or
            query_lower in idx.get("description", "").lower()):
            results.append(idx)
    
    return results


def search_commodities(query: str) -> List[Dict]:
    """Search commodities by name or symbol."""
    query_lower = query.lower()
    results = []
    
    for commodity in get_all_commodities():
        if (query_lower in commodity.get("symbol", "").lower() or
            query_lower in commodity.get("name", "").lower() or
            query_lower in commodity.get("type", "").lower()):
            results.append(commodity)
    
    return results


def get_market_stats() -> Dict:
    """Return market statistics and metadata."""
    stocks = get_all_stocks()
    indices = get_all_indices()
    commodities = get_all_commodities()
    
    return {
        "total_stocks": len(stocks),
        "total_indices": len(indices),
        "total_commodities": len(commodities),
        "markets": {
            "us": len([s for s in stocks if s.get("symbol", "").isupper() and not s.get("symbol", "").endswith((".NS", ".BO"))]),
            "india": len([s for s in stocks if s.get("symbol", "").endswith((".NS", ".BO"))]),
        },
        "timestamp": "dynamic"
    }
