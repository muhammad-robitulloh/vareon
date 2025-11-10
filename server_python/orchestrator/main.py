from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, status
from sqlalchemy.orm import Session
import uuid
import json
import os

from .connection_manager import manager
from .event_handler import event_handler
from server_python.auth import get_current_websocket_user, User
from server_python.database import get_db, User as DBUser

app = FastAPI()

# Determine the project root directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir)) # Goes up two levels

# Helper to get the DB user from the authenticated user
def get_db_user(user: User = Depends(get_current_websocket_user), db: Session = Depends(get_db)) -> DBUser:
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    # This should not happen if token is valid, but as a safeguard:
    if not db_user:
        raise WebSocketDisconnect(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
    return db_user


@app.websocket("/ws/arcana/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    session_id: str,
    current_user: DBUser = Depends(get_db_user), # Use the new dependency
    db: Session = Depends(get_db)
):
    await manager.connect(session_id, websocket)
    await event_handler.initialize_session(session_id, current_user, db, project_root)
    
    try:
        while True:
            data = await websocket.receive_text()
            try:
                event = json.loads(data)
                response = await event_handler.handle_event(session_id, event)
                if response: # Only send if a response is generated
                    await manager.send_to_session(session_id, json.dumps(response))
            except json.JSONDecodeError:
                error_response = {"type": "error", "payload": {"message": "Invalid JSON format"}}
                await manager.send_to_session(session_id, json.dumps(error_response))
            except Exception as e:
                error_response = {"type": "error", "payload": {"message": f"Error handling event: {str(e)}"}}
                await manager.send_to_session(session_id, json.dumps(error_response))

    except WebSocketDisconnect:
        print(f"Session {session_id} disconnected.")
        manager.disconnect(session_id)
        await event_handler.cleanup_session(session_id)

# This is just for standalone testing of the orchestrator
@app.get("/")
def read_root():
    return {"Hello": "Orchestrator"}
