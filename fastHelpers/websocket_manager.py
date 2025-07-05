from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
import time

async def websocket_handler(websocket: WebSocket):
    """Main WebSocket handler - NO AUTH BULLSHIT"""
    
    # Accept connection immediately - fuck token validation
    await websocket.accept()
    print(f"WebSocket connected - no auth required")

    # Send welcome message
    welcome_msg = {
        "type": "connection",
        "message": "FastAPI server says: Connection established ⚡ (NO AUTH)",
        "timestamp": time.time()
    }
    await websocket.send_text(json.dumps(welcome_msg))

    try:
        while True:
            # Wait for client message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            print(f"Received: {message_data}")

            # Echo response
            response = {
                "type": "echo",
                "original": message_data,
                "server_response": f"Server received: {message_data.get('message', 'No message')}",
                "timestamp": time.time()
            }
            await websocket.send_text(json.dumps(response))

            # Special response for "hello gui"
            if message_data.get("message", "").lower() == "hello gui":
                special_response = {
                    "type": "greeting",
                    "message": "Hello Laravel frontend! 🚀 WebSocket is working perfectly (NO AUTH).",
                    "status": "connected",
                    "timestamp": time.time()
                }
                await websocket.send_text(json.dumps(special_response))

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        # Cleanup happens automatically when function ends
        pass