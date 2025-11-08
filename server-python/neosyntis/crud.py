from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
import json

from database import Workflow, Dataset, TelemetryData, MLModel, TrainingJob # Changed from ..database
from .schemas import WorkflowCreate, WorkflowUpdate, DatasetCreate, DatasetUpdate, TelemetryDataCreate, MLModelCreate, MLModelUpdate, TrainingJobCreate, TrainingJobUpdate

### Workflow CRUD Operations ###

def get_workflow(db: Session, workflow_id: str):
    return db.query(Workflow).filter(Workflow.id == workflow_id).first()

def get_workflows(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(Workflow).filter(Workflow.owner_id == owner_id).offset(skip).limit(limit).all()

def create_workflow(db: Session, workflow: WorkflowCreate, owner_id: str):
    db_workflow = Workflow(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=workflow.name,
        description=workflow.description,
        status=workflow.status,
        steps=workflow.steps,
        created_at=workflow.created_at if workflow.created_at else datetime.utcnow(),
        updated_at=workflow.updated_at if workflow.updated_at else datetime.utcnow()
    )
    db.add(db_workflow)
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

def update_workflow(db: Session, workflow_id: str, workflow: WorkflowUpdate):
    db_workflow = get_workflow(db, workflow_id)
    if db_workflow:
        if workflow.name is not None:
            db_workflow.name = workflow.name
        if workflow.description is not None:
            db_workflow.description = workflow.description
        if workflow.status is not None:
            db_workflow.status = workflow.status
        if workflow.steps is not None:
            db_workflow.steps = workflow.steps
        db_workflow.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_workflow)
    return db_workflow

def delete_workflow(db: Session, workflow_id: str):
    db_workflow = get_workflow(db, workflow_id)
    if db_workflow:
        db.delete(db_workflow)
        db.commit()
    return db_workflow

### Dataset CRUD Operations ###

def get_dataset(db: Session, dataset_id: str):
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def get_datasets(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(Dataset).filter(Dataset.owner_id == owner_id).offset(skip).limit(limit).all()

def create_dataset(db: Session, dataset: DatasetCreate, owner_id: str):
    db_dataset = Dataset(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=dataset.name,
        description=dataset.description,
        file_path=dataset.file_path,
        size_bytes=dataset.size_bytes,
        format=dataset.format,
        uploaded_at=dataset.uploaded_at if dataset.uploaded_at else datetime.utcnow()
    )
    db.add(db_dataset)
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def update_dataset(db: Session, dataset_id: str, dataset: DatasetUpdate):
    db_dataset = get_dataset(db, dataset_id)
    if db_dataset:
        if dataset.name is not None:
            db_dataset.name = dataset.name
        if dataset.description is not None:
            db_dataset.description = dataset.description
        if dataset.file_path is not None:
            db_dataset.file_path = dataset.file_path
        if dataset.size_bytes is not None:
            db_dataset.size_bytes = dataset.size_bytes
        if dataset.format is not None:
            db_dataset.format = dataset.format
        if dataset.uploaded_at is not None:
            db_dataset.uploaded_at = dataset.uploaded_at
        db.commit()
        db.refresh(db_dataset)
    return db_dataset

def delete_dataset(db: Session, dataset_id: str):
    db_dataset = get_dataset(db, dataset_id)
    if db_dataset:
        db.delete(db_dataset)
        db.commit()
    return db_dataset

### TelemetryData CRUD Operations ###

def create_telemetry_data(db: Session, telemetry_data: TelemetryDataCreate, owner_id: str):
    db_telemetry = TelemetryData(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        timestamp=telemetry_data.timestamp if telemetry_data.timestamp else datetime.utcnow(),
        metric_name=telemetry_data.metric_name,
        value=telemetry_data.value,
        workflow_id=telemetry_data.workflow_id,
        dataset_id=telemetry_data.dataset_id,
        device_id=telemetry_data.device_id
    )
    db.add(db_telemetry)
    db.commit()
    db.refresh(db_telemetry)
    return db_telemetry

def get_telemetry_data(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(TelemetryData).filter(TelemetryData.owner_id == owner_id).offset(skip).limit(limit).all()

def get_telemetry_data_by_metric(db: Session, owner_id: str, metric_name: str, skip: int = 0, limit: int = 100):
    return db.query(TelemetryData).filter(TelemetryData.owner_id == owner_id, TelemetryData.metric_name == metric_name).offset(skip).limit(limit).all()

### MLModel CRUD Operations ###

def get_ml_model(db: Session, model_id: str):
    return db.query(MLModel).filter(MLModel.id == model_id).first()

def get_ml_models(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(MLModel).filter(MLModel.owner_id == owner_id).offset(skip).limit(limit).all()

def create_ml_model(db: Session, model: MLModelCreate, owner_id: str):
    db_model = MLModel(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=model.name,
        version=model.version,
        status=model.status,
        path_to_artifact=model.path_to_artifact,
        training_dataset_id=model.training_dataset_id,
        deployed_at=model.deployed_at,
        created_at=model.created_at if model.created_at else datetime.utcnow(),
        updated_at=model.updated_at if model.updated_at else datetime.utcnow()
    )
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def update_ml_model(db: Session, model_id: str, model: MLModelUpdate):
    db_model = get_ml_model(db, model_id)
    if db_model:
        if model.name is not None:
            db_model.name = model.name
        if model.version is not None:
            db_model.version = model.version
        if model.status is not None:
            db_model.status = model.status
        if model.path_to_artifact is not None:
            db_model.path_to_artifact = model.path_to_artifact
        if model.training_dataset_id is not None:
            db_model.training_dataset_id = model.training_dataset_id
        if model.deployed_at is not None:
            db_model.deployed_at = model.deployed_at
        db_model.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_model)
    return db_model

def delete_ml_model(db: Session, model_id: str):
    db_model = get_ml_model(db, model_id)
    if db_model:
        db.delete(db_model)
        db.commit()
    return db_model

### TrainingJob CRUD Operations ###

def get_training_job(db: Session, job_id: str):
    return db.query(TrainingJob).filter(TrainingJob.id == job_id).first()

def get_training_jobs(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(TrainingJob).filter(TrainingJob.owner_id == owner_id).offset(skip).limit(limit).all()

def create_training_job(db: Session, job: TrainingJobCreate, owner_id: str):
    db_job = TrainingJob(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        model_id=job.model_id,
        status=job.status,
        start_time=job.start_time if job.start_time else datetime.utcnow(),
        end_time=job.end_time,
        metrics=json.dumps(job.metrics) if job.metrics else None,
        logs=job.logs,
        created_at=job.created_at if job.created_at else datetime.utcnow(),
        updated_at=job.updated_at if job.updated_at else datetime.utcnow()
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_training_job(db: Session, job_id: str, job: TrainingJobUpdate):
    db_job = get_training_job(db, job_id)
    if db_job:
        if job.status is not None:
            db_job.status = job.status
        if job.end_time is not None:
            db_job.end_time = job.end_time
        if job.metrics is not None:
            db_job.metrics = json.dumps(job.metrics)
        if job.logs is not None:
            db_job.logs = job.logs
        db_job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_job)
    return db_job