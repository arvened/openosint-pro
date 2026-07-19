# ✅ ФАЙЛ 8

**Название:** `test_whois.py`

```python
"""
Tests for WHOIS Lookup Module

Coverage: 60%+
License: MIT
"""

import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from datetime import datetime

from whois import WHOISRecord, WHOISParser, WHOISLookup, WHOIS_SERVERS


class TestWHOISRecord:
    """Test WHOIS record dataclass."""
    
    def test_record_creation(self):
        """Test creating WHOIS record."""
        record = WHOISRecord(
            domain="example.com",
            registrar="VeriSign",
            created_date="1995-08-14",
        )
        
        assert record.domain == "example.com"
        assert record.registrar == "VeriSign"
        assert record.created_date == "1995-08-14"
    
    def test_record_defaults(self):
        """Test WHOIS record defaults."""
        record = WHOISRecord(domain="example.com")
        
        assert record.nameservers == []
        assert record.status == []
        assert record.retrieved_at is not None
    
    def test_record_to_dict(self):
        """Test converting record to dict."""
        record = WHOISRecord(
            domain="example.com",
            registrar="VeriSign",
        )
        
        data = record.to_dict()
        
        assert data["domain"] == "example.com"
        assert data["registrar"] == "VeriSign"
        assert isinstance(data, dict)


class TestWHOISParser:
    """Test WHOIS response parser."""
    
    def test_parse_registrar(self):
        """Test parsing registrar."""
        response = "Registrar: VeriSign Global Registry Services"
        
        record = WHOISParser.parse("example.com", response)
        
        assert record.registrar is not None
        assert "VeriSign" in record.registrar
    
    def test_parse_dates(self):
        """Test parsing dates."""
        response = """
        Creation Date: 1995-08-14T04:00:00Z
        Expiration Date: 2025-08-14T04:00:00Z
        """
        
        record = WHOISParser.parse("example.com", response)
        
        assert record.created_date is not None
        assert record.expiration_date is not None
    
    def test_parse_nameservers(self):
        """Test parsing nameservers."""
        response = """
        Name Server: NS1.EXAMPLE.COM
        Name Server: NS2.EXAMPLE.COM
        Nameserver: NS3.EXAMPLE.COM
        """
        
        record = WHOISParser.parse("example.com", response)
        
        assert len(record.nameservers) >= 2
        assert any("NS1" in ns for ns in record.nameservers)
    
    def test_parse_status(self):
        """Test parsing status."""
        response = """
        Domain Status: clientDeleteProhibited https://icann.org/epp#clientDeleteProhibited
        Domain Status: clientTransferProhibited https://icann.org/epp#clientTransferProhibited
        """
        
        record = WHOISParser.parse("example.com", response)
        
        assert len(record.status) >= 1
    
    def test_parse_emails(self):
        """Test parsing email addresses."""
        response = """
        Registrant Email: admin@example.com
        Admin Email: admin-contact@example.com
        Tech Email: tech@example.com
        """
        
        record = WHOISParser.parse("example.com", response)
        
        assert record.registrant_email is not None
        assert record.admin_email is not None
        assert record.tech_email is not None
    
    def test_parse_date_iso_format(self):
        """Test parsing ISO date format."""
        date_str = "2020-01-15T10:30:45Z"
        
        normalized = WHOISParser._parse_date(date_str)
        
        assert "2020-01-15" in normalized
    
    def test_parse_date_dmy_format(self):
        """Test parsing DD-MMM-YYYY date format."""
        date_str = "14-Aug-1995"
        
        normalized = WHOISParser._parse_date(date_str)
        
        assert "1995" in normalized
    
    def test_parse_date_invalid(self):
        """Test parsing invalid date."""
        date_str = "invalid-date-string"
        
        normalized = WHOISParser._parse_date(date_str)
        
        assert normalized is not None


class TestWHOISLookup:
    """Test WHOIS lookup."""
    
    def test_get_tld(self):
        """Test extracting TLD."""
        lookup = WHOISLookup()
        
        tld = lookup._get_tld("example.com")
        
        assert tld == "com"
    
    def test_get_tld_multi_level(self):
        """Test extracting multi-level TLD."""
        lookup = WHOISLookup()
        
        tld = lookup._get_tld("example.co.uk")
        
        assert tld == "uk"
    
    def test_get_whois_server(self):
        """Test getting WHOIS server."""
        lookup = WHOISLookup()
        
        server = lookup._get_whois_server("example.com")
        
        assert server == WHOIS_SERVERS.get("com")
    
    def test_get_whois_server_unknown_tld(self):
        """Test getting WHOIS server for unknown TLD."""
        lookup = WHOISLookup()
        
        server = lookup._get_whois_server("example.xyz")
        
        assert server is not None
    
    def test_validate_domain(self):
        """Test domain validation."""
        lookup = WHOISLookup()
        
        assert lookup._validate_domain("example.com") is True
        assert lookup._validate_domain("ex") is False
        assert lookup._validate_domain("..com") is False
        assert lookup._validate_domain(".example.com") is False
    
    @pytest.mark.asyncio
    async def test_lookup_success(self):
        """Test successful WHOIS lookup."""
        lookup = WHOISLookup()
        
        with patch.object(lookup, '_whois_query') as mock_query:
            mock_query.return_value = "Registrar: VeriSign\nCreation Date: 1995-08-14"
            
            with patch('asyncio.get_event_loop') as mock_loop:
                mock_loop.return_value.run_in_executor = AsyncMock(
                    return_value="Registrar: VeriSign\nCreation Date: 1995-08-14"
                )
                
                result = await lookup.lookup("example.com")
                
                assert result is not None
                assert result.domain == "example.com"
    
    @pytest.mark.asyncio
    async def test_lookup_invalid_domain(self):
        """Test WHOIS lookup with invalid domain."""
        lookup = WHOISLookup()
        
        result = await lookup.lookup("invalid")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_lookup_batch(self):
        """Test batch WHOIS lookup."""
        lookup = WHOISLookup()
        domains = ["example.com", "google.com", "github.com"]
        
        with patch.object(lookup, 'lookup') as mock_lookup:
            mock_lookup.return_value = WHOISRecord(
                domain="example.com",
                registrar="VeriSign"
            )
            
            results = await lookup.lookup_batch(domains)
            
            assert len(results) == 3


class TestWHOISServers:
    """Test WHOIS servers configuration."""
    
    def test_whois_servers_present(self):
        """Test that WHOIS_SERVERS dict is populated."""
        assert len(WHOIS_SERVERS) > 0
    
    def test_whois_servers_have_com(self):
        """Test that .com is configured."""
        assert "com" in WHOIS_SERVERS
    
    def test_whois_servers_values_are_strings(self):
        """Test that all WHOIS servers are strings."""
        assert all(isinstance(v, str) for v in WHOIS_SERVERS.values())


class TestWHOISEdgeCases:
    """Test edge cases."""
    
    def test_empty_whois_response(self):
        """Test parsing empty response."""
        record = WHOISParser.parse("example.com", "")
        
        assert record.domain == "example.com"
        assert record.registrar is None
    
    def test_comments_in_whois(self):
        """Test parsing response with comments."""
        response = """
        % This is a comment
        % Another comment
        Registrar: VeriSign
        """
        
        record = WHOISParser.parse("example.com", response)
        
        assert record.registrar is not None
    
    def test_unicode_in_whois(self):
        """Test parsing response with unicode."""
        response = "Registrar: Example™ Registrar"
        
        record = WHOISParser.parse("example.com", response)
        
        assert record.registrar is not None


@pytest.fixture
def lookup():
    """Fixture for WHOIS lookup."""
    return WHOISLookup()


@pytest.fixture
def parser():
    """Fixture for WHOIS parser."""
    return WHOISParser()
```

---

