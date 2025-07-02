# main.py - Modular FastAPI Application (Secured)
from fastapi import FastAPI, WebSocket
import uvicorn
import sys
import os

# Add fastHelpers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'fastHelpers'))

# Import modular components
from fastHelpers.config_router import router as config_router
from fastHelpers.websocket_manager import websocket_handler, manager
from fastHelpers.security import get_cors_middleware, security_manager

# Initialize FastAPI app 👈
app = FastAPI(
    title="QuestBot", 
    version="1.0.0",
    description="Modular FastAPI server for job application automation"
)

# Security middleware stack
cors_class, cors_options = get_cors_middleware()
app.add_middleware(cors_class, **cors_options)
app.middleware("http")(security_manager.auth_middleware)           
app.middleware("http")(security_manager.rate_limit_middleware)
app.middleware("http")(security_manager.security_headers_middleware)

# Include routers
app.include_router(config_router)

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_handler(websocket)

# Basic endpoints
@app.get("/")
async def root():
    return {
        "message": "Job Applier FastAPI Server",
        "version": "1.0.0",
        "websocket_endpoint": "/ws",
        "config_endpoints": [
            "/api/update-personals",
            "/api/get-personals", 
            "/api/update-secrets",
            "/api/get-secrets"
        ],
        "security": "enabled"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "active_connections": manager.get_connection_count(),
        "modules": ["config_router", "websocket_manager", "auth", "security"]
    }

# Server startup
if __name__ == "__main__":
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8001, 
        reload=True,
        log_level="info"
    )