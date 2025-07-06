# main.py - Modular FastAPI Application (NO SECURITY)
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import sys
import os
import subprocess
import asyncio
from pathlib import Path

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
        "script_endpoints": [
            "/api/run-bot",
            "/api/stop-bot",
            "/api/bot-status"
        ],
        "security": "DISABLED"
    }

# Global process tracker
bot_process = None

@app.post("/api/run-bot")
async def run_bot():
    global bot_process
    
    try:
        # Check if bot is already running
        if bot_process and bot_process.poll() is None:
            return {"status": "error", "message": "Bot is already running"}
        
        # Updated path to modular script
        script_path = Path(__file__).parent / "app" / "linkedinBot" / "linkedinRun.py"
        if not script_path.exists():
            raise HTTPException(status_code=404, detail="linkedinRun.py not found")
        
        # Start the bot process
        bot_process = subprocess.Popen([
            "python3.13", str(script_path)
        ], cwd=str(script_path.parent))
        
        return {
            "status": "success", 
            "message": "Bot started successfully",
            "pid": bot_process.pid
        }
        
    except Exception as e:
        return {"status": "error", "message": f"Failed to start bot: {str(e)}"}

@app.post("/api/stop-bot")
async def stop_bot():
    global bot_process
    
    try:
        if bot_process and bot_process.poll() is None:
            bot_process.terminate()
            bot_process.wait(timeout=10)  # Wait up to 10 seconds
            return {"status": "success", "message": "Bot stopped successfully"}
        else:
            return {"status": "error", "message": "Bot is not running"}
    except Exception as e:
        return {"status": "error", "message": f"Failed to stop bot: {str(e)}"}

@app.get("/api/bot-status")
async def bot_status():
    global bot_process
    
    if bot_process and bot_process.poll() is None:
        return {
            "status": "running",
            "pid": bot_process.pid,
            "message": "Bot is currently running"
        }
    else:
        return {
            "status": "stopped",
            "message": "Bot is not running"
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