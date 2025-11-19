from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional # Added Optional
import json
import os
import httpx
from fastapi import HTTPException, BackgroundTasks

from server_python.database import LLMProvider, LLMModel, RoutingRule, User # Changed from ..database
from .crud import decrypt_api_key # Import the decrypt function
from .schemas import IntentDetectionResponse # Import the new schema
from server_python.llm_service import get_openrouter_completion # Import the generic LLM completion service

# Placeholder for LLM API call function
async def call_llm_api(
    provider: LLMProvider, 
    model_name: str, 
    api_key: str, 
    messages: List[Dict[str, Any]], # Now required
    tools: Optional[List[Dict[str, Any]]] = None,
    temperature: float = 0.7, # Add temperature
    top_p: float = 1.0 # Add top_p
) -> Dict[str, Any]:
    headers = {}
    payload = {}
    api_endpoint = ""
    
    # Handle mock provider for tests
    if "mock-llm.com" in provider.base_url.lower():
        # This is a mock call, return a mock response
        # This part will be overridden by mocker in tests, but it's good to have a default
        return {"message": {"content": "Mock LLM response"}}

    # Determine provider type and configure request accordingly
    if "openrouter" in provider.base_url.lower(): # Assuming OpenRouter for now
        print(f"DEBUG: OpenRouter API Key (first 5 chars): {api_key[:5] if api_key else 'None'}")
        print(f"DEBUG: OpenRouter Model Name: {model_name}")
        headers = {
            "HTTP-Referer": "http://localhost:3000", # Replace with your actual app URL
            "X-Title": "Vareon", # Replace with your actual app name
            "Content-Type": "application/json"
        }
        if api_key: # Only add Authorization header if api_key is not empty
            headers["Authorization"] = f"Bearer {api_key}"
        payload = {
            "model": model_name,
            "messages": messages,
            "temperature": temperature,
            "top_p": top_p
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        api_endpoint = f"{provider.base_url.rstrip('/')}/chat/completions" # Corrected OpenRouter API endpoint
        print(f"DEBUG: OpenRouter API Endpoint: {api_endpoint}")
        print(f"DEBUG: OpenRouter Payload: {json.dumps(payload, indent=2)}")
    elif "generativelanguage.googleapis.com" in provider.base_url.lower(): # Example for Google Gemini
        headers = {
            "Content-Type": "application/json"
        }
        # Gemini expects 'contents' with 'parts'
        gemini_contents = []
        for msg in messages:
            if msg["role"] == "user":
                gemini_contents.append({"parts": [{"text": msg["content"]}]})
            elif msg["role"] == "assistant":
                gemini_contents.append({"parts": [{"text": msg["content"]}]})
            # Gemini doesn't directly support system role in the same way,
            # so system messages might need to be prepended to the first user message or handled differently.
            # For simplicity, we'll just pass user/assistant messages.
        
        payload = {
            "contents": gemini_contents,
            "generationConfig": {
                "temperature": temperature,
                "topP": top_p
            }
        }
        # Assuming model_name is like "gemini-pro" and base_url is like "https://generativelanguage.googleapis.com/v1beta"
        api_endpoint = f"{provider.base_url}/models/{model_name}:generateContent?key={api_key}"
    else:
        raise HTTPException(status_code=500, detail=f"Unsupported LLM provider: {provider.name}")

    try:
        async with httpx.AsyncClient() as client:
            if "generativelanguage.googleapis.com" in provider.base_url.lower():
                response = await client.post(api_endpoint, headers=headers, json=payload, timeout=60.0)
            else: # Default to JSON payload for other providers like OpenRouter
                response = await client.post(api_endpoint, headers=headers, json=payload, timeout=60.0)
            
            response.raise_for_status()
            response_data = response.json()
            
            # Flexible response handling
            if "openrouter" in provider.base_url.lower():
                message = response_data['choices'][0]['message']
                usage = response_data.get('usage', {})
                return {
                    "message": message, # This can contain 'content' or 'tool_calls'
                    "prompt_tokens": usage.get('prompt_tokens', 0),
                    "completion_tokens": usage.get('completion_tokens', 0),
                    "total_tokens": usage.get('total_tokens', 0),
                    "model_used": model_name
                }
            elif "generativelanguage.googleapis.com" in provider.base_url.lower():
                content = response_data['candidates'][0]['content']['parts'][0]['text']
                # Placeholder for token usage - Gemini API usually provides this
                # For now, estimate based on content length
                prompt_tokens = sum(len(msg["content"].split()) for msg in messages if "content" in msg)
                completion_tokens = len(content.split())
                return {
                    "message": {"role": "assistant", "content": content},
                    "prompt_tokens": prompt_tokens,
                    "completion_tokens": completion_tokens,
                    "total_tokens": prompt_tokens + completion_tokens,
                    "model_used": model_name
                }
    except httpx.RequestError as e:
        print(f"HTTPX Request Error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM API request failed: {e.__class__.__name__} - {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTPX Status Error: {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=e.response.status_code, detail=f"LLM API returned an error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"An unexpected error occurred during LLM API call: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


async def detect_intent(db: Session, user: User, prompt: str) -> IntentDetectionResponse:
    """
    Detects the intent of the user's prompt using an LLM.
    """
    # 1. Select an LLM model suitable for intent detection
    # Look for a model specifically tagged for 'intent_detection' role
    intent_model = db.query(LLMModel).filter(LLMModel.role == "intent_detection", LLMModel.is_active == True).first()
    if not intent_model:
        # Fallback to a general chat model if no specific intent model is found
        intent_model = db.query(LLMModel).filter(LLMModel.type == "chat", LLMModel.is_active == True).first()
        if not intent_model:
            raise HTTPException(status_code=500, detail="No active LLM model found for intent detection or general chat.")

    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == intent_model.provider_id).first()
    if not llm_provider:
        raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {intent_model.model_name}")
    
    print(f"DEBUG: LLM Provider for intent detection: {llm_provider.__dict__}")
from server_python.database import LLMProvider, LLMModel, RoutingRule, User, SystemPrompt, UserLLMPreference # Import UserLLMPreference
from .crud import decrypt_api_key, get_system_prompt_by_name # Import the decrypt function and new crud function
from .schemas import IntentDetectionResponse # Import the new schema
from server_python.llm_service import get_openrouter_completion # Import the generic LLM completion service

# ... (existing code) ...

async def detect_intent(db: Session, user: User, prompt: str) -> IntentDetectionResponse:
    """
    Detects the intent of the user's prompt using an LLM.
    """
    # 1. Select an LLM model suitable for intent detection
    # Look for a model specifically tagged for 'intent_detection' role
    intent_model = db.query(LLMModel).filter(LLMModel.role == "intent_detection", LLMModel.is_active == True).first()
    if not intent_model:
        # Fallback to a general chat model if no specific intent model is found
        intent_model = db.query(LLMModel).filter(LLMModel.type == "chat", LLMModel.is_active == True).first()
        if not intent_model:
            raise HTTPException(status_code=500, detail="No active LLM model found for intent detection or general chat.")

    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == intent_model.provider_id).first()
    if not llm_provider:
        raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {intent_model.model_name}")
    
    api_key = decrypt_api_key(llm_provider.api_key_encrypted)

    # 2. Construct the prompt for intent detection
    # Fetch system prompt from database
    db_system_prompt = get_system_prompt_by_name(db, "intent_detection_prompt")
    if db_system_prompt:
        system_prompt_content = db_system_prompt.content
    else:
        # Fallback hardcoded prompt if not found in DB
        system_prompt_content = """You are an AI intent detection system. Your task is to classify user prompts into one of the following categories:
- 'shell_command': The user wants to execute a command in a terminal or get a shell command.
- 'code_generation': The user wants to generate code, get code examples, or debug code.
- 'file_operation': The user wants to perform operations on files (create, read, write, delete, list, move, etc.).
- 'conversation': The user is engaging in a general conversation, asking questions, or seeking information.
- 'arcana_agent_management': The user is asking to create, list, update, or delete Arcana agents.
- 'unknown': The intent cannot be clearly determined from the provided categories.

Provide your response in a JSON format with the following keys:
- 'intent': The detected intent category.
- 'confidence': A float between 0.0 and 1.0 indicating your confidence in the detection.
- 'reasoning': A brief explanation of why you chose this intent.

Example JSON output:
{"intent": "shell_command", "confidence": 0.95, "reasoning": "The prompt explicitly asks to 'run a command'."}
{"intent": "code_generation", "confidence": 0.88, "reasoning": "The prompt mentions 'Python code' and 'function'."}
{"intent": "conversation", "confidence": 0.70, "reasoning": "The prompt is a general greeting."}
{"intent": "file_operation", "confidence": 0.90, "reasoning": "The prompt asks to 'create a new file'."}
{"intent": "arcana_agent_management", "confidence": 0.92, "reasoning": "The prompt asks to 'list my agents'."}
"""
    user_prompt_message = {"role": "user", "content": f"Classify the following user prompt: '{prompt}'"}
    
    messages = [
        {"role": "system", "content": system_prompt_content},
        user_prompt_message
    ]

    # 3. Call the LLM
    try:
        llm_response_data = await call_llm_api(
            provider=llm_provider,
            model_name=intent_model.model_name,
            messages=messages,
            api_key=api_key,
            temperature=0.2, # Lower temperature for more deterministic output
            top_p=0.9
        )
        
        llm_content = llm_response_data["message"]["content"]
        print(f"DEBUG: LLM content for intent detection: {llm_content}") # <--- ADD THIS LINE
        
        # 4. Parse the LLM's JSON response
        parsed_response = json.loads(llm_content)
        
        return IntentDetectionResponse(
            intent=parsed_response.get("intent", "unknown"),
            confidence=parsed_response.get("confidence", 0.5),
            reasoning=parsed_response.get("reasoning", "LLM-based intent detection.")
        )
    except json.JSONDecodeError:
        print(f"LLM response was not valid JSON: {llm_content}")
        return IntentDetectionResponse(intent="unknown", confidence=0.3, reasoning="LLM response not valid JSON.")
    except Exception as e:
        print(f"Error during LLM intent detection: {e}")
        return IntentDetectionResponse(intent="unknown", confidence=0.1, reasoning=f"Error: {e}")


