"""
API Gateway & Middleware for OpenOSINT Pro

Features:
- API key authentication
- Rate limiting (token bucket)
- Standard response formatting
- Request/response logging
- CORS configuration
- Error handling

Author: Eduard Arbitman
License: MIT
"""

import logging
import uuid
import time
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


@dataclass
class APIKey:
    """API key dataclass."""
    
    key: str
    name: str
    rate_limit: int = 100
    request_count: int = 0
    last_used: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    
    def update_usage(self) -> None:
        """Update usage statistics."""
        self.request_count += 1
        self.last_used = datetime.now()


class APIKeyManager:
    """Manages API keys."""
    
    def __init__(self):
        """Initialize API key manager."""
        self.keys: Dict[str, APIKey] = {}
    
    def create_key(self, name: str, rate_limit: int = 100) -> str:
        """Create new API key."""
        key = f"sk_{uuid.uuid4().hex[:32]}"
        self.keys[key] = APIKey(key=key, name=name, rate_limit=rate_limit)
        logger.info(f"Created API key: {name}")
        return key
    
    def validate_key(self, key: str) -> Optional[APIKey]:
        """Validate API key."""
        if key in self.keys:
            api_key = self.keys[key]
            api_key.update_usage()
            return api_key
        
        logger.warning(f"Invalid API key: {key}")
        return None
    
    def revoke_key(self, key: str) -> bool:
        """Revoke API key."""
        if key in self.keys:
            del self.keys[key]
            logger.info(f"Revoked API key: {key}")
            return True
        
        return False
    
    def get_key_info(self, key: str) -> Optional[Dict[str, Any]]:
        """Get API key information."""
        if key in self.keys:
            api_key = self.keys[key]
            return {
                "key": api_key.key,
                "name": api_key.name,
                "rate_limit": api_key.rate_limit,
                "request_count": api_key.request_count,
                "last_used": api_key.last_used.isoformat() if api_key.last_used else None,
                "created_at": api_key.created_at.isoformat(),
            }
        
        return None


