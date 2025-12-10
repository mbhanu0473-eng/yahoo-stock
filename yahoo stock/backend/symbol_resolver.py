"""
Symbol resolver: Maps user input (ticker or name) to normalized stock symbols.
Supports 40+ stocks including US and Indian stocks, plus major indices.
"""

ASSET_MAPPING = {
    # US Stocks - Technology
    "apple": "AAPL",
    "aapl": "AAPL",
    "microsoft": "MSFT",
    "msft": "MSFT",
    "google": "GOOGL",
    "googl": "GOOGL",
    "nvidia": "NVDA",
    "nvda": "NVDA",
    "meta": "META",
    "facebook": "META",
    "tesla": "TSLA",
    "tsla": "TSLA",
    
    # US Stocks - Finance & Retail
    "amazon": "AMZN",
    "amzn": "AMZN",
    "berkshire": "BRK.B",
    "brk.b": "BRK.B",
    "jpmorgan": "JPM",
    "jpm": "JPM",
    "goldman": "GS",
    "gs": "GS",
    "bank of america": "BAC",
    "bac": "BAC",
    "wells fargo": "WFC",
    "wfc": "WFC",
    "walmart": "WMT",
    "wmt": "WMT",
    
    # US Stocks - Healthcare & Pharma
    "johnson": "JNJ",
    "jnj": "JNJ",
    "pfizer": "PFE",
    "pfe": "PFE",
    "moderna": "MRNA",
    "mrna": "MRNA",
    "eli lilly": "LLY",
    "lly": "LLY",
    "abbvie": "ABBV",
    "abbv": "ABBV",
    
    # US Stocks - Energy & Industrial
    "exxon": "XOM",
    "xom": "XOM",
    "chevron": "CVX",
    "cvx": "CVX",
    "general electric": "GE",
    "ge": "GE",
    "caterpillar": "CAT",
    "cat": "CAT",
    
    # Indian Stocks - IT
    "tata consultancy": "TCS.NS",
    "tcs": "TCS.NS",
    "infosys": "INFY.NS",
    "infy": "INFY.NS",
    "wipro": "WIPRO.NS",
    "hcl": "HCLTECH.NS",
    
    # Indian Stocks - Finance & Banking
    "reliance": "RELIANCE.NS",
    "hdfc bank": "HDFCBANK.NS",
    "hdfcbank": "HDFCBANK.NS",
    "icici bank": "ICICIBANK.NS",
    "icicibank": "ICICIBANK.NS",
    "axis bank": "AXISBANK.NS",
    "axisbank": "AXISBANK.NS",
    "sbi": "SBIN.NS",
    
    # Indian Stocks - Other
    "tatasteel": "TATASTEEL.NS",
    "maruti": "MARUTI.NS",
    "sunpharma": "SUNPHARMA.NS",
    "ongc": "ONGC.NS",
    
    # Major Indices
    "nifty": "^NSEI",
    "nifty 50": "^NSEI",
    "nse": "^NSEI",
    "sensex": "^BSESN",
    "bse": "^BSESN",
    "nasdaq": "^IXIC",
    "sp500": "^GSPC",
    "s&p 500": "^GSPC",
    "dow": "^DJI",
    "dow jones": "^DJI",
}


def resolve_symbol(user_input: str) -> dict:
    """
    Resolve user input to a stock symbol.
    
    Strategy:
    1. Try exact match in ASSET_MAPPING
    2. Try partial match
    3. Assume input is a ticker symbol
    
    Returns dict with: symbol, name, type, confidence
    """
    user_input = user_input.strip().lower()
    
    # Try direct exact match
    if user_input in ASSET_MAPPING:
        symbol = ASSET_MAPPING[user_input]
        return {
            "symbol": symbol,
            "name": user_input.title(),
            "type": _get_asset_type(symbol),
            "confidence": "high",
        }
    
    # Try partial match (for multi-word inputs like "gold price")
    for key, symbol in ASSET_MAPPING.items():
        if key in user_input or user_input in key:
            return {
                "symbol": symbol,
                "name": key.title(),
                "type": _get_asset_type(symbol),
                "confidence": "medium",
            }
    
    # Assume it's a ticker symbol (AAPL, ^NSEI, etc)
    if user_input and not any(c.isspace() for c in user_input):
        return {
            "symbol": user_input.upper(),
            "name": user_input.upper(),
            "type": "unknown",
            "confidence": "low",
        }
    
    # Fallback
    return {
        "symbol": user_input.upper(),
        "name": user_input,
        "type": "unknown",
        "confidence": "low",
    }


def _get_asset_type(symbol: str) -> str:
    """Determine asset type from symbol format."""
    if symbol.endswith("=F"):
        return "commodity"
    elif symbol.startswith("^"):
        return "index"
    elif symbol.endswith((".NS", ".BO")):
        return "stock_india"
    elif symbol.endswith("=X"):
        return "currency"
    else:
        return "stock"


def extract_symbols_from_query(query: str) -> list:
    """
    Extract asset symbols from natural language query.
    Splits by spaces and resolves each token.
    
    Example: "Compare gold vs silver" -> [GC=F, SI=F]
    """
    tokens = query.lower().split()
    found_symbols = []
    
    for token in tokens:
        # Clean punctuation
        token = token.strip(",.;:")
        
        # Try to resolve each token
        result = resolve_symbol(token)
        if result["confidence"] in ("high", "medium"):
            # Avoid duplicates
            if result["symbol"] not in [s["symbol"] for s in found_symbols]:
                found_symbols.append(result)
    
    return found_symbols
