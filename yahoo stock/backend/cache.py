"""
Cache module for stock market data.
Implements in-memory caching with TTL to avoid repeated yfinance calls.
"""

from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import json


class DataCache:
    """Simple in-memory cache with TTL."""
    
    def __init__(self, ttl_minutes: int = 15):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl_minutes = ttl_minutes
    
    def get(self, key: str) -> Optional[Dict]:
        """Retrieve value from cache if not expired."""
        if key not in self.cache:
            return None
        
        entry = self.cache[key]
        if datetime.now() > entry["expires_at"]:
            # Cache expired, remove it
            del self.cache[key]
            return None
        
        return entry["value"]
    
    def set(self, key: str, value: Dict) -> None:
        """Store value in cache with TTL."""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(minutes=self.ttl_minutes),
            "created_at": datetime.now()
        }
    
    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
    
    def cleanup_expired(self) -> None:
        """Remove all expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items()
            if datetime.now() > entry["expires_at"]
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict:
        """Return cache statistics."""
        self.cleanup_expired()
        return {
            "total_entries": len(self.cache),
            "ttl_minutes": self.ttl_minutes,
        }


# Global cache instance
market_cache = DataCache(ttl_minutes=15)
