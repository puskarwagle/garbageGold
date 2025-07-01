# main.py - Modular FastAPI Application

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add fastHelpers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'fastHelpers'))

# Import modular components
from fastHelpers.config_router import router as config_router
from fastHelpers.websocket_manager import websocket_handler, manager

# Initialize FastAPI app
app = FastAPI(
    title="Job Applier API", 
    version="1.0.0",
    description="Modular FastAPI server for job application automation"
)

# CORS middleware for Laravel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "active_connections": manager.get_connection_count(),
        "modules": ["config_router", "websocket_manager"]
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