def _evaluate_condition(condition_obj: Dict[str, Any], intent: str, prompt: str) -> bool:
    if "all" in condition_obj: # AND combinator
        return all(_evaluate_condition(sub_cond, intent, prompt) for sub_cond in condition_obj["all"])
    elif "any" in condition_obj: # OR combinator
        return any(_evaluate_condition(sub_cond, intent, prompt) for sub_cond in condition_obj["any"])
    else: # Individual condition
        fact = condition_obj.get("fact")
        operator = condition_obj.get("operator")
        value = condition_obj.get("value")

        if fact == "intent":
            target_value = intent
        elif fact == "prompt":
            target_value = prompt
        else:
            return False # Unknown fact

        if operator == "equals":
            return target_value.lower() == str(value).lower()
        elif operator == "contains":
            return str(value).lower() in target_value.lower()
        elif operator == "startsWith":
            return target_value.lower().startswith(str(value).lower())
        elif operator == "endsWith":
            return target_value.lower().endswith(str(value).lower())
        else:
            return False # Unknown operator

def evaluate_routing_rules(db: Session, user: User, intent: str, prompt: str) -> Optional[LLMModel]:
    # Fetch all routing rules for the user, ordered by priority
    rules = db.query(RoutingRule).filter(RoutingRule.owner_id == str(user.id)).order_by(RoutingRule.priority.desc()).all()

    for rule in rules:
        try:
            condition_obj = json.loads(rule.condition)
            if _evaluate_condition(condition_obj, intent, prompt):
                # Find the target model
                model = db.query(LLMModel).filter(LLMModel.model_name == rule.target_model).first()
                if model:
                    return model
        except json.JSONDecodeError:
            print(f"Warning: Routing rule {rule.id} has invalid JSON condition: {rule.condition}")
            continue # Skip this rule if condition is malformed JSON
        except Exception as e:
            print(f"Error evaluating routing rule {rule.id}: {e}")
            continue
    return None

