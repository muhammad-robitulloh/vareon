from sqlalchemy.orm import Session
import uuid
import json
from typing import List, Optional, Dict, Any # Added Dict, Any
from datetime import datetime
import hashlib # Import hashlib

from . import schemas
from server_python.schemas import ArcanaApiKeyCreate, UserCliConfigCreate # Import ArcanaApiKeyCreate and UserCliConfigCreate from top-level schemas
from server_python.database import ArcanaAgent as DBArcanaAgent, ArcanaAgentJob as DBArcanaAgentJob, ArcanaAgentJobLog as DBArcanaAgentJobLog, ArcanaApiKey as DBArcanaApiKey
from server_python.encryption_utils import encrypt_api_key, decrypt_api_key

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
) -> schemas.ArcanaAgentJobResponse: # Change return type hint
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

    # Explicitly create and return the Pydantic response model
    deserialized_message_history = json.loads(db_job.message_history) if db_job.message_history else None
    deserialized_original_request = schemas.AgentExecuteRequest.parse_obj(json.loads(db_job.original_request)) if db_job.original_request else None

    return schemas.ArcanaAgentJobResponse(
        id=db_job.id,
        agent_id=db_job.agent_id,
        owner_id=db_job.owner_id,
        status=db_job.status,
        goal=db_job.goal,
        created_at=db_job.created_at,
        updated_at=db_job.updated_at,
        ended_at=db_job.ended_at,
        final_output=db_job.final_output,
        message_history=deserialized_message_history,
        original_request=deserialized_original_request
    )

def get_agent_job(db: Session, job_id: str, owner_id: str) -> Optional[schemas.ArcanaAgentJobResponse]: # Change return type
    """
    Retrieves a specific agent job.
    """
    db_job = db.query(DBArcanaAgentJob).filter(DBArcanaAgentJob.id == job_id, DBArcanaAgentJob.owner_id == owner_id).first()
    if db_job:
        deserialized_message_history = None
        if db_job.message_history:
            deserialized_message_history = json.loads(db_job.message_history)
        
        deserialized_original_request = None
        if db_job.original_request:
            try:
                parsed_request = json.loads(db_job.original_request)
                deserialized_original_request = schemas.AgentExecuteRequest.parse_obj(parsed_request)
            except (json.JSONDecodeError, ValueError):
                deserialized_original_request = None
        
        # Create and return the Pydantic response model explicitly
        return schemas.ArcanaAgentJobResponse(
            id=db_job.id,
            agent_id=db_job.agent_id,
            owner_id=db_job.owner_id,
            status=db_job.status,
            goal=db_job.goal,
            created_at=db_job.created_at,
            updated_at=db_job.updated_at,
            ended_at=db_job.ended_at,
            final_output=db_job.final_output,
            message_history=deserialized_message_history,
            original_request=deserialized_original_request
        )
    return None

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

