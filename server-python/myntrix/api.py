import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import psutil # Import psutil
import json # Import json

from database import get_db, User as DBUser
from auth import get_current_user
from . import crud, schemas

router = APIRouter()

### Agent Management ###

@router.post("/agents/", response_model=schemas.AgentResponse, status_code=status.HTTP_201_CREATED)
def create_agent(agent: schemas.AgentCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.create_agent(db=db, agent=agent, owner_id=str(current_user.id))
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.get("/agents/", response_model=List[schemas.AgentResponse])
def read_agents(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    agents = crud.get_agents(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    for agent in agents:
        if agent.configuration:
            agent.configuration = json.loads(agent.configuration)
    return agents

@router.get("/agents/{agent_id}", response_model=schemas.AgentResponse)
def read_agent(agent_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.put("/agents/{agent_id}", response_model=schemas.AgentResponse)
def update_agent(agent_id: str, agent: schemas.AgentUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    db_agent = crud.update_agent(db, agent_id=agent_id, agent=agent)
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.post("/agents/{agent_id}/start", response_model=schemas.AgentResponse)
def start_agent(agent_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    # Simulate actual logic to start the agent process
    print(f"Starting agent {db_agent.name} (ID: {agent_id})...")
    # In a real scenario, this would involve spawning a new process,
    # making an API call to a container orchestrator, etc.
    db_agent.status = "running"
    db_agent.last_run = datetime.utcnow()
    db.commit()
    db.refresh(db_agent)
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.post("/agents/{agent_id}/stop", response_model=schemas.AgentResponse)
def stop_agent(agent_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    # Simulate actual logic to stop the agent process
    print(f"Stopping agent {db_agent.name} (ID: {agent_id})...")
    # In a real scenario, this would involve sending a termination signal,
    # making an API call to a container orchestrator, etc.
    db_agent.status = "stopped"
    db.commit()
    db.refresh(db_agent)
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.post("/agents/{agent_id}/restart", response_model=schemas.AgentResponse)
def restart_agent(agent_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    # Simulate actual logic to restart the agent process
    print(f"Restarting agent {db_agent.name} (ID: {agent_id})...")
    # In a real scenario, this would involve sending a restart command,
    # or stopping and then starting the process/container.
    db_agent.status = "restarting" # Or directly "running" after restart logic
    db_agent.last_run = datetime.utcnow()
    db.commit()
    db.refresh(db_agent)
    if db_agent.configuration:
        db_agent.configuration = json.loads(db_agent.configuration)
    return db_agent

@router.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_agent(agent_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_agent = crud.get_agent(db, agent_id=agent_id)
    if db_agent is None or db_agent.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agent not found")
    
    crud.delete_agent(db, agent_id=agent_id)
    return {"ok": True}

### Device Control ###

@router.post("/devices/", response_model=schemas.DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(device: schemas.DeviceCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.create_device(db=db, device=device, owner_id=str(current_user.id))
    if db_device.configuration:
        db_device.configuration = json.loads(db_device.configuration)
    return db_device

@router.get("/devices/", response_model=List[schemas.DeviceResponse])
def read_devices(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    devices = crud.get_devices(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    for device in devices:
        if device.configuration:
            device.configuration = json.loads(device.configuration)
    return devices

@router.get("/devices/{device_id}", response_model=schemas.DeviceResponse)
def read_device(device_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    if db_device.configuration:
        db_device.configuration = json.loads(db_device.configuration)
    return db_device

@router.put("/devices/{device_id}", response_model=schemas.DeviceResponse)
def update_device(device_id: str, device: schemas.DeviceUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    db_device = crud.update_device(db, device_id=device_id, device=device)
    if db_device.configuration:
        db_device.configuration = json.loads(db_device.configuration)
    return db_device

@router.delete("/devices/{device_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_device(device_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    crud.delete_device(db, device_id=device_id)
    return {"ok": True}

@router.post("/devices/{device_id}/connect", response_model=schemas.DeviceResponse)
def connect_device(device_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # Simulate actual logic to connect to the device
    print(f"Connecting to device {db_device.name} (ID: {device_id})...")
    # In a real scenario, this would involve establishing a physical or network connection
    db_device.status = "connected"
    db_device.last_seen = datetime.utcnow()
    db.commit()
    db.refresh(db_device)
    if db_device.configuration:
        db_device.configuration = json.loads(db_device.configuration)
    return db_device

@router.post("/devices/{device_id}/disconnect", response_model=schemas.DeviceResponse)
def disconnect_device(device_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # Simulate actual logic to disconnect from the device
    print(f"Disconnecting from device {db_device.name} (ID: {device_id})...")
    # In a real scenario, this would involve closing the physical or network connection
    db_device.status = "disconnected"
    db.commit()
    db.refresh(db_device)
    if db_device.configuration:
        db_device.configuration = json.loads(db_device.configuration)
    return db_device

@router.post("/devices/{device_id}/command", response_model=Dict[str, str])
async def send_device_command(device_id: str, command: Dict[str, str], current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # TODO: Implement actual logic to send command to the device
    print(f"Sending command '{command.get('command')}' to device {db_device.name}")
    return {"message": f"Command '{command.get('command')}' sent to device {db_device.name} (placeholder)."}

@router.post("/devices/{device_id}/upload")
async def upload_file_to_device(device_id: str, file: UploadFile = File(...), current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_device = crud.get_device(db, device_id=device_id)
    if db_device is None or db_device.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Device not found")
    
    # TODO: Implement actual logic to upload file to the device
    file_content = await file.read()
    print(f"Uploading file '{file.filename}' ({len(file_content)} bytes) to device {db_device.name}")
    return {"message": f"File '{file.filename}' uploaded to device {db_device.name} (placeholder)."}

# WebSocket endpoint for telemetry
@router.websocket("/ws/myntrix/telemetry/{device_id}")
async def websocket_telemetry_endpoint(websocket: WebSocket, device_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Received telemetry from device {device_id}: {data}")
            await websocket.send_text(f"Message received from device {device_id}: {data}")
    except WebSocketDisconnect:
        print(f"Device {device_id} disconnected from telemetry WebSocket.")
    except Exception as e:
        print(f"Error in telemetry WebSocket for device {device_id}: {e}")
    finally:
        await websocket.close()

### Resource Monitoring ###

@router.get("/system-metrics", response_model=Dict[str, Any])
async def get_system_metrics(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check for mock mode environment variable
    if os.getenv("VAREON_MOCK_SYSTEM_METRICS", "false").lower() == "true":
        # Fallback to mock data
        return {
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "memory_total": 8 * 1024 * 1024 * 1024, # 8 GB
            "memory_available": 5 * 1024 * 1024 * 1024, # 5 GB
            "timestamp": datetime.utcnow().isoformat(),
            "mocked": True
        }

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_info.percent,
            "memory_total": memory_info.total,
            "memory_available": memory_info.available,
            "timestamp": datetime.utcnow().isoformat()
        }
    except PermissionError:
        # If PermissionError occurs, log it and fall back to mock data
        print("WARNING: Permission denied to access system metrics. Falling back to mock data.")
        return {
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "memory_total": 8 * 1024 * 1024 * 1024, # 8 GB
            "memory_available": 5 * 1024 * 1024 * 1024, # 5 GB
            "timestamp": datetime.utcnow().isoformat(),
            "mocked": True,
            "reason": "PermissionError accessing system metrics"
        }
    except Exception as e:
        # Catch any other unexpected errors and fall back to mock data
        print(f"ERROR: Failed to get system metrics: {e}. Falling back to mock data.")
        return {
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "memory_total": 8 * 1024 * 1024 * 1024, # 8 GB
            "memory_available": 5 * 1024 * 1024 * 1024, # 5 GB
            "timestamp": datetime.utcnow().isoformat(),
            "mocked": True,
            "reason": f"Unexpected error: {e}"
        }

@router.get("/jobs/", response_model=List[schemas.JobResponse])
def read_jobs(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    jobs = crud.get_jobs(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    for job in jobs:
        if job.details:
            job.details = json.loads(job.details)
    return jobs

### Task Scheduling ###

@router.post("/tasks/", response_model=schemas.ScheduledTaskResponse, status_code=status.HTTP_201_CREATED)
def create_scheduled_task(task: schemas.ScheduledTaskCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_task = crud.create_scheduled_task(db=db, task=task, owner_id=str(current_user.id))
    if db_task.action:
        db_task.action = json.loads(db_task.action)
    return db_task

@router.get("/tasks/", response_model=List[schemas.ScheduledTaskResponse])
def read_scheduled_tasks(skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    tasks = crud.get_scheduled_tasks(db, owner_id=str(current_user.id), skip=skip, limit=limit)
    for task in tasks:
        if task.action:
            task.action = json.loads(task.action)
    return tasks

@router.get("/tasks/{task_id}", response_model=schemas.ScheduledTaskResponse)
def read_scheduled_task(task_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_task = crud.get_scheduled_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled Task not found")
    if db_task.action:
        db_task.action = json.loads(db_task.action)
    return db_task

@router.put("/tasks/{task_id}", response_model=schemas.ScheduledTaskResponse)
def update_scheduled_task(task_id: str, task: schemas.ScheduledTaskUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_task = crud.get_scheduled_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled Task not found")
    
    db_task = crud.update_scheduled_task(db, task_id=task_id, task=task)
    if db_task.action:
        db_task.action = json.loads(db_task.action)
    return db_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_scheduled_task(task_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_task = crud.get_scheduled_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled Task not found")
    
    crud.delete_scheduled_task(db, task_id=task_id)
    return {"ok": True}

@router.post("/tasks/{task_id}/run", response_model=schemas.TaskRunResponse)
def run_scheduled_task(task_id: str, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_task = crud.get_scheduled_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled Task not found")
    
    # For now, simulate task execution and update status
    print(f"Executing scheduled task {db_task.name} (ID: {task_id})...")
    
    # Create a new task run entry
    task_run_create = schemas.TaskRunCreate(
        task_id=task_id, 
        status="running", 
        logs=f"Task '{db_task.name}' manually triggered at {datetime.utcnow().isoformat()}."
    )
    db_task_run = crud.create_task_run(db, task_run_create)

    # Simulate work and update status to completed
    db_task_run.status = "completed"
    db_task_run.end_time = datetime.utcnow()
    db_task_run.logs += f"\nTask '{db_task.name}' completed at {db_task_run.end_time.isoformat()}."
    db.add(db_task_run)
    db.commit()
    db.refresh(db_task_run)

    if db_task_run.logs:
        try:
            db_task_run.logs = json.loads(db_task_run.logs)
        except json.JSONDecodeError:
            pass # Keep as string if not valid JSON
    return db_task_run

@router.get("/tasks/history/{task_id}", response_model=List[schemas.TaskRunResponse])
def get_task_history(task_id: str, skip: int = 0, limit: int = 100, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    db_task = crud.get_scheduled_task(db, task_id=task_id)
    if db_task is None or db_task.owner_id != str(current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scheduled Task not found")
    
    task_runs = crud.get_task_runs_for_task(db, task_id=task_id, skip=skip, limit=limit)
    return task_runs

### 3D Visualization ###

@router.get("/visualization-data", response_model=Dict[str, Any])
async def get_visualization_data(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization
    
    # Aggregate data from agents
    agents = crud.get_agents(db, owner_id=str(current_user.id))
    agent_data = []
    for agent in agents:
        agent_data.append({
            "id": agent.id,
            "name": agent.name,
            "type": agent.type,
            "status": agent.status,
            "health": agent.health,
            "last_run": agent.last_run.isoformat() if agent.last_run else None,
            "configuration": json.loads(agent.configuration) if agent.configuration else {}
        })

    # Aggregate data from devices
    devices = crud.get_devices(db, owner_id=str(current_user.id))
    device_data = []
    for device in devices:
        device_data.append({
            "id": device.id,
            "name": device.name,
            "type": device.type,
            "connection_string": device.connection_string,
            "status": device.status,
            "last_seen": device.last_seen.isoformat() if device.last_seen else None,
            "firmware_version": device.firmware_version,
            "configuration": json.loads(device.configuration) if device.configuration else {}
        })

    return {
        "agents": agent_data,
        "devices": device_data,
        "timestamp": datetime.utcnow().isoformat()
    }