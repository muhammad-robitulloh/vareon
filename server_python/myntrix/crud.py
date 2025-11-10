from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import json

from database import Agent, Device, Job, ScheduledTask, TaskRun # Changed from ..database
from .schemas import AgentCreate, AgentUpdate, DeviceCreate, DeviceUpdate, JobCreate, JobUpdate, ScheduledTaskCreate, ScheduledTaskUpdate, TaskRunCreate, TaskRunUpdate

### Agent CRUD Operations ###

def get_agent(db: Session, agent_id: str):
    return db.query(Agent).filter(Agent.id == agent_id).first()

def get_agents(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(Agent).filter(Agent.owner_id == owner_id).offset(skip).limit(limit).all()

def create_agent(db: Session, agent: AgentCreate, owner_id: str):
    db_agent = Agent(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=agent.name,
        type=agent.type,
        status=agent.status,
        health=agent.health,
        last_run=agent.last_run,
        configuration=json.dumps(agent.configuration) if agent.configuration else None
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent

def update_agent(db: Session, agent_id: str, agent: AgentUpdate):
    db_agent = get_agent(db, agent_id)
    if db_agent:
        if agent.name is not None:
            db_agent.name = agent.name
        if agent.type is not None:
            db_agent.type = agent.type
        if agent.status is not None:
            db_agent.status = agent.status
        if agent.health is not None:
            db_agent.health = agent.health
        if agent.last_run is not None:
            db_agent.last_run = agent.last_run
        if agent.configuration is not None:
            db_agent.configuration = json.dumps(agent.configuration)
        db.commit()
        db.refresh(db_agent)
    return db_agent

def delete_agent(db: Session, agent_id: str):
    db_agent = get_agent(db, agent_id)
    if db_agent:
        db.delete(db_agent)
        db.commit()
    return db_agent

### Device CRUD Operations ###

def get_device(db: Session, device_id: str):
    return db.query(Device).filter(Device.id == device_id).first()

def get_devices(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(Device).filter(Device.owner_id == owner_id).offset(skip).limit(limit).all()

def create_device(db: Session, device: DeviceCreate, owner_id: str):
    db_device = Device(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=device.name,
        type=device.type,
        connection_string=device.connection_string,
        status=device.status,
        last_seen=device.last_seen,
        firmware_version=device.firmware_version,
        configuration=json.dumps(device.configuration) if device.configuration else None
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device

def update_device(db: Session, device_id: str, device: DeviceUpdate):
    db_device = get_device(db, device_id)
    if db_device:
        if device.name is not None:
            db_device.name = device.name
        if device.type is not None:
            db_device.type = device.type
        if device.connection_string is not None:
            db_device.connection_string = device.connection_string
        if device.status is not None:
            db_device.status = device.status
        if device.last_seen is not None:
            db_device.last_seen = device.last_seen
        if device.firmware_version is not None:
            db_device.firmware_version = device.firmware_version
        if device.configuration is not None:
            db_device.configuration = json.dumps(device.configuration)
        db.commit()
        db.refresh(db_device)
    return db_device

def delete_device(db: Session, device_id: str):
    db_device = get_device(db, device_id)
    if db_device:
        db.delete(db_device)
        db.commit()
    return db_device

### Job CRUD Operations ###

def get_job(db: Session, job_id: str):
    return db.query(Job).filter(Job.id == job_id).first()

def get_jobs(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(Job).filter(Job.owner_id == owner_id).offset(skip).limit(limit).all()

def create_job(db: Session, job: JobCreate, owner_id: str):
    db_job = Job(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=job.name,
        type=job.type,
        status=job.status,
        progress=job.progress,
        created_at=job.created_at if job.created_at else datetime.utcnow(),
        updated_at=job.updated_at if job.updated_at else datetime.utcnow(),
        logs=job.logs,
        details=json.dumps(job.details) if job.details else None
    )
    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job

def update_job(db: Session, job_id: str, job: JobUpdate):
    db_job = get_job(db, job_id)
    if db_job:
        if job.name is not None:
            db_job.name = job.name
        if job.type is not None:
            db_job.type = job.type
        if job.status is not None:
            db_job.status = job.status
        if job.progress is not None:
            db_job.progress = job.progress
        if job.logs is not None:
            db_job.logs = job.logs
        if job.details is not None:
            db_job.details = json.dumps(job.details)
        db_job.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_job)
    return db_job

def delete_job(db: Session, job_id: str):
    db_job = get_job(db, job_id)
    if db_job:
        db.delete(db_job)
        db.commit()
    return db_job

### Scheduled Task CRUD Operations ###

def get_scheduled_task(db: Session, task_id: str):
    return db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()

def get_scheduled_tasks(db: Session, owner_id: str, skip: int = 0, limit: int = 100):
    return db.query(ScheduledTask).filter(ScheduledTask.owner_id == owner_id).offset(skip).limit(limit).all()

def create_scheduled_task(db: Session, task: ScheduledTaskCreate, owner_id: str):
    db_task = ScheduledTask(
        id=str(uuid.uuid4()),
        owner_id=owner_id,
        name=task.name,
        schedule=task.schedule,
        action=json.dumps(task.action),
        enabled=task.enabled,
        created_at=task.created_at if task.created_at else datetime.utcnow(),
        updated_at=task.updated_at if task.updated_at else datetime.utcnow()
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def update_scheduled_task(db: Session, task_id: str, task: ScheduledTaskUpdate):
    db_task = get_scheduled_task(db, task_id)
    if db_task:
        if task.name is not None:
            db_task.name = task.name
        if task.schedule is not None:
            db_task.schedule = task.schedule
        if task.action is not None:
            db_task.action = json.dumps(task.action)
        if task.enabled is not None:
            db_task.enabled = task.enabled
        db_task.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_task)
    return db_task

def delete_scheduled_task(db: Session, task_id: str):
    db_task = get_scheduled_task(db, task_id)
    if db_task:
        db.delete(db_task)
        db.commit()
    return db_task

### Task Run CRUD Operations ###

def get_task_run(db: Session, run_id: str):
    return db.query(TaskRun).filter(TaskRun.id == run_id).first()

def get_task_runs_for_task(db: Session, task_id: str, skip: int = 0, limit: int = 100):
    return db.query(TaskRun).filter(TaskRun.task_id == task_id).offset(skip).limit(limit).all()

def create_task_run(db: Session, run: TaskRunCreate):
    db_run = TaskRun(
        id=str(uuid.uuid4()),
        task_id=run.task_id,
        start_time=run.start_time if run.start_time else datetime.utcnow(),
        end_time=run.end_time,
        status=run.status,
        logs=run.logs
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    return db_run

def update_task_run(db: Session, run_id: str, run: TaskRunUpdate):
    db_run = get_task_run(db, run_id)
    if db_run:
        if run.end_time is not None:
            db_run.end_time = run.end_time
        if run.status is not None:
            db_run.status = run.status
        if run.logs is not None:
            db_run.logs = run.logs
        db.commit()
        db.refresh(db_run)
    return db_run