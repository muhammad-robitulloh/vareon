from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, Dict, Any
import json

from server_python.database import LLMModel, LLMProvider, User
from server_python.cognisys.crud import decrypt_api_key
from server_python.cognisys.llm_interaction import call_llm_api # Re-use the call_llm_api from cognisys
from . import schemas

async def generate_code(db: Session, user: User, request: schemas.CodeGenerationRequest) -> schemas.CodeGenerationResponse:
    """
    Generates code based on a natural language prompt using an LLM.
    """
    # 1. Select an LLM model suitable for code generation
    code_gen_model = None
    if request.model_name:
        code_gen_model = db.query(LLMModel).filter(LLMModel.model_name == request.model_name, LLMModel.is_active == True).first()
    
    if not code_gen_model:
        # Look for a model specifically tagged for 'code_generation' role
        code_gen_model = db.query(LLMModel).filter(LLMModel.role == "code_generation", LLMModel.is_active == True).first()
    
    if not code_gen_model:
        # Fallback to a general chat model if no specific code_generation model is found
        code_gen_model = db.query(LLMModel).filter(LLMModel.type == "chat", LLMModel.is_active == True).first()
        if not code_gen_model:
            raise HTTPException(status_code=500, detail="No active LLM model found for code generation or general chat.")

    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == code_gen_model.provider_id).first()
    if not llm_provider:
        raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {code_gen_model.model_name}")
    
    api_key = decrypt_api_key(llm_provider.api_key_encrypted)

    # 2. Construct the prompt for code generation
    system_prompt = f"""You are an expert {request.language} programmer. Your task is to generate clean, efficient, and runnable {request.language} code based on the user's request.
If the user provides context or existing code, incorporate it appropriately.
Provide only the code in your response, enclosed in a {request.language} markdown block. Do not include any conversational text outside the markdown block.
If you need to explain something, include it as comments within the code.
If the request is unclear, make reasonable assumptions and generate the most likely useful code.
"""
    user_prompt_content = f"Generate {request.language} code for the following request: '{request.prompt}'"
    if request.context:
        user_prompt_content += f"\n\nHere is some additional context or existing code:\n```\n{request.context}\n```"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_content}
    ]

    # 3. Call the LLM
    try:
        llm_response_data = await call_llm_api(
            provider=llm_provider,
            model_name=code_gen_model.model_name,
            messages=messages,
            api_key=api_key,
            temperature=0.7, # Can be adjusted for creativity
            top_p=1.0
        )
        
        llm_content = llm_response_data["message"]["content"]
        
        # Extract code from markdown block
        code_block_start = llm_content.find(f"```{request.language}")
        code_block_end = llm_content.rfind("```")

        generated_code = ""
        if code_block_start != -1 and code_block_end != -1 and code_block_start < code_block_end:
            generated_code = llm_content[code_block_start + len(f"```{request.language}"):code_block_end].strip()
        else:
            # If no markdown block, assume the whole response is code or try to extract
            generated_code = llm_content.strip()

        return schemas.CodeGenerationResponse(
            generated_code=generated_code,
            language=request.language,
            model_used=code_gen_model.model_name,
            reasoning=None, # LLM is instructed not to provide reasoning outside code comments
            success=True
        )
    except Exception as e:
        print(f"Error during LLM code generation: {e}")
        return schemas.CodeGenerationResponse(
            generated_code="",
            language=request.language,
            model_used=code_gen_model.model_name,
            success=False,
            error_message=f"Failed to generate code: {e}"
        )
