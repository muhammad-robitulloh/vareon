from sqlalchemy.orm import Session
import uuid
import json
from typing import List, Optional, Dict, Any # Added Dict, Any
from datetime import datetime

from . import schemas
from server_python.database import ArcanaAgent as DBArcanaAgent, ArcanaAgentJob as DBArcanaAgentJob, ArcanaAgentJobLog as DBArcanaAgentJobLog

def get_agent(db: Session, agent_id: str, owner_id: str):
    """
    Retrieve a single Arcana agent by its ID and owner.
    """
    return db.query(DBArcanaAgent).filter(DBArcanaAgent.id == agent_id, DBArcanaAgent.owner_id == owner_id).first()

def get_agents(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of Arcana agents for a specific owner.
    """
    return db.query(DBArcanaAgent).filter(DBArcanaAgent.owner_id == owner_id).offset(skip).limit(limit).all()

def create_agent(db: Session, agent: schemas.ArcanaAgentCreate, owner_id: str):
    """
    Create a new Arcana agent.
    """
    config_dict = agent.configuration if agent.configuration else {}
    if agent.target_repo_path:
        config_dict['target_repo_path'] = agent.target_repo_path
    if agent.target_branch:
        config_dict['target_branch'] = agent.target_branch

    db_agent = DBArcanaAgent(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=agent.name,
        persona=agent.persona,
        mode=agent.mode,
        objective=agent.objective,
        status=agent.status,
        configuration=json.dumps(config_dict)
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_agent(db: Session, agent_id: str, agent: schemas.ArcanaAgentUpdate, owner_id: str):
    """
    Update an existing Arcana agent.
    """
    db_agent = get_agent(db, agent_id, owner_id)
    if not db_agent:
        return None

    update_data = agent.dict(exclude_unset=True)
    
    # Handle configuration updates
    current_config = json.loads(db_agent.configuration) if db_agent.configuration else {}
    
    if 'configuration' in update_data and update_data['configuration'] is not None:
        current_config.update(update_data['configuration'])
    
    if 'target_repo_path' in update_data and update_data['target_repo_path'] is not None:
        current_config['target_repo_path'] = update_data['target_repo_path']
    if 'target_branch' in update_data and update_data['target_branch'] is not None:
        current_config['target_branch'] = update_data['target_branch']

    # Remove target_repo_path and target_branch from update_data to avoid direct column update
    update_data.pop('target_repo_path', None)
    update_data.pop('target_branch', None)

    db_agent.configuration = json.dumps(current_config)

    for key, value in update_data.items():
        if key != 'configuration': # Configuration is handled separately
            setattr(db_agent, key, value)

    db.commit()
    db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: str, owner_id: str):
    """
    Delete an Arcana agent.
    """
    db_agent = get_agent(db, agent_id, owner_id)
    if not db_agent:
        return None
    
    db.delete(db_agent)
    db.commit()
    return db_agent

### Agent Job and Log CRUD Operations ###

def create_agent_job(
    db: Session, 
    agent_id: str, 
    owner_id: str, 
    goal: str, 
    message_history: Optional[List[Dict[str, Any]]] = None,
    original_request: Optional[schemas.AgentExecuteRequest] = None
) -> DBArcanaAgentJob:
    """
    Creates a new job for an Arcana agent.
    """
    db_job = DBArcanaAgentJob(
        id=str(uuid.uuid4()),
        agent_id=agent_id,
        owner_id=owner_id,
        goal=goal,
        status="starting",
        message_history=json.dumps(message_history) if message_history else None,
        original_request=json.dumps(original_request.dict()) if original_request else None
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def get_agent_job(db: Session, job_id: str, owner_id: str) -> Optional[DBArcanaAgentJob]:
    """
    Retrieves a specific agent job.
    """
    db_job = db.query(DBArcanaAgentJob).filter(DBArcanaAgentJob.id == job_id, DBArcanaAgentJob.owner_id == owner_id).first()
    if db_job:
        if db_job.message_history:
            db_job.message_history = json.loads(db_job.message_history)
        if db_job.original_request:
            db_job.original_request = schemas.AgentExecuteRequest.parse_raw(db_job.original_request)
    return db_job

def update_agent_job_status(db: Session, job_id: str, status: str, final_output: str = None, message_history: Optional[List[Dict[str, Any]]] = None):
    """
    Updates the status, optionally the final output, and message history of an agent job.
    """
    db_job = db.query(DBArcanaAgentJob).filter(DBArcanaAgentJob.id == job_id).first()
    if db_job:
        db_job.status = status
        if status in ["completed", "failed"]:
            db_job.ended_at = datetime.utcnow()
        if final_output:
            db_job.final_output = final_output
        if message_history is not None:
            db_job.message_history = json.dumps(message_history)
        db.commit()
        db.refresh(db_job)

        # Send status update via WebSocket
        status_message = {
            "type": "agent_status_update",
            "payload": {
                "job_id": job_id,
                "status": db_job.status,
                "updated_at": db_job.updated_at.isoformat(),
                "final_output": db_job.final_output
            }
        }
        # This needs to be awaited, but this function is not async.
        # For now, we'll call it without await, which means it will run in the background
        # and might not be guaranteed to send before the function returns.
        # A more robust solution would involve making this function async or using a background task.
        import asyncio
        asyncio.create_task(manager.send_to_session(job_id, json.dumps(status_message)))
    return db_job

from server_python.orchestrator.connection_manager import manager # Import the WebSocket manager

async def add_agent_job_log(db: Session, job_id: str, log_type: str, content: str):
    """
    Adds a log entry to an agent job and sends it via WebSocket.
    """
    db_log = DBArcanaAgentJobLog(
        id=str(uuid.uuid4()),
        job_id=job_id,
        timestamp=datetime.utcnow(),
        log_type=log_type,
        content=content
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)

    # Send log via WebSocket
    log_message = {
        "type": "agent_log",
        "payload": {
            "job_id": job_id,
            "log_id": str(db_log.id),
            "timestamp": db_log.timestamp.isoformat(),
            "log_type": db_log.log_type,
            "content": db_log.content
        }
    }
    await manager.send_to_session(job_id, json.dumps(log_message))

def get_recent_agent_job_logs(db: Session, job_id: str, limit: int = 5) -> List[schemas.ArcanaAgentJobLogResponse]:
    """
    Retrieves the last N log entries for a specific agent job.
    """
    logs = db.query(DBArcanaAgentJobLog).filter(DBArcanaAgentJobLog.job_id == job_id)\
        .order_by(DBArcanaAgentJobLog.timestamp.desc())\
        .limit(limit).all()
    return [schemas.ArcanaAgentJobLogResponse.from_orm(log) for log in reversed(logs)] # Return in chronological order

def get_agent_jobs_for_agent(db: Session, agent_id: str, owner_id: str, skip: int = 0, limit: int = 10) -> List[DBArcanaAgentJob]:
    """
    Retrieves all jobs for a specific agent.
    """
    jobs = db.query(DBArcanaAgentJob).filter(
        DBArcanaAgentJob.agent_id == agent_id,
        DBArcanaAgentJob.owner_id == owner_id
    ).order_by(DBArcanaAgentJob.created_at.desc()).offset(skip).limit(limit).all()
    
    for job in jobs:
        if job.message_history:
            job.message_history = json.loads(job.message_history)
        if job.original_request:
            job.original_request = schemas.AgentExecuteRequest.parse_raw(job.original_request)
    return jobs
