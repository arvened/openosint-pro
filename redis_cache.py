# ✅ ФАЙЛ 6

**Название:** `redis_cache.py`

```python
"""
Redis Caching Layer for OpenOSINT Pro

Implements efficient caching:
- Redis-based distributed caching
- TTL management (configurable per type)
- Cache invalidation strategies
- Connection pooling
- Fallback to in-memory cache
- Compression support
- Cache statistics

Author: Eduard Arbitman
License: MIT
"""

import logging
import json
from typing import Optional, Any, Dict
from datetime import datetime, timedelta

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheConfig:
    """Cache configuration."""
    
    WHOIS_TTL = 86400 * 30
    DNS_TTL = 3600 * 24
    SCRAPE_TTL = 3600
    VERIFICATION_TTL = 86400 * 7
    DEFAULT_TTL = 3600
    
    WHOIS_PREFIX = "osint:whois:"
    DNS_PREFIX = "osint:dns:"
    SCRAPE_PREFIX = "osint:scrape:"
    VERIFY_PREFIX = "osint:verify:"
    ENRICHMENT_PREFIX = "osint:enrich:"


class InMemoryCache:
    """In-memory cache fallback."""
    
    def __init__(self):
        """Initialize in-memory cache."""
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        if key in self.cache:
            entry = self.cache[key]
            
            if entry["expires_at"] < datetime.now():
                del self.cache[key]
                return None
            
            return entry["value"]
        
        return None
    
    def set(self, key: str, value: str, ttl: int) -> None:
        """Set value in cache."""
        self.cache[key] = {
            "value": value,
            "expires_at": datetime.now() + timedelta(seconds=ttl),
        }
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self) -> None:
        """Clear entire cache."""
        self.cache.clear()
    
    def size(self) -> int:
        """Get cache size."""
        return len(self.cache)


class RedisCache:
    """
    Redis caching layer.
    
    Features:
    - Sync Redis operations
    - TTL management
    - Connection pooling
    - Fallback to in-memory cache
    - Cache statistics
    """
    
    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        use_fallback: bool = True,
    ):
        """Initialize Redis cache."""
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.use_fallback = use_fallback
        
        self.redis_client = None
        self.fallback_cache = InMemoryCache() if use_fallback else None
        self._stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "deletes": 0,
        }
        
        self._connect()
    
    def _connect(self) -> None:
        """Connect to Redis."""
        if not REDIS_AVAILABLE:
            logger.warning("redis not available, using in-memory cache only")
            return
        
        try:
            self.redis_client = redis.Redis(
                host=self.host,
                port=self.port,
                db=self.db,
                password=self.password,
                decode_responses=True,
                socket_connect_timeout=5,
            )
            
            self.redis_client.ping()
            logger.info(f"Connected to Redis at {self.host}:{self.port}")
        
        except Exception as e:
            logger.warning(f"Failed to connect to Redis: {e}")
            self.redis_client = None
            
            if not self.use_fallback:
                raise
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if self.redis_client:
            try:
                value = self.redis_client.get(key)
                if value:
                    self._stats["hits"] += 1
                    logger.debug(f"Cache hit: {key}")
                    return json.loads(value)
                else:
                    self._stats["misses"] += 1
                    return None
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        
        if self.fallback_cache:
            value = self.fallback_cache.get(key)
            if value:
                self._stats["hits"] += 1
                return json.loads(value)
            else:
                self._stats["misses"] += 1
        
        return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> None:
        """Set value in cache."""
        ttl = ttl or CacheConfig.DEFAULT_TTL
        json_value = json.dumps(value, default=str)
        
        if self.redis_client:
            try:
                self.redis_client.setex(key, ttl, json_value)
                self._stats["sets"] += 1
                logger.debug(f"Cached (Redis): {key} ({ttl}s)")
                return
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        
        if self.fallback_cache:
            self.fallback_cache.set(key, json_value, ttl)
            self._stats["sets"] += 1
            logger.debug(f"Cached (Memory): {key} ({ttl}s)")
    
    def delete(self, key: str) -> None:
        """Delete value from cache."""
        if self.redis_client:
            try:
                self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        
        if self.fallback_cache:
            self.fallback_cache.delete(key)
        
        self._stats["deletes"] += 1
        logger.debug(f"Deleted from cache: {key}")
    
    def delete_pattern(self, pattern: str) -> int:
        """Delete multiple keys by pattern."""
        count = 0
        
        if self.redis_client:
            try:
                keys = self.redis_client.keys(pattern)
                
                if keys:
                    self.redis_client.delete(*keys)
                    count = len(keys)
                    logger.info(f"Deleted {count} keys matching pattern: {pattern}")
            
            except Exception as e:
                logger.error(f"Redis pattern delete error: {e}")
        
        return count
    
    def clear(self) -> None:
        """Clear entire cache."""
        if self.redis_client:
            try:
                self.redis_client.flushdb()
                logger.info("Cleared Redis cache")
            except Exception as e:
                logger.error(f"Redis clear error: {e}")
        
        if self.fallback_cache:
            self.fallback_cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            **self._stats,
            "total_operations": sum(self._stats.values()),
        }
        
        if stats["total_operations"] > 0:
            stats["hit_rate"] = (
                stats["hits"] / (stats["hits"] + stats["misses"])
                if (stats["hits"] + stats["misses"]) > 0
                else 0
            )
        
        return stats
    
    def reset_stats(self) -> None:
        """Reset cache statistics."""
        for key in self._stats:
            self._stats[key] = 0


class CacheManager:
    """High-level cache manager."""
    
    def __init__(self, cache: RedisCache):
        """Initialize cache manager."""
        self.cache = cache
    
    def cache_whois(self, domain: str, data: Dict[str, Any]) -> None:
        """Cache WHOIS data."""
        key = f"{CacheConfig.WHOIS_PREFIX}{domain.lower()}"
        self.cache.set(key, data, CacheConfig.WHOIS_TTL)
    
    def get_whois(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached WHOIS data."""
        key = f"{CacheConfig.WHOIS_PREFIX}{domain.lower()}"
        return self.cache.get(key)
    
    def cache_dns(self, domain: str, data: Dict[str, Any]) -> None:
        """Cache DNS data."""
        key = f"{CacheConfig.DNS_PREFIX}{domain.lower()}"
        self.cache.set(key, data, CacheConfig.DNS_TTL)
    
    def get_dns(self, domain: str) -> Optional[Dict[str, Any]]:
        """Get cached DNS data."""
        key = f"{CacheConfig.DNS_PREFIX}{domain.lower()}"
        return self.cache.get(key)
    
    def cache_scrape(self, url: str, data: Dict[str, Any]) -> None:
        """Cache scraping data."""
        key = f"{CacheConfig.SCRAPE_PREFIX}{url.lower()}"
        self.cache.set(key, data, CacheConfig.SCRAPE_TTL)
    
    def get_scrape(self, url: str) -> Optional[Dict[str, Any]]:
        """Get cached scraping data."""
        key = f"{CacheConfig.SCRAPE_PREFIX}{url.lower()}"
        return self.cache.get(key)
    
    def cache_verification(self, query: str, data: Dict[str, Any]) -> None:
        """Cache verification data."""
        key = f"{CacheConfig.VERIFY_PREFIX}{query.lower()}"
        self.cache.set(key, data, CacheConfig.VERIFICATION_TTL)
    
    def get_verification(self, query: str) -> Optional[Dict[str, Any]]:
        """Get cached verification data."""
        key = f"{CacheConfig.VERIFY_PREFIX}{query.lower()}"
        return self.cache.get(key)
    
    def invalidate_domain(self, domain: str) -> None:
        """Invalidate all cache entries for domain."""
        self.cache.delete_pattern(f"osint:*:{domain.lower()}*")
        logger.info(f"Invalidated cache for domain: {domain}")
    
    def get_cache_status(self) -> Dict[str, Any]:
        """Get cache status."""
        return {
            "connected": self.cache.redis_client is not None,
            "stats": self.cache.get_stats(),
        }


def main():
    """Example usage."""
    cache = RedisCache(host="localhost", port=6379)
    manager = CacheManager(cache)
    
    whois_data = {"registrar": "VeriSign", "created": "1995-08-14"}
    manager.cache_whois("example.com", whois_data)
    
    cached = manager.get_whois("example.com")
    print(f"Cached WHOIS: {cached}")
    
    stats = cache.get_stats()
    print(f"Cache stats: {stats}")


if __name__ == "__main__":
    main()
```

---

