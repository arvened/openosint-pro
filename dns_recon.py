"""
DNS Reconnaissance Module for OpenOSINT Pro

Features:
- A/AAAA/MX/TXT/SOA/NS/CNAME/SRV record lookup
- Reverse DNS lookup
- Batch async queries
- Result caching
- Fallback to socket

Author: Eduard Arbitman
License: MIT
"""

import logging
import asyncio
import socket
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

try:
    import dns.resolver
    import dns.reversename
    DNSPYTHON_AVAILABLE = True
except ImportError:
    DNSPYTHON_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class DNSRecord:
    """DNS record dataclass."""
    
    domain: str
    record_type: str
    value: str
    ttl: Optional[int] = None
    priority: Optional[int] = None
    retrieved_at: str = ""
    
    def __post_init__(self):
        """Initialize defaults."""
        if not self.retrieved_at:
            self.retrieved_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class DNSResolver:
    """
    DNS resolver with support for multiple record types.
    
    Features:
    - A/AAAA records (IPv4/IPv6)
    - MX records (mail servers)
    - TXT records (SPF, DKIM, DMARC)
    - SOA records (authority)
    - NS records (nameservers)
    - CNAME records (aliases)
    - SRV records (services)
    - Reverse DNS
    """
    
    def __init__(self, timeout: int = 5):
        """Initialize DNS resolver."""
        self.timeout = timeout
        self.cache: Dict[str, List[DNSRecord]] = {}
    
    async def resolve_a(self, domain: str) -> List[str]:
        """Resolve A records (IPv4)."""
        return await self._resolve(domain, "A")
    
    async def resolve_aaaa(self, domain: str) -> List[str]:
        """Resolve AAAA records (IPv6)."""
        return await self._resolve(domain, "AAAA")
    
    async def resolve_mx(self, domain: str) -> List[Dict[str, Any]]:
        """Resolve MX records (mail servers)."""
        records = await self._resolve(domain, "MX")
        return [{"value": r, "priority": None} for r in records]
    
    async def resolve_txt(self, domain: str) -> List[str]:
        """Resolve TXT records (SPF, DKIM, DMARC)."""
        return await self._resolve(domain, "TXT")
    
    async def resolve_ns(self, domain: str) -> List[str]:
        """Resolve NS records (nameservers)."""
        return await self._resolve(domain, "NS")
    
    async def resolve_cname(self, domain: str) -> List[str]:
        """Resolve CNAME records (aliases)."""
        return await self._resolve(domain, "CNAME")
    
    async def resolve_soa(self, domain: str) -> List[str]:
        """Resolve SOA records (authority)."""
        return await self._resolve(domain, "SOA")
    
    async def resolve_srv(self, domain: str, service: str = "_sip._tcp") -> List[str]:
        """Resolve SRV records (services)."""
        query_domain = f"{service}.{domain}"
        return await self._resolve(query_domain, "SRV")
    
    async def reverse_lookup(self, ip: str) -> Optional[str]:
        """Reverse DNS lookup."""
        try:
            if DNSPYTHON_AVAILABLE:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    self._reverse_lookup_dnspython,
                    ip
                )
                return result
            else:
                return await self._reverse_lookup_socket(ip)
        
        except Exception as e:
            logger.error(f"Reverse lookup failed for {ip}: {e}")
            return None
    
    async def _resolve(self, domain: str, record_type: str) -> List[str]:
        """Resolve DNS records."""
        cache_key = f"{domain}:{record_type}"
        
        if cache_key in self.cache:
            logger.debug(f"Cache hit for {cache_key}")
            return [r.value for r in self.cache[cache_key]]
        
        try:
            if DNSPYTHON_AVAILABLE:
                loop = asyncio.get_event_loop()
                results = await loop.run_in_executor(
                    None,
                    self._resolve_dnspython,
                    domain,
                    record_type
                )
            else:
                results = await self._resolve_socket(domain, record_type)
            
            records = [
                DNSRecord(domain=domain, record_type=record_type, value=str(r))
                for r in results
            ]
            self.cache[cache_key] = records
            
            logger.info(f"Resolved {record_type} for {domain}: {len(results)} records")
            return results
        
        except Exception as e:
            logger.error(f"DNS resolution failed for {domain} ({record_type}): {e}")
            return []
    
    def _resolve_dnspython(self, domain: str, record_type: str) -> List[str]:
        """Resolve using dnspython (blocking)."""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout
            
            answers = resolver.resolve(domain, record_type)
            results = []
            
            for rdata in answers:
                if record_type == "MX":
                    results.append(f"{rdata.preference} {rdata.exchange}")
                elif record_type == "SRV":
                    results.append(f"{rdata.priority} {rdata.weight} {rdata.port} {rdata.target}")
                else:
                    results.append(str(rdata))
            
            return results
        
        except Exception as e:
            logger.debug(f"dnspython resolution failed: {e}")
            return []
    
    async def _resolve_socket(self, domain: str, record_type: str) -> List[str]:
        """Fallback socket-based resolution (IPv4 A records only)."""
        if record_type not in ["A", "AAAA"]:
            logger.debug(f"Socket fallback not available for {record_type}")
            return []
        
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(
                None,
                socket.getaddrinfo,
                domain,
                None,
                socket.AF_INET if record_type == "A" else socket.AF_INET6
            )
            
            ips = []
            for family, socktype, proto, canonname, sockaddr in info:
                ip = sockaddr[0]
                if ip not in ips:
                    ips.append(ip)
            
            return ips
        
        except Exception as e:
            logger.debug(f"Socket resolution failed: {e}")
            return []
    
    def _reverse_lookup_dnspython(self, ip: str) -> Optional[str]:
        """Reverse lookup using dnspython (blocking)."""
        try:
            rev_name = dns.reversename.from_address(ip)
            resolver = dns.resolver.Resolver()
            resolver.timeout = self.timeout
            
            answers = resolver.resolve(rev_name, "PTR")
            return str(answers[0])
        
        except Exception as e:
            logger.debug(f"Reverse lookup failed: {e}")
            return None
    
    async def _reverse_lookup_socket(self, ip: str) -> Optional[str]:
        """Reverse lookup using socket (blocking)."""
        try:
            loop = asyncio.get_event_loop()
            hostname, aliaslist, ipaddrlist = await loop.run_in_executor(
                None,
                socket.gethostbyaddr,
                ip
            )
            return hostname
        
        except Exception as e:
            logger.debug(f"Socket reverse lookup failed: {e}")
            return None
    
    async def get_all_records(self, domain: str) -> Dict[str, List[str]]:
        """Get all common DNS records for domain."""
        return {
            "A": await self.resolve_a(domain),
            "AAAA": await self.resolve_aaaa(domain),
            "MX": await self.resolve_mx(domain),
            "TXT": await self.resolve_txt(domain),
            "NS": await self.resolve_ns(domain),
            "CNAME": await self.resolve_cname(domain),
            "SOA": await self.resolve_soa(domain),
        }
    
    async def batch_query(
        self,
        domains: List[str],
        record_types: List[str],
        concurrency: int = 5
    ) -> Dict[str, Dict[str, List[str]]]:
        """Query multiple domains and record types concurrently."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def query_with_semaphore(domain: str, record_type: str):
            async with semaphore:
                records = await self._resolve(domain, record_type)
                return (domain, record_type, records)
        
        tasks = [
            query_with_semaphore(domain, rtype)
            for domain in domains
            for rtype in record_types
        ]
        
        results = {}
        query_results = await asyncio.gather(*tasks)
        
        for domain, rtype, records in query_results:
            if domain not in results:
                results[domain] = {}
            results[domain][rtype] = records
        
        return results
    
    def clear_cache(self) -> None:
        """Clear DNS cache."""
        self.cache.clear()
        logger.info("DNS cache cleared")
    
    def get_cache_size(self) -> int:
        """Get cache size."""
        return len(self.cache)
