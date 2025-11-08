from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: str
    username: str

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class Role(BaseModel):
    id: str
    name: str
    permissions: List[str] = []

class Permission(BaseModel):
    id: str
    name: str

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires_at: Optional[datetime] = None
    roles: List[Role] = [] # Add roles to the User model

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

class Agent(BaseModel):
    id: str
    name: str
    status: str # e.g., 'online', 'offline', 'busy'
    agent_type: str # e.g., 'data_collector', 'analyzer', 'executor'

class AgentCreate(BaseModel):
    name: str
    agent_type: str

class HardwareDevice(BaseModel):
    id: str
    name: str
    device_type: str
    status: str # e.g., 'connected', 'disconnected', 'error'

class HardwareDeviceUpdate(BaseModel):
    status: str

class Workflow(BaseModel):
    id: str
    name: str
    status: str # e.g., 'running', 'completed', 'failed', 'pending'
    steps: List[str]

class WorkflowCreate(BaseModel):
    name: str
    steps: List[str]

class Dataset(BaseModel):
    id: str
    name: str
    size_mb: float
    format: str
    creation_date: datetime

class DatasetCreate(BaseModel):
    name: str
    size_mb: float
    format: str

class RoutingRule(BaseModel):
    id: str
    name: str
    condition: str # e.g., "user_location == 'US'"
    target_model: str # e.g., "gpt-4", "gemini-pro"
    priority: int

class RoutingRuleCreate(BaseModel):
    name: str
    condition: str
    target_model: str
    priority: int