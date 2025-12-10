"""
RAG (Retrieval-Augmented Generation) Pipeline Module.

This module implements a retrieval-augmented generation pipeline for financial analysis.
It uses mock Pinecone vector store to store historical summaries and generate AI-powered
market insights. The pipeline combines historical data, technical indicators, and 
LLM-based analysis to provide meaningful financial recommendations.
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
import hashlib

_PINECONE_STORE = {}


def initialize_pinecone():
    """Initialize the mock Pinecone vector store for storing financial documents."""
    pass


def embed_text(text: str) -> List[float]:
    """
    Convert text to a numerical embedding vector.
    
    Uses MD5 hash to generate a consistent, deterministic embedding from text.
    This mock implementation is suitable for demonstration; production systems would use
    real embedding models like sentence-transformers or OpenAI embeddings.
    
    Args:
        text: The text string to embed
        
    Returns:
        List of floats representing the text embedding (64-dimensional vector)
    """
    hash_obj = hashlib.md5(text.encode())
    hash_hex = hash_obj.hexdigest()
    return [float(ord(c)) / 255.0 for c in hash_hex[:64]]


def store_historical_summary(symbol: str, period_summary: str, date_range: tuple):
    """
    Store a historical price summary in the mock vector database.
    
    Creates a document containing the summary text and its embedding, indexed by symbol
    and date range. This allows later retrieval of relevant historical context for analysis.
    
    Args:
        symbol: Stock ticker or asset identifier (e.g., "AAPL", "GOLD")
        period_summary: Text summary of price movement during the period
        date_range: Tuple of (start_date, end_date) strings for the summary period
    """
    embedding = embed_text(period_summary)
    doc_id = f"{symbol}_{date_range[0]}_{date_range[1]}"
    
    _PINECONE_STORE[doc_id] = {
        "id": doc_id,
        "symbol": symbol,
        "text": period_summary,
        "embedding": embedding,
        "date_range": date_range,
    }


def retrieve_relevant_chunks(query: str, symbols: List[str], top_k: int = 3) -> List[Dict]:
    """
    Retrieve relevant historical summaries for the given query and symbols.
    
    Searches the vector store for documents matching the requested symbols and returns
    the top_k most relevant documents to provide context for the analysis.
    
    Args:
        query: User's analytical question (for potential future semantic search)
        symbols: List of asset symbols to retrieve summaries for
        top_k: Maximum number of documents to return (default: 3)
        
    Returns:
        List of matching document dictionaries from the vector store
    """
    query_embedding = embed_text(query)
    
    relevant_docs = [
        doc for doc in _PINECONE_STORE.values()
        if doc["symbol"] in symbols
    ]
    
    if not relevant_docs:
        return []
    
    return relevant_docs[:top_k]


def build_rag_prompt(
    user_query: str,
    symbols: List[str],
    historical_summaries: List[str],
    technical_indicators: Dict,
) -> str:
    """
    Build a comprehensive prompt for the LLM using retrieved context.
    
    Combines the user's query with historical context, technical indicators, and
    system instructions to create a prompt that guides the LLM toward generating
    relevant, user-friendly financial analysis.
    
    Args:
        user_query: The user's question about the assets
        symbols: List of assets being analyzed
        historical_summaries: Historical price movement summaries for context
        technical_indicators: Dictionary of technical metrics (SMA, volatility, etc.)
        
    Returns:
        A formatted prompt string ready for LLM processing
    """
    
    prompt = f"""You are a financial analyst AI. Answer the following user query based on the provided market data and historical context.

User Query: {user_query}

Symbols: {', '.join(symbols)}

Historical Context:
{chr(10).join(historical_summaries)}

Technical Indicators:
{technical_indicators}

Please provide:
1. A concise summary of price trends for the requested assets.
2. Comparison (if multiple assets) highlighting key differences.
3. A brief, user-friendly observation about performance or volatility.
4. A simple recommendation-style insight (e.g., "uptrend", "consolidating", etc.) WITHOUT financial advice.

Keep the response clear and informative for a retail investor."""
    
    return prompt


def call_llm_stub(prompt: str) -> str:
    """
    Generate a financial analysis response using mock LLM responses.
    
    This is a stub implementation that returns rule-based responses based on keywords
    in the prompt. In production, this would call a real LLM API (OpenAI, Anthropic, etc.)
    to generate dynamic, context-aware analysis.
    
    Args:
        prompt: The formatted prompt containing query and context
        
    Returns:
        A string containing the financial analysis response
    """
    if "apple" in prompt.lower() and "microsoft" in prompt.lower():
        return (
            "Both Apple and Microsoft are leading technology stocks with strong fundamentals. "
            "Apple focuses on consumer electronics and services, while Microsoft leads in cloud and enterprise software. "
            "Both show consistent growth with healthy profit margins. "
            "Both stocks are in an uptrend with strong institutional support."
        )
    elif "tech" in prompt.lower() or "technology" in prompt.lower():
        return (
            "Technology stocks have shown resilience with strong earnings growth. "
            "The sector benefits from cloud adoption, AI developments, and digital transformation. "
            "Recent consolidation suggests accumulation phase. Watch for earnings announcements."
        )
    elif "compare" in prompt.lower() or "vs" in prompt.lower():
        return (
            "The selected stocks show different growth profiles: "
            "Some focus on growth with higher volatility, others on stability with consistent dividends. "
            "Diversification across different sectors helps reduce portfolio risk. "
            "Consider your investment timeline and risk tolerance."
        )
    elif "india" in prompt.lower() or ".ns" in prompt.lower():
        return (
            "Indian stocks offer exposure to one of the world's fastest-growing economies. "
            "IT companies provide global exposure with lower volatility. Banking and industrial stocks benefit from domestic growth. "
            "Recent market breadth shows strong participation across sectors. "
            "Monitor rupee strength and economic indicators."
        )
    else:
        return (
            "The stock is showing mixed signals. Recent price action suggests consolidation. "
            "Watch for volume patterns and technical support levels for directional clues. "
            "Consider the company's fundamentals and earnings outlook for long-term decisions."
        )


def generate_analysis(
    user_query: str,
    symbols: List[str],
    historical_data_dict: Dict,
    technical_indicators_dict: Dict,
) -> str:
    """
    Generate comprehensive financial analysis for the requested assets.
    
    This is the main entry point for the RAG pipeline. It:
    1. Converts historical data to summaries
    2. Stores summaries in the vector database
    3. Builds an LLM prompt with retrieved context
    4. Calls the LLM (or stub) to generate analysis
    5. Returns the analysis response
    
    Args:
        user_query: The user's analytical question
        symbols: List of asset symbols to analyze
        historical_data_dict: Dictionary mapping symbols to their historical OHLCV data
        technical_indicators_dict: Dictionary of technical indicators for each symbol
        
    Returns:
        A string containing the generated financial analysis
    """
    summaries = []
    for symbol in symbols:
        if symbol in historical_data_dict:
            data = historical_data_dict[symbol]
            if data:
                first_date = data[0]["date"]
                last_date = data[-1]["date"]
                summary = f"{symbol}: From {first_date} to {last_date}, price moved from {data[0]['close']} to {data[-1]['close']}."
                summaries.append(summary)
                store_historical_summary(symbol, summary, (first_date, last_date))
    
    prompt = build_rag_prompt(
        user_query,
        symbols,
        summaries,
        technical_indicators_dict,
    )
    
    analysis = call_llm_stub(prompt)
    
    return analysis
