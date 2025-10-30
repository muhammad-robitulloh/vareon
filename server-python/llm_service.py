import httpx
import os
import logging
from dotenv import load_dotenv
from typing import List, Dict, Any

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemini-pro")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# In-memory storage for conversation history
# In a real app, this would be persisted in a database or a dedicated session store
conversation_histories: Dict[str, List[Dict[str, str]]] = {}

# Limit the number of turns in a conversation for this prototype
MAX_CONVERSATION_TURNS = 5

async def get_openrouter_completion(user_id: str, message: str) -> str:
    if not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "YOUR_OPENROUTER_API_KEY":
        logger.error("OPENROUTER_API_KEY is not set or is default. Please configure it in .env")
        return "Error: OpenRouter API key not configured."

    # Initialize history for the user if it doesn't exist
    if user_id not in conversation_histories:
        conversation_histories[user_id] = []

    # Add user's message to history
    conversation_histories[user_id].append({"role": "user", "content": message})

    # Trim history to MAX_CONVERSATION_TURNS
    if len(conversation_histories[user_id]) > MAX_CONVERSATION_TURNS:
        # Keep the last MAX_CONVERSATION_TURNS messages
        conversation_histories[user_id] = conversation_histories[user_id][-MAX_CONVERSATION_TURNS:]

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": conversation_histories[user_id]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{OPENROUTER_BASE_URL}/chat/completions", headers=headers, json=payload, timeout=30.0)
            response.raise_for_status() # Raise an exception for 4xx or 5xx responses
            
            response_data = response.json()
            if "choices" in response_data and response_data["choices"]:
                llm_response_content = response_data["choices"][0]["message"]["content"]
                # Add LLM's response to history
                conversation_histories[user_id].append({"role": "assistant", "content": llm_response_content})
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

# Function to clear conversation history for a user
def clear_conversation_history(user_id: str):
    if user_id in conversation_histories:
        del conversation_histories[user_id]
        logger.info(f"Conversation history cleared for user: {user_id}")

