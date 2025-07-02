# fastHelpers/security.py - Security Middleware & Config
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import time
from collections import defaultdict
from typing import Dict
import os


class SecurityManager:
    def __init__(self):
        self.rate_limit_storage: Dict[str, list] = defaultdict(list)
        self.max_requests_per_minute = int(os.getenv("RATE_LIMIT", "60"))

    async def rate_limit_middleware(self, request: Request, call_next):
        """Basic rate limiting"""
        client_ip = request.client.host
        current_time = time.time()

        # Clean old requests (older than 1 minute)
        self.rate_limit_storage[client_ip] = [
            req_time for req_time in self.rate_limit_storage[client_ip]
            if current_time - req_time < 60
        ]

        # Check rate limit
        if len(self.rate_limit_storage[client_ip]) >= self.max_requests_per_minute:
            return JSONResponse(
                {"error": "Rate limit exceeded"},
                status_code=429
            )

        # Add current request
        self.rate_limit_storage[client_ip].append(current_time)

        return await call_next(request)

    async def security_headers_middleware(self, request: Request, call_next):
        """Add security headers"""
        response = await call_next(request)

        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        })

        return response


def get_cors_middleware():
    """CORS configuration"""
    allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")

    return CORSMiddleware(
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
        max_age=600,  # Cache preflight for 10 minutes
    )


# Global security instance
security_manager = SecurityManager()