from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class WorkflowBase(BaseModel):
    name: str
    description: Optional[str] = None
    status: str
    steps: str # Assuming steps are stored as a JSON string
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class WorkflowCreate(WorkflowBase):
    pass

class WorkflowUpdate(WorkflowBase):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    steps: Optional[str] = None

class WorkflowInDBBase(WorkflowBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class WorkflowResponse(WorkflowBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class DatasetBase(BaseModel):
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None
    format: str
    uploaded_at: Optional[datetime] = None

class DatasetCreate(DatasetBase):
    pass

class DatasetUpdate(DatasetBase):
    name: Optional[str] = None
    description: Optional[str] = None
    file_path: Optional[str] = None
    size_bytes: Optional[int] = None
    format: Optional[str] = None
    uploaded_at: Optional[datetime] = None

class DatasetInDBBase(DatasetBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class DatasetResponse(DatasetBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class TelemetryDataBase(BaseModel):
    timestamp: Optional[datetime] = None
    metric_name: str
    value: float
    workflow_id: Optional[str] = None
    dataset_id: Optional[str] = None
    device_id: Optional[str] = None

class TelemetryDataCreate(TelemetryDataBase):
    pass

class TelemetryDataResponse(TelemetryDataBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class MLModelBase(BaseModel):
    name: str
    version: str
    status: str = "registered"
    path_to_artifact: Optional[str] = None
    training_dataset_id: Optional[str] = None
    deployed_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class MLModelCreate(MLModelBase):
    pass

class MLModelUpdate(MLModelBase):
    name: Optional[str] = None
    version: Optional[str] = None
    status: Optional[str] = None
    path_to_artifact: Optional[str] = None
    training_dataset_id: Optional[str] = None
    deployed_at: Optional[datetime] = None

class MLModelInDBBase(MLModelBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class MLModelResponse(MLModelBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class TrainingJobBase(BaseModel):
    model_id: str
    status: str = "pending"
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class TrainingJobCreate(TrainingJobBase):
    pass

class TrainingJobUpdate(TrainingJobBase):
    status: Optional[str] = None
    end_time: Optional[datetime] = None
    metrics: Optional[Dict[str, Any]] = None
    logs: Optional[str] = None

class TrainingJobInDBBase(TrainingJobBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True

class TrainingJobResponse(TrainingJobBase):
    id: str
    owner_id: str

    class Config:
        orm_mode = True