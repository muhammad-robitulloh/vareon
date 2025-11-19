from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import Optional, Dict, Any, List, Callable
import json

from server_python.database import User, ArcanaAgent
from server_python.llm_service import get_openrouter_completion
from server_python.cognisys.llm_interaction import call_llm_api
from server_python.cognisys.crud import decrypt_api_key
from server_python.database import LLMModel, LLMProvider, UserLLMPreference # Import UserLLMPreference
from . import schemas, crud
from .code_generation_service import generate_code
from .shell_translation_service import translate_shell_command
from .file_management_service import perform_file_operation
from .reasoning_service import generate_reasoning
from server_python.git_service.service import GitService # Import GitService
from terminal.service import TerminalService # Import TerminalService
from server_python.context_memory import crud as context_crud # Import context_memory crud
from server_python.context_memory import schemas as context_schemas # Import context_memory schemas

from server_python.orchestrator.connection_manager import manager # Import the WebSocket manager

async def reflect(db: Session, user: User, job_id: str, context: str) -> str:
    """
    Reflects on the context and decides the next step.
    """
    await crud.add_agent_job_log(db, job_id, "thought", "Reflecting on the situation.")
    
    reflection_prompt = f"Given the following context, what is the next logical step?"
    
    reasoning_res = await generate_reasoning(db, user, schemas.ReasoningRequest(prompt=reflection_prompt, context=context, task_type="reflection"))
    
    if reasoning_res.success:
        reflection_summary = reasoning_res.summary
        await crud.add_agent_job_log(db, job_id, "thought", f"Reflection summary: {reflection_summary}")
        return reflection_summary
    else:
        await crud.add_agent_job_log(db, job_id, "warning", f"Could not generate reflection: {reasoning_res.error_message}")
        return "Could not reflect on the situation."

async def request_human_input(db: Session, job_id: str, message_to_user: str) -> Dict[str, Any]:
    """
    Requests human input from the user and pauses the agent's execution.
    Includes recent log entries as context for the human.
    """
    recent_logs = crud.get_recent_agent_job_logs(db, job_id, limit=5) # Get last 5 logs
    context_message = ""
    if recent_logs:
        context_message = "\n\n--- Recent Agent Activity ---\n"
        for log in recent_logs:
            context_message += f"[{log.timestamp.strftime('%H:%M:%S')}] {log.log_type.upper()}: {log.content}\n"
        context_message += "-----------------------------\n"

    full_message_to_user = f"{message_to_user}{context_message}\nPlease provide your input to guide the agent."

    await crud.add_agent_job_log(db, job_id, "human_input_needed", full_message_to_user)
    crud.update_agent_job_status(db, job_id, "awaiting_human_input")
    return {"status": "awaiting_human_input", "message": full_message_to_user}

