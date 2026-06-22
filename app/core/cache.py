import time
from typing import Any, Dict, Optional

class ContextCache:
    """In-memory TTL cache for Context objects."""
    
    def __init__(self, ttl_seconds: int = 300):
        self.ttl_seconds = ttl_seconds
        self._cache: Dict[str, dict] = {}
        
    def get(self, key: str) -> Optional[Any]:
        """Retrieve an item from cache if it exists and has not expired."""
        if key in self._cache:
            item = self._cache[key]
            if time.time() < item["expires_at"]:
                return item["value"]
            else:
                del self._cache[key]
        return None
        
    def set(self, key: str, value: Any) -> None:
        """Store an item in the cache with the configured TTL."""
        self._cache[key] = {
            "value": value,
            "expires_at": time.time() + self.ttl_seconds
        }
        
    def invalidate(self, key: str) -> None:
        """Remove an item from the cache."""
        if key in self._cache:
            del self._cache[key]
            
    def clear(self) -> None:
        """Clear all cached items."""
        self._cache.clear()

# Global cache instance
context_cache = ContextCache()
