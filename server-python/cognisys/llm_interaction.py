from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional # Added Optional
import json
import os
import httpx
from fastapi import HTTPException

from database import LLMProvider, LLMModel, RoutingRule, User # Changed from ..database
from .crud import decrypt_api_key # Import the decrypt function

# Placeholder for LLM API call function
async def call_llm_api(provider: LLMProvider, model_name: str, prompt: str, api_key: str) -> Dict[str, Any]:
    # This is a simplified example for OpenRouter.
    # Real implementation would need to handle different LLM providers and their specific API formats.
    headers = {
        "Authorization": f"Bearer {api_key}",
        "HTTP-Referer": "http://localhost:3000", # Replace with your actual app URL
        "X-Title": "Vareon", # Replace with your actual app name
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": prompt}]
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{provider.base_url}/chat/completions", headers=headers, json=payload, timeout=60.0)
            response.raise_for_status()
            response_data = response.json()
            
            # Extract content and token usage
            content = response_data['choices'][0]['message']['content']
            prompt_tokens = response_data['usage']['prompt_tokens']
            completion_tokens = response_data['usage']['completion_tokens']
            total_tokens = response_data['usage']['total_tokens']

            return {
                "content": content,
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "model_used": model_name
            }
    except httpx.RequestError as e:
        print(f"HTTPX Request Error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM API request failed: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTPX Status Error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"LLM API returned an error: {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred during LLM API call: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


def detect_intent(prompt: str) -> str:
    # Simple keyword-based intent detection
    prompt_lower = prompt.lower()
    if "weather" in prompt_lower:
        return "get_weather"
    if "agent" in prompt_lower or "myntrix" in prompt_lower:
        return "myntrix_agent_interaction"
    if "workflow" in prompt_lower or "neosyntis" in prompt_lower:
        return "neosyntis_workflow_interaction"
    if "llm" in prompt_lower or "model" in prompt_lower or "chat" in prompt_lower:
        return "llm_chat"
    return "general_query"

def evaluate_routing_rules(db: Session, user: User, intent: str, prompt: str) -> Optional[LLMModel]:
    # Fetch all routing rules for the user, ordered by priority
    rules = db.query(RoutingRule).filter(RoutingRule.owner_id == str(user.id)).order_by(RoutingRule.priority.desc()).all()

    for rule in rules:
        # Simple condition evaluation (can be expanded to a mini-language parser)
        # For now, let's assume conditions are simple string matches or "true"
        condition_met = False
        if rule.condition.lower() == "true":
            condition_met = True
        elif rule.condition.lower() == intent.lower(): # Match intent
            condition_met = True
        elif rule.condition.lower() in prompt.lower(): # Keyword in prompt
            condition_met = True
        # Add more sophisticated condition evaluation here

        if condition_met:
            # Find the target model
            model = db.query(LLMModel).filter(LLMModel.model_name == rule.target_model).first()
            if model:
                return model
    return None

async def process_chat_request(db: Session, user: User, prompt: str) -> Dict[str, Any]:
    # 1. Intent Detection
    intent = detect_intent(prompt)
    print(f"Detected intent: {intent}")

    # 2. Rule Evaluation to select model
    selected_llm_model = evaluate_routing_rules(db, user, intent, prompt)

    if not selected_llm_model:
        # Fallback to a default model if no rule matches
        selected_llm_model = db.query(LLMModel).filter(LLMModel.model_name == "google/gemini-pro").first()
        if not selected_llm_model:
            raise HTTPException(status_code=500, detail="No default LLM model configured.")
        print(f"No routing rule matched, falling back to default model: {selected_llm_model.model_name}")
    else:
        print(f"Routing rule matched, selected model: {selected_llm_model.model_name}")

    # Get the provider for the selected model
    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == selected_llm_model.provider_id).first()
    if not llm_provider:
        raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {selected_llm_model.model_name}")

    # Decrypt API key
    api_key = decrypt_api_key(llm_provider.api_key_encrypted)

    # 3. LLM Interaction
    llm_response = await call_llm_api(llm_provider, selected_llm_model.model_name, prompt, api_key)

    # 4. Token Counting (already handled in call_llm_api)

    # 5. Visualization Data Generation (simplified for now)
    # This would typically involve more complex logic to show the flow
    nodes = [
        {"id": "user_prompt", "type": "input", "data": {"label": f"User Prompt: {prompt[:20]}..."}, "position": {"x": 0, "y": 0}},
        {"id": "intent_detection", "data": {"label": f"Intent: {intent}"}, "position": {"x": 0, "y": 100}},
        {"id": "rule_evaluation", "data": {"label": f"Rule Evaluation (Model: {selected_llm_model.model_name})"}, "position": {"x": 0, "y": 200}},
        {"id": "llm_call", "data": {"label": f"LLM Call ({selected_llm_model.model_name})"}, "position": {"x": 0, "y": 300}},
        {"id": "llm_response", "type": "output", "data": {"label": f"LLM Response: {llm_response['content'][:20]}..."}, "position": {"x": 0, "y": 400}},
    ]
    edges = [
        {"id": "e1-2", "source": "user_prompt", "target": "intent_detection"},
        {"id": "e2-3", "source": "intent_detection", "target": "rule_evaluation"},
        {"id": "e3-4", "source": "rule_evaluation", "target": "llm_call"},
        {"id": "e4-5", "source": "llm_call", "target": "llm_response"},
    ]

    return {
        "response_content": llm_response['content'],
        "model_used": llm_response['model_used'],
        "tokens_used": llm_response['total_tokens'],
        "visualization_data": {"nodes": nodes, "edges": edges}
    }