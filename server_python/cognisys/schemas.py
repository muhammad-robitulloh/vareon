from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import uuid
from datetime import datetime

# --- LLM Provider Schemas ---

class LLMProviderBase(BaseModel):
    name: str
    base_url: str
    enabled: bool = True
    organization_id: Optional[str] = None

class LLMProviderCreate(LLMProviderBase):
    api_key: str = Field(..., description="API key for the LLM provider. Will be encrypted.")

class LLMProviderUpdate(LLMProviderBase):
    name: Optional[str] = None
    base_url: Optional[str] = None
    enabled: Optional[bool] = None
    api_key: Optional[str] = None # Allow updating API key
    organization_id: Optional[str] = None

class LLMProviderResponse(LLMProviderBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- LLM Model Schemas ---

class LLMModelBase(BaseModel):
    provider_id: str
    model_name: str
    type: Optional[str] = None # e.g., "chat", "completion", "embedding"
    is_active: bool = True
    reasoning: bool = False # Does this model support reasoning traces?
    role: Optional[str] = None # e.g., "general", "code_gen", "intent_detection"
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None

class LLMModelCreate(LLMModelBase):
    pass

class LLMModelUpdate(LLMModelBase):
    provider_id: Optional[str] = None
    model_name: Optional[str] = None
    type: Optional[str] = None
    is_active: Optional[bool] = None
    reasoning: Optional[bool] = None
    role: Optional[str] = None
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None

class LLMModelResponse(LLMModelBase):
    id: str
    provider_id: str # Ensure this is str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Routing Rule Schemas ---

class RoutingRuleBase(BaseModel):
    name: str
    condition: str # e.g., "user_role == 'admin'", "prompt contains 'code generation'"
    target_model: str # The model_name or service to route to
    priority: int = Field(..., ge=0, description="Lower number means higher priority")

class RoutingRuleCreate(RoutingRuleBase):
    pass

class RoutingRuleUpdate(RoutingRuleBase):
    name: Optional[str] = None
    condition: Optional[str] = None
    target_model: Optional[str] = None
    priority: Optional[int] = None

class RoutingRuleResponse(RoutingRuleBase):
    id: str
    owner_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

# --- Chat Interaction Schemas (for Cognisys's direct chat endpoint) ---
class ChatRequest(BaseModel):
    prompt: str
    model_name: Optional[str] = None # Allow specifying model for direct chat
    conversation_id: Optional[uuid.UUID] = None # Optional: to continue a conversation

class ChatResponse(BaseModel):
    response: str
    model_used: str
    conversation_id: Optional[uuid.UUID] = None # Optional: to continue a conversation
    message_id: Optional[uuid.UUID] = None
    visualization_data: Optional[Dict[str, Any]] = None

# --- Intent Detection Schemas ---
class IntentDetectionRequest(BaseModel):
    prompt: str = Field(..., description="The user's natural language prompt to detect intent from.")

class IntentDetectionResponse(BaseModel):
    intent: str = Field(..., description="The detected intent (e.g., 'shell_command', 'code_generation', 'conversation', 'file_operation').")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of the detected intent.")
    reasoning: Optional[str] = Field(None, description="Optional explanation for the detected intent.")