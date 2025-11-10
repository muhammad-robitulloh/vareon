import httpx
import os
import logging
from dotenv import load_dotenv
import uuid # Import uuid
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database import Agent as DBAgent, Workflow as DBWorkflow, ChatMessage as DBChatMessage, Conversation as DBConversation, User as DBUser, LLMProvider, LLMModel # Import necessary DB models
from datetime import datetime, timezone # Import datetime and timezone for utcnow

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-pro")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

async def get_openrouter_completion(user_id: str, message: str, model_name: Optional[str] = None, db: Optional[Session] = None, owner_id: Optional[str] = None, conversation_id: Optional[uuid.UUID] = None) -> str:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY":
        logger.error("OPENROUTER_API_KEY is not set or is default. Please configure it in .env")
        return "Error: OpenRouter API key not configured."

    messages_payload = []

    # Fetch conversation history from the database if conversation_id is provided
    if db and conversation_id and owner_id:
        conversation_messages = db.query(DBChatMessage).filter(
            DBChatMessage.conversation_id == str(conversation_id),
            DBChatMessage.user_id == owner_id
        ).order_by(DBChatMessage.timestamp).all()
        
        for msg in conversation_messages:
            messages_payload.append({"role": msg.sender, "content": msg.message_content})
    
    # --- Arcana Contextual Awareness ---
    context_message = ""
    if db and owner_id:
        if "workflow status" in message.lower():
            workflows = db.query(DBWorkflow).filter(DBWorkflow.owner_id == owner_id).all()
            if workflows:
                context_message += "Current workflows:\n"
                for wf in workflows:
                    context_message += f"- {wf.name} (ID: {wf.id}, Status: {wf.status})\n"
            else:
                context_message += "No workflows found.\n"
        
        if "agent status" in message.lower():
            agents = db.query(DBAgent).filter(DBAgent.owner_id == owner_id).all()
            if agents:
                context_message += "Current agents:\n"
                for agent in agents:
                    context_message += f"- {agent.name} (ID: {agent.id}, Type: {agent.type}, Status: {agent.status})\n" # Corrected agent.agent_type to agent.type
            else:
                context_message += "No agents found.\n"
    
    # Prepend context to the user's message if available
    if context_message:
        full_message = f"{context_message}\nUser query: {message}"
    else:
        full_message = message

    # Add user's current message to the payload
    messages_payload.append({"role": "user", "content": full_message})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name if model_name else OPENROUTER_MODEL,
        "messages": messages_payload
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30.0)
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses
            
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                llm_response_content = response_data["choices"][0]["message"]["content"]
                # Add LLM's response to history (REMOVED - now handled by main.py)
                return llm_response_content
            else:
                logger.error(f"OpenRouter API response missing choices: {response_data}")
                return "Error: Could not get a valid response from LLM."
    except httpx.RequestError as e:
        logger.error(f"OpenRouter API request failed: {e}")
        return f"Error: Failed to connect to OpenRouter API. {e}"
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter API returned an error: {e.response.status_code} - {e.response.text}")
        return f"Error: OpenRouter API returned an error. Status: {e.response.status_code}. Details: {e.response.text}"
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        return f"Error: An unexpected error occurred. {e}"

# Function to clear conversation history for a user (REMOVED - now handled by main.py)
# def clear_conversation_history(db: Session, owner_id: str, conversation_id: Optional[uuid.UUID] = None):
#     if conversation_id:
#         db.query(DBChatMessage).filter(DBChatMessage.conversation_id == str(conversation_id), DBChatMessage.user_id == owner_id).delete()
#         db.query(DBConversation).filter(DBConversation.id == str(conversation_id), DBConversation.user_id == owner_id).delete()
#         db.commit()
#         logger.info(f"Conversation history cleared for conversation: {conversation_id} for user: {owner_id}")
#     else:
#         # Clear all conversations and messages for the user
#         conversations = db.query(DBConversation).filter(DBConversation.user_id == owner_id).all()
#         for conv in conversations:
#             db.query(DBChatMessage).filter(DBChatMessage.conversation_id == str(conv.id)).delete()
#             db.delete(conv)
#         db.commit()
#         logger.info(f"All conversation history cleared for user: {owner_id}")

async def utilize_arcana_llm_task(llm_task: str, input_data: str, user_id: str, db: Session) -> str:
    """
    Placeholder for Arcana LLM task utilization.
    This function would interpret the llm_task and input_data to
    perform specific LLM operations, potentially beyond simple completion.
    """
    logger.info(f"Utilizing Arcana LLM task: {llm_task} with input: {input_data} for user: {user_id}")
    # For now, we'll just return a mock response
    return f"Arcana processed LLM task '{llm_task}' with data '{input_data}'. (Mocked response) Run in {datetime.now(timezone.utc)}"

async def trigger_myntrix_agent_task(agent_id: str, task_details: Dict[str, Any], user_id: str, db: Session) -> bool:
    """
    Placeholder for triggering a Myntrix agent task.
    """
    logger.info(f"Triggering Myntrix agent {agent_id} for user {user_id} with details: {task_details}")
    # For now, just simulate success
    return True

async def manage_myntrix_model_task(model_id: str, operation: str, user_id: str, db: Session) -> bool:
    """
    Placeholder for managing a Myntrix ML model task.
    """
    logger.info(f"Managing Myntrix ML model {model_id} with operation {operation} for user {user_id}")
    # For now, just simulate success
    return True