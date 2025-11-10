from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class AgentBase(BaseModel):
    name: str
    type: str
    status: str
    health: int = 100
    last_run: Optional[datetime] = None
    configuration: Optional[Dict[str, Any]] = None

class AgentCreate(AgentBase):
    pass

class AgentUpdate(AgentBase):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    health: Optional[int] = None
    last_run: Optional[datetime] = None
    configuration: Optional[Dict[str, Any]] = None

class AgentInDBBase(AgentBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class AgentResponse(AgentBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class DeviceBase(BaseModel):
    name: str
    type: str
    connection_string: str
    status: str = "disconnected"
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class DeviceCreate(DeviceBase):
    pass

class DeviceUpdate(DeviceBase):
    name: Optional[str] = None
    type: Optional[str] = None
    connection_string: Optional[str] = None
    status: Optional[str] = None
    last_seen: Optional[datetime] = None
    firmware_version: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = None

class DeviceInDBBase(DeviceBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class DeviceResponse(DeviceBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class JobBase(BaseModel):
    name: str
    type: str
    status: str
    progress: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    logs: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class JobCreate(JobBase):
    pass

class JobUpdate(JobBase):
    name: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    progress: Optional[int] = None
    logs: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class JobInDBBase(JobBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class JobResponse(JobBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class ScheduledTaskBase(BaseModel):
    name: str
    schedule: str
    action: Dict[str, Any] # Action payload as JSON
    enabled: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class ScheduledTaskCreate(ScheduledTaskBase):
    pass

class ScheduledTaskUpdate(ScheduledTaskBase):
    name: Optional[str] = None
    schedule: Optional[str] = None
    action: Optional[Dict[str, Any]] = None
    enabled: Optional[bool] = None

class ScheduledTaskInDBBase(ScheduledTaskBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class ScheduledTaskResponse(ScheduledTaskBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class TaskRunBase(BaseModel):
    task_id: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    status: str
    logs: Optional[str] = None

class TaskRunCreate(TaskRunBase):
    pass

class TaskRunUpdate(TaskRunBase):
    end_time: Optional[datetime] = None
    status: Optional[str] = None
    logs: Optional[str] = None

class TaskRunInDBBase(TaskRunBase):
    id: str

    class Config:
        orm_mode = True

class TaskRunResponse(TaskRunBase):
    id: str

    class Config:
        orm_mode = True