from .tools import tools_schema, tool_registry
import asyncio
import json

async def process_chat_request(
    db: Session, 
    user: User, 
    prompt: str, 
    session_data: Dict[str, Any],
    background_tasks: BackgroundTasks # Added background_tasks
) -> Dict[str, Any]:
    
    terminal_service = session_data.get("terminal")
    if not terminal_service:
        raise HTTPException(status_code=500, detail="Terminal service not available for this session.")

    # --- Visualization Setup ---
    nodes = [{"id": "user_prompt", "type": "input", "data": {"label": f"User: {prompt[:30]}..."}, "position": {"x": 0, "y": 0}}]
    edges = []
    last_node_id = "user_prompt"
    y_pos = 100

    # 1. Intent Detection
    intent_response = await detect_intent(db, user, prompt) # Use the new LLM-based intent detection
    intent = intent_response.intent
    print(f"DEBUG: Detected intent: {intent} (Confidence: {intent_response.confidence:.2f})")

    # Initialize messages list with the user's prompt
    messages = [{"role": "user", "content": prompt}]

    # 2. Model Selection (based on intent or routing rules)
    nodes.append({"id": "intent", "data": {"label": f"Intent: {intent} (Conf: {intent_response.confidence:.2f})"}, "position": {"x": 0, "y": y_pos}})
    edges.append({"id": f"e-{last_node_id}-intent", "source": last_node_id, "target": "intent"})
    last_node_id = "intent"
    y_pos += 100

    # 2. Rule Evaluation and Visualization
    all_routing_rules = db.query(RoutingRule).filter(RoutingRule.owner_id == str(user.id)).order_by(RoutingRule.priority.desc()).all()
    print(f"DEBUG: Found {len(all_routing_rules)} routing rules for user {user.id}.")
    
    rule_evaluation_node_id = "rule_evaluation"
    nodes.append({"id": rule_evaluation_node_id, "data": {"label": "Evaluating Routing Rules"}, "position": {"x": 0, "y": y_pos}})
    edges.append({"id": f"e-{last_node_id}-{rule_evaluation_node_id}", "source": last_node_id, "target": rule_evaluation_node_id})
    last_node_id = rule_evaluation_node_id
    y_pos += 100

    selected_llm_model = None
    for rule in all_routing_rules:
        rule_node_id = f"rule_{rule.id}"
        try:
            condition_obj = json.loads(rule.condition)
            condition_matched = _evaluate_condition(condition_obj, intent, prompt)
            print(f"DEBUG: Evaluating rule '{rule.name}' (ID: {rule.id}). Condition: {rule.condition}. Matched: {condition_matched}")
            
            nodes.append({
                "id": rule_node_id,
                "data": {
                    "label": f"Rule: {rule.name} (P: {rule.priority})",
                    "subLabel": f"Condition: {'Matched' if condition_matched else 'Not Matched'}",
                    "status": "success" if condition_matched else "default"
                },
                "position": {"x": 0, "y": y_pos}
            })
            edges.append({"id": f"e-{last_node_id}-{rule_node_id}", "source": last_node_id, "target": rule_node_id})
            last_node_id = rule_node_id
            y_pos += 70 # Smaller increment for rules

            if condition_matched and not selected_llm_model:
                model = db.query(LLMModel).filter(LLMModel.model_name == rule.target_model).first()
                if model:
                    selected_llm_model = model
                    print(f"DEBUG: Rule '{rule.name}' matched. Selected model: {selected_llm_model.model_name}")
                    nodes[-1]["data"]["status"] = "primary" # Highlight selected rule
                    nodes[-1]["data"]["subLabel"] += " (Selected)"
                    break # Found a matching rule, stop evaluating
                else:
                    print(f"DEBUG: Rule '{rule.name}' matched, but target model '{rule.target_model}' not found.")
        except json.JSONDecodeError:
            nodes.append({
                "id": rule_node_id,
                "data": {
                    "label": f"Rule: {rule.name} (P: {rule.priority})",
                    "subLabel": "Condition: Invalid JSON",
                    "status": "destructive"
                },
                "position": {"x": 0, "y": y_pos}
            })
            edges.append({"id": f"e-{last_node_id}-{rule_node_id}", "source": last_node_id, "target": rule_node_id})
            last_node_id = rule_node_id
            y_pos += 70
            print(f"Warning: Routing rule {rule.id} has invalid JSON condition: {rule.condition}")
            continue # Skip this rule if condition is malformed JSON
        except Exception as e:
            nodes.append({
                "id": rule_node_id,
                "data": {
                    "label": f"Rule: {rule.name} (P: {rule.priority})",
                    "subLabel": f"Error: {e}",
                    "status": "destructive"
                },
                "position": {"x": 0, "y": y_pos}
            })
            edges.append({"id": f"e-{last_node_id}-{rule_node_id}", "source": last_node_id, "target": rule_node_id})
            last_node_id = rule_node_id
            y_pos += 70
            print(f"Error evaluating routing rule {rule.id}: {e}")
            continue

    if not selected_llm_model:
        print("DEBUG: No model selected by routing rules. Checking user preferences for default model.")
        # Try to get user's default LLM preference
        user_preferences = db.query(UserLLMPreference).filter(UserLLMPreference.user_id == str(user.id)).first()
        if user_preferences:
            print(f"DEBUG: User preferences found. Default model ID: {user_preferences.default_model_id}")
            if user_preferences.default_model_id:
                selected_llm_model = db.query(LLMModel).filter(LLMModel.id == user_preferences.default_model_id).first()
                if not selected_llm_model:
                    print(f"ERROR: User's default LLM model (ID: {user_preferences.default_model_id}) not found in DB.")
                    raise HTTPException(status_code=500, detail=f"User's default LLM model (ID: {user_preferences.default_model_id}) not found.")
                else:
                    print(f"DEBUG: User's default model '{selected_llm_model.model_name}' found and selected.")
            else:
                print("DEBUG: User preferences found, but no default_model_id is set.")
        else:
            print("DEBUG: No user preferences found.")
        
        if not selected_llm_model:
            # If no routing rule matched and no valid user default is set
            print("ERROR: No default LLM model configured or selected via routing rules.")
            raise HTTPException(status_code=500, detail="No default LLM model configured or selected via routing rules.")
    else:
        print(f"DEBUG: Model '{selected_llm_model.model_name}' selected via routing rules.")
        
    nodes.append({"id": "model_selection", "data": {"label": f"Selected Model: {selected_llm_model.model_name}"}, "position": {"x": 0, "y": y_pos}})
    edges.append({"id": f"e-{last_node_id}-model_selection", "source": last_node_id, "target": "model_selection"})
    last_node_id = "model_selection"
    y_pos += 100

    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == selected_llm_model.provider_id).first()
    if not llm_provider: raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {selected_llm_model.model_name}")
    api_key = decrypt_api_key(llm_provider.api_key_encrypted)
    # DEBUGGING: Print the decrypted key to verify it's not empty
    print(f"DEBUG: Decrypted API Key (first 5 chars): {api_key[:5] if api_key else 'None'}")
    print(f"DEBUG: Type of api_key after decryption: {type(api_key)}")
    print(f"DEBUG: Value of api_key after decryption (first 5 chars): {api_key[:5] if api_key else 'None'}")

    # --- Tool-Calling Loop ---
    for i in range(5): # Limit iterations
        node_id = f"llm_call_{i+1}"
        nodes.append({"id": node_id, "data": {"label": f"LLM Call #{i+1}"}, "position": {"x": 0, "y": y_pos}})
        edges.append({"id": f"e-{last_node_id}-{node_id}", "source": last_node_id, "target": node_id})
        last_node_id = node_id
        y_pos += 100

        try:
            llm_response = await call_llm_api(
                provider=llm_provider, model_name=selected_llm_model.model_name,
                messages=messages, api_key=api_key, tools=tools_schema
            )
        except HTTPException as e:
            print(f"ERROR: HTTPException caught in process_chat_request: {e.detail}")
            raise e
        
        response_message = llm_response.get("message", {})
        messages.append(response_message)

        if not response_message.get("tool_calls"):
            final_content = response_message.get("content")
            node_id = "final_response"
            nodes.append({"id": node_id, "type": "output", "data": {"label": f"Response: {final_content[:30]}..."}, "position": {"x": 0, "y": y_pos}})
            edges.append({"id": f"e-{last_node_id}-{node_id}", "source": last_node_id, "target": node_id})
            return {
                "response": final_content,
                "model_used": selected_llm_model.model_name,
                "visualization_data": {"nodes": nodes, "edges": edges}
            }

        # --- Execute Tool Calls ---
        tool_calls = response_message["tool_calls"]
        node_id = f"tool_execution_{i+1}"
        tool_labels = ", ".join([tc['function']['name'] for tc in tool_calls])
        nodes.append({"id": node_id, "data": {"label": f"Tools: {tool_labels}"}, "position": {"x": 0, "y": y_pos}})
        edges.append({"id": f"e-{last_node_id}-{node_id}", "source": last_node_id, "target": node_id})
        last_node_id = node_id
        y_pos += 100

        tool_results = []
        for tool_call in tool_calls:
            function_name = tool_call['function']['name']
            function_to_call = tool_registry.get(function_name)
            
            if not function_to_call:
                result_content = f"Error: Tool '{function_name}' not found."
            else:
                try:
                    function_args = json.loads(tool_call['function']['arguments'])
                    # Pass the full context to the tool function
                    result_content = await function_to_call(
                        db=db, 
                        user=user, 
                        terminal_service=terminal_service, 
                        background_tasks=background_tasks,
                        **function_args
                    )
                except Exception as e:
                    result_content = f"Error executing tool '{function_name}': {e}"

            tool_results.append({
                "tool_call_id": tool_call['id'], "role": "tool",
                "name": function_name, "content": result_content,
            })
        
        messages.extend(tool_results)

    final_message = messages[-1].get("content", "Max tool call iterations reached.")
    return {
        "response": final_message,
        "model_used": selected_llm_model.model_name,
        "visualization_data": {"nodes": nodes, "edges": edges}
    }