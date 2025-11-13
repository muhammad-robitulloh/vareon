from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
import uuid

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserBase(BaseModel):
    email: str
    username: str

class PermissionBase(BaseModel):
    name: str

class Permission(PermissionBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class RoleBase(BaseModel):
    name: str

class Role(RoleBase):
    id: uuid.UUID
    permissions: List[Permission] = []

    class Config:
        orm_mode = True

class UserCreate(UserBase):
    password: str

class UserInDB(UserBase):
    hashed_password: str

class User(UserBase):
    id: uuid.UUID
    is_active: bool
    is_verified: bool = False
    verification_token: Optional[str] = None
    verification_token_expires_at: Optional[datetime] = None
    roles: List[Role] = []

    class Config:
        orm_mode = True

class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

class MessageResponse(BaseModel):
    message: str

class Agent(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID # Added owner_id
    name: str
    status: str # e.g., 'online', 'offline', 'busy'
    agent_type: str # e.g., 'data_collector', 'analyzer', 'executor'

class AgentCreate(BaseModel):
    name: str
    agent_type: str

class HardwareDevice(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID # Added owner_id
    name: str
    device_type: str
    status: str # e.g., 'connected', 'disconnected', 'error'

class HardwareDeviceUpdate(BaseModel):
    status: str

class Workflow(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID # Added owner_id
    name: str
    status: str # e.g., 'running', 'completed', 'failed', 'pending'
    steps: List[str]

class WorkflowCreate(BaseModel):
    name: str
    steps: List[str]

class Dataset(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID # Added owner_id
    name: str
    size_mb: float
    format: str
    creation_date: datetime

class DatasetCreate(BaseModel):
    name: str
    size_mb: float
    format: str

class RoutingRule(BaseModel):
    id: uuid.UUID
    owner_id: uuid.UUID # Added owner_id
    name: str
    condition: str # e.g., "user_location == 'US'"
    target_model: str # e.g., "gpt-4", "gemini-pro"
    priority: int

class RoutingRuleCreate(BaseModel):
    name: str
    condition: str
    target_model: str
    priority: int

class TelemetryData(BaseModel):
    source_id: str # ID of the agent or device sending telemetry
    source_type: str # e.g., "agent", "hardware_device"
    metric_name: str # e.g., "cpu_usage", "memory_usage", "task_completed"
    metric_value: float # The value of the metric
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ChatMessage(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    sender: str # "user" or "llm"
    message_content: str
    timestamp: datetime

    class Config:
        orm_mode = True

class ConversationBase(BaseModel):
    title: Optional[str] = None

class ConversationCreate(ConversationBase):
    pass

class ConversationUpdate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[uuid.UUID] = None # Optional: if part of an existing conversation

class ChatResponse(BaseModel):
    response: str
    conversation_id: uuid.UUID
    message_id: uuid.UUID

class ContextMemoryBase(BaseModel):
    key: str
    value: str # Storing as string, assuming JSON string or plain text

class ContextMemoryCreate(ContextMemoryBase):
    pass

class ContextMemoryUpdate(BaseModel):
    value: str # Only value can be updated

class ContextMemory(ContextMemoryBase):
    id: uuid.UUID
    user_id: uuid.UUID
    last_accessed: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LLMProviderBase(BaseModel):
    name: str
    base_url: str

class LLMProviderCreate(LLMProviderBase):
    api_key: str # API key will be encrypted before saving

class LLMProviderUpdate(LLMProviderBase):
    api_key: Optional[str] = None # API key can be updated
    name: Optional[str] = None
    base_url: Optional[str] = None

class LLMProvider(LLMProviderBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LLMModelBase(BaseModel):
    provider_id: uuid.UUID
    model_name: str
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None

class LLMModelCreate(LLMModelBase):
    pass

class LLMModelUpdate(LLMModelBase):
    provider_id: Optional[uuid.UUID] = None
    model_name: Optional[str] = None

class LLMModel(LLMModelBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    provider: LLMProvider # Nested provider info

    class Config:
        orm_mode = True

class UserLLMPreferenceBase(BaseModel):
    default_model_id: Optional[uuid.UUID] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None

class UserLLMPreferenceCreate(UserLLMPreferenceBase):
    pass

class UserLLMPreferenceUpdate(UserLLMPreferenceBase):
    pass

class UserLLMPreference(UserLLMPreferenceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    default_model: Optional[LLMModel] = None # Nested model info

    class Config:
        orm_mode = True

class TerminalSessionBase(BaseModel):
    status: str = "active" # "active", "closed"
    last_command: Optional[str] = None

class TerminalSessionCreate(BaseModel):
    pass # No initial data needed for creation, defaults handle it

class TerminalSessionUpdate(TerminalSessionBase):
    ended_at: Optional[datetime] = None
    status: Optional[str] = None

class TerminalSession(TerminalSessionBase):
    id: uuid.UUID
    user_id: uuid.UUID
    started_at: datetime
    ended_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class TerminalCommandHistoryCreate(BaseModel):
    session_id: uuid.UUID
    command: str
    output: Optional[str] = None

class TerminalCommandHistory(TerminalCommandHistoryCreate):
    id: uuid.UUID
    timestamp: datetime

    class Config:
        orm_mode = True

class SystemStatusModule(BaseModel):
    status: str
    uptime: Optional[str] = None
    activeChats: Optional[int] = 0
    messagesProcessed: Optional[int] = 0
    avgResponseTime: Optional[str] = None
    activeAgents: Optional[int] = 0
    jobsCompleted: Optional[int] = 0
    devicesConnected: Optional[int] = 0
    activeWorkflows: Optional[int] = 0
    datasetsManaged: Optional[int] = 0
    searchQueriesProcessed: Optional[int] = 0
    modelsActive: Optional[int] = 0
    routingRules: Optional[int] = 0
    requestsRouted: Optional[int] = 0
    cpu_percent: Optional[float] = 0.0
    memory_percent: Optional[float] = 0.0
    memory_total: Optional[int] = 0
    memory_available: Optional[int] = 0
    system_metrics_mocked: Optional[bool] = False
    system_metrics_reason: Optional[str] = None

    class Config:
        orm_mode = True

class SystemStatus(BaseModel):
    arcana: SystemStatusModule
    myntrix: SystemStatusModule
    neosyntis: SystemStatusModule
    cognisys: SystemStatusModule
    mocked: Optional[bool] = False
    reason: Optional[str] = None