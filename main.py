# main.py - Modular FastAPI Application (NO SECURITY)
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os

# Add fastHelpers to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'fastHelpers'))

# Import modular components
from fastHelpers.config_router import router as config_router
from fastHelpers.websocket_manager import websocket_handler

# Initialize FastAPI app 👈
app = FastAPI(
    title="QuestBot",
    version="1.0.0",
    description="Modular FastAPI server for job application automation"
)

# Basic CORS only - fuck everything else
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# REGISTER THE CONFIG ROUTER - THIS WAS MISSING
app.include_router(config_router)

# WebSocket endpoint - direct connection
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
            "/api/get-secrets",
            "/api/update-bot-config",
            "/api/update-questions",
            "/api/get-questions",
            "/api/update-search",
            "/api/get-search",
            "/api/update-settings",
            "/api/get-settings"
        ],
        "security": "DISABLED"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "modules": ["config_router", "websocket_manager"],
        "security": "DISABLED"
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