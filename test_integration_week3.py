# ✅ ФАЙЛ 10

**Название:** `test_integration_week3.py`

```python
"""
Integration tests for Week 3-4 modules:
- API Gateway
- Result Aggregation Engine
- Redis Caching Layer

Coverage: 60%+
License: MIT
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from middleware import (
    APIKey,
    APIKeyManager,
    StandardResponse,
    RateLimiter,
    APIGateway,
    CORSMiddleware,
    ErrorHandler,
)

from engine import (
    AggregatedRecord,
    DataDeduplicator,
    TimestampNormalizer,
    ResultAggregator,
    DataSource,
)

from redis_cache import (
    CacheConfig,
    InMemoryCache,
    RedisCache,
    CacheManager,
)


# ==================== GATEWAY TESTS ====================

class TestAPIKey:
    """Test API Key management."""
    
    def test_api_key_creation(self):
        """Test creating API key."""
        key = APIKey("test_key_12345", "Test Key", rate_limit=100)
        
        assert key.key == "test_key_12345"
        assert key.name == "Test Key"
        assert key.rate_limit == 100
        assert key.request_count == 0
    
    def test_api_key_usage_update(self):
        """Test updating key usage."""
        key = APIKey("test_key", "Test", 100)
        
        assert key.request_count == 0
        key.update_usage()
        assert key.request_count == 1
        assert key.last_used is not None


class TestAPIKeyManager:
    """Test API Key Manager."""
    
    def test_create_key(self):
        """Test creating new key."""
        manager = APIKeyManager()
        
        key = manager.create_key("Test Key", rate_limit=50)
        
        assert key.startswith("sk_")
        assert len(key) > 10
    
    def test_validate_key(self):
        """Test validating key."""
        manager = APIKeyManager()
        
        key = manager.create_key("Test Key")
        api_key = manager.validate_key(key)
        
        assert api_key is not None
        assert api_key.name == "Test Key"
    
    def test_validate_invalid_key(self):
        """Test validating invalid key."""
        manager = APIKeyManager()
        
        api_key = manager.validate_key("invalid_key_xyz")
        
        assert api_key is None
    
    def test_revoke_key(self):
        """Test revoking key."""
        manager = APIKeyManager()
        
        key = manager.create_key("Test Key")
        revoked = manager.revoke_key(key)
        
        assert revoked is True
        assert manager.validate_key(key) is None
    
    def test_get_key_info(self):
        """Test getting key info."""
        manager = APIKeyManager()
        
        key = manager.create_key("Test Key", rate_limit=100)
        info = manager.get_key_info(key)
        
        assert info is not None
        assert info["name"] == "Test Key"
        assert info["rate_limit"] == 100


class TestStandardResponse:
    """Test standard response formatting."""
    
    def test_success_response(self):
        """Test success response."""
        response = StandardResponse.success(
            data={"result": "ok"},
            status_code=200,
            message="Success"
        )
        
        assert response["status"] == "success"
        assert response["code"] == 200
        assert response["data"] == {"result": "ok"}
        assert "timestamp" in response
        assert "request_id" in response
    
    def test_error_response(self):
        """Test error response."""
        response = StandardResponse.error(
            error_type="validation_error",
            message="Invalid input",
            status_code=400,
            details={"field": "email", "reason": "invalid"}
        )
        
        assert response["status"] == "error"
        assert response["code"] == 400
        assert response["error_type"] == "validation_error"
        assert response["details"]["field"] == "email"


class TestRateLimiter:
    """Test rate limiting."""
    
    def test_within_limit(self):
        """Test request within limit."""
        limiter = RateLimiter()
        
        assert limiter.check_limit("user1", limit=5, window=60) is True
    
    def test_exceed_limit(self):
        """Test exceeding limit."""
        limiter = RateLimiter()
        
        for _ in range(5):
            limiter.check_limit("user1", limit=5, window=60)
        
        assert limiter.check_limit("user1", limit=5, window=60) is False
    
    def test_reset_limiter(self):
        """Test resetting limiter."""
        limiter = RateLimiter()
        
        limiter.check_limit("user1", limit=1, window=60)
        limiter.reset("user1")
        
        assert limiter.check_limit("user1", limit=1, window=60) is True


class TestAPIGateway:
    """Test API Gateway."""
    
    def test_gateway_initialization(self):
        """Test gateway initialization."""
        gateway = APIGateway()
        
        assert gateway.key_manager is not None
        assert gateway.rate_limiter is not None
        assert isinstance(gateway.request_log, list)
    
    def test_authenticate(self):
        """Test authentication."""
        gateway = APIGateway()
        
        key = gateway.create_api_key("Test")
        api_key = gateway.authenticate(key)
        
        assert api_key is not None
    
    def test_authenticate_invalid(self):
        """Test authentication with invalid token."""
        gateway = APIGateway()
        
        api_key = gateway.authenticate("invalid_token")
        
        assert api_key is None
    
    def test_check_rate_limit(self):
        """Test rate limit check."""
        gateway = APIGateway()
        
        key = gateway.create_api_key("Test", rate_limit=5)
        api_key = gateway.authenticate(key)
        
        assert gateway.check_rate_limit(api_key) is True
    
    def test_log_request(self):
        """Test request logging."""
        gateway = APIGateway()
        
        key = gateway.create_api_key("Test")
        api_key = gateway.authenticate(key)
        
        gateway.log_request("GET", "/api/v1/test", api_key, 200, 0.1)
        
        log = gateway.get_request_log(limit=1)
        assert len(log) > 0


class TestCORSMiddleware:
    """Test CORS middleware."""
    
    def test_cors_headers_allowed_origin(self):
        """Test CORS headers for allowed origin."""
        origin = "http://localhost:3000"
        headers = CORSMiddleware.get_headers(origin)
        
        assert "Access-Control-Allow-Origin" in headers
        assert headers["Access-Control-Allow-Origin"] == origin
    
    def test_cors_headers_unknown_origin(self):
        """Test CORS headers for unknown origin."""
        headers = CORSMiddleware.get_headers("https://unknown.com")
        
        assert len(headers) == 0


class TestErrorHandler:
    """Test error handler."""
    
    def test_auth_error(self):
        """Test auth error."""
        response = ErrorHandler.handle_auth_error()
        
        assert response["status"] == "error"
        assert response["code"] == 401
    
    def test_rate_limit_error(self):
        """Test rate limit error."""
        response = ErrorHandler.handle_rate_limit_error()
        
        assert response["status"] == "error"
        assert response["code"] == 429
    
    def test_validation_error(self):
        """Test validation error."""
        details = {"field": "email", "reason": "invalid"}
        response = ErrorHandler.handle_validation_error(details)
        
        assert response["status"] == "error"
        assert response["code"] == 400


# ==================== AGGREGATION TESTS ====================

class TestAggregatedRecord:
    """Test aggregated record."""
    
    def test_record_creation(self):
        """Test creating aggregated record."""
        record = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"registrar": "VeriSign"}
        )
        
        assert record.query == "example.com"
        assert record.query_type == "domain"
        assert len(record.sources) == 0
    
    def test_add_source(self):
        """Test adding source."""
        record = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={}
        )
        
        record.add_source("whois")
        record.add_source("dns")
        
        assert "whois" in record.sources
        assert "dns" in record.sources
    
    def test_add_tag(self):
        """Test adding tag."""
        record = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={}
        )
        
        record.add_tag("domain")
        record.add_tag("whois")
        
        assert "domain" in record.tags
        assert "whois" in record.tags


class TestDataDeduplicator:
    """Test data deduplication."""
    
    def test_duplicate_detection(self):
        """Test detecting duplicates."""
        dedup = DataDeduplicator()
        
        record1 = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"registrar": "VeriSign"}
        )
        
        dedup.add_record("example.com", record1)
        
        assert dedup.is_duplicate("example.com", record1) is True
    
    def test_different_data(self):
        """Test detecting different data."""
        dedup = DataDeduplicator()
        
        record1 = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"registrar": "VeriSign"}
        )
        
        record2 = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"registrar": "Registry.com"}
        )
        
        dedup.add_record("example.com", record1)
        
        assert dedup.is_duplicate("example.com", record2) is False


class TestTimestampNormalizer:
    """Test timestamp normalization."""
    
    def test_normalize_iso_string(self):
        """Test normalizing ISO string."""
        ts = "2020-01-15T10:30:45Z"
        
        normalized = TimestampNormalizer.normalize(ts)
        
        assert "2020-01-15" in normalized
    
    def test_normalize_datetime(self):
        """Test normalizing datetime object."""
        dt = datetime(2020, 1, 15, 10, 30, 45)
        
        normalized = TimestampNormalizer.normalize(dt)
        
        assert "2020-01-15" in normalized
    
    def test_normalize_unix_timestamp(self):
        """Test normalizing Unix timestamp."""
        unix_ts = 1579612245
        
        normalized = TimestampNormalizer.normalize(unix_ts)
        
        assert "2020-01" in normalized


class TestResultAggregator:
    """Test result aggregation."""
    
    def test_aggregate_whois(self):
        """Test aggregating WHOIS results."""
        aggregator = ResultAggregator()
        
        whois_data = {
            "registrar": "VeriSign",
            "created_date": "1995-08-14",
            "expiration_date": "2025-08-14",
            "nameservers": ["ns1.example.com", "ns2.example.com"],
        }
        
        record = aggregator.aggregate_whois_results("example.com", whois_data)
        
        assert record is not None
        assert record.query == "example.com"
        assert "whois" in record.sources
    
    def test_aggregate_dns(self):
        """Test aggregating DNS results."""
        aggregator = ResultAggregator()
        
        dns_data = {
            "A": [{"value": "192.168.1.1", "ttl": 3600}],
            "MX": [{"value": "mail.example.com", "priority": 10, "ttl": 3600}],
        }
        
        record = aggregator.aggregate_dns_results("example.com", dns_data)
        
        assert record is not None
        assert "dns" in record.sources
        assert "192.168.1.1" in record.data["a_records"]
    
    def test_add_record(self):
        """Test adding record."""
        aggregator = ResultAggregator()
        
        record = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"test": "data"}
        )
        
        added = aggregator.add_record("example.com", record)
        
        assert added is True
        assert len(aggregator.records["example.com"]) == 1
    
    def test_merge_records(self):
        """Test merging multiple records."""
        aggregator = ResultAggregator()
        
        record1 = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"registrar": "VeriSign"}
        )
        record1.add_source("whois")
        
        record2 = AggregatedRecord(
            query="example.com",
            query_type="domain",
            data={"a_record": "192.168.1.1"}
        )
        record2.add_source("dns")
        
        aggregator.add_record("example.com", record1)
        aggregator.add_record("example.com", record2)
        
        merged = aggregator.merge_records("example.com")
        
        assert merged is not None
        assert "whois" in merged["sources"]
        assert "dns" in merged["sources"]


# ==================== CACHE TESTS ====================

class TestInMemoryCache:
    """Test in-memory cache."""
    
    def test_set_and_get(self):
        """Test setting and getting value."""
        cache = InMemoryCache()
        
        cache.set("key1", "value1", 3600)
        result = cache.get("key1")
        
        assert result == "value1"
    
    def test_get_nonexistent(self):
        """Test getting non-existent key."""
        cache = InMemoryCache()
        
        result = cache.get("nonexistent")
        
        assert result is None
    
    def test_delete(self):
        """Test deleting key."""
        cache = InMemoryCache()
        
        cache.set("key1", "value1", 3600)
        cache.delete("key1")
        result = cache.get("key1")
        
        assert result is None


class TestRedisCache:
    """Test Redis cache."""
    
    def test_fallback_initialization(self):
        """Test initialization with fallback."""
        cache = RedisCache(
            host="localhost",
            port=6379,
            use_fallback=True
        )
        
        assert cache.fallback_cache is not None
    
    def test_set_and_get(self):
        """Test set and get with fallback."""
        cache = RedisCache(use_fallback=True)
        
        cache.set("key1", {"data": "value"}, 3600)
        result = cache.get("key1")
        
        assert result is not None
        assert result["data"] == "value"
    
    def test_stats(self):
        """Test cache statistics."""
        cache = RedisCache(use_fallback=True)
        
        stats = cache.get_stats()
        
        assert "hits" in stats
        assert "misses" in stats
        assert "sets" in stats


class TestCacheManager:
    """Test cache manager."""
    
    def test_cache_whois(self):
        """Test caching WHOIS data."""
        cache = RedisCache(use_fallback=True)
        manager = CacheManager(cache)
        
        whois_data = {"registrar": "VeriSign"}
        manager.cache_whois("example.com", whois_data)
        
        cached = manager.get_whois("example.com")
        
        assert cached["registrar"] == "VeriSign"
    
    def test_cache_dns(self):
        """Test caching DNS data."""
        cache = RedisCache(use_fallback=True)
        manager = CacheManager(cache)
        
        dns_data = {"a_records": ["192.168.1.1"]}
        manager.cache_dns("example.com", dns_data)
        
        cached = manager.get_dns("example.com")
        
        assert "192.168.1.1" in cached["a_records"]
    
    def test_cache_verification(self):
        """Test caching verification data."""
        cache = RedisCache(use_fallback=True)
        manager = CacheManager(cache)
        
        verify_data = {"valid": True, "score": 0.95}
        manager.cache_verification("test@example.com", verify_data)
        
        cached = manager.get_verification("test@example.com")
        
        assert cached["valid"] is True


# ==================== FIXTURES ====================

@pytest.fixture
def api_key_manager():
    """Fixture for API key manager."""
    return APIKeyManager()


@pytest.fixture
def result_aggregator():
    """Fixture for result aggregator."""
    return ResultAggregator()


@pytest.fixture
def cache_manager():
    """Fixture for cache manager."""
    cache = RedisCache(use_fallback=True)
    return CacheManager(cache)


@pytest.fixture
def api_gateway():
    """Fixture for API gateway."""
    return APIGateway()
