from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
import logging

from server_python.database import get_db, User as DBUser
from server_python.auth import get_current_user
from . import crud, schemas
from server_python.schemas import ArcanaCliCommandResponse, ArcanaCliCommandRequest, ArcanaApiKeyResponse # Import ArcanaCliCommandResponse, ArcanaCliCommandRequest, and ArcanaApiKeyResponse from top-level schemas
from . import code_generation_service
from . import shell_translation_service
from . import reasoning_service
from . import file_management_service
from . import agent_orchestration_service

# Initialize a logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/version")
async def get_backend_version():
    """
    Returns the current version of the Arcana backend.
    """
    return {"version": "0.1.0-alpha"} # Hardcoded for now, can be dynamic later

@router.get("/file-tree/", response_model=List[schemas.FileInfo])
async def get_arcana_file_tree(
    current_user: DBUser = Depends(get_current_user)
):
    """
    Retrieves the entire file tree for the user's sandboxed project directory.
    This provides a hierarchical view of all files and folders.
    """
    logger.info(f"User {current_user.id} requested file tree.")
    return await file_management_service.get_file_tree(current_user)

@router.post("/agents/", response_model=schemas.ArcanaAgentResponse, status_code=status.HTTP_201_CREATED)
def create_arcana_agent(
    agent: schemas.ArcanaAgentCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new Arcana agent for the current user.
    """
    logger.info(f"User {current_user.id} is creating a new Arcana agent named '{agent.name}'.")
    db_agent = crud.create_agent(db=db, agent=agent, owner_id=str(current_user.id))
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    logger.info(f"Successfully created agent {db_agent.id} for user {current_user.id}.")
    return db_agent

@router.get("/agents/", response_model=List[schemas.ArcanaAgentResponse])
def read_arcana_agents(
    skip: int = 0,
    limit: int = 100,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve all Arcana agents for the current user.
    """
    logger.info(f"User {current_user.id} is reading their Arcana agents.")
    agents = crud.get_agents(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    for agent in agents:
        if agent.configuration:
            agent.configuration = json.loads(agent.configuration)
    return agents

@router.get("/agents/{agent_id}", response_model=schemas.ArcanaAgentResponse)
def read_arcana_agent(
    agent_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific Arcana agent by its ID.
    """
    logger.info(f"User {current_user.id} is reading Arcana agent {agent_id}.")
    db_agent = crud.get_agent(db, agent_id=agent_id, owner_id=str(current_user.id))
    if db_agent is None:
        logger.warning(f"User {current_user.id} failed to find Arcana agent {agent_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arcana Agent not found")
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.put("/agents/{agent_id}", response_model=schemas.ArcanaAgentResponse)
def update_arcana_agent(
    agent_id: str,
    agent: schemas.ArcanaAgentUpdate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an Arcana agent.
    """
    logger.info(f"User {current_user.id} is updating Arcana agent {agent_id}.")
    db_agent = crud.update_agent(db, agent_id=agent_id, agent=agent, owner_id=str(current_user.id))
    if db_agent is None:
        logger.warning(f"User {current_user.id} failed to update non-existent Arcana agent {agent_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arcana Agent not found")
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    logger.info(f"Successfully updated agent {agent_id} for user {current_user.id}.")
    return db_agent

@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_arcana_agent(
    agent_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an Arcana agent.
    """
    logger.info(f"User {current_user.id} is deleting Arcana agent {agent_id}.")
    db_agent = crud.delete_agent(db, agent_id=agent_id, owner_id=str(current_user.id))
    if db_agent is None:
        logger.warning(f"User {current_user.id} failed to delete non-existent Arcana agent {agent_id}.")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arcana Agent not found")
    logger.info(f"Successfully deleted agent {agent_id} for user {current_user.id}.")
    return {"ok": True}

@router.post("/generate-code", response_model=schemas.CodeGenerationResponse)
async def generate_code_endpoint(
    request: schemas.CodeGenerationRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates code based on a natural language prompt.
    """
    logger.info(f"User {current_user.id} requested code generation.")
    return await code_generation_service.generate_code(db, current_user, request)

@router.post("/translate-shell-command", response_model=schemas.ShellCommandTranslationResponse)
async def translate_shell_command_endpoint(
    request: schemas.ShellCommandTranslationRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Translates a natural language instruction into a shell command.
    """
    logger.info(f"User {current_user.id} requested shell command translation.")
    return await shell_translation_service.translate_shell_command(db, current_user, request)

@router.post("/generate-reasoning", response_model=schemas.ReasoningResponse)
async def generate_reasoning_endpoint(
    request: schemas.ReasoningRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a detailed reasoning trace for a given task.
    """
    logger.info(f"User {current_user.id} requested reasoning generation.")
    return await reasoning_service.generate_reasoning(db, current_user, request)

@router.post("/file-operations", response_model=schemas.FileOperationResponse)
async def file_operations_endpoint(
    request: schemas.FileOperationRequest,
    current_user: DBUser = Depends(get_current_user) # No DB session needed for file ops
):
    """
    Performs various file operations within the user's sandboxed directory.
    """
    logger.info(f"User {current_user.id} requested file operation: {request.operation} on path '{request.path}'.")
    return await file_management_service.perform_file_operation(current_user, request)

@router.post("/agents/{agent_id}/execute", response_model=schemas.ArcanaAgentJobResponse)
async def execute_arcana_agent_task(
    agent_id: str,
    request: schemas.AgentExecuteRequest,
    background_tasks: BackgroundTasks,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes a task for a specific Arcana Agent as a background job.
    """
    logger.info(f"User {current_user.id} requested to execute task for agent {agent_id}.")
    if str(request.agent_id) != agent_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent ID in path and request body do not match.")

    initial_messages = [{"role": "user", "content": request.task_prompt}]

    job = crud.create_agent_job(
        db,
        agent_id=agent_id,
        owner_id=str(current_user.id),
        goal=request.task_prompt,
        message_history=initial_messages,
        original_request=request
    )
    logger.info(f"Created job {job.id} for agent {agent_id}.")

    background_tasks.add_task(
        agent_orchestration_service.execute_agent_task,
        db,
        current_user,
        request,
        job.id,
        initial_messages=initial_messages,
        original_request_obj=request
    )
    logger.info(f"Added job {job.id} to background tasks for execution.")

    return job

@router.get("/agents/{agent_id}/jobs/", response_model=List[schemas.ArcanaAgentJobResponse])
def get_agent_jobs(
    agent_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10
):
    """
    Get all jobs for a specific agent.
    """
    logger.info(f"User {current_user.id} is fetching jobs for agent {agent_id}.")
    return crud.get_agent_jobs_for_agent(db, agent_id=agent_id, owner_id=str(current_user.id), skip=skip, limit=limit)

@router.get("/jobs/{job_id}", response_model=schemas.ArcanaAgentJobResponse)
def get_agent_job(
    job_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the status and details of a specific agent job.
    """
    logger.info(f"User {current_user.id} is fetching job {job_id}.")
    job = crud.get_agent_job(db, job_id=job_id, owner_id=str(current_user.id))
    if not job:
        logger.warning(f"User {current_user.id} failed to find job {job_id}.")
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.get("/jobs/{job_id}/logs", response_model=List[schemas.ArcanaAgentJobLogResponse])
def get_agent_job_logs(
    job_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the logs for a specific agent job.
    """
    logger.info(f"User {current_user.id} is fetching logs for job {job_id}.")
    job = crud.get_agent_job(db, job_id=job_id, owner_id=str(current_user.id))
    if not job:
        logger.warning(f"User {current_user.id} failed to find job {job_id} while fetching logs.")
        raise HTTPException(status_code=404, detail="Job not found")
    return job.logs

@router.post("/jobs/{job_id}/submit_human_input", response_model=schemas.ArcanaAgentJobResponse)
async def submit_human_input(
    job_id: str,
    human_input_request: schemas.HumanInputRequest,
    background_tasks: BackgroundTasks,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits human input to an agent job that is awaiting human input and resumes its execution.
    """
    logger.info(f"User {current_user.id} is submitting human input for job {job_id}.")
    job = crud.get_agent_job(db, job_id=job_id, owner_id=str(current_user.id))
    if not job:
        logger.warning(f"User {current_user.id} failed to find job {job_id} for human input.")
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status != "awaiting_human_input":
        logger.warning(f"User {current_user.id} tried to submit input to job {job_id} which is not awaiting input (status: {job.status}).")
        raise HTTPException(status_code=400, detail="Job is not awaiting human input.")

    human_message = {"role": "user", "content": human_input_request.human_input}
    updated_messages = job.message_history if job.message_history else []
    updated_messages.append(human_message)

    crud.add_agent_job_log(db, job_id, "human_input", human_input_request.human_input)
    crud.update_agent_job_status(db, job_id, "resumed", message_history=updated_messages)
    logger.info(f"Job {job_id} status updated to 'resumed' after receiving human input.")

    if not job.original_request:
        logger.error(f"Original request not found for job {job_id}. Cannot resume.")
        raise HTTPException(status_code=500, detail="Original request not found for resuming job.")

    background_tasks.add_task(
        agent_orchestration_service.execute_agent_task,
        db,
        current_user,
        job.original_request,
        job.id,
        initial_messages=updated_messages,
        original_request_obj=job.original_request
    )
    logger.info(f"Resumed job {job.id} and added to background tasks.")

    updated_job = crud.get_agent_job(db, job_id=job_id, owner_id=str(current_user.id))
    return updated_job

@router.post("/jobs/{job_id}/resume")
async def resume_agent_job(
    job_id: str,
    background_tasks: BackgroundTasks,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Resume a job that is awaiting human input.
    This endpoint is now deprecated in favor of submit_human_input.
    """
    logger.warning(f"Deprecated endpoint /resume called for job {job_id}.")
    raise HTTPException(status_code=400, detail="This endpoint is deprecated. Use /jobs/{job_id}/submit_human_input instead.")

@router.post("/cli/execute", response_model=ArcanaCliCommandResponse)
async def execute_cli_command(
    request: ArcanaCliCommandRequest,
    background_tasks: BackgroundTasks, # Correctly inject BackgroundTasks
    db: Session = Depends(get_db)
):
    """
    Executes a command received from the Arcana CLI.
    This endpoint validates the API key and routes the command to the appropriate Arcana service.
    """
    db_api_key = crud.get_api_key_by_key(db, request.api_key)
    if not db_api_key or not db_api_key.is_active:
        logger.warning(f"Unauthorized CLI access attempt with invalid/inactive API Key: {request.api_key[:8]}...")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API Key. Please check your key or generate a new one from the Vareon dashboard."
        )

    # Use the user_id associated with the API key
    current_user = DBUser(id=db_api_key.user_id, email=f"cli_user_{db_api_key.user_id}@vareon.com")
    logger.info(f"CLI command received from user {current_user.id} (via API Key '{db_api_key.name}'): '{request.command}' with args: {request.args}")

    try:
        response_output = ""
        response_message = "Command executed successfully."
        
        # Basic command routing
        if request.command == "generate-code":
            if not request.args or len(request.args) < 1:
                logger.warning(f"User {current_user.id} failed 'generate-code': Missing prompt.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing argument: 'prompt' is required for 'generate-code'. Usage: arcana generate-code <prompt>"
                )
            prompt = request.args[0]
            code_request = schemas.CodeGenerationRequest(prompt=prompt)
            code_response = await code_generation_service.generate_code(db, current_user, code_request)
            response_output = code_response.generated_code
            response_message = "Code generated successfully."
            logger.info(f"User {current_user.id} successfully executed 'generate-code'. Output length: {len(response_output)}.")
        elif request.command == "translate-shell":
            if not request.args or len(request.args) < 1:
                logger.warning(f"User {current_user.id} failed 'translate-shell': Missing instruction.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing argument: 'instruction' is required for 'translate-shell'. Usage: arcana translate-shell <instruction>"
                )
            instruction = request.args[0]
            shell_request = schemas.ShellCommandTranslationRequest(instruction=instruction)
            shell_response = await shell_translation_service.translate_shell_command(db, current_user, shell_request)
            response_output = shell_response.shell_command
            response_message = "Shell command translated successfully."
            logger.info(f"User {current_user.id} successfully executed 'translate-shell'. Output: '{response_output}'.")
        elif request.command == "reason":
            if not request.args or len(request.args) < 1:
                logger.warning(f"User {current_user.id} failed 'reason': Missing prompt.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing argument: 'prompt' is required for 'reason'. Usage: arcana reason <prompt>"
                )
            prompt = request.args[0]
            reasoning_request = schemas.ReasoningRequest(prompt=prompt)
            reasoning_response = await reasoning_service.generate_reasoning(db, current_user, reasoning_request)
            response_output = reasoning_response.reasoning_trace
            response_message = "Reasoning generated successfully."
            logger.info(f"User {current_user.id} successfully executed 'reason'. Output length: {len(response_output)}.")
        elif request.command == "file-operation":
            if not request.args or len(request.args) < 2: # operation and path are minimum
                logger.warning(f"User {current_user.id} failed 'file-operation': Missing operation or path.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing arguments: 'operation' and 'path' are required for 'file-operation'. Usage: arcana file-operation <operation> <path> [content]"
                )
            operation = request.args[0]
            path = request.args[1]
            content = request.args[2] if len(request.args) > 2 else None
            
            file_op_request = schemas.FileOperationRequest(operation=operation, path=path, content=content)
            file_op_response = await file_management_service.perform_file_operation(current_user, file_op_request)
            response_output = file_op_response.message
            response_message = f"File operation '{operation}' on '{path}' completed."
            logger.info(f"User {current_user.id} successfully executed 'file-operation' ('{operation}' on '{path}').")
        elif request.command == "agent-execute":
            if not request.args or len(request.args) < 2:
                logger.warning(f"User {current_user.id} failed 'agent-execute': Missing agent ID or task prompt.")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Missing arguments: 'agent_id' and 'task_prompt' are required for 'agent-execute'. Usage: arcana agent-execute <agent_id> <task_prompt>"
                )
            agent_id = request.args[0]
            task_prompt = request.args[1]
            
            # Create the agent job
            agent_execute_request = schemas.AgentExecuteRequest(agent_id=agent_id, task_prompt=task_prompt)
            job = crud.create_agent_job(
                db,
                agent_id=agent_id,
                owner_id=str(current_user.id),
                goal=task_prompt,
                message_history=[{"role": "user", "content": task_prompt}],
                original_request=agent_execute_request
            )
            logger.info(f"Created job {job.id} for agent {agent_id} for user {current_user.id}.")

            # Run the agent task in the background
            background_tasks.add_task( # Use the injected background_tasks
                agent_orchestration_service.execute_agent_task,
                db,
                current_user,
                agent_execute_request,
                job.id,
                initial_messages=[{"role": "user", "content": task_prompt}],
                original_request_obj=agent_execute_request
            )
            response_output = f"Job ID: {job.id}"
            response_message = "Agent task initiated. Use 'arcana job-status <job_id>' to check progress."
            logger.info(f"User {current_user.id} successfully initiated 'agent-execute' for agent {agent_id}. Job ID: {job.id}.")
        else:
            logger.warning(f"User {current_user.id} attempted unknown command: '{request.command}'.")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unknown command: '{request.command}'. Please refer to the CLI documentation for available commands."
            )

        return schemas.ArcanaCliCommandResponse(
            status="success",
            message=response_message,
            output=response_output
        )
    except HTTPException as e:
        logger.error(f"CLI command execution failed for user {current_user.id} with HTTP {e.status_code}: {e.detail}")
        return schemas.ArcanaCliCommandResponse(
            status="error",
            message=e.detail,
            error=e.detail
        )
    except Exception as e:
        logger.exception(f"An unexpected internal server error occurred during CLI command execution for user {current_user.id}.")
        return schemas.ArcanaCliCommandResponse(
            status="error",
            message="An unexpected internal server error occurred. Please try again later.",
            error=str(e)
        )

@router.post("/api-keys/", response_model=ArcanaApiKeyResponse, status_code=status.HTTP_201_CREATED)
def create_arcana_api_key(
    api_key_data: schemas.ArcanaApiKeyCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generates a new Arcana API key for the current user.
    """
    logger.info(f"User {current_user.id} is generating a new API key.")
    db_api_key = crud.create_api_key(db=db, api_key_data=api_key_data, owner_id=str(current_user.id))
    # Return the raw key only on creation
    return schemas.ArcanaApiKeyResponse(
        id=db_api_key.id,
        key=db_api_key.raw_key, # raw_key is temporarily attached in crud.create_api_key
        user_id=db_api_key.user_id,
        name=db_api_key.name,
        created_at=db_api_key.created_at,
        expires_at=db_api_key.expires_at,
        is_active=db_api_key.is_active
    )

@router.get("/api-keys/", response_model=List[ArcanaApiKeyResponse])
def get_arcana_api_keys(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieves all Arcana API keys for the current user.
    """
    logger.info(f"User {current_user.id} is retrieving their API keys.")
    api_keys = crud.get_api_keys_for_user(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    # Do not return the actual key for existing keys for security reasons
    return [
        schemas.ArcanaApiKeyResponse(
            id=key.id,
            key="****************", # Mask the key for retrieval
            user_id=key.user_id,
            name=key.name,
            created_at=key.created_at,
            expires_at=key.expires_at,
            is_active=key.is_active
        ) for key in api_keys
    ]

@router.delete("/api-keys/{api_key_id}", status_code=status.HTTP_204_NO_CONTENT)
def deactivate_arcana_api_key(
    api_key_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deactivates an Arcana API key for the current user.
    """
    logger.info(f"User {current_user.id} is deactivating API key {api_key_id}.")
    db_api_key = crud.deactivate_api_key(db, api_key_id=api_key_id, owner_id=str(current_user.id))
    if db_api_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found or not owned by user.")
    logger.info(f"API key {api_key_id} deactivated for user {current_user.id}.")
    return {"ok": True}

@router.post("/api-keys/{api_key_id}/rotate", response_model=ArcanaApiKeyResponse)
def rotate_arcana_api_key(
    api_key_id: str,
    new_key_name: str, # Expecting the new key's name in the request body
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rotates an Arcana API key: deactivates the old one and creates a new one.
    """
    logger.info(f"User {current_user.id} is rotating API key {api_key_id}.")
    new_key = crud.rotate_api_key(db, api_key_id=api_key_id, owner_id=str(current_user.id), new_key_name=new_key_name)
    if new_key is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="API Key not found or not owned by user.")
    
    # Return the raw key of the newly generated key
    return schemas.ArcanaApiKeyResponse(
        id=new_key.id,
        key=new_key.raw_key, # raw_key is temporarily attached in crud.create_api_key
        user_id=new_key.user_id,
        name=new_key.name,
        created_at=new_key.created_at,
        expires_at=new_key.expires_at,
        is_active=new_key.is_active
    )

@router.post("/cli-configs/", response_model=schemas.UserCliConfigResponse)
def create_or_update_cli_config(
    config_data: schemas.UserCliConfigCreate,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Creates a new CLI configuration setting or updates an existing one for the current user.
    """
    logger.info(f"User {current_user.id} is setting CLI config '{config_data.key}'.")
    db_config = crud.create_or_update_user_cli_config(db, str(current_user.id), config_data)
    return db_config

@router.get("/cli-configs/", response_model=List[schemas.UserCliConfigResponse])
def get_all_cli_configs(
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    Retrieves all CLI configuration settings for the current user.
    """
    logger.info(f"User {current_user.id} is retrieving all CLI configs.")
    configs = crud.get_all_user_cli_configs(db, str(current_user.id), skip=skip, limit=limit)
    return configs

@router.get("/cli-configs/{key}", response_model=schemas.UserCliConfigResponse)
def get_cli_config(
    key: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieves a specific CLI configuration setting for the current user by key.
    """
    logger.info(f"User {current_user.id} is retrieving CLI config '{key}'.")
    db_config = crud.get_user_cli_config(db, str(current_user.id), key)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CLI configuration not found.")
    return db_config

@router.delete("/cli-configs/{key}", status_code=status.HTTP_204_NO_CONTENT)
def delete_cli_config(
    key: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a specific CLI configuration setting for the current user by key.
    """
    logger.info(f"User {current_user.id} is deleting CLI config '{key}'.")
    db_config = crud.delete_user_cli_config(db, str(current_user.id), key)
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="CLI configuration not found.")
    return {"ok": True}

