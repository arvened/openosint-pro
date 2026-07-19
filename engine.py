# ✅ ФАЙЛ 5

**Название:** `engine.py`

```python
"""
Result Aggregation Engine for OpenOSINT Pro

Aggregates and normalizes results from multiple OSINT modules:
- Unified response formatting
- Data deduplication
- Timestamp normalization
- Source tracking
- Confidence scoring
- Relationship mapping

Author: Eduard Arbitman
License: MIT
"""

import logging
from typing import List, Dict, Any, Optional, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class DataSource(Enum):
    """Data source enumeration."""
    SCRAPING = "scraping"
    WHOIS = "whois"
    DNS = "dns"
    SEARCH = "search"
    ENRICHMENT = "enrichment"
    VERIFICATION = "verification"


@dataclass
class AggregatedRecord:
    """Aggregated OSINT record."""
    
    query: str
    query_type: str
    data: Dict[str, Any]
    sources: List[str] = field(default_factory=list)
    confidence: float = 0.0
    retrieved_at: str = field(default_factory=lambda: datetime.now().isoformat())
    tags: List[str] = field(default_factory=list)
    relationships: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_source(self, source: str) -> None:
        """Add data source."""
        if source not in self.sources:
            self.sources.append(source)
    
    def add_tag(self, tag: str) -> None:
        """Add tag."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def add_relationship(self, related_query: str) -> None:
        """Add related query."""
        if related_query not in self.relationships:
            self.relationships.append(related_query)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    def get_hash(self) -> str:
        """Get content hash for deduplication."""
        content = json.dumps(self.data, sort_keys=True, default=str)
        return hashlib.sha256(content.encode()).hexdigest()


class DataDeduplicator:
    """Deduplicates aggregated records."""
    
    def __init__(self):
        """Initialize deduplicator."""
        self.hashes: Dict[str, Set[str]] = {}
    
    def add_record(self, query: str, record: AggregatedRecord) -> None:
        """Add record and track hash."""
        if query not in self.hashes:
            self.hashes[query] = set()
        
        hash_value = record.get_hash()
        self.hashes[query].add(hash_value)
    
    def is_duplicate(self, query: str, record: AggregatedRecord) -> bool:
        """Check if record is duplicate."""
        if query not in self.hashes:
            return False
        
        hash_value = record.get_hash()
        return hash_value in self.hashes[query]


class TimestampNormalizer:
    """Normalizes timestamps across sources."""
    
    @staticmethod
    def normalize(timestamp: Any) -> str:
        """Normalize timestamp to ISO format."""
        if isinstance(timestamp, str):
            formats = [
                "%Y-%m-%dT%H:%M:%SZ",
                "%Y-%m-%d %H:%M:%S",
                "%Y-%m-%d",
                "%d-%b-%Y",
                "%d/%m/%Y",
            ]
            
            for fmt in formats:
                try:
                    dt = datetime.strptime(timestamp, fmt)
                    return dt.isoformat()
                except ValueError:
                    continue
            
            return timestamp
        
        elif isinstance(timestamp, datetime):
            return timestamp.isoformat()
        
        elif isinstance(timestamp, int):
            try:
                dt = datetime.fromtimestamp(timestamp)
                return dt.isoformat()
            except Exception:
                return str(timestamp)
        
        return str(timestamp)


class ResultAggregator:
    """
    Aggregates results from multiple OSINT modules.
    
    Features:
    - Unified response formatting
    - Automatic deduplication
    - Timestamp normalization
    - Source tracking
    - Confidence scoring
    - Relationship mapping
    """
    
    def __init__(self):
        """Initialize result aggregator."""
        self.deduplicator = DataDeduplicator()
        self.normalizer = TimestampNormalizer()
        self.records: Dict[str, List[AggregatedRecord]] = {}
    
    def aggregate_scraping_results(
        self,
        query: str,
        scrape_result: Dict[str, Any],
    ) -> Optional[AggregatedRecord]:
        """Aggregate web scraping results."""
        if not scrape_result or scrape_result.get("status") != 200:
            return None
        
        record = AggregatedRecord(
            query=query,
            query_type="url",
            data={
                "status": scrape_result.get("status"),
                "content_length": len(scrape_result.get("content", "")),
                "headers": scrape_result.get("headers", {}),
                "title": scrape_result.get("title"),
                "description": scrape_result.get("description"),
            },
            confidence=0.9,
        )
        
        record.add_source(DataSource.SCRAPING.value)
        record.add_tag("web")
        record.add_tag("scraped")
        
        return record
    
    def aggregate_whois_results(
        self,
        domain: str,
        whois_result: Dict[str, Any],
    ) -> Optional[AggregatedRecord]:
        """Aggregate WHOIS results."""
        if not whois_result or not whois_result.get("registrar"):
            return None
        
        created = self.normalizer.normalize(whois_result.get("created_date"))
        expires = self.normalizer.normalize(whois_result.get("expiration_date"))
        
        record = AggregatedRecord(
            query=domain,
            query_type="domain",
            data={
                "registrar": whois_result.get("registrar"),
                "created_date": created,
                "expiration_date": expires,
                "nameservers": whois_result.get("nameservers", []),
                "status": whois_result.get("status", []),
                "registrant_email": whois_result.get("registrant_email"),
                "admin_email": whois_result.get("admin_email"),
                "tech_email": whois_result.get("tech_email"),
            },
            confidence=0.95,
        )
        
        record.add_source(DataSource.WHOIS.value)
        record.add_tag("domain")
        record.add_tag("whois")
        
        for ns in whois_result.get("nameservers", []):
            record.add_relationship(ns)
        
        return record
    
    def aggregate_dns_results(
        self,
        domain: str,
        dns_results: Dict[str, List[Dict[str, Any]]],
    ) -> Optional[AggregatedRecord]:
        """Aggregate DNS results."""
        if not dns_results:
            return None
        
        a_records = [r.get("value") for r in dns_results.get("A", [])]
        aaaa_records = [r.get("value") for r in dns_results.get("AAAA", [])]
        mx_records = [r.get("value") for r in dns_results.get("MX", [])]
        txt_records = [r.get("value") for r in dns_results.get("TXT", [])]
        
        record = AggregatedRecord(
            query=domain,
            query_type="domain",
            data={
                "a_records": a_records,
                "aaaa_records": aaaa_records,
                "mx_records": mx_records,
                "txt_records": txt_records,
                "spf_enabled": any("v=spf1" in txt for txt in txt_records),
            },
            confidence=0.9,
        )
        
        record.add_source(DataSource.DNS.value)
        record.add_tag("dns")
        record.add_tag("network")
        
        for ip in a_records + aaaa_records:
            record.add_relationship(ip)
        for mx in mx_records:
            record.add_relationship(mx)
        
        return record
    
    def aggregate_verification_results(
        self,
        query: str,
        query_type: str,
        is_valid: bool,
        details: Dict[str, Any],
    ) -> AggregatedRecord:
        """Aggregate verification results."""
        record = AggregatedRecord(
            query=query,
            query_type=query_type,
            data={
                "valid": is_valid,
                "in_breaches": details.get("in_breaches", False),
                "verification_score": details.get("score", 0.0),
                **details,
            },
            confidence=0.85,
        )
        
        record.add_source(DataSource.VERIFICATION.value)
        record.add_tag("verified")
        
        if is_valid:
            record.add_tag("valid")
        else:
            record.add_tag("invalid")
        
        return record
    
    def add_record(
        self,
        query: str,
        record: AggregatedRecord,
    ) -> bool:
        """Add aggregated record."""
        if self.deduplicator.is_duplicate(query, record):
            logger.info(f"Skipped duplicate record for {query}")
            return False
        
        self.deduplicator.add_record(query, record)
        
        if query not in self.records:
            self.records[query] = []
        
        self.records[query].append(record)
        logger.info(f"Added aggregated record for {query}")
        
        return True
    
    def get_records(self, query: str) -> List[Dict[str, Any]]:
        """Get aggregated records for query."""
        records = self.records.get(query, [])
        return [r.to_dict() for r in records]
    
    def merge_records(self, query: str) -> Optional[Dict[str, Any]]:
        """Merge multiple records for query into single result."""
        records = self.records.get(query, [])
        
        if not records:
            return None
        
        if len(records) == 1:
            return records[0].to_dict()
        
        merged = AggregatedRecord(
            query=query,
            query_type=records[0].query_type,
            data={},
            sources=[],
            confidence=0.0,
        )
        
        for record in records:
            for source in record.sources:
                merged.add_source(source)
            
            for tag in record.tags:
                merged.add_tag(tag)
            
            for rel in record.relationships:
                merged.add_relationship(rel)
            
            merged.data.update(record.data)
        
        merged.confidence = sum(r.confidence for r in records) / len(records)
        
        logger.info(f"Merged {len(records)} records for {query}")
        
        return merged.to_dict()
    
    def get_comprehensive_report(self, query: str) -> Dict[str, Any]:
        """Generate comprehensive report for query."""
        merged = self.merge_records(query)
        
        if not merged:
            return {
                "query": query,
                "found": False,
                "message": "No results found",
                "timestamp": datetime.now().isoformat(),
            }
        
        return {
            "query": query,
            "found": True,
            "result": merged,
            "record_count": len(self.records.get(query, [])),
            "sources": merged.get("sources", []),
            "confidence": merged.get("confidence", 0.0),
            "tags": merged.get("tags", []),
            "relationships": merged.get("relationships", []),
            "timestamp": datetime.now().isoformat(),
        }


async def aggregate_domain_osint(
    domain: str,
    whois_result: Optional[Dict[str, Any]] = None,
    dns_results: Optional[Dict[str, Any]] = None,
    scrape_result: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Aggregate all OSINT data for domain."""
    aggregator = ResultAggregator()
    
    if whois_result:
        record = aggregator.aggregate_whois_results(domain, whois_result)
        if record:
            aggregator.add_record(domain, record)
    
    if dns_results:
        record = aggregator.aggregate_dns_results(domain, dns_results)
        if record:
            aggregator.add_record(domain, record)
    
    if scrape_result:
        record = aggregator.aggregate_scraping_results(domain, scrape_result)
        if record:
            aggregator.add_record(domain, record)
    
    return aggregator.get_comprehensive_report(domain)
```

---

