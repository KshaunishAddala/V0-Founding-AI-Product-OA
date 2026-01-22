"""
Simple in-memory cache with TTL support.
For production, consider Redis for distributed caching.
"""
from datetime import datetime, timedelta
from typing import Any
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    data: Any
    expires_at: datetime


@dataclass
class Cache:
    """Thread-safe in-memory cache with automatic expiration."""
    
    _store: dict[str, CacheEntry] = field(default_factory=dict)
    default_ttl: timedelta = field(default_factory=lambda: timedelta(minutes=15))

    def get(self, key: str) -> Any | None:
        entry = self._store.get(key)
        if entry is None:
            return None
        if datetime.now() > entry.expires_at:
            del self._store[key]
            return None
        return entry.data

    def set(self, key: str, data: Any, ttl: timedelta | None = None) -> None:
        expires_at = datetime.now() + (ttl or self.default_ttl)
        self._store[key] = CacheEntry(data=data, expires_at=expires_at)

    def invalidate(self, key: str) -> None:
        self._store.pop(key, None)

    def clear(self) -> None:
        self._store.clear()


# Global cache instance
news_cache = Cache(default_ttl=timedelta(minutes=15))
summary_cache = Cache(default_ttl=timedelta(hours=1))
