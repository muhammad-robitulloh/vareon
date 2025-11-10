from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, Dict, Any
import json

from server_python.database import LLMModel, LLMProvider, User
from server_python.cognisys.crud import decrypt_api_key
from server_python.cognisys.llm_interaction import call_llm_api # Re-use the call_llm_api from cognisys
from . import schemas

# Simple whitelist/blacklist for demonstration purposes
DANGEROUS_COMMANDS = ["rm -rf", "sudo", "mkfs", "dd"]
SAFE_COMMANDS_KEYWORDS = ["ls", "cd", "pwd", "echo", "grep", "find", "cat"]

def check_command_safety(command: str) -> (bool, Optional[str]):
    command_lower = command.lower()
    for dangerous in DANGEROUS_COMMANDS:
        if dangerous in command_lower:
            return False, f"Command contains potentially dangerous sequence: '{dangerous}'"
    
    # More sophisticated checks could go here
    # For now, a very basic check
    if any(keyword in command_lower for keyword in SAFE_COMMANDS_KEYWORDS):
        return True, None
    
    return True, None # Assume safe if no dangerous commands found and no specific safe keywords matched

async def translate_shell_command(db: Session, user: User, request: schemas.ShellCommandTranslationRequest) -> schemas.ShellCommandTranslationResponse:
    """
    Translates a natural language instruction into a shell command using an LLM.
    """
    # 1. Select an LLM model suitable for shell command translation
    shell_trans_model = None
    if request.model_name:
        shell_trans_model = db.query(LLMModel).filter(LLMModel.model_name == request.model_name, LLMModel.is_active == True).first()
    
    if not shell_trans_model:
        # Look for a model specifically tagged for 'shell_translation' role
        shell_trans_model = db.query(LLMModel).filter(LLMModel.role == "shell_translation", LLMModel.is_active == True).first()
    
    if not shell_trans_model:
        # Fallback to a general chat model if no specific shell_translation model is found
        shell_trans_model = db.query(LLMModel).filter(LLMModel.type == "chat", LLMModel.is_active == True).first()
        if not shell_trans_model:
            raise HTTPException(status_code=500, detail="No active LLM model found for shell command translation or general chat.")

    llm_provider = db.query(LLMProvider).filter(LLMProvider.id == shell_trans_model.provider_id).first()
    if not llm_provider:
        raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {shell_trans_model.model_name}")
    
    api_key = decrypt_api_key(llm_provider.api_key_encrypted)

    # 2. Construct the prompt for shell command translation
    system_prompt = f"""You are an expert {request.shell_type} shell command translator. Your task is to convert natural language instructions into a single, executable {request.shell_type} command.
Provide only the command in your response. Do not include any conversational text or explanations outside of a JSON object.
If you need to explain something, include it in the 'reasoning' field of the JSON.
If the instruction is unclear, ask for clarification or make a reasonable assumption.

Provide your response in a JSON format with the following keys:
- 'command': The translated shell command.
- 'reasoning': A brief explanation of the command or any assumptions made.

Example JSON output:
{{"command": "ls -lha", "reasoning": "Lists all files and directories in long format, including hidden ones."}}
{{"command": "git status", "reasoning": "Checks the status of the current git repository."}}
"""
    user_prompt_content = f"Translate the following instruction into a {request.shell_type} command: '{request.prompt}'"
    if request.current_directory:
        user_prompt_content += f"\nAssume the current working directory is: '{request.current_directory}'"
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt_content}
    ]

    # 3. Call the LLM
    try:
        llm_response_data = await call_llm_api(
            provider=llm_provider,
            model_name=shell_trans_model.model_name,
            messages=messages,
            api_key=api_key,
            temperature=0.2, # Lower temperature for more deterministic output
            top_p=0.9
        )
        
        llm_content = llm_response_data["message"]["content"]
        
        # 4. Parse the LLM's JSON response
        parsed_response = json.loads(llm_content)
        translated_command = parsed_response.get("command", "")
        reasoning = parsed_response.get("reasoning", "LLM-based translation.")

        is_safe, safety_warning = check_command_safety(translated_command)

        return schemas.ShellCommandTranslationResponse(
            translated_command=translated_command,
            reasoning=reasoning,
            model_used=shell_trans_model.model_name,
            is_safe=is_safe,
            safety_warning=safety_warning,
            success=True
        )
    except json.JSONDecodeError:
        print(f"LLM response was not valid JSON: {llm_content}")
        return schemas.ShellCommandTranslationResponse(
            translated_command="",
            reasoning="LLM response not valid JSON.",
            model_used=shell_trans_model.model_name,
            is_safe=False,
            safety_warning="LLM provided malformed response.",
            success=False,
            error_message="LLM provided malformed JSON response."
        )
    except Exception as e:
        print(f"Error during LLM shell command translation: {e}")
        return schemas.ShellCommandTranslationResponse(
            translated_command="",
            reasoning=f"Error: {e}",
            model_used=shell_trans_model.model_name,
            is_safe=False,
            safety_warning=f"An error occurred during translation: {e}",
            success=False,
            error_message=f"Failed to translate command: {e}"
        )
