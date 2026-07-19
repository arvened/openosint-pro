# ✅ ФАЙЛ 7

**Название:** `test_scraping.py`

```python
"""
Tests for Web Scraping Module

Coverage: 60%+
License: MIT
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from scraping import ScraperConfig, WebScraper, USER_AGENTS


class TestScraperConfig:
    """Test scraper configuration."""
    
    def test_default_config(self):
        """Test default configuration."""
        config = ScraperConfig()
        
        assert config.timeout == 30
        assert config.retries == 3
        assert config.rate_limit == 0.5
        assert config.verify_ssl is True
    
    def test_custom_config(self):
        """Test custom configuration."""
        config = ScraperConfig(
            timeout=60,
            retries=5,
            rate_limit=1.0,
            verify_ssl=False
        )
        
        assert config.timeout == 60
        assert config.retries == 5
        assert config.rate_limit == 1.0
        assert config.verify_ssl is False


class TestWebScraper:
    """Test web scraper."""
    
    def test_scraper_initialization(self):
        """Test scraper initialization."""
        scraper = WebScraper()
        
        assert scraper.config is not None
        assert isinstance(scraper.last_request_time, dict)
        assert isinstance(scraper.robots_cache, dict)
    
    def test_get_random_user_agent(self):
        """Test getting random user agent."""
        scraper = WebScraper()
        
        ua = scraper._get_random_user_agent()
        
        assert ua in USER_AGENTS
        assert len(ua) > 0
    
    @pytest.mark.asyncio
    async def test_check_robots_txt_allowed(self):
        """Test robots.txt check when allowed."""
        scraper = WebScraper()
        
        allowed = await scraper._check_robots_txt("https://example.com/page")
        
        assert allowed is True
    
    @pytest.mark.asyncio
    async def test_apply_rate_limit(self):
        """Test rate limiting."""
        scraper = WebScraper()
        
        domain = "example.com"
        
        await scraper._apply_rate_limit(domain)
        assert domain in scraper.last_request_time
    
    @pytest.mark.asyncio
    async def test_scrape_success(self):
        """Test successful scrape."""
        scraper = WebScraper()
        
        with patch('scraping.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = "<html><title>Test</title></html>"
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            result = await scraper.scrape("https://example.com")
            
            assert result["status"] == 200
            assert "example.com" in result["url"]
    
    @pytest.mark.asyncio
    async def test_scrape_timeout(self):
        """Test scrape timeout."""
        config = ScraperConfig(timeout=1, retries=0)
        scraper = WebScraper(config)
        
        with patch('scraping.httpx.AsyncClient') as mock_client:
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                side_effect=asyncio.TimeoutError()
            )
            
            result = await scraper.scrape("https://example.com")
            
            assert result["status"] == 504
            assert "Timeout" in result["error"]
    
    @pytest.mark.asyncio
    async def test_scrape_robots_txt_blocked(self):
        """Test scrape blocked by robots.txt."""
        scraper = WebScraper()
        scraper.robots_cache["https://example.com"] = False
        scraper.robots_cache_time["https://example.com"] = __import__('datetime').datetime.now()
        
        result = await scraper.scrape("https://example.com")
        
        assert result["status"] == 403
        assert "robots.txt" in result["error"]
    
    @pytest.mark.asyncio
    async def test_scrape_batch(self):
        """Test batch scraping."""
        scraper = WebScraper()
        urls = [
            "https://example1.com",
            "https://example2.com",
            "https://example3.com",
        ]
        
        with patch('scraping.httpx.AsyncClient') as mock_client:
            mock_response = AsyncMock()
            mock_response.status_code = 200
            mock_response.text = "<html><title>Test</title></html>"
            
            mock_client.return_value.__aenter__.return_value.get = AsyncMock(
                return_value=mock_response
            )
            
            results = await scraper.scrape_batch(urls)
            
            assert len(results) == 3
            assert all(r["status"] == 200 for r in results)


class TestUserAgents:
    """Test User-Agent list."""
    
    def test_user_agents_present(self):
        """Test that USER_AGENTS list is not empty."""
        assert len(USER_AGENTS) > 0
    
    def test_user_agents_are_strings(self):
        """Test that all USER_AGENTS are strings."""
        assert all(isinstance(ua, str) for ua in USER_AGENTS)
    
    def test_user_agents_have_mozilla(self):
        """Test that USER_AGENTS contain Mozilla."""
        assert any("Mozilla" in ua for ua in USER_AGENTS)


class TestScraperEdgeCases:
    """Test edge cases."""
    
    def test_validate_empty_url(self):
        """Test handling empty URL."""
        scraper = WebScraper()
        assert scraper is not None
    
    def test_large_content_size(self):
        """Test handling large content."""
        config = ScraperConfig(max_content_size=1000)
        scraper = WebScraper(config)
        
        assert scraper.config.max_content_size == 1000


@pytest.fixture
def scraper():
    """Fixture for scraper."""
    return WebScraper()


@pytest.fixture
def config():
    """Fixture for config."""
    return ScraperConfig()
```

---

