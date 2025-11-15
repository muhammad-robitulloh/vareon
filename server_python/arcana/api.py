from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import json
import asyncio
import logging

from server_python.database import get_db, User as DBUser
from server_python.auth import get_current_user
from . import crud, schemas
from . import code_generation_service
from . import shell_translation_service
from . import reasoning_service
from . import file_management_service
from . import agent_orchestration_service

# Initialize a logger for this module
logger = logging.getLogger(__name__)

router = APIRouter()

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

