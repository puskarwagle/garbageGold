#main.py
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import json
import uvicorn
from fastapi import HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
import os

app = FastAPI(title="Job Applier API", version="1.0.0")

# Add the fastHelpers directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'fastHelpers'))

from fastHelpers.config_updater import ConfigUpdater

# Pydantic model for the form data
class PersonalsData(BaseModel):
    first_name: str
    middle_name: Optional[str] = ""
    last_name: str
    phone_number: str
    current_city: Optional[str] = ""
    street: Optional[str] = ""
    state: Optional[str] = ""
    zipcode: Optional[str] = ""
    country: Optional[str] = ""
    ethnicity: Optional[str] = ""
    gender: Optional[str] = ""
    disability_status: Optional[str] = ""
    veteran_status: Optional[str] = ""

# Initialize config updater
config_updater = ConfigUpdater()

@app.post("/api/update-personals")
async def update_personals(data: PersonalsData):
    """Update sersonals.py with form data"""
    try:
        # Convert Pydantic model to dict
        form_data = data.dict()
        
        # Create backup first
        backup_path = config_updater.backup_config("sersonals.py")
        
        # Update the file
        result = config_updater.update_personals(form_data)
        
        if result["status"] == "success":
            return {
                "success": True,
                "message": result["message"],
                "backup_created": backup_path,
                "file_path": result["file_path"]
            }
        else:
            raise HTTPException(status_code=500, detail=result["message"])
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.get("/api/get-personals")
async def get_current_personals():
    """Get current sersonals.py configuration"""
    try:
        config_data = config_updater.read_current_personals()
        
        if "error" in config_data:
            raise HTTPException(status_code=404, detail=config_data["error"])
        
        return {"success": True, "data": config_data}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")

@app.post("/api/restore-personals-backup")
async def restore_personals_backup():
    """Restore sersonals.py from backup"""
    try:
        import shutil
        from pathlib import Path
        
        config_path = Path(__file__).parent / "config"
        source_backup = config_path / "sersonals.py.backup"
        target_file = config_path / "sersonals.py"
        
        if not source_backup.exists():
            raise HTTPException(status_code=404, detail="No backup file found")
        
        shutil.copy2(source_backup, target_file)
        
        return {
            "success": True,
            "message": "sersonals.py restored from backup successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")


# CORS for Laravel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],  # Laravel default
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"Client disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Connection died, remove it
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    
    # Send welcome message
    await manager.send_personal_message(
        json.dumps({
            "type": "connection",
            "message": "FastAPI server says: Connection established ⚡",
            "timestamp": asyncio.get_event_loop().time()
        }), 
        websocket
    )
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            print(f"Received: {message_data}")
            
            # Echo back with server response
            response = {
                "type": "echo",
                "original": message_data,
                "server_response": f"Server received: {message_data.get('message', 'No message')}",
                "timestamp": asyncio.get_event_loop().time()
            }
            
            await manager.send_personal_message(json.dumps(response), websocket)
            
            # If client says hello, respond with special message
            if message_data.get("message", "").lower() == "hello gui":
                special_response = {
                    "type": "greeting",
                    "message": "Hello Laravel frontend! 🚀 WebSocket is working perfectly.",
                    "status": "connected",
                    "timestamp": asyncio.get_event_loop().time()
                }
                await manager.send_personal_message(json.dumps(special_response), websocket)
    
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Job Applier FastAPI Server", "websocket_endpoint": "/ws"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "connections": len(manager.active_connections)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=True)
