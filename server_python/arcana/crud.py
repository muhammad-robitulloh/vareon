from sqlalchemy.orm import Session
import uuid
import json

from . import schemas
from server_python.database import ArcanaAgent as DBArcanaAgent

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
    db_agent = DBArcanaAgent(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=agent.name,
        persona=agent.persona,
        mode=agent.mode,
        objective=agent.objective,
        status=agent.status,
        configuration=json.dumps(agent.configuration) if agent.configuration else None
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
    
    if 'configuration' in update_data and update_data['configuration'] is not None:
        update_data['configuration'] = json.dumps(update_data['configuration'])

    for key, value in update_data.items():
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
