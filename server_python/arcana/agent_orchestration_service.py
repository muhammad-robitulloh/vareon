from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, Dict, Any, List
import json

from server_python.database import User, ArcanaAgent
from server_python.llm_service import get_openrouter_completion # Import the simpler service
from server_python.cognisys.llm_interaction import call_llm_api # For tool-using agents
from server_python.cognisys.crud import decrypt_api_key
from server_python.database import LLMModel, LLMProvider
from . import schemas
from .code_generation_service import generate_code
from .shell_translation_service import translate_shell_command
from .file_management_service import perform_file_operation
from .reasoning_service import generate_reasoning

# Placeholder for tool definitions that agents can use
# This should ideally be dynamically loaded or managed
AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "generate_code",
            "description": "Generates code in a specified programming language based on a natural language prompt.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The natural language prompt for code generation."},
                    "language": {"type": "string", "description": "The programming language (e.g., 'python', 'javascript')."},
                    "context": {"type": "string", "description": "Additional context or existing code."}
                },
                "required": ["prompt", "language"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "translate_shell_command",
            "description": "Translates a natural language instruction into a shell command.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The natural language instruction."},
                    "current_directory": {"type": "string", "description": "The current working directory."},
                    "shell_type": {"type": "string", "description": "The type of shell (e.g., 'bash')."}
                },
                "required": ["prompt"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "perform_file_operation",
            "description": "Performs various file operations (read, write, delete, list, create_directory) within the user's sandboxed directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["read", "write", "delete", "list", "create_directory"], "description": "The file operation to perform."},
                    "path": {"type": "string", "description": "The path to the file or directory."},
                    "content": {"type": "string", "description": "Content to write for 'write' operation."},
                    "recursive": {"type": "boolean", "description": "For 'list' or 'delete' operations, whether to operate recursively."}
                },
                "required": ["action", "path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "generate_reasoning",
            "description": "Generates a detailed reasoning trace explaining the AI's thought process for a given task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "The user's prompt or task for which reasoning is required."},
                    "context": {"type": "string", "description": "Additional context for reasoning."},
                    "task_type": {"type": "string", "description": "The type of task (e.g., 'general', 'code_generation')."}
                },
                "required": ["prompt"]
            }
        }
    }
]