class StandardResponse:
    """Standard API response formatter."""
    
    @staticmethod
    def success(
        data: Any,
        status_code: int = 200,
        message: str = "Success",
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format success response."""
        if not request_id:
            request_id = str(uuid.uuid4())
        
        return {
            "status": "success",
            "code": status_code,
            "message": message,
            "data": data,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
        }
    
    @staticmethod
    def error(
        error_type: str,
        message: str,
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Format error response."""
        if not request_id:
            request_id = str(uuid.uuid4())
        
        return {
            "status": "error",
            "code": status_code,
            "error_type": error_type,
            "message": message,
            "details": details or {},
            "request_id": request_id,
            "timestamp": datetime.now().isoformat(),
        }


class RateLimiter:
    """Token bucket rate limiter."""
    
    def __init__(self):
        """Initialize rate limiter."""
        self.buckets: Dict[str, Dict[str, Any]] = {}
    
    def check_limit(
        self,
        identifier: str,
        limit: int = 100,
        window: int = 60,
    ) -> bool:
        """Check if request is within limit."""
        now = time.time()
        
        if identifier not in self.buckets:
            self.buckets[identifier] = {
                "tokens": limit,
                "last_update": now,
                "window": window,
            }
            return True
        
        bucket = self.buckets[identifier]
        time_passed = now - bucket["last_update"]
        
        bucket["tokens"] = min(
            limit,
            bucket["tokens"] + (time_passed * (limit / window))
        )
        bucket["last_update"] = now
        
        if bucket["tokens"] >= 1:
            bucket["tokens"] -= 1
            return True
        
        return False
    
    def reset(self, identifier: str) -> None:
        """Reset rate limiter for identifier."""
        if identifier in self.buckets:
            del self.buckets[identifier]


class APIGateway:
    """
    API Gateway orchestrator.
    
    Handles:
    - Authentication
    - Rate limiting
    - Response formatting
    - Error handling
    - Request logging
    """
    
    def __init__(self):
        """Initialize API gateway."""
        self.key_manager = APIKeyManager()
        self.rate_limiter = RateLimiter()
        self.request_log: List[Dict[str, Any]] = []
    
    def authenticate(self, token: str) -> Optional[APIKey]:
        """Authenticate request."""
        if not token or not token.startswith("sk_"):
            return None
        
        return self.key_manager.validate_key(token)
    
    def check_rate_limit(self, api_key: APIKey) -> bool:
        """Check rate limit for API key."""
        return self.rate_limiter.check_limit(
            api_key.key,
            limit=api_key.rate_limit,
            window=60
        )
    
    def log_request(
        self,
        method: str,
        endpoint: str,
        api_key: Optional[APIKey] = None,
        status_code: int = 200,
        response_time: float = 0.0,
    ) -> None:
        """Log API request."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "endpoint": endpoint,
            "api_key": api_key.name if api_key else "unknown",
            "status_code": status_code,
            "response_time_ms": response_time * 1000,
        }
        
        self.request_log.append(log_entry)
        logger.info(f"{method} {endpoint} - {status_code} ({response_time*1000:.2f}ms)")
    
    def get_request_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get request log."""
        return self.request_log[-limit:]
    
    def create_api_key(self, name: str, rate_limit: int = 100) -> str:
        """Create new API key."""
        return self.key_manager.create_key(name, rate_limit)
    
    def revoke_api_key(self, key: str) -> bool:
        """Revoke API key."""
        return self.key_manager.revoke_key(key)


class CORSMiddleware:
    """CORS middleware configuration."""
    
    ALLOWED_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:8000",
        "https://example.com",
    ]
    
    ALLOWED_METHODS = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    
    ALLOWED_HEADERS = [
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ]
    
    @staticmethod
    def get_headers(origin: str) -> Dict[str, str]:
        """Get CORS headers."""
        if origin in CORSMiddleware.ALLOWED_ORIGINS:
            return {
                "Access-Control-Allow-Origin": origin,
                "Access-Control-Allow-Methods": ", ".join(CORSMiddleware.ALLOWED_METHODS),
                "Access-Control-Allow-Headers": ", ".join(CORSMiddleware.ALLOWED_HEADERS),
                "Access-Control-Allow-Credentials": "true",
            }
        
        return {}


class RequestLogger:
    """Request/response logging."""
    
    @staticmethod
    def log_request(
        method: str,
        path: str,
        headers: Dict[str, str],
        query_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log incoming request."""
        logger.debug(
            f"Incoming request: {method} {path} | "
            f"User-Agent: {headers.get('User-Agent', 'unknown')}"
        )
        
        if query_params:
            logger.debug(f"Query params: {query_params}")
    
    @staticmethod
    def log_response(
        status_code: int,
        response_time: float,
        response_size: int,
    ) -> None:
        """Log outgoing response."""
        logger.debug(
            f"Outgoing response: {status_code} | "
            f"Time: {response_time*1000:.2f}ms | "
            f"Size: {response_size} bytes"
        )


class ErrorHandler:
    """Centralized error handling."""
    
    @staticmethod
    def handle_auth_error() -> Dict[str, Any]:
        """Handle authentication error."""
        return StandardResponse.error(
            error_type="authentication_error",
            message="Invalid or missing API key",
            status_code=401,
        )
    
    @staticmethod
    def handle_rate_limit_error(retry_after: int = 60) -> Dict[str, Any]:
        """Handle rate limit error."""
        return StandardResponse.error(
            error_type="rate_limit_error",
            message="Rate limit exceeded",
            status_code=429,
            details={"retry_after": retry_after},
        )
    
    @staticmethod
    def handle_validation_error(details: Dict[str, str]) -> Dict[str, Any]:
        """Handle validation error."""
        return StandardResponse.error(
            error_type="validation_error",
            message="Validation failed",
            status_code=400,
            details=details,
        )
    
    @staticmethod
    def handle_internal_error(error: Exception) -> Dict[str, Any]:
        """Handle internal server error."""
        logger.error(f"Internal server error: {error}")
        
        return StandardResponse.error(
            error_type="internal_server_error",
            message="An internal error occurred",
            status_code=500,
        )
