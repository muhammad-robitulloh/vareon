from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class LLMProviderBase(BaseModel):
    name: str
    base_url: str
    enabled: bool = True # New field
    organization_id: Optional[str] = None # New field

class LLMProviderCreate(LLMProviderBase):
    api_key: str # API key is required for creation

class LLMProviderUpdate(LLMProviderBase):
    name: Optional[str] = None
    base_url: Optional[str] = None
    enabled: Optional[bool] = None # New field
    organization_id: Optional[str] = None # New field
    api_key: Optional[str] = None # API key can be updated

class LLMProviderInDBBase(LLMProviderBase):
    id: str
    api_key_encrypted: str # Stored encrypted
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LLMProviderResponse(LLMProviderBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LLMModelBase(BaseModel):
    provider_id: str
    model_name: str
    type: Optional[str] = None # New field
    is_active: bool = True # New field
    reasoning: bool = False # New field
    role: Optional[str] = None # New field
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None

class LLMModelCreate(LLMModelBase):
    pass

class LLMModelUpdate(LLMModelBase):
    provider_id: Optional[str] = None
    model_name: Optional[str] = None
    type: Optional[str] = None # New field
    is_active: Optional[bool] = None # New field
    reasoning: Optional[bool] = None # New field
    role: Optional[str] = None # New field
    max_tokens: Optional[int] = None
    cost_per_token: Optional[float] = None

class LLMModelInDBBase(LLMModelBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class LLMModelResponse(LLMModelBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RoutingRuleBase(BaseModel):
    owner_id: str
    name: str
    condition: str
    target_model: str
    priority: int

class RoutingRuleCreate(RoutingRuleBase):
    pass

class RoutingRuleUpdate(RoutingRuleBase):
    owner_id: Optional[str] = None
    name: Optional[str] = None
    condition: Optional[str] = None
    target_model: Optional[str] = None
    priority: Optional[int] = None

class RoutingRuleInDBBase(RoutingRuleBase):
    id: str

    class Config:
        orm_mode = True

class RoutingRuleResponse(RoutingRuleBase):
    id: str

    class Config:
        orm_mode = True

class ChatRequest(BaseModel):
    prompt: str

class ChatResponse(BaseModel):
    response_content: str
    model_used: str
    tokens_used: int
    visualization_data: Dict[str, Any]