async def add_agent_job_log(db: Session, job_id: str, log_type: str, content: Any):
    """
    Adds a log entry to an agent job and sends it via WebSocket.
    """
    # Serialize content if it's a dictionary or list
    if isinstance(content, (dict, list)):
        serialized_content = json.dumps(content)
    else:
        serialized_content = str(content) # Ensure content is always a string

    db_log = DBArcanaAgentJobLog(
        id=str(uuid.uuid4()),
        job_id=job_id,
        timestamp=datetime.utcnow(),
        log_type=log_type,
        content=serialized_content
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

def get_agent_jobs_for_agent(db: Session, agent_id: str, owner_id: str, skip: int = 0, limit: int = 10) -> List[schemas.ArcanaAgentJobResponse]: # Change return type
    """
    Retrieves all jobs for a specific agent.
    """
    db_jobs = db.query(DBArcanaAgentJob).filter(
        DBArcanaAgentJob.agent_id == agent_id,
        DBArcanaAgentJob.owner_id == owner_id
    ).order_by(DBArcanaAgentJob.created_at.desc()).offset(skip).limit(limit).all()
    
    response_jobs = []
    for db_job in db_jobs:
        deserialized_message_history = None
        if db_job.message_history:
            deserialized_message_history = json.loads(db_job.message_history)
        
        deserialized_original_request = None
        if db_job.original_request:
            try:
                parsed_request = json.loads(db_job.original_request)
                deserialized_original_request = schemas.AgentExecuteRequest.parse_obj(parsed_request)
            except (json.JSONDecodeError, ValueError):
                deserialized_original_request = None
        
        response_jobs.append(
            schemas.ArcanaAgentJobResponse(
                id=db_job.id,
                agent_id=db_job.agent_id,
                owner_id=db_job.owner_id,
                status=db_job.status,
                goal=db_job.goal,
                created_at=db_job.created_at,
                updated_at=db_job.updated_at,
                ended_at=db_job.ended_at,
                final_output=db_job.final_output,
                message_history=deserialized_message_history,
                original_request=deserialized_original_request
            )
        )
    return response_jobs


### Arcana API Key CRUD Operations ###

def create_api_key(db: Session, api_key_data: ArcanaApiKeyCreate, owner_id: str) -> DBArcanaApiKey:
    """
    Creates a new Arcana API key for a user.
    """
    # Generate a UUID for the core of the key
    key_uuid = str(uuid.uuid4())
    
    # Create a simple checksum (e.g., first 4 chars of SHA256 hash of the UUID)
    checksum = hashlib.sha256(key_uuid.encode()).hexdigest()[:4]
    
    # Combine prefix, UUID, and checksum
    raw_key = f"arc_{key_uuid}.{checksum}"
    
    encrypted_key = encrypt_api_key(raw_key)

    db_api_key = DBArcanaApiKey(
        id=str(uuid.uuid4()),
        key=encrypted_key,
        user_id=owner_id,
        name=api_key_data.name,
        expires_at=api_key_data.expires_at,
        is_active=api_key_data.is_active
    )
    db.add(db_api_key)
    db.commit()
    db.refresh(db_api_key)
    db_api_key.raw_key = raw_key # Temporarily attach raw key for response
    return db_api_key

def get_api_key_by_key(db: Session, api_key: str) -> Optional[DBArcanaApiKey]:
    """
    Retrieves an Arcana API key by its raw (unencrypted) key.
    This function iterates through active and non-expired keys and decrypts them for comparison.
    """
    now = datetime.utcnow()
    all_active_keys = db.query(DBArcanaApiKey).filter(
        DBArcanaApiKey.is_active == True,
        (DBArcanaApiKey.expires_at == None) | (DBArcanaApiKey.expires_at > now)
    ).all()
    for db_key in all_active_keys:
        try:
            decrypted_key = decrypt_api_key(db_key.key)
            if decrypted_key == api_key:
                return db_key
        except InvalidToken:
            pass # Ignore invalid tokens, treat as not found
        except Exception as e:
            # Log decryption errors but don't expose them
            print(f"Error decrypting API key {db_key.id}: {e}")
            continue
    return None

def get_api_keys_for_user(db: Session, owner_id: str, skip: int = 0, limit: int = 100) -> List[DBArcanaApiKey]:
    """
    Retrieves all Arcana API keys for a specific user.
    """
    return db.query(DBArcanaApiKey).filter(DBArcanaApiKey.user_id == owner_id).offset(skip).limit(limit).all()

def deactivate_api_key(db: Session, api_key_id: str, owner_id: str) -> Optional[DBArcanaApiKey]:
    """
    Deactivates an Arcana API key.
    """
    db_api_key = db.query(DBArcanaApiKey).filter(DBArcanaApiKey.id == api_key_id, DBArcanaApiKey.user_id == owner_id).first()
    if db_api_key:
        db_api_key.is_active = False
        db.commit()
        db.refresh(db_api_key)
    return db_api_key

def rotate_api_key(db: Session, api_key_id: str, owner_id: str, new_key_name: str) -> Optional[DBArcanaApiKey]:
    """
    Rotates an Arcana API key: deactivates the old one and creates a new one.
    """
    old_key = deactivate_api_key(db, api_key_id, owner_id)
    if not old_key:
        return None
    
    # Create a new key with the specified name
    new_key_data = schemas.ArcanaApiKeyCreate(name=new_key_name)
    new_key = create_api_key(db, new_key_data, owner_id)
    return new_key

### User CLI Configuration CRUD Operations ###
from server_python.database import UserCliConfig as DBUserCliConfig # Import the UserCliConfig model

def create_or_update_user_cli_config(db: Session, user_id: str, config_data: schemas.UserCliConfigCreate) -> DBUserCliConfig:
    """
    Creates a new user CLI configuration or updates an existing one.
    """
    db_config = db.query(DBUserCliConfig).filter(
        DBUserCliConfig.user_id == user_id,
        DBUserCliConfig.key == config_data.config_key
    ).first()

    if db_config:
        db_config.value = json.dumps(config_data.config_value) # Ensure JSON is dumped
        db.commit()
        db.refresh(db_config)
    else:
        db_config = DBUserCliConfig(
            id=str(uuid.uuid4()),
            user_id=user_id,
            key=config_data.config_key,
            value=json.dumps(config_data.config_value) # Ensure JSON is dumped
        )
        db.add(db_config)
        db.commit()
        db.refresh(db_config)
    return db_config

def get_user_cli_config(db: Session, user_id: str, key: str) -> Optional[schemas.UserCliConfigResponse]: # Change return type
    """
    Retrieves a specific user CLI configuration by key.
    """
    db_config = db.query(DBUserCliConfig).filter(
        DBUserCliConfig.user_id == user_id,
        DBUserCliConfig.key == key
    ).first()
    if db_config:
        return schemas.UserCliConfigResponse(
            id=db_config.id,
            user_id=db_config.user_id,
            config_key=db_config.key,
            config_value=json.loads(db_config.value),
            created_at=db_config.created_at,
            updated_at=db_config.updated_at
        )
    return None

def get_all_user_cli_configs(db: Session, user_id: str, skip: int = 0, limit: int = 100) -> List[schemas.UserCliConfigResponse]: # Change return type
    """
    Retrieves all CLI configuration settings for a specific user.
    """
    db_configs = db.query(DBUserCliConfig).filter(DBUserCliConfig.user_id == user_id).offset(skip).limit(limit).all()
    return [
        schemas.UserCliConfigResponse(
            id=db_config.id,
            user_id=db_config.user_id,
            config_key=db_config.key,
            config_value=json.loads(db_config.value),
            created_at=db_config.created_at,
            updated_at=db_config.updated_at
        ) for db_config in db_configs
    ]

def delete_user_cli_config(db: Session, user_id: str, key: str) -> Optional[DBUserCliConfig]:
    """
    Deletes a specific user CLI configuration.
    """
    db_config = db.query(DBUserCliConfig).filter(
        DBUserCliConfig.user_id == user_id,
        DBUserCliConfig.key == key
    ).first()
    if db_config:
        db.delete(db_config)
        db.commit()
    return db_config