from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Base model for a generic context item stored in the DB
class ContextMemoryBase(BaseModel):
    key: str
    value: Dict[str, Any]

class ContextMemoryCreate(ContextMemoryBase):
    pass

class ContextMemory(ContextMemoryBase):
    id: str
    user_id: str
    last_accessed: datetime
    
    class Config:
        orm_mode = True

# Schemas for specific context types, matching the frontend
class UserPreference(BaseModel):
    id: str
    key: str
    value: str
    source: str

class ProjectKnowledge(BaseModel):
    id: str
    repo: str
    summary: str
    techStack: List[str]

class ConversationSnippet(BaseModel):
    id: str
    topic: str
    summary: str
    timestamp: str

# Response model for the frontend
class FullContextResponse(BaseModel):
    userPreferences: List[UserPreference]
    projectKnowledge: List[ProjectKnowledge]
    conversationSnippets: List[ConversationSnippet]