async def execute_agent_task(db: Session, user: User, request: schemas.AgentExecuteRequest) -> schemas.AgentExecuteResponse:
    """
    Executes a task for a given Arcana Agent based on its mode and configuration.
    """
    print(f"DEBUG: In execute_agent_task, searching for agent_id: {request.agent_id} with owner_id: {user.id}")
    db_agent = db.query(ArcanaAgent).filter(ArcanaAgent.id == str(request.agent_id), ArcanaAgent.owner_id == str(user.id)).first()
    if not db_agent:
        # Let's see what's in the DB
        all_agents = db.query(ArcanaAgent).all()
        print(f"DEBUG: Agent not found. Agents in DB: {[a.id for a in all_agents]}")
        # Also print the owner_id of the agent we're looking for, if it exists
        agent_in_db = db.query(ArcanaAgent).filter(ArcanaAgent.id == str(request.agent_id)).first()
        if agent_in_db:
            print(f"DEBUG: Agent {agent_in_db.id} found in DB, but owner_id mismatch. DB owner_id: {agent_in_db.owner_id}, expected owner_id: {user.id}")
        raise HTTPException(status_code=404, detail="Arcana Agent not found.")

    actions_taken = []
    output = ""
    status = "in_progress"
    error_message = None

    try:
        if db_agent.mode == "chat":
            # Agent acts as a specialized chatbot
            # Use a simpler chat completion service, not one that requires a terminal
            model_name = "general-chat-model" # Or get from agent config
            if db_agent.configuration and db_agent.configuration.get("llm_model"):
                model_name = db_agent.configuration["llm_model"]
            
            # Construct a simple prompt with the agent's persona
            full_prompt = f"Persona: {db_agent.persona}\n\nUser: {request.task_prompt}\n\nAssistant:"
            
            chat_response = await get_openrouter_completion(user.id, full_prompt, model_name, db, user.id)
            output = chat_response
            actions_taken.append(f"Chat response generated using model: {model_name}")
            status = "success"

        elif db_agent.mode == "tool_user":
            # Agent uses LLM with tools to accomplish the task
            # This involves a loop of LLM calls and tool executions
            messages = [{"role": "system", "content": f"You are {db_agent.name}, a {db_agent.persona} agent. Your objective is: {db_agent.objective or 'assist the user'}. Accomplish the following task: {request.task_prompt}"}]
            if request.context:
                messages.append({"role": "user", "content": f"Context: {request.context}"})
            messages.append({"role": "user", "content": request.task_prompt})

            # Select an LLM model for the agent (e.g., a general chat model or one specified in agent config)
            agent_llm_model = db.query(LLMModel).filter(LLMModel.model_name == "general-chat-model", LLMModel.is_active == True).first() # Default
            if db_agent.configuration and db_agent.configuration.get("llm_model"):
                agent_llm_model = db.query(LLMModel).filter(LLMModel.model_name == db_agent.configuration["llm_model"], LLMModel.is_active == True).first()
            if not agent_llm_model:
                raise HTTPException(status_code=500, detail="No active LLM model found for agent.")
            
            llm_provider = db.query(LLMProvider).filter(LLMProvider.id == agent_llm_model.provider_id).first()
            if not llm_provider:
                raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {agent_llm_model.model_name}")
            api_key = decrypt_api_key(llm_provider.api_key_encrypted)

            for i in range(5): # Max 5 tool-calling iterations
                llm_response = await call_llm_api(
                    provider=llm_provider, model_name=agent_llm_model.model_name,
                    messages=messages, api_key=api_key, tools=AGENT_TOOLS_SCHEMA
                )
                response_message = llm_response.get("message", {})
                messages.append(response_message)

                if not response_message.get("tool_calls"):
                    output = response_message.get("content", "Agent completed task.")
                    status = "success"
                    break
                
                tool_calls = response_message["tool_calls"]
                tool_results = []
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    
                    result_content = f"Error: Tool '{function_name}' not found or not implemented."
                    actions_taken.append(f"Attempted tool call: {function_name} with args {function_args}")

                    # Dynamically call the appropriate service function
                    if function_name == "generate_code":
                        code_req = schemas.CodeGenerationRequest(**function_args)
                        code_res = await generate_code(db, user, code_req)
                        result_content = code_res.generated_code if code_res.success else code_res.error_message
                    elif function_name == "translate_shell_command":
                        shell_req = schemas.ShellCommandTranslationRequest(**function_args)
                        shell_res = await translate_shell_command(db, user, shell_req)
                        result_content = shell_res.translated_command if shell_res.success else shell_res.error_message
                    elif function_name == "perform_file_operation":
                        file_req = schemas.FileOperationRequest(**function_args)
                        file_res = await perform_file_operation(user, file_req)
                        result_content = file_res.message
                        if file_res.content: result_content += f"\nContent: {file_res.content}"
                        if file_res.file_list: result_content += f"\nFiles: {[f.name for f in file_res.file_list]}"
                    elif function_name == "generate_reasoning":
                        reason_req = schemas.ReasoningRequest(**function_args)
                        reason_res = await generate_reasoning(db, user, reason_req)
                        result_content = reason_res.summary if reason_res.success else reason_res.error_message
                    
                    tool_results.append({
                        "tool_call_id": tool_call['id'], "role": "tool",
                        "name": function_name, "content": result_content,
                    })
                messages.extend(tool_results)
            
            if status != "success":
                output = "Agent reached max tool call iterations without completing task."
                status = "failed"

        elif db_agent.mode == "autonomous":
            # This mode would involve a more complex planning and execution loop.
            # For now, a simplified version: LLM plans, then executes first step.
            messages = [{"role": "system", "content": f"You are {db_agent.name}, an autonomous agent. Your objective is: {db_agent.objective or 'autonomously accomplish tasks'}. Plan and execute the following task: {request.task_prompt}"}]
            if request.context:
                messages.append({"role": "user", "content": f"Context: {request.context}"})
            messages.append({"role": "user", "content": request.task_prompt})

            # Select an LLM model for the agent (e.g., a general chat model or one specified in agent config)
            agent_llm_model = db.query(LLMModel).filter(LLMModel.model_name == "general-chat-model", LLMModel.is_active == True).first() # Default
            if db_agent.configuration and db_agent.configuration.get("llm_model"):
                agent_llm_model = db.query(LLMModel).filter(LLMModel.model_name == db_agent.configuration["llm_model"], LLMModel.is_active == True).first()
            if not agent_llm_model:
                raise HTTPException(status_code=500, detail="No active LLM model found for autonomous agent.")
            
            llm_provider = db.query(LLMProvider).filter(LLMProvider.id == agent_llm_model.provider_id).first()
            if not llm_provider:
                raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {agent_llm_model.model_name}")
            api_key = decrypt_api_key(llm_provider.api_key_encrypted)

            # Autonomous agents might use reasoning to plan
            reasoning_res = await generate_reasoning(db, user, schemas.ReasoningRequest(prompt=request.task_prompt, context=request.context, task_type="autonomous_agent_task"))
            actions_taken.append(f"Generated reasoning: {reasoning_res.summary}")
            
            # Then use tools based on the plan (simplified for now)
            llm_response = await call_llm_api(
                provider=llm_provider, model_name=agent_llm_model.model_name,
                messages=messages, api_key=api_key, tools=AGENT_TOOLS_SCHEMA
            )
            response_message = llm_response.get("message", {})
            messages.append(response_message)

            if response_message.get("tool_calls"):
                tool_calls = response_message["tool_calls"]
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    actions_taken.append(f"Autonomous agent executed tool: {function_name} with args {function_args}")
                    # Execute tool (similar to tool_user mode, but potentially more complex orchestration)
                    # For simplicity, just log for now
                    output += f"\nExecuted {function_name} with {function_args}"
                status = "success"
            else:
                output = response_message.get("content", "Autonomous agent completed task.")
                status = "success"

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported agent mode: {db_agent.mode}")

    except HTTPException as e:
        print(f"DEBUG: HTTPException in execute_agent_task: {e.detail}")
        status = "failed"
        error_message = e.detail
    except Exception as e:
        print(f"DEBUG: Exception in execute_agent_task: {e}")
        status = "failed"
        error_message = str(e)

    return schemas.AgentExecuteResponse(
        agent_id=db_agent.id,
        status=status,
        output=output,
        actions_taken=actions_taken,
        error_message=error_message
    )
