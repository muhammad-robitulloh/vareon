from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
import uuid # Import uuid
import os # Import os
from datetime import datetime # Added this line

from server_python.database import get_db, User as DBUser, Workflow, Dataset, MLModel
from server_python.auth import get_current_user
from . import crud, schemas, storage_service

router = APIRouter()

### Workflow Management ###

@router.post("/workflows/", response_model=schemas.WorkflowResponse, status_code=status.HTTP_201_CREATED)
def create_workflow(workflow: schemas.WorkflowCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_workflow = crud.create_workflow(db=db, workflow=workflow, owner_id=str(current_user.id))
    return db_workflow

@router.get("/workflows/", response_model=List[schemas.WorkflowResponse])
def read_workflows(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    workflows = crud.get_workflows(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    return workflows

@router.get("/workflows/{workflow_id}", response_model=schemas.WorkflowResponse)
def read_workflow(workflow_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow(db, workflow_id=workflow_id)
    if db_workflow is None or db_workflow.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return db_workflow

@router.put("/workflows/{workflow_id}", response_model=schemas.WorkflowResponse)
def update_workflow(workflow_id: str, workflow: schemas.WorkflowUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow(db, workflow_id=workflow_id)
    if db_workflow is None or db_workflow.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    db_workflow = crud.update_workflow(db, workflow_id=workflow_id, workflow=workflow)
    return db_workflow

@router.delete("/workflows/{workflow_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_workflow(workflow_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow(db, workflow_id=workflow_id)
    if db_workflow is None or db_workflow.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    crud.delete_workflow(db, workflow_id=workflow_id)
    return {"ok": True}

@router.post("/workflows/{workflow_id}/trigger", response_model=schemas.WorkflowResponse)
def trigger_workflow(workflow_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow(db, workflow_id=workflow_id)
    if db_workflow is None or db_workflow.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    
    # Simulate actual logic to trigger workflow execution
    print(f"Triggering workflow {db_workflow.name} (ID: {workflow_id})...")
    # In a real scenario, this would involve:
    # 1. Spawning a background task (e.g., using Celery, asyncio.create_task)
    # 2. Passing the workflow ID and any necessary context to the background task
    # 3. The background task would then interpret and execute the workflow steps.
    db_workflow.status = "running"
    db.commit()
    db.refresh(db_workflow)
    return db_workflow

@router.get("/workflows/{workflow_id}/status", response_model=schemas.WorkflowResponse)
def get_workflow_status(workflow_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_workflow = crud.get_workflow(db, workflow_id=workflow_id)
    if db_workflow is None or db_workflow.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")
    return db_workflow

### Dataset Management ###

@router.post("/datasets/upload", response_model=schemas.DatasetResponse, status_code=status.HTTP_201_CREATED)
async def upload_dataset(
    name: str,
    format: str,
    file: UploadFile,
    description: Optional[str] = None,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Save file to storage
    dataset_id = str(uuid.uuid4())
    file_path = await storage_service.save_dataset_file(file, dataset_id)
    size_bytes = file.size

    dataset_create = schemas.DatasetCreate(
        name=name,
        description=description,
        file_path=file_path,
        size_bytes=size_bytes,
        format=format
    )
    db_dataset = crud.create_dataset(db=db, dataset=dataset_create, owner_id=str(current_user.id))
    return db_dataset

@router.get("/datasets/", response_model=List[schemas.DatasetResponse])
def read_datasets(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    datasets = crud.get_datasets(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    return datasets

@router.get("/datasets/{dataset_id}", response_model=schemas.DatasetResponse)
def read_dataset(dataset_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None or db_dataset.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    return db_dataset

@router.put("/datasets/{dataset_id}", response_model=schemas.DatasetResponse)
def update_dataset(dataset_id: str, dataset: schemas.DatasetUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None or db_dataset.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    db_dataset = crud.update_dataset(db, dataset_id=dataset_id, dataset=dataset)
    return db_dataset

@router.delete("/datasets/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(dataset_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None or db_dataset.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    # Delete file from storage
    if db_dataset.file_path:
        storage_service.delete_dataset_file(db_dataset.file_path)

    crud.delete_dataset(db, dataset_id=dataset_id)
    return {"ok": True}

@router.get("/datasets/{dataset_id}/download")
async def download_dataset(dataset_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_dataset = crud.get_dataset(db, dataset_id=dataset_id)
    if db_dataset is None or db_dataset.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset not found")
    
    if not db_dataset.file_path or not os.path.exists(db_dataset.file_path):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Dataset file not found")
    
    return FileResponse(path=db_dataset.file_path, filename=db_dataset.name, media_type="application/octet-stream")

### Telemetry ###

@router.post("/telemetry/ingest", status_code=status.HTTP_201_CREATED)
def ingest_telemetry(telemetry_data: schemas.TelemetryDataCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_telemetry = crud.create_telemetry_data(db=db, telemetry_data=telemetry_data, owner_id=str(current_user.id))
    return db_telemetry

@router.get("/telemetry/", response_model=List[schemas.TelemetryDataResponse])
def get_telemetry(
    metric_name: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: Add authentication/authorization
    if metric_name:
        telemetry_data = crud.get_telemetry_data_by_metric(db, owner_id=str(current_user.id), metric_name=metric_name, skip=skip, limit=limit)
    else:
        telemetry_data = crud.get_telemetry_data(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    return telemetry_data

### Search Engine ###

@router.get("/search", response_model=List[Dict[str, Any]])
def search_neosyntis_entities(
    query: str,
    entity_type: Optional[str] = None,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # TODO: Add authentication/authorization
    results = []
    search_pattern = f"%{query}%"

    if entity_type is None or entity_type == "workflows":
        workflows = db.query(Workflow).filter(
            Workflow.owner_id == str(current_user.id),
            (Workflow.name.ilike(search_pattern)) | (Workflow.description.ilike(search_pattern))
        ).all()
        for wf in workflows:
            results.append({
                "type": "workflow",
                "id": wf.id,
                "name": wf.name,
                "description": wf.description,
                "status": wf.status
            })

    if entity_type is None or entity_type == "datasets":
        datasets = db.query(Dataset).filter(
            Dataset.owner_id == str(current_user.id),
            (Dataset.name.ilike(search_pattern)) | (Dataset.description.ilike(search_pattern))
        ).all()
        for ds in datasets:
            results.append({
                "type": "dataset",
                "id": ds.id,
                "name": ds.name,
                "description": ds.description,
                "format": ds.format
            })
    
    if entity_type is None or entity_type == "ml_models":
        ml_models = db.query(MLModel).filter(
            MLModel.owner_id == str(current_user.id),
            (MLModel.name.ilike(search_pattern)) | (MLModel.version.ilike(search_pattern))
        ).all()
        for model in ml_models:
            results.append({
                "type": "ml_model",
                "id": model.id,
                "name": model.name,
                "version": model.version,
                "status": model.status
            })
    
    return results

### Model Deployment & Machine Learning ###

@router.post("/models/", response_model=schemas.MLModelResponse, status_code=status.HTTP_201_CREATED)
def create_ml_model(model: schemas.MLModelCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_model = crud.create_ml_model(db=db, model=model, owner_id=str(current_user.id))
    return db_model

@router.get("/models/", response_model=List[schemas.MLModelResponse])
def read_ml_models(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    models = crud.get_ml_models(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    return models

@router.get("/models/{model_id}", response_model=schemas.MLModelResponse)
def read_ml_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_model = crud.get_ml_model(db, model_id=model_id)
    if db_model is None or db_model.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ML Model not found")
    return db_model

@router.put("/models/{model_id}", response_model=schemas.MLModelResponse)
def update_ml_model(model_id: str, model: schemas.MLModelUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_model = crud.get_ml_model(db, model_id=model_id)
    if db_model is None or db_model.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ML Model not found")
    
    db_model = crud.update_ml_model(db, model_id=model_id, model=model)
    return db_model

@router.delete("/models/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_ml_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_model = crud.get_ml_model(db, model_id=model_id)
    if db_model is None or db_model.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ML Model not found")
    
    crud.delete_ml_model(db, model_id=model_id)
    return {"ok": True}

@router.post("/models/{model_id}/deploy", response_model=schemas.MLModelResponse)
def deploy_ml_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_model = crud.get_ml_model(db, model_id=model_id)
    if db_model is None or db_model.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ML Model not found")
    
    # Simulate actual deployment logic
    print(f"Deploying ML model {db_model.name} (ID: {model_id})...")
    # In a real scenario, this would involve:
    # 1. Interacting with a model serving infrastructure (e.g., TensorFlow Serving, TorchServe)
    # 2. Containerizing the model and deploying it to a platform (e.g., Kubernetes)
    # 3. Loading the model into memory for inference if it's a local deployment
    db_model.status = "deployed"
    db_model.deployed_at = datetime.utcnow()
    db.commit()
    db.refresh(db_model)
    return db_model

@router.post("/models/{model_id}/train", response_model=schemas.TrainingJobResponse)
def train_ml_model(model_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_model = crud.get_ml_model(db, model_id=model_id)
    if db_model is None or db_model.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="ML Model not found")
    
    # Simulate actual training logic
    print(f"Initiating training for ML model {db_model.name} (ID: {model_id})...")
    # In a real scenario, this would involve:
    # 1. Spawning a background task for training
    # 2. Integrating with ML frameworks (e.g., scikit-learn, TensorFlow, PyTorch)
    # 3. Managing training data and tracking progress
    training_job_create = schemas.TrainingJobCreate(model_id=model_id, status="running")
    db_training_job = crud.create_training_job(db, training_job_create, owner_id=str(current_user.id))
    if db_training_job.metrics:
        db_training_job.metrics = json.loads(db_training_job.metrics)
    return db_training_job

@router.get("/training-jobs/", response_model=List[schemas.TrainingJobResponse])
def read_training_jobs(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    jobs = crud.get_training_jobs(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    for job in jobs:
        if job.metrics:
            job.metrics = json.loads(job.metrics)
    return jobs

@router.get("/training-jobs/{job_id}", response_model=schemas.TrainingJobResponse)
def read_training_job(job_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_job = crud.get_training_job(db, job_id=job_id)
    if db_job is None or db_job.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Training Job not found")
    if db_job.metrics:
        db_job.metrics = json.loads(db_job.metrics)
    return db_job