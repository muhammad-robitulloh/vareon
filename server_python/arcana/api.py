from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from server_python.database import get_db, User as DBUser
from server_python.auth import get_current_user
from . import crud, schemas
from . import code_generation_service # Import the new service
from . import shell_translation_service # Import the new service
from . import reasoning_service # Import the new service
from . import file_management_service # Import the new service
from . import agent_orchestration_service # Import the new service

router = APIRouter()

@router.post("/agents/", response_model=schemas.ArcanaAgentResponse, status_code=status.HTTP_201_CREATED)
def create_arcana_agent(
    agent: schemas.ArcanaAgentCreate, 
    current_user: DBUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Create a new Arcana agent for the current user.
    """
    db_agent = crud.create_agent(db=db, agent=agent, owner_id=str(current_user.id))
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
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
    db_agent = crud.get_agent(db, agent_id=agent_id, owner_id=str(current_user.id))
    if db_agent is None:
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
    db_agent = crud.update_agent(db, agent_id=agent_id, agent=agent, owner_id=str(current_user.id))
    if db_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arcana Agent not found")
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
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
    db_agent = crud.delete_agent(db, agent_id=agent_id, owner_id=str(current_user.id))
    if db_agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Arcana Agent not found")
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
    return await reasoning_service.generate_reasoning(db, current_user, request)

@router.post("/file-operations", response_model=schemas.FileOperationResponse)
async def file_operations_endpoint(
    request: schemas.FileOperationRequest,
    current_user: DBUser = Depends(get_current_user) # No DB session needed for file ops
):
    """
    Performs various file operations within the user's sandboxed directory.
    """
    return await file_management_service.perform_file_operation(current_user, request)

@router.post("/agents/{agent_id}/execute", response_model=schemas.AgentExecuteResponse)
async def execute_arcana_agent_task(
    agent_id: str,
    request: schemas.AgentExecuteRequest,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Executes a task for a specific Arcana Agent.
    """
    # Ensure the agent_id in the path matches the one in the request body
    if str(request.agent_id) != agent_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Agent ID in path and request body do not match.")
    
    return await agent_orchestration_service.execute_agent_task(db, current_user, request)
