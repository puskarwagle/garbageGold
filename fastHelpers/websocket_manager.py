# fastHelpers/websocket_manager.py

from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
from typing import List

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"Client connected. Total: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            print(f"Client disconnected. Total: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Error sending message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str):
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception:
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for conn in disconnected:
            self.disconnect(conn)
    
    def get_connection_count(self) -> int:
        return len(self.active_connections)

# Global manager instance
manager = ConnectionManager()

async def websocket_handler(websocket: WebSocket):
    """Main WebSocket handler"""
    await manager.connect(websocket)
    
    # Send welcome message
    welcome_msg = {
        "type": "connection",
        "message": "FastAPI server says: Connection established ⚡",
        "timestamp": asyncio.get_event_loop().time()
    }
    await manager.send_personal_message(json.dumps(welcome_msg), websocket)
    
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
            
            # Special greeting handler
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
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)