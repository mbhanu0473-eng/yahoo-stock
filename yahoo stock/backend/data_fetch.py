"""
Data fetch module: Fetch historical data from Yahoo Finance using yfinance.
Provides OHLCV data, technical indicators, and 52-week metrics.
"""

import yfinance as yf
from datetime import datetime, timedelta
from typing import Optional, Dict, List
import pandas as pd


def fetch_historical_data(
    symbol: str,
    period: str = "1y",
    interval: str = "1d",
) -> Optional[Dict]:
    """
    Fetch historical OHLCV data for a symbol from Yahoo Finance.
    
    Args:
        symbol: Stock/commodity ticker (e.g., "AAPL", "GC=F", "^NSEI")
        period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y')
        interval: Data interval ('1m', '5m', '15m', '30m', '60m', '1d', '1wk', '1mo')
    
    Returns:
        Dict with: symbol, name, data, current_price, change_pct, high_52w, low_52w, currency, metadata
        Returns None if no data found
    """
    try:
        # Fetch data from Yahoo Finance
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return None
        
        # Get additional info (company name, sector, etc)
        try:
            info = ticker.info
        except:
            info = {}
        
        # Convert dataframe to list of OHLCV records
        data_list = []
        for date, row in hist.iterrows():
            data_list.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(float(row["Open"]), 2),
                "high": round(float(row["High"]), 2),
                "low": round(float(row["Low"]), 2),
                "close": round(float(row["Close"]), 2),
                "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
            })
        
        # Calculate current metrics
        current_price = float(hist["Close"].iloc[-1])
        previous_price = float(hist["Close"].iloc[0])
        change_pct = ((current_price - previous_price) / previous_price * 100) if previous_price != 0 else 0
        
        # Get 52-week high/low
        year_ago = datetime.now() - timedelta(days=365)
        hist_1y = ticker.history(start=year_ago, interval="1d")
        high_52w = float(hist_1y["High"].max()) if not hist_1y.empty else current_price
        low_52w = float(hist_1y["Low"].min()) if not hist_1y.empty else current_price
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "data": data_list,
            "current_price": round(current_price, 2),
            "change_pct": round(change_pct, 2),
            "high_52w": round(high_52w, 2),
            "low_52w": round(low_52w, 2),
            "currency": info.get("currency", "USD"),
            "metadata": {
                "description": info.get("description", ""),
                "sector": info.get("sector", ""),
                "industry": info.get("industry", ""),
            }
        }
    
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None


def calculate_technical_indicators(data: List[Dict]) -> Dict:
    """
    Calculate simple technical indicators from OHLCV data.
    
    Includes: SMA (Simple Moving Averages), volatility, trend detection
    
    Args:
        data: List of OHLCV dicts
    
    Returns:
        Dict with: sma_20, sma_50, volatility, trend
    """
    if not data or len(data) < 2:
        return {}
    
    closes = [d["close"] for d in data]
    
    # Simple Moving Averages
    sma_20 = sum(closes[-20:]) / min(20, len(closes)) if len(closes) >= 20 else sum(closes) / len(closes)
    sma_50 = sum(closes[-50:]) / min(50, len(closes)) if len(closes) >= 50 else sum(closes) / len(closes)
    
    # Volatility: calculate standard deviation of returns
    returns = [(closes[i] - closes[i-1]) / closes[i-1] for i in range(1, len(closes))]
    volatility = (sum(r**2 for r in returns) / len(returns)) ** 0.5 if returns else 0
    
    # Trend: compare recent average to historical average
    recent_avg = sum(closes[-5:]) / len(closes[-5:]) if len(closes) >= 5 else closes[-1]
    earlier_avg = sum(closes[-20:]) / len(closes[-20:]) if len(closes) >= 20 else closes[0]
    trend = "uptrend" if recent_avg > earlier_avg else "downtrend"
    
    return {
        "sma_20": round(sma_20, 2),
        "sma_50": round(sma_50, 2),
        "volatility": round(volatility, 4),
        "trend": trend,
    }


def summarize_period(data: List[Dict], start_date: Optional[str] = None, end_date: Optional[str] = None) -> str:
    """
    Generate text summary of price action over a period.
    Useful for RAG pipeline context.
    
    Args:
        data: List of OHLCV dicts
        start_date: Optional filter (YYYY-MM-DD)
        end_date: Optional filter (YYYY-MM-DD)
    
    Returns:
        Text summary of price movement
    """
    if not data:
        return "No data available"
    
    # Filter by date range if specified
    filtered = data
    if start_date:
        filtered = [d for d in data if d["date"] >= start_date]
    if end_date:
        filtered = [d for d in filtered if d["date"] <= end_date]
    
    if not filtered:
        return "No data in specified period"
    
    # Calculate summary metrics
    first = filtered[0]
    last = filtered[-1]
    high = max(d["high"] for d in filtered)
    low = min(d["low"] for d in filtered)
    
    change = last["close"] - first["close"]
    change_pct = (change / first["close"] * 100) if first["close"] != 0 else 0
    
    return (
        f"Period {first['date']} to {last['date']}: "
        f"Opened at {first['close']}, closed at {last['close']} "
        f"({change_pct:+.2f}%). "
        f"Range: {low:.2f} - {high:.2f}."
    )
