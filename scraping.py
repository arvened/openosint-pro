# ✅ ФАЙЛ 1

**Название:** `scraping.py`

```python
"""
Web Scraping Module for OpenOSINT Pro

Async HTTP scraping with:
- User-Agent rotation
- Robots.txt compliance
- Retry logic
- Rate limiting
- Link/title/meta extraction

Author: Eduard Arbitman
License: MIT
"""

import logging
import asyncio
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import aiohttp
import httpx
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import time

logger = logging.getLogger(__name__)


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Android 11; Mobile; rv:89.0) Gecko/89.0 Firefox/89.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/91.0.4472.124",
]


class ScraperConfig:
    """Web scraper configuration."""
    
    def __init__(
        self,
        timeout: int = 30,
        retries: int = 3,
        rate_limit: float = 0.5,
        max_content_size: int = 10 * 1024 * 1024,
        verify_ssl: bool = True,
    ):
        """Initialize scraper config."""
        self.timeout = timeout
        self.retries = retries
        self.rate_limit = rate_limit
        self.max_content_size = max_content_size
        self.verify_ssl = verify_ssl


class WebScraper:
    """
    Async web scraper with safety features.
    
    Features:
    - User-Agent rotation
    - Robots.txt compliance
    - Automatic retry logic
    - Rate limiting
    - Content extraction
    """
    
    def __init__(self, config: Optional[ScraperConfig] = None):
        """Initialize web scraper."""
        self.config = config or ScraperConfig()
        self.last_request_time: Dict[str, float] = {}
        self.robots_cache: Dict[str, bool] = {}
        self.robots_cache_time: Dict[str, datetime] = {}
    
    def _get_random_user_agent(self) -> str:
        """Get random User-Agent."""
        import random
        return random.choice(USER_AGENTS)
    
    async def _check_robots_txt(self, url: str) -> bool:
        """Check if URL is allowed by robots.txt."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        
        if domain in self.robots_cache:
            cache_time = self.robots_cache_time.get(domain)
            if cache_time and (datetime.now() - cache_time).seconds < 86400:
                return self.robots_cache[domain]
        
        robots_url = f"{domain}/robots.txt"
        
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                response = await client.get(robots_url)
                
                if response.status_code == 200:
                    content = response.text
                    
                    if "Disallow: /" in content:
                        self.robots_cache[domain] = False
                        self.robots_cache_time[domain] = datetime.now()
                        logger.warning(f"robots.txt blocks all: {domain}")
                        return False
                    
                    self.robots_cache[domain] = True
                    self.robots_cache_time[domain] = datetime.now()
                    return True
                
                self.robots_cache[domain] = True
                return True
        
        except Exception as e:
            logger.debug(f"robots.txt check failed: {e}")
            return True
    
    async def _apply_rate_limit(self, domain: str) -> None:
        """Apply rate limiting per domain."""
        if domain in self.last_request_time:
            elapsed = time.time() - self.last_request_time[domain]
            if elapsed < self.config.rate_limit:
                await asyncio.sleep(self.config.rate_limit - elapsed)
        
        self.last_request_time[domain] = time.time()
    
    async def scrape(self, url: str, retry_count: int = 0) -> Dict[str, Any]:
        """Scrape URL with retry logic."""
        parsed = urlparse(url)
        domain = parsed.netloc
        
        if not await self._check_robots_txt(url):
            return {
                "status": 403,
                "error": "Blocked by robots.txt",
                "url": url,
            }
        
        await self._apply_rate_limit(domain)
        
        headers = {"User-Agent": self._get_random_user_agent()}
        
        try:
            async with httpx.AsyncClient(
                timeout=self.config.timeout,
                verify=self.config.verify_ssl,
            ) as client:
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    content = response.text
                    
                    if len(content) > self.config.max_content_size:
                        content = content[:self.config.max_content_size]
                    
                    soup = BeautifulSoup(content, "html.parser")
                    
                    title = None
                    if soup.title:
                        title = soup.title.string
                    
                    description = None
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc:
                        description = meta_desc.get("content")
                    
                    links = []
                    for link in soup.find_all("a", href=True):
                        href = link["href"]
                        if href.startswith("http"):
                            links.append(href)
                        else:
                            links.append(urljoin(url, href))
                    
                    return {
                        "status": 200,
                        "url": url,
                        "content": content,
                        "content_length": len(content),
                        "title": title,
                        "description": description,
                        "links": links[:50],
                        "scraped_at": datetime.now().isoformat(),
                    }
                
                return {
                    "status": response.status_code,
                    "error": f"HTTP {response.status_code}",
                    "url": url,
                }
        
        except asyncio.TimeoutError:
            if retry_count < self.config.retries:
                logger.info(f"Timeout, retrying {url} ({retry_count + 1}/{self.config.retries})")
                await asyncio.sleep(2 ** retry_count)
                return await self.scrape(url, retry_count + 1)
            
            return {
                "status": 504,
                "error": "Timeout after retries",
                "url": url,
            }
        
        except Exception as e:
            if retry_count < self.config.retries:
                logger.info(f"Error, retrying {url}: {e}")
                await asyncio.sleep(2 ** retry_count)
                return await self.scrape(url, retry_count + 1)
            
            return {
                "status": 500,
                "error": str(e),
                "url": url,
            }
    
    async def scrape_batch(self, urls: List[str], concurrency: int = 5) -> List[Dict[str, Any]]:
        """Scrape multiple URLs concurrently."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def scrape_with_semaphore(url: str):
            async with semaphore:
                return await self.scrape(url)
        
        tasks = [scrape_with_semaphore(url) for url in urls]
        return await asyncio.gather(*tasks)
