# Changelog

Dates are ISO 8601.

## [Unreleased] - 2026-09-20

### Fixed
- Removed pasted instruction text from scraping.py, engine.py, redis_cache.py and four test files (they were not valid Python).
- Rate limiter now counts the first request of a new identifier.
- WHOIS parser now recognises "Name Server:" lines written with a space.
- test_reverse_lookup now mocks the dnspython path, so it does not depend on the network.

### Added
- requirements.txt and requirements-dev.txt.

### Removed
- political_ops_detection.py and its test (out of scope for the project; the file was not valid Python).
- Internal status reports and notes that claimed the work was complete.

## [0.1.0-beta]

Pre-grant prototype snapshot. Earlier notes about production readiness, 70+ tests, 61% coverage and a FastAPI-compatible REST API were not verified and are withdrawn.