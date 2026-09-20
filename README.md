# OpenOSINT Pro

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Prototype OSINT toolkit in Python: web scraping, WHOIS lookup, DNS reconnaissance, and a small layer for result aggregation, caching and API-key / rate-limit handling.

## Project status

Pre-grant proof of concept. Early stage, not production-ready.

An application (ID 2026-06-3ac, 40,000 EUR) has been submitted to the NLnet NGI Zero Commons Fund and is under review. No funding has been awarded. Anything listed under "Planned" would only be funded if the application is approved; dates depend on the project start date confirmed by NLnet.

Parts of the code were drafted with AI coding assistants (Claude). The maintainer is responsible for the repository.

## What exists today

Flat Python modules in the repository root:

- scraping.py: asynchronous web scraper (aiohttp, BeautifulSoup) with User-Agent rotation, robots.txt checks and retries
- whois.py: WHOIS lookup and response parser
- dns_recon.py: DNS record resolver (uses dnspython when installed, socket fallback for basic lookups)
- engine.py: aggregation of results from several sources
- middleware.py: in-process API-key handling, token-bucket rate limiter and request log
- redis_cache.py: caching layer
- Automated tests for all modules (pytest)

Measured on 2026-09-20 with Python 3.12: all 106 automated tests pass (the full run takes about five minutes). Line coverage of the six modules is 75% (from 58% for redis_cache.py to 93% for `middleware.py`).

## Known limitations

- There is no HTTP server yet. middleware.py contains classes meant for a future API; FastAPI is not used.
- Six tests of the Redis cache take about 50 seconds each because they wait for a Redis server that is not running; the whole run takes about five minutes.
- Not tested at scale or in production.

## Planned (not implemented)

- Python package layout and a tests/ directory
- REST API
- Documentation with usage examples
- Independent security audit
- Container image

## Quick start

Tested with Python 3.12.
git clone https://github.com/arvened/openosint-pro.git
cd openosint-pro
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements-dev.txt
python -m pytest -q

## Responsible use

Web scraping and WHOIS lookups can involve personal data (for example registrant contact details). Anyone using this code must comply with applicable law (including GDPR) and with the terms of the services they query. The scraper rotates User-Agent strings and checks robots.txt; this does not replace permission from the site owner.

## Contributing

Issues and pull requests are welcome.

## License

MIT, see [LICENSE](LICENSE).