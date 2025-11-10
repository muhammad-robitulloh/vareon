from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, Dict, Any, List
import json

from server_python.database import LLMModel, LLMProvider, User
from server_python.cognisys.crud import decrypt_api_key
from server_python.cognisys.llm_interaction import call_llm_api # Re-use the call_llm_api from cognisys
from . import schemas

async def generate_reasoning(db: Session, user: User, request: schemas.ReasoningRequest) -> schemas.ReasoningResponse:
    """
    Generates a detailed reasoning trace explaining the AI's thought process for a given task.
    """
    # 1. Select an LLM model suitable for reasoning
    reasoning_model = None
    if request.model_name:
        reasoning_model = db.query(LLMModel).filter(LLMModel.model_name == request.model_name, LLMModel.is_active == True).first()
    
    if not reasoning_model:
        # Look for a model specifically tagged for 'reasoning' role
        reasoning_model = db.query(LLMModel).filter(LLMModel.role == "reasoning", LLMModel.is_active == True).first()
    
    if not reasoning_model:
        # Fallback to a general chat model if no specific reasoning model is found
        reasoning_model = db.query(LLMModel).filter(LLMModel.type == "chat", LLMModel.is_active == True).first()
        if not reasoning_model:
            raise HTTPException(status_code=500, detail="No active LLM model found for reasoning or general chat.")

    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == reasoning_model.provider_id).first()
    if not llm_provider:
        raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {reasoning_model.model_name}")
    
    api_key = decrypt_api_key(llm_provider.api_key_encrypted)

    # 2. Construct the prompt for reasoning generation
    system_prompt = f"""You are an AI assistant specialized in explaining your thought process.
Given a user's prompt and context, generate a detailed step-by-step reasoning trace that explains how you would approach and solve the task.
Focus on the logical steps, decisions, and potential actions you would take.
Provide your response in a JSON format with the following keys:
- 'reasoning_trace': A list of objects, where each object represents a step in your reasoning. Each step object should have:
    - 'step_number': Integer, the order of the step.
    - 'description': String, a detailed description of the step.
    - 'action': Optional String, the action planned or taken for this step (e.g., "Call LLM", "Execute shell command", "Generate code").
    - 'outcome': Optional String, the expected outcome of the action.
- 'summary': A high-level summary of your overall reasoning.

Example JSON output:
{{
    "reasoning_trace": [
        {{"step_number": 1, "description": "Analyze the user's request to identify the core task and any constraints.", "action": "Parse user prompt", "outcome": "Identified task: 'Generate Python script to list files'."}},
        {{"step_number": 2, "description": "Determine the best tool or LLM for the identified task. For code generation, a code-focused LLM is preferred.", "action": "Select LLM model", "outcome": "Selected 'code_generation' model."}},
        {{"step_number": 3, "description": "Formulate a precise prompt for the selected LLM, including language and specific requirements.", "action": "Construct LLM prompt", "outcome": "LLM prompt ready."}},
        {{"step_number": 4, "description": "Call the LLM with the formulated prompt.", "action": "Call LLM API", "outcome": "Received LLM response with generated code."}}
    ],
    "summary": "The AI analyzed the request, selected a code generation model, formulated a prompt, and called the LLM to generate the script."
}}
"""
    user_prompt_content = f"Generate a reasoning trace for the following task: '{request.prompt}'"
    if request.context:
        user_prompt_content += f"\n\nHere is some additional context:\n```\n{request.context}\n```"
    if request.task_type != "general":
        user_prompt_content += f"\nConsider this as a '{request.task_type}' task."
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_content}
    ]

    # 3. Call the LLM
    try:
        llm_response_data = await call_llm_api(
            provider=llm_provider,
            model_name=reasoning_model.model_name,
            messages=messages,
            api_key=api_key,
            temperature=0.2, # Lower temperature for more deterministic output
            top_p=0.9
        )
        
        llm_content = llm_response_data["message"]["content"]
        
        # 4. Parse the LLM's JSON response
        parsed_response = json.loads(llm_content)
        
        reasoning_trace = [schemas.ReasoningStep(**step) for step in parsed_response.get("reasoning_trace", [])]
        summary = parsed_response.get("summary")

        return schemas.ReasoningResponse(
            reasoning_trace=reasoning_trace,
            summary=summary,
            model_used=reasoning_model.model_name,
            success=True
        )
    except json.JSONDecodeError:
        print(f"LLM response was not valid JSON for reasoning: {llm_content}")
        return schemas.ReasoningResponse(
            reasoning_trace=[],
            summary="LLM provided malformed JSON response for reasoning.",
            model_used=reasoning_model.model_name,
            success=False,
            error_message="LLM provided malformed JSON response."
        )
    except Exception as e:
        print(f"Error during LLM reasoning generation: {e}")
        return schemas.ReasoningResponse(
            reasoning_trace=[],
            summary=f"Failed to generate reasoning: {e}",
            model_used=reasoning_model.model_name,
            success=False,
            error_message=f"Failed to generate reasoning: {e}"
        )
