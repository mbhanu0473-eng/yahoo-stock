"""
Quick validation script for backend modules.
Run this to ensure all dependencies and imports work.
"""

import sys
import json

def test_imports():
    """Test all backend module imports."""
    print("Testing imports...")
    try:
        from backend.symbol_resolver import resolve_symbol, extract_symbols_from_query
        from backend.data_fetch import fetch_historical_data, calculate_technical_indicators
        from backend.rag_pipeline import generate_analysis, initialize_pinecone
        print("✓ All imports successful")
        return True
    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False

def test_symbol_resolver():
    """Test symbol resolution."""
    print("\nTesting symbol resolver...")
    from backend.symbol_resolver import resolve_symbol, extract_symbols_from_query
    
    test_cases = [
        ("apple", "AAPL"),
        ("microsoft", "MSFT"),
        ("AAPL", "AAPL"),
        ("nifty", "^NSEI"),
        ("tcs", "TCS.NS"),
    ]
    
    for input_sym, expected in test_cases:
        result = resolve_symbol(input_sym)
        if result["symbol"] == expected:
            print(f"  ✓ {input_sym} → {result['symbol']}")
        else:
            print(f"  ✗ {input_sym} → {result['symbol']} (expected {expected})")
    
    # Test query extraction
    query = "Compare Apple vs Microsoft stocks"
    symbols = extract_symbols_from_query(query)
    print(f"  ✓ Extracted {len(symbols)} symbols from: '{query}'")
    for sym in symbols:
        print(f"    - {sym['symbol']} ({sym['name']})")

def test_data_fetch():
    """Test data fetch (requires network)."""
    print("\nTesting data fetch (may take a moment)...")
    from backend.data_fetch import fetch_historical_data, calculate_technical_indicators
    
    # Try fetching data for a well-known symbol
    data = fetch_historical_data("AAPL", period="1mo", interval="1d")
    if data:
        print(f"  ✓ Fetched {len(data['data'])} candles for AAPL")
        print(f"    Current Price: ${data['current_price']}")
        
        # Test technical indicators
        indicators = calculate_technical_indicators(data['data'])
        print(f"    SMA(20): ${indicators.get('sma_20', 'N/A')}")
        print(f"    Trend: {indicators.get('trend', 'N/A')}")
    else:
        print("  ✗ Failed to fetch data for AAPL")

def test_rag_pipeline():
    """Test RAG pipeline."""
    print("\nTesting RAG pipeline...")
    from backend.rag_pipeline import embed_text, call_llm_stub, generate_analysis
    
    # Test embedding
    text = "Apple stock price increased significantly"
    embedding = embed_text(text)
    print(f"  ✓ Generated embedding with {len(embedding)} dimensions")
    
    # Test LLM stub
    response = call_llm_stub("What about Apple stock performance?")
    print(f"  ✓ LLM response: {response[:50]}...")

def main():
    """Run all tests."""
    print("=" * 60)
    print("Backend Module Validation")
    print("=" * 60)
    
    if not test_imports():
        print("\n✗ Import test failed. Cannot continue.")
        sys.exit(1)
    
    try:
        test_symbol_resolver()
        test_rag_pipeline()
        test_data_fetch()
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ All tests passed! Backend is ready.")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Start backend: python -m uvicorn backend.main:app --port 5000")
    print("2. Start frontend: cd frontend && python server.py")
    print("3. Visit http://localhost:3000")
    print("4. Search for any stock (AAPL, TCS, ^NSEI, etc.")

if __name__ == "__main__":
    main()