AGENT_TOOLS_SCHEMA = [
    {
        "type": "function",
        "function":
            {
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
            "description": "Performs various file operations (read, write, delete, list, create_directory, read_many, edit) within the user's sandboxed directory.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action": {"type": "string", "enum": ["read", "write", "delete", "list", "create_directory", "read_many", "edit"], "description": "The file operation to perform."},
                    "path": {"type": "string", "description": "The path to the file or directory. For 'read_many', this is a list of paths."},
                    "content": {"type": "string", "description": "Content to write for 'write' or 'edit' operation."},
                    "recursive": {"type": "boolean", "description": "For 'list' or 'delete' operations, whether to operate recursively."}
                },
                "required": ["action", "path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "reflect",
            "description": "Reflect on the current situation, analyze the output of previous actions, and decide on the next step.",
            "parameters": {
                "type": "object",
                "properties": {
                    "prompt": {"type": "string", "description": "A prompt for the reflection, summarizing the current state and asking for the next action."},
                    "context": {"type": "string", "description": "The output of the previous action or any other relevant context."}
                },
                "required": ["prompt", "context"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_human_input",
            "description": "Requests input or clarification from the human user and pauses the agent's execution until input is provided. Use this when the agent needs human guidance or approval to proceed.",
            "parameters": {
                "type": "object",
                "properties": {
                    "message_to_user": {"type": "string", "description": "The message or question to display to the human user."}
                },
                "required": ["message_to_user"]
            }
        }
    },
    schemas.GIT_GET_DIFF_TOOL_SCHEMA, # Add the new Git diff tool schema
    schemas.RUN_TESTS_TOOL_SCHEMA, # Add the new run tests tool schema
    schemas.STORE_CONTEXT_ITEM_TOOL_SCHEMA, # Add the new store context item tool schema
    schemas.RETRIEVE_CONTEXT_ITEMS_TOOL_SCHEMA # Add the new retrieve context items tool schema
]

# Define agent-specific tool registry
agent_tool_registry: Dict[str, Callable] = {
    "reflect": reflect,
    "request_human_input": request_human_input,
    "generate_code": generate_code,
    "translate_shell_command": translate_shell_command,
    "perform_file_operation": perform_file_operation,
    "generate_reasoning": generate_reasoning,
    "git_get_diff": lambda git_service, local_path, path=None: git_service.get_diff(local_path=local_path, request=schemas.GitDiffRequest(path=path)),
    "run_tests": lambda terminal_service, local_path, command: terminal_service.execute_command(f"cd {local_path} && {command}"),
    "store_context_item": lambda db, user, item_type, key, value: context_crud.create_context_item(db=db, user_id=str(user.id), key=f"{context_crud.CONTEXT_KEY_PREFIXES.get(item_type)}{key}", value=value),
    "retrieve_context_items": lambda db, user, item_type=None, key=None: context_crud.get_all_context_for_user(db=db, user_id=str(user.id)) if not item_type and not key else [item for category in context_crud.get_all_context_for_user(db=db, user_id=str(user.id)).values() for item in category if (not item_type or item.get('type') == item_type) and (not key or item.get('key') == key)],
}


async def execute_agent_task(db: Session, user: User, request: schemas.AgentExecuteRequest, job_id: str):
    """
    Executes a task for a given Arcana Agent, logging progress to the database.
    """
    await crud.add_agent_job_log(db, job_id, "info", f"Starting job {job_id} for agent {request.agent_id}")
    
    try:
        db_agent = db.query(ArcanaAgent).filter(ArcanaAgent.id == str(request.agent_id), ArcanaAgent.owner_id == str(user.id)).first()
        if not db_agent:
            raise HTTPException(status_code=404, detail="Arcana Agent not found.")

        # Extract target_repo_path and target_branch from agent configuration or request
        agent_config = json.loads(db_agent.configuration) if db_agent.configuration else {}
        target_repo_path = request.target_repo_path or agent_config.get('target_repo_path')
        target_branch = request.target_branch or agent_config.get('target_branch')

        if not target_repo_path:
            await crud.add_agent_job_log(db, job_id, "error", "No target repository path specified for the agent.")
            crud.update_agent_job_status(db, job_id, "failed", final_output="No target repository path specified.")
            return

        # Initialize services that tools might need
        git_service = GitService(db, user)
        terminal_service = TerminalService(session_id=job_id, user_id=str(user.id)) # Corrected initialization

        crud.update_agent_job_status(db, job_id, "planning")
        await crud.add_agent_job_log(db, job_id, "thought", f"Agent '{db_agent.name}' starting task: {request.task_prompt}")
        await crud.add_agent_job_log(db, job_id, "info", f"Operating on repository: {target_repo_path}, branch: {target_branch or 'default'}")
        final_output = ""
        if db_agent.mode == "chat":
            # This mode is typically handled by the main chat interface,
            # but if an agent is set to 'chat' mode, it might just respond directly.
            # For now, we'll treat it as a simple LLM call without tools.
            await crud.add_agent_job_log(db, job_id, "thought", "Agent in chat mode. Responding directly.")
            
            # Determine LLM model for the agent
            agent_llm_model = None
            if agent_config.get('default_model_id'):
                agent_llm_model = db.query(LLMModel).filter(LLMModel.id == agent_config['default_model_id'], LLMModel.is_active == True).first()
            
            if not agent_llm_model:
                user_preferences = db.query(UserLLMPreference).filter(UserLLMPreference.user_id == str(user.id)).first()
                if user_preferences and user_preferences.default_model_id:
                    agent_llm_model = db.query(LLMModel).filter(LLMModel.id == user_preferences.default_model_id, LLMModel.is_active == True).first()

            if not agent_llm_model:
                raise HTTPException(status_code=500, detail="No active LLM model configured for agent or user default.")
            
            llm_provider = db.query(LLMProvider).filter(LLMProvider.id == agent_llm_model.provider_id).first()
            if not llm_provider:
                raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {agent_llm_model.model_name}")
            api_key = decrypt_api_key(llm_provider.api_key_encrypted)
            messages = [{"role": "system", "content": f"You are {db_agent.name}, a {db_agent.persona} agent. Your objective is: {db_agent.objective or 'assist the user'}. Respond to the user's prompt."}]
            if request.context:
                messages.append({"role": "user", "content": f"Context: {request.context}"})
            messages.append({"role": "user", "content": request.task_prompt})
            llm_response = await call_llm_api(
                provider=llm_provider, model_name=agent_llm_model.model_name,
                messages=messages, api_key=api_key
            )
            final_output = llm_response.get("message", {}).get("content", "No response from LLM.")
            await crud.add_agent_job_log(db, job_id, "thought", f"Chat mode response: {final_output}")
        elif db_agent.mode == "tool_user" or db_agent.mode == "autonomous":
            # Combine AGENT_TOOLS_SCHEMA with Git tools from cognisys.tools
            from server_python.cognisys.tools import tools_schema as cognisys_tools_schema
            all_tools_schema = AGENT_TOOLS_SCHEMA + cognisys_tools_schema
            system_message_content = f"You are {db_agent.name}, a {db_agent.persona} agent. Your objective is: {db_agent.objective or 'assist the user'}. Accomplish the following task: {request.task_prompt}"
            if target_repo_path:
                system_message_content += f"\nYour current working repository is: {target_repo_path}"
                if target_branch:
                    system_message_content += f" on branch: {target_branch}"
            messages = [{"role": "system", "content": system_message_content}]
            if request.context:
                messages.append({"role": "user", "content": f"Context: {request.context}"})
            messages.append({"role": "user", "content": request.task_prompt})
            # Determine LLM model for the agent
            agent_llm_model = None
            if agent_config.get('default_model_id'):
                agent_llm_model = db.query(LLMModel).filter(LLMModel.id == agent_config['default_model_id'], LLMModel.is_active == True).first()
            
            if not agent_llm_model:
                user_preferences = db.query(UserLLMPreference).filter(UserLLMPreference.user_id == str(user.id)).first()
                if user_preferences and user_preferences.default_model_id:
                    agent_llm_model = db.query(LLMModel).filter(LLMModel.id == user_preferences.default_model_id, LLMModel.is_active == True).first()

            if not agent_llm_model:
                raise HTTPException(status_code=500, detail="No active LLM model configured for agent or user default.")
            
            llm_provider = db.query(LLMProvider).filter(LLMProvider.id == agent_llm_model.provider_id).first()
            if not llm_provider:
                raise HTTPException(status_code=500, detail=f"LLM Provider not found for model {agent_llm_model.model_name}")
            api_key = decrypt_api_key(llm_provider.api_key_encrypted)

            for i in range(5): # Limit iterations
                crud.update_agent_job_status(db, job_id, f"thinking_step_{i+1}")
                await crud.add_agent_job_log(db, job_id, "thought", f"LLM call iteration {i+1}")
                llm_response = await call_llm_api(
                    provider=llm_provider, model_name=agent_llm_model.model_name,
                    messages=messages, api_key=api_key, tools=all_tools_schema
                )
                response_message = llm_response.get("message", {})
                messages.append(response_message)
                if not response_message.get("tool_calls"):
                    final_output = response_message.get("content", "Agent completed task.")
                    await crud.add_agent_job_log(db, job_id, "thought", f"Task completed. Final output: {final_output}")
                    break
                tool_calls = response_message["tool_calls"]
                await crud.add_agent_job_log(db, job_id, "thought", f"Decided to use tools: {[tc['function']['name'] for tc in tool_calls]}")
                tool_results = []
                for tool_call in tool_calls:
                    function_name = tool_call['function']['name']
                    function_args = json.loads(tool_call['function']['arguments'])
                    await crud.add_agent_job_log(db, job_id, "command", f"Executing tool '{function_name}' with args: {function_args}")
                    result_content = f"Error: Tool '{function_name}' not found."

                    tool_func = agent_tool_registry.get(function_name) # Check agent-specific registry

                    if tool_func:
                        try:
                            # Special handling for request_human_input
                            if function_name == "request_human_input":
                                # This tool will update job status and return a signal to pause
                                result = await tool_func(db=db, job_id=job_id, **function_args)
                                if result.get("status") == "awaiting_human_input":
                                    # Agent is waiting for human input, so we return immediately
                                    await crud.add_agent_job_log(db, job_id, "info", "Agent paused, awaiting human input.")
                                    return # Exit the task execution loop
                                result_content = result.get("message", "Human input requested.")
                            elif function_name == "reflect":
                                result_content = await tool_func(db=db, user=user, job_id=job_id, **function_args)
                            elif function_name == "generate_code":
                                code_req = schemas.CodeGenerationRequest(**function_args)
                                code_res = await tool_func(db, user, code_req)
                                result_content = code_res.generated_code if code_res.success else code_res.error_message
                            elif function_name == "translate_shell_command":
                                shell_req = schemas.ShellCommandTranslationRequest(**function_args)
                                shell_res = await tool_func(db, user, shell_req)
                                result_content = shell_res.translated_command if shell_res.success else shell_res.error_message
                            elif function_name == "perform_file_operation":
                                file_req = schemas.FileOperationRequest(**function_args)
                                file_res = await tool_func(user, file_req)
                                result_content = file_res.message
                            elif function_name == "generate_reasoning":
                                reason_req = schemas.ReasoningRequest(**function_args)
                                reason_res = await tool_func(db, user, reason_req)
                                result_content = reason_res.summary if reason_res.success else reason_res.error_message
                            elif function_name.startswith("git_"):
                                result_content = await tool_func(git_service=git_service, local_path=target_repo_path, **function_args)
                            elif function_name == "execute_shell_command":
                                result_content = await tool_func(terminal_service=terminal_service, **function_args)
                            elif function_name == "run_tests":
                                result_content = await tool_func(terminal_service=terminal_service, local_path=target_repo_path, **function_args)
                            elif function_name == "store_context_item":
                                result_content = await tool_func(db=db, user=user, **function_args)
                            elif function_name == "retrieve_context_items":
                                result_content = await tool_func(db=db, user=user, **function_args)
                            else:
                                result_content = f"Error: Tool '{function_name}' not implemented in agent orchestration."
                        except Exception as e:
                            result_content = f"Error executing tool '{function_name}': {e}"
                    else:
                        result_content = f"Error: Tool '{function_name}' not found in registry."
                    await crud.add_agent_job_log(db, job_id, "output", result_content)
                    tool_results.append({
                        "tool_call_id": tool_call['id'], "role": "tool",
                        "name": function_name, "content": result_content,
                    })
                messages.extend(tool_results)
            
            # If loop finishes without breaking due to human input, update status
            if crud.get_agent_job(db, job_id, str(user.id)).status != "awaiting_human_input":
                crud.update_agent_job_status(db, job_id, "completed", final_output=final_output)
    except Exception as e:
        await crud.add_agent_job_log(db, job_id, "error", f"An unexpected error occurred: {e}")
        crud.update_agent_job_status(db, job_id, "failed", final_output=f"Error: {e}")
