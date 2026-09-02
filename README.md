# OpenOSINT Pro

⚠️ **Proof of Concept (v0.1.0-beta)**

This is an early-stage proof-of-concept under active development.
Project runs: September 2026 - August 2027.
Grant application submitted to NLnet Foundation NGI Zero Commons Fund (2026-06-3ac) — status: pending review.

---

Open-source OSINT reconnaissance toolkit for domain, email, and network intelligence gathering.

| License | Python | Tests | Coverage |
|---------|--------|-------|----------|
| MIT | 3.10+ | 70+ passing | 61% |

OpenOSINT Pro is a comprehensive open-source toolkit for OSINT (Open Source Intelligence) reconnaissance. Gather domain information, WHOIS data, DNS records, and perform web scraping with a unified, production-ready API.

Grant application submitted to: [NLnet Foundation](https://nlnet.nl)
NGI Zero Commons Fund (2026-06-3ac) | €40,000 | Status: Pending review

---

## 🎯 Features

### Core OSINT Modules

**Web Scraping 🌐**
- Async HTTP scraping with httpx
- User-Agent rotation (10+ browser agents)
- Robots.txt compliance checking
- Automatic retry with exponential backoff
- Per-domain rate limiting
- HTML link/title/meta extraction

**WHOIS Lookup 📋**
- Domain WHOIS information retrieval
- Automatic WHOIS server detection (13+ TLDs)
- Registrar, dates, nameservers extraction
- Batch lookups with concurrency control
- Result caching (30-day TTL)
- Email extraction (registrant, admin, tech)

**DNS Reconnaissance 🔗**
- A/AAAA/MX/TXT/SOA/NS/CNAME/SRV records
- Reverse DNS lookups
- Batch async queries (concurrency: 5)
- dnspython + socket fallback
- DNS result caching (24-hour TTL)
- SPF/DKIM/DMARC detection

### Integration Layer

**API Gateway 🛡️**
- RESTful API (FastAPI-compatible)
- API key authentication (Bearer tokens)
- Token bucket rate limiting
- CORS middleware
- Request/response logging
- Standardized JSON responses
- Request ID tracking

**Result Aggregation 📊**
- Multi-source result consolidation
- Confidence scoring per record
- Relationship mapping
- Comprehensive report generation

**Caching Layer 🔄**
- Redis-backed distributed caching
- In-memory fallback (no Redis required)
- Configurable TTLs per data type
- Cache statistics (hits, misses)
- Pattern-based cache invalidation
- JSON serialization support

---

## How it differs from existing OSINT tools

| Tool | Covers | Missing |
|---|---|---|
| theHarvester | Email/subdomain gathering from open sources | No unified API, no result aggregation with confidence scoring |
| Recon-ng | Modular recon framework | CLI-only, no REST API, no built-in caching |
| SpiderFoot | Automated OSINT reconnaissance | Heavy self-hosted tool, no production-ready API layer |

**OpenOSINT Pro** combines web scraping, WHOIS, and DNS recon into a single REST API with confidence scoring and SHA256-based deduplication — what existing tools require manual gluing together.

---

## 📊 Project Stats

**Production Code:** 2,070+ lines
**Test Code:** 810+ lines
**Test Coverage:** 61%
**Modules:** 6 complete
**Test Files:** 4 complete
**Tests Passing:** 70+
**Documentation:** 1,550+ lines

---

## 🚀 Quick Start

### Installation

**Requirements**
- Python 3.10+
- pip or poetry
- Redis (optional, falls back to in-memory cache)

### From GitHub

```bash
# Clone repository
git clone https://github.com/arvened/openosint-pro
cd openosint-pro

# Install dependencies
pip install httpx pydantic redis pytest

# Run tests
pytest -v --cov=. --cov-report=html

# Docker (coming in Week 5-6)
docker build -t openosint-pro .
docker run -p 8000:8000 openosint-pro


📚 Usage Examples

1. Web Scraping
import asyncio
from scraping import WebScraper, ScraperConfig

async def scrape_example():
    config = ScraperConfig(timeout=30)
    scraper = WebScraper(config)
    result = await scraper.scrape("https://example.com")
    print(f"Status: {result['status']}")
    print(f"Title: {result['title']}")
    print(f"Links: {result['links'][:5]}")

asyncio.run(scrape_example())

Output:
{
  "status": 200,
  "url": "https://example.com",
  "title": "Example Domain",
  "links": ["https://www.iana.org/domains/example", ...],
  "content_length": 1256,
  "scraped_at": "2026-08-11T10:30:45.123Z"
}

2. WHOIS Lookup
import asyncio
from whois import WHOISLookup

async def whois_example():
    lookup = WHOISLookup(timeout=10)
    record = await lookup.lookup("example.com")
    print(f"Registrar: {record.registrar}")
    print(f"Created: {record.created_date}")
    print(f"Expires: {record.expiration_date}")
    print(f"Nameservers: {record.nameservers}")

asyncio.run(whois_example())

Output
Registrar: VeriSign Global Registry Services
Created: 1995-08-14T04:00:00
Expires: 2025-08-14T04:00:00
Nameservers: ['A.IANA-SERVERS.NET', 'B.IANA-SERVERS.NET']

3. DNS Reconnaissance

import asyncio
from dns_recon import DNSResolver

async def dns_example():
    resolver = DNSResolver(timeout=5)
    records = await resolver.get_all_records("example.com")
    print(f"A Records: {records['A']}")
    print(f"MX Records: {records['MX']}")
    print(f"TXT Records: {records['TXT']}")

asyncio.run(dns_example())

Output:
A Records: ['93.184.216.34']
MX Records: []
TXT Records: ['v=spf1 -all']

4. API Gateway
from middleware import APIGateway

gateway = APIGateway()
api_key = gateway.create_api_key("MyApp")
authenticated_key = gateway.authenticate_key(api_key)
within_limit = gateway.check_rate_limit(api_key)
logs = gateway.get_request_log(limit=5)
print(f"Last request: {logs[-1]}")

5. Result Aggregation
from engine import ResultAggregator

aggregator = ResultAggregator()
whois_data = {
    "registrar": "VeriSign",
    "created_date": "1995-08-14",
    "expiration_date": "2025-08-14",
    "nameservers": ["ns1.example.com"]
}

record = aggregator.aggregate_whois_record(whois_data)
aggregator.add_record("example.com", record)
report = aggregator.get_comprehensive_report("example.com")
print(f"Found: {report['found']}")
print(f"Confidence: {report['confidence']}")

6. Caching
from redis_cache import RedisCache, CacheManager

cache = RedisCache(host="localhost", port=6379)
manager = CacheManager(cache)
whois_data = {"registrar": "VeriSign", "created_date": "1995-08-14"}
manager.cache_whois("example.com", whois_data)
cached = manager.get_whois("example.com")
status = manager.get_cache_status()
print(f"Cache hits: {status['stats']['hits']}")

🧪 Testing

Run All Tests

# Basic test run
pytest -v

# With coverage report
pytest -v --cov=. --cov-report=html --cov-report=term

# Specific test file
pytest test_scraping.py -v

# Specific test function
pytest test_whois.py::TestWHOISLookup -v

Coverage

Current coverage: 61% (target: 60%+)

Module	Coverage
Web Scraping	62%
WHOIS Lookup	61%
DNS Reconnaissance	63%
API Gateway	60%
Aggregation Engine	60%
Caching Layer	60%
AVERAGE	61%

Test Statistics

	•	Total tests: 70+
	•	Passing: 70+
	•	Coverage target: 60%+
	•	Current: 61% ✅

	•	httpx >= 0.24.0 (Async HTTP)
	•	pydantic >= 2.0.0 (Data validation)
	•	redis >= 4.5.0 (Caching, optional)

Testing

	•	pytest >= 7.4.0
	•	pytest-asyncio >= 0.21.0
	•	pytest-cov >= 4.1.0

Optional

	•	dnspython >= 2.3.0 (DNS library)
	•	beautifulsoup4 >= 4.12.0 (HTML parsing)

🚀 Roadmap

After grant approval:

	•	Security audit
	•	API documentation (Swagger/OpenAPI)
	•	Deployment guide
	•	Docker image
	•	v0.1.0 production release

Planned:

	•	GraphQL API
	•	Machine learning models
	•	Advanced analytics

📁 Project Structure
openosint-pro/
├── scraping.py               # Web scraping module
├── whois.py                  # WHOIS lookup module
├── dns_recon.py              # DNS reconnaissance module
├── middleware.py             # API gateway middleware
├── engine.py                 # Result aggregation engine
├── redis_cache.py            # Caching layer
├── political_ops_detection.py # Political operations detector
├── test_scraping.py          # Scraping tests
├── test_whois.py             # WHOIS tests
├── test_dns_recon.py         # DNS tests
├── test_integration_week3.py  # Integration tests
├── CHANGELOG.md              # Version history
├── WEEK1-2_COMPLETION_SUMMARY.md
├── WEEK3-4_COMPLETION_SUMMARY.md
├── PROJECT_STATUS.md         # Current progress
├── GIT_COMMIT_MANIFEST.md    # Deployment guide
├── README.md                 # This file
├── LICENSE                   # MIT license
└── .gitignore

💻 Development Setup
# Clone repo
git clone https://github.com/arvened/openosint-pro
cd openosint-pro

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest -v --cov

# Code formatting
black .

# Type checking
mypy .

Commit Guidelines
feat: add new feature
test: add/modify tests
docs: update documentation
fix: bug fix
perf: performance improvement
refactor: code refactoring



	•	CHANGELOG.md — Version history
	•	PROJECT_STATUS.md — Current progress
	•	GIT_COMMIT_MANIFEST.md — Deployment guide
	•	NLnet Foundation

🙏 Acknowledgments

This project has submitted a grant application to NLnet Foundation NGI Zero Commons Fund.

Grant application submitted to
NLnet Foundation NGI Zero Commons Fund
Status: Pending review

OpenOSINT Pro – Open Source OSINT for Everyone

Current Version: 0.1.0-beta
Status: Active Development (pre-grant proof-of-concept)
Last Updated: September 2, 2026

Made with ❤️ by Eduard Arbitman and the ARVEN team
























