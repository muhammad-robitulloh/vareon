from sqlalchemy.orm import Session
from typing import Dict, Any

from server_python.database import User as DBUser
from . import llm_interaction

class ChatService:
    def __init__(self, db: Session):
        self.db = db

    async def handle_message(self, user: DBUser, prompt: str, session_data: Dict[str, Any], agent_id: str | None = None) -> Dict[str, Any]:
        """
        Handles an incoming chat message, processes it with tool-calling capabilities, and returns a response.
        """
        print(f"ChatService handling message for user {user.id}: '{prompt}' with agent_id: {agent_id}")

        response_data = await llm_interaction.process_chat_request(
            db=self.db, 
            user=user, 
            prompt=prompt,
            session_data=session_data,
            agent_id=agent_id
        )
        
        return response_data

# You can create a single instance or create one per request depending on dependency management
# For now, we'll instantiate it where needed.
