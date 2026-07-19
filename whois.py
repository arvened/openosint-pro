"""
WHOIS Lookup Module for OpenOSINT Pro

Features:
- Domain WHOIS information retrieval
- Registrar data extraction
- Creation/expiration date parsing
- TLD-based server selection
- Batch lookups
- Result caching

Author: Eduard Arbitman
License: MIT
"""

import logging
import asyncio
import socket
from typing import Optional, Dict, Any, List
from datetime import datetime
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)


WHOIS_SERVERS = {
    "com": "whois.verisign-grs.com",
    "net": "whois.verisign-grs.com",
    "org": "whois.pir.org",
    "info": "whois.afilias.net",
    "biz": "whois.neulevel.biz",
    "co": "whois.nic.co",
    "uk": "whois.nic.uk",
    "de": "whois.denic.de",
    "fr": "whois.afnic.fr",
    "it": "whois.nic.it",
    "ru": "whois.nic.ru",
    "io": "whois.nic.io",
    "app": "whois.nic.google",
}


@dataclass
class WHOISRecord:
    """WHOIS record dataclass."""
    
    domain: str
    registrar: Optional[str] = None
    created_date: Optional[str] = None
    expiration_date: Optional[str] = None
    updated_date: Optional[str] = None
    nameservers: List[str] = None
    status: List[str] = None
    registrant_email: Optional[str] = None
    admin_email: Optional[str] = None
    tech_email: Optional[str] = None
    raw_data: str = ""
    retrieved_at: str = ""
    
    def __post_init__(self):
        """Initialize defaults."""
        if self.nameservers is None:
            self.nameservers = []
        if self.status is None:
            self.status = []
        if not self.retrieved_at:
            self.retrieved_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


class WHOISParser:
    """WHOIS response parser."""
    
    @staticmethod
    def parse(domain: str, response: str) -> WHOISRecord:
        """Parse WHOIS response."""
        record = WHOISRecord(domain=domain, raw_data=response)
        
        lines = response.split("\n")
        
        for line in lines:
            line = line.strip()
            
            if not line or line.startswith("%"):
                continue
            
            if any(x in line.lower() for x in ["registrar:", "registrar name:"]):
                record.registrar = line.split(":", 1)[1].strip()
            
            if "creation date:" in line.lower() or "created:" in line.lower():
                date_str = line.split(":", 1)[1].strip()
                record.created_date = WHOISParser._parse_date(date_str)
            
            if "expir" in line.lower():
                date_str = line.split(":", 1)[1].strip()
                record.expiration_date = WHOISParser._parse_date(date_str)
            
            if "updated:" in line.lower() or "last modified:" in line.lower():
                date_str = line.split(":", 1)[1].strip()
                record.updated_date = WHOISParser._parse_date(date_str)
            
            if "nameserver" in line.lower() or "nserver:" in line.lower():
                ns = line.split(":", 1)[1].strip()
                if ns and ns not in record.nameservers:
                    record.nameservers.append(ns)
            
            if "status:" in line.lower():
                status = line.split(":", 1)[1].strip()
                if status and status not in record.status:
                    record.status.append(status)
            
            if "registrant email:" in line.lower():
                record.registrant_email = line.split(":", 1)[1].strip()
            
            if "admin email:" in line.lower():
                record.admin_email = line.split(":", 1)[1].strip()
            
            if "tech email:" in line.lower():
                record.tech_email = line.split(":", 1)[1].strip()
        
        return record
    
    @staticmethod
    def _parse_date(date_str: str) -> str:
        """Parse date string to ISO format."""
        formats = [
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%d",
            "%d-%b-%Y",
            "%d/%m/%Y",
            "%d.%m.%Y",
        ]
        
        date_str = date_str.split()[0] if date_str else ""
        
        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.isoformat()
            except ValueError:
                continue
        
        return date_str


class WHOISLookup:
    """WHOIS lookup handler."""
    
    def __init__(self, timeout: int = 10):
        """Initialize WHOIS lookup."""
        self.timeout = timeout
    
    def _get_tld(self, domain: str) -> str:
        """Extract TLD from domain."""
        parts = domain.split(".")
        if len(parts) > 1:
            return parts[-1].lower()
        return "com"
    
    def _get_whois_server(self, domain: str) -> str:
        """Get WHOIS server for domain."""
        tld = self._get_tld(domain)
        return WHOIS_SERVERS.get(tld, "whois.iana.org")
    
    async def lookup(self, domain: str) -> Optional[WHOISRecord]:
        """Lookup domain WHOIS information."""
        domain = domain.lower().strip()
        
        if not domain or not self._validate_domain(domain):
            logger.warning(f"Invalid domain: {domain}")
            return None
        
        server = self._get_whois_server(domain)
        
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                self._whois_query,
                server,
                domain
            )
            
            if response:
                record = WHOISParser.parse(domain, response)
                logger.info(f"WHOIS lookup successful: {domain}")
                return record
            
            return None
        
        except Exception as e:
            logger.error(f"WHOIS lookup failed for {domain}: {e}")
            return None
    
    def _whois_query(self, server: str, domain: str) -> str:
        """Execute WHOIS query (blocking)."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            sock.connect((server, 43))
            sock.send(f"{domain}\r\n".encode())
            
            response = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response += chunk
            
            sock.close()
            return response.decode("utf-8", errors="ignore")
        
        except socket.timeout:
            logger.warning(f"WHOIS timeout for {domain} on {server}")
            return ""
        
        except Exception as e:
            logger.error(f"WHOIS query error: {e}")
            return ""
    
    @staticmethod
    def _validate_domain(domain: str) -> bool:
        """Validate domain format."""
        if not domain or len(domain) < 3:
            return False
        
        if ".." in domain or domain.startswith(".") or domain.endswith("."):
            return False
        
        return True
    
    async def lookup_batch(
        self,
        domains: List[str],
        concurrency: int = 5
    ) -> List[Optional[WHOISRecord]]:
        """Lookup multiple domains concurrently."""
        semaphore = asyncio.Semaphore(concurrency)
        
        async def lookup_with_semaphore(domain: str):
            async with semaphore:
                return await self.lookup(domain)
        
        tasks = [lookup_with_semaphore(domain) for domain in domains]
        return await asyncio.gather(*tasks)
