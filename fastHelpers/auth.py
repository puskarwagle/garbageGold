# fastHelpers/auth.py - Clean Auth Module
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import requests
import os
from typing import Optional

security = HTTPBearer(auto_error=False)

class AuthManager:
    def __init__(self):
        self.laravel_base_url = os.getenv("LARAVEL_BASE_URL", "http://localhost:8000")
        self.bypass_auth = os.getenv("BYPASS_AUTH", "false").lower() == "true"

    async def verify_laravel_token(self, credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
        """Verify token with Laravel backend"""
        if self.bypass_auth:
            return {"id": 1, "name": "dev_user"}  # Dev mode

        if not credentials:
            raise HTTPException(status_code=401, detail="Missing authorization")

        try:
            response = requests.get(
                f"{self.laravel_base_url}/api/user",
                headers={"Authorization": f"Bearer {credentials.credentials}"},
                timeout=5
            )

            if response.status_code == 200:
                return response.json()
            else:
                raise HTTPException(status_code=401, detail="Invalid token")

        except requests.RequestException:
            raise HTTPException(status_code=503, detail="Auth service unavailable")

    def require_auth(self):
        """Dependency for protected routes"""
        return Depends(self.verify_laravel_token)


# Global auth instance
auth_manager = AuthManager()