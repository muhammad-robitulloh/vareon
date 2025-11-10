import asyncio
import json
from typing import Dict, Any
from sqlalchemy.orm import Session

from terminal.service import TerminalService
from cognisys.service import ChatService
from .connection_manager import manager
from database import User as DBUser

class EventHandler:
    def __init__(self):
        self.sessions: Dict[str, Dict[str, Any]] = {}

    async def initialize_session(self, session_id: str, user: DBUser, db: Session, project_root: str):
        if session_id not in self.sessions:
            terminal_service = TerminalService(session_id, str(user.id))
            chat_service = ChatService(db) # ChatService needs the db session
            
            self.sessions[session_id] = {
                "user": user,
                "db": db,
                "terminal": terminal_service,
                "chat": chat_service,
                "terminal_task": None,
            }
            
            master_reader = await terminal_service.start_session(project_root)
            
            terminal_task = asyncio.create_task(
                self.forward_shell_output(session_id, master_reader)
            )
            self.sessions[session_id]["terminal_task"] = terminal_task
            
            print(f"Initialized services for session: {session_id}")

    async def cleanup_session(self, session_id: str):
        if session_id in self.sessions:
            session_data = self.sessions[session_id]
            if session_data["terminal_task"]:
                session_data["terminal_task"].cancel()
            await session_data["terminal"].close_session()
            
            del self.sessions[session_id]
            print(f"Cleaned up services for session: {session_id}")

    async def forward_shell_output(self, session_id: str, reader):
        """Reads from the shell's output and sends it to the WebSocket client."""
        try:
            while True:
                output = await asyncio.to_thread(reader.read, 1024)
                if not output:
                    print(f"Shell output stream for session {session_id} ended.")
                    break
                
                response = {
                    "type": "shell_output",
                    "payload": {"data": output.decode(errors='ignore')}
                }
                await manager.send_to_session(session_id, json.dumps(response))
        except Exception as e:
            print(f"Error in forward_shell_output for session {session_id}: {e}")
        finally:
            print(f"forward_shell_output task for session {session_id} finishing.")


    async def handle_event(self, session_id: str, event: Dict[str, Any]):
        event_type = event.get("type")
        payload = event.get("payload", {})
        
        print(f"Handling event '{event_type}' for session '{session_id}'")
        
        session_data = self.sessions.get(session_id)
        if not session_data:
            return {"type": "error", "payload": {"message": "Session not initialized."}}

        if event_type == "shell_input":
            session_data["terminal"].write(payload.get("data", ""))
            return None
        elif event_type == "shell_resize":
            cols = payload.get("cols")
            rows = payload.get("rows")
            if cols and rows:
                session_data["terminal"].resize(cols, rows)
            return None
        elif event_type == "chat_message":
            chat_service = session_data["chat"]
            user = session_data["user"]
            prompt = payload.get("prompt", "")
            
            # Pass the entire session_data dictionary
            response_data = await chat_service.handle_message(user, prompt, session_data)
            
            return {
                "type": "chat_response",
                "payload": response_data
            }
        elif event_type == "start_agent":
            # This is where we would call the Agent service
            pass
        else:
            print(f"Unknown event type: {event_type}")

        # This is a placeholder response for non-shell events
        return {
            "type": "response",
            "for_event": event_type,
            "payload": {"status": "received"}
        }

event_handler = EventHandler()
