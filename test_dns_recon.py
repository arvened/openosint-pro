# ✅ ФАЙЛ 9

**Название:** `test_dns_recon.py`

```python
"""
Tests for DNS Reconnaissance Module

Coverage: 60%+
License: MIT
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from dns_recon import DNSRecord, DNSResolver


class TestDNSRecord:
    """Test DNS record dataclass."""
    
    def test_record_creation(self):
        """Test creating DNS record."""
        record = DNSRecord(
            domain="example.com",
            record_type="A",
            value="192.168.1.1",
            ttl=3600,
        )
        
        assert record.domain == "example.com"
        assert record.record_type == "A"
        assert record.value == "192.168.1.1"
        assert record.ttl == 3600
    
    def test_record_defaults(self):
        """Test DNS record defaults."""
        record = DNSRecord(
            domain="example.com",
            record_type="A",
            value="192.168.1.1",
        )
        
        assert record.retrieved_at is not None
        assert record.priority is None
    
    def test_record_to_dict(self):
        """Test converting record to dict."""
        record = DNSRecord(
            domain="example.com",
            record_type="A",
            value="192.168.1.1",
        )
        
        data = record.to_dict()
        
        assert data["domain"] == "example.com"
        assert data["record_type"] == "A"
        assert isinstance(data, dict)


class TestDNSResolver:
    """Test DNS resolver."""
    
    def test_resolver_initialization(self):
        """Test resolver initialization."""
        resolver = DNSResolver()
        
        assert resolver.timeout == 5
        assert isinstance(resolver.cache, dict)
    
    @pytest.mark.asyncio
    async def test_resolve_a_records(self):
        """Test resolving A records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["192.168.1.1", "192.168.1.2"]
            
            result = await resolver.resolve_a("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_aaaa_records(self):
        """Test resolving AAAA records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["2001:db8::1"]
            
            result = await resolver.resolve_aaaa("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_mx_records(self):
        """Test resolving MX records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["mail.example.com"]
            
            result = await resolver.resolve_mx("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_txt_records(self):
        """Test resolving TXT records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["v=spf1 include:example.com ~all"]
            
            result = await resolver.resolve_txt("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_ns_records(self):
        """Test resolving NS records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["ns1.example.com", "ns2.example.com"]
            
            result = await resolver.resolve_ns("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_cname_records(self):
        """Test resolving CNAME records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["alias.example.com"]
            
            result = await resolver.resolve_cname("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_soa_records(self):
        """Test resolving SOA records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["ns1.example.com. admin.example.com. 2020010101"]
            
            result = await resolver.resolve_soa("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_resolve_srv_records(self):
        """Test resolving SRV records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["10 60 5060 sipserver.example.com"]
            
            result = await resolver.resolve_srv("example.com")
            
            assert isinstance(result, list)
    
    @pytest.mark.asyncio
    async def test_reverse_lookup(self):
        """Test reverse DNS lookup."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_reverse_lookup_socket') as mock_reverse:
            mock_reverse.return_value = "example.com"
            
            result = await resolver.reverse_lookup("192.168.1.1")
            
            assert result is not None
    
    @pytest.mark.asyncio
    async def test_resolve_with_cache(self):
        """Test caching of DNS results."""
        resolver = DNSResolver()
        cache_key = "example.com:A"
        
        with patch.object(resolver, '_resolve_dnspython') as mock_resolve:
            mock_resolve.return_value = ["192.168.1.1"]
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(
                    return_value=["192.168.1.1"]
                )
                
                result1 = await resolver._resolve("example.com", "A")
                result2 = await resolver._resolve("example.com", "A")
                
                assert result1 == result2
                assert cache_key in resolver.cache
    
    @pytest.mark.asyncio
    async def test_get_all_records(self):
        """Test getting all DNS records."""
        resolver = DNSResolver()
        
        with patch.object(resolver, 'resolve_a') as mock_a, \
             patch.object(resolver, 'resolve_aaaa') as mock_aaaa, \
             patch.object(resolver, 'resolve_mx') as mock_mx, \
             patch.object(resolver, 'resolve_txt') as mock_txt, \
             patch.object(resolver, 'resolve_ns') as mock_ns, \
             patch.object(resolver, 'resolve_cname') as mock_cname, \
             patch.object(resolver, 'resolve_soa') as mock_soa:
            
            mock_a.return_value = ["192.168.1.1"]
            mock_aaaa.return_value = ["2001:db8::1"]
            mock_mx.return_value = ["mail.example.com"]
            mock_txt.return_value = ["v=spf1 ~all"]
            mock_ns.return_value = ["ns1.example.com"]
            mock_cname.return_value = []
            mock_soa.return_value = []
            
            result = await resolver.get_all_records("example.com")
            
            assert "A" in result
            assert "AAAA" in result
            assert "MX" in result
    
    @pytest.mark.asyncio
    async def test_batch_query(self):
        """Test batch DNS queries."""
        resolver = DNSResolver()
        domains = ["example.com", "google.com"]
        record_types = ["A", "MX"]
        
        with patch.object(resolver, '_resolve') as mock_resolve:
            mock_resolve.return_value = ["192.168.1.1"]
            
            result = await resolver.batch_query(domains, record_types)
            
            assert isinstance(result, dict)
            assert len(result) > 0
    
    def test_clear_cache(self):
        """Test clearing cache."""
        resolver = DNSResolver()
        resolver.cache["test"] = ["value"]
        
        resolver.clear_cache()
        
        assert len(resolver.cache) == 0
    
    def test_get_cache_size(self):
        """Test getting cache size."""
        resolver = DNSResolver()
        resolver.cache["test"] = ["value"]
        
        size = resolver.get_cache_size()
        
        assert size == 1


class TestDNSResolverEdgeCases:
    """Test edge cases."""
    
    @pytest.mark.asyncio
    async def test_resolve_invalid_domain(self):
        """Test resolving invalid domain."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve_dnspython') as mock_resolve:
            mock_resolve.return_value = []
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(
                    return_value=[]
                )
                
                result = await resolver._resolve("invalid..domain", "A")
                
                assert result == []
    
    @pytest.mark.asyncio
    async def test_resolve_empty_result(self):
        """Test resolving with empty result."""
        resolver = DNSResolver()
        
        with patch.object(resolver, '_resolve_dnspython') as mock_resolve:
            mock_resolve.return_value = []
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(
                    return_value=[]
                )
                
                result = await resolver._resolve("example.com", "UNKNOWN")
                
                assert result == []
    
    @pytest.mark.asyncio
    async def test_reverse_lookup_invalid_ip(self):
        """Test reverse lookup with invalid IP."""
        resolver = DNSResolver()
        
        result = await resolver.reverse_lookup("invalid-ip")
        
        assert result is None


class TestDNSCache:
    """Test DNS caching."""
    
    def test_cache_initialization(self):
        """Test cache initialization."""
        resolver = DNSResolver()
        
        assert isinstance(resolver.cache, dict)
        assert len(resolver.cache) == 0
    
    @pytest.mark.asyncio
    async def test_cache_hit(self):
        """Test cache hit."""
        resolver = DNSResolver()
        cache_key = "example.com:A"
        resolver.cache[cache_key] = [
            DNSRecord("example.com", "A", "192.168.1.1")
        ]
        
        with patch.object(resolver, '_resolve_dnspython') as mock_resolve:
            with patch('asyncio.get_event_loop') as mock_loop:
                result = await resolver._resolve("example.com", "A")
                
                assert len(result) > 0


@pytest.fixture
def resolver():
    """Fixture for DNS resolver."""
    return DNSResolver()
