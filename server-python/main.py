import logging
from datetime import datetime, timedelta, timezone
import os
import sys
import argparse
import time

import pty
import asyncio
import json
from typing import List, Dict, Any
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, WebSocket, WebSocketDisconnect, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel

# Add the script's directory to sys.path for relative imports if run directly
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Now relative imports should work if main.py is run directly
from database import Base, engine, SessionLocal, setup_default_user, get_user_from_db, create_user_in_db, get_db, User as DBUser, get_user_by_username_or_email # Alias User from database to DBUser
from auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, generate_verification_token, send_verification_email, PermissionChecker, VERIFICATION_TOKEN_EXPIRE_MINUTES, get_websocket_token, get_current_websocket_user
from schemas import Token, User, UserCreate, UserBase, Agent, AgentCreate, HardwareDevice, HardwareDeviceUpdate, Workflow, WorkflowCreate, Dataset, DatasetCreate, RoutingRule, RoutingRuleCreate, MessageResponse, UserUpdate
import llm_service # Import the new LLM service

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    # Create database tables if they don't exist
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created or already exist.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
    
    # Setup default user and roles/permissions
    db = SessionLocal()
    try:
        setup_default_user(db, get_password_hash)
    finally:
        db.close()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

module_startup_times = {
    "arcana": datetime.now(timezone.utc),
    "myntrix": datetime.now(timezone.utc),
    "neosyntis": datetime.now(timezone.utc),
    "cognisys": datetime.now(timezone.utc),
}

# In-memory storage for simulated hardware devices
simulated_hardware_devices: Dict[str, HardwareDevice] = {
    "device-1": HardwareDevice(id="device-1", name="Sensor Array 7", device_type="sensor", status="connected"),
    "device-2": HardwareDevice(id="device-2", name="Robotic Arm Alpha", device_type="actuator", status="disconnected"),
}

# In-memory storage for simulated workflows
simulated_workflows: Dict[str, Workflow] = {
    "workflow-1": Workflow(id="workflow-1", name="Data Processing Pipeline", status="completed", steps=["fetch_data", "clean_data", "analyze_data"]),
    "workflow-2": Workflow(id="workflow-2", name="Report Generation", status="pending", steps=["gather_info", "format_report", "distribute_report"]),
}

# In-memory storage for simulated datasets
simulated_datasets: Dict[str, Dataset] = {
    "dataset-1": Dataset(id="dataset-1", name="Customer Data Q1", size_mb=102.5, format="csv", creation_date=datetime.now(timezone.utc) - timedelta(days=30)),
    "dataset-2": Dataset(id="dataset-2", name="Product Images", size_mb=1230.0, format="zip", creation_date=datetime.now(timezone.utc) - timedelta(days=90)),
}

# In-memory storage for simulated routing rules
simulated_routing_rules: Dict[str, RoutingRule] = {
    "rule-1": RoutingRule(id="rule-1", name="High Priority User", condition="user.tier == 'premium'", target_model="gpt-4", priority=10),
    "rule-2": RoutingRule(id="rule-2", name="Default Route", condition="true", target_model="gemini-pro", priority=1),
}

# Simple in-memory cache
cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 5 # Cache validity in seconds

# --- Agent Management API ---
@app.get("/api/myntrix/agents", response_model=List[Agent])
async def list_myntrix_agents():
    # For now, return a hardcoded list of agents
    return [
        {"id": "agent-1", "name": "Data Harvester", "status": "online", "agent_type": "data_collector"},
        {"id": "agent-2", "name": "Model Trainer", "status": "busy", "agent_type": "analyzer"},
        {"id": "agent-3", "name": "Task Executor", "status": "offline", "agent_type": "executor"},
    ]

# --- Hardware Integration API ---
@app.get("/api/myntrix/hardware", response_model=List[HardwareDevice])
async def list_myntrix_hardware():
    return list(simulated_hardware_devices.values())

@app.post("/api/myntrix/hardware/{device_id}/status")
async def update_myntrix_hardware_status(device_id: str, update: HardwareDeviceUpdate):
    if device_id not in simulated_hardware_devices:
        raise HTTPException(status_code=404, detail="Device not found")
    simulated_hardware_devices[device_id].status = update.status
    logger.info(f"Simulated hardware device {device_id} status updated to {update.status}")
    if "myntrix_status" in cache: del cache["myntrix_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": f"Device {device_id} status updated to {update.status}"}

# --- Workflow Automation API ---
@app.get("/api/neosyntis/workflows", response_model=List[Workflow])
async def list_neosyntis_workflows():
    return list(simulated_workflows.values())

@app.post("/api/neosyntis/workflows/{workflow_id}/trigger")
async def trigger_neosyntis_workflow(workflow_id: str):
    if workflow_id not in simulated_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    simulated_workflows[workflow_id].status = "running" # Simulate triggering
    logger.info(f"Simulated workflow {workflow_id} triggered.")
    if "neosyntis_status" in cache: del cache["neosyntis_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": f"Workflow {workflow_id} triggered successfully!"}

@app.get("/api/neosyntis/workflows/{workflow_id}/status")
async def get_neosyntis_workflow_status(workflow_id: str):
    if workflow_id not in simulated_workflows:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return {"status": simulated_workflows[workflow_id].status}

# --- Dataset Management API ---
@app.get("/api/neosyntis/datasets", response_model=List[Dataset])
async def list_neosyntis_datasets():
    return list(simulated_datasets.values())

@app.post("/api/neosyntis/datasets/upload")
async def upload_neosyntis_dataset(dataset: DatasetCreate):
    new_id = f"dataset-{len(simulated_datasets) + 1}"
    new_dataset = Dataset(id=new_id, creation_date=datetime.now(timezone.utc), **dataset.model_dump())
    simulated_datasets[new_id] = new_dataset
    logger.info(f"Simulated dataset {new_id} uploaded: {dataset.name}")
    if "neosyntis_status" in cache: del cache["neosyntis_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": f"Dataset {new_id} uploaded successfully!", "dataset_id": new_id}

@app.get("/api/neosyntis/datasets/{dataset_id}/download")
async def download_neosyntis_dataset(dataset_id: str):
    if dataset_id not in simulated_datasets:
        raise HTTPException(status_code=404, detail="Dataset not found")
    logger.info(f"Simulated dataset {dataset_id} downloaded.")
    return {"message": f"Dataset {dataset_id} downloaded successfully!", "dataset_name": simulated_datasets[dataset_id].name}

# --- Multimodel Routing API ---
@app.get("/api/cognisys/routing-rules", response_model=List[RoutingRule])
async def list_cognisys_routing_rules():
    return list(simulated_routing_rules.values())

@app.post("/api/cognisys/routing-rules", response_model=RoutingRule)
async def create_cognisys_routing_rule(rule: RoutingRuleCreate):
    new_id = f"rule-{len(simulated_routing_rules) + 1}"
    new_rule = RoutingRule(id=new_id, **rule.model_dump())
    simulated_routing_rules[new_id] = new_rule
    logger.info(f"Simulated routing rule {new_id} created: {rule.name}")
    if "cognisys_status" in cache: del cache["cognisys_status"]
    if "system_status" in cache: del cache["system_status"]
    return new_rule

@app.put("/api/cognisys/routing-rules/{rule_id}", response_model=RoutingRule)
async def update_cognisys_routing_rule(rule_id: str, rule: RoutingRuleCreate):
    if rule_id not in simulated_routing_rules:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    updated_rule = RoutingRule(id=rule_id, **rule.model_dump())
    simulated_routing_rules[rule_id] = updated_rule
    logger.info(f"Simulated routing rule {rule_id} updated: {rule.name}")
    if "cognisys_status" in cache: del cache["cognisys_status"]
    if "system_status" in cache: del cache["system_status"]
    return updated_rule

@app.delete("/api/cognisys/routing-rules/{rule_id}")
async def delete_cognisys_routing_rule(rule_id: str):
    if rule_id not in simulated_routing_rules:
        raise HTTPException(status_code=404, detail="Routing rule not found")
    del simulated_routing_rules[rule_id]
    logger.info(f"Simulated routing rule {rule_id} deleted.")
    if "cognisys_status" in cache: del cache["cognisys_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": f"Routing rule {rule_id} deleted successfully!"}

# --- API Routes ---
@app.get("/health")
async def health_check():
    logger.info("Health check endpoint accessed.")
    return {"status": "ok"}

@app.post("/api/register", response_model=MessageResponse)
async def register_user(user: UserCreate, request: Request, db: Session = Depends(get_db)):
    db_user = get_user_from_db(db, user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    db_email = db.query(DBUser).filter(DBUser.email == user.email).first()
    if db_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    verification_token = generate_verification_token()
    verification_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES) # Token valid for 24 hours

    new_user = create_user_in_db(db, user.username, hashed_password, user.email, verification_token, verification_token_expires_at)
    
    verification_link = f"{request.base_url}verify-email?token={verification_token}&email={new_user.email}"
    logger.info(f"User {new_user.username} registered successfully. Verification email with link sent to {new_user.email}.")
    
    try:
        send_verification_email(new_user.email, verification_link)
    except HTTPException as e:
        # If email sending fails, we might want to delete the user or mark for retry
        logger.error(f"Failed to send verification email for user {new_user.username}: {e.detail}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User registered, but failed to send verification email.")

    return {"message": "Registration successful. Please check your email to verify your account."}

class VerifyEmailRequest(BaseModel):
    email: str
    token: str

@app.post("/api/verify-email")
async def verify_email(request: VerifyEmailRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(DBUser).filter(DBUser.email == request.email).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if user.is_verified:
            return {"message": "Email already verified.", "status": "success"}

        if not user.verification_token or user.verification_token != request.token:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")

        if user.verification_token_expires_at:
            # Make user.verification_token_expires_at timezone-aware (UTC) for comparison
            # Assuming it was stored as UTC but retrieved as naive
            aware_expiration_time = user.verification_token_expires_at.replace(tzinfo=timezone.utc)
            if aware_expiration_time < datetime.now(timezone.utc):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired.")

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None
        db.commit()
        db.refresh(user)
        logger.info(f"User {user.username} (email: {user.email}) successfully verified their email.")
        return {"message": "Email verified successfully!", "status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"An unexpected error occurred during email verification for email {request.email}: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during email verification.")

@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username_or_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for username: {form_data.username} - Incorrect credentials.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        logger.warning(f"Failed login attempt for username: {form_data.username} - Email not verified.")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for a verification link."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"User {user.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard", response_model=User)
async def read_dashboard(current_user: User = Depends(PermissionChecker(["admin_access"]))):
    return current_user

class SystemStatusModule(BaseModel):
    status: str
    uptime: str
    activeChats: int = 0
    messagesProcessed: int = 0
    avgResponseTime: str = "0s"
    activeAgents: int = 0
    jobsCompleted: int = 0
    devicesConnected: int = 0
    activeWorkflows: int = 0
    datasetsManaged: int = 0
    searchQueriesProcessed: int = 0
    modelsActive: int = 0
    routingRules: int = 0
    requestsRouted: int = 0

class SystemStatus(BaseModel):
    arcana: SystemStatusModule
    myntrix: SystemStatusModule
    neosyntis: SystemStatusModule
    cognisys: SystemStatusModule

class ArcanaStatus(BaseModel):
    status: str
    uptime: str
    activeChats: int
    messagesProcessed: int
    avgResponseTime: str

def format_timedelta(td: timedelta) -> str:
    total_seconds = int(td.total_seconds())
    days = total_seconds // (24 * 3600)
    hours = (total_seconds % (24 * 3600)) // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60

    parts = []
    if days > 0: parts.append(f"{days}d")
    if hours > 0: parts.append(f"{hours}h")
    if minutes > 0: parts.append(f"{minutes}m")
    if seconds > 0 or not parts: parts.append(f"{seconds}s") # Ensure at least seconds are shown

    return " ".join(parts)

@app.get("/api/system/status", response_model=SystemStatus)
async def get_system_status():
    cache_key = "system_status"
    if cache_key in cache and (datetime.now(timezone.utc) - cache[cache_key]["timestamp"]).total_seconds() < CACHE_TTL_SECONDS:
        return cache[cache_key]["data"]

    current_time = datetime.now(timezone.utc)

    arcana_uptime = format_timedelta(current_time - module_startup_times["arcana"])
    myntrix_uptime = format_timedelta(current_time - module_startup_times["myntrix"])
    neosyntis_uptime = format_timedelta(current_time - module_startup_times["neosyntis"])
    cognisys_uptime = format_timedelta(current_time - module_startup_times["cognisys"])

    response_data = {
        "arcana": {
            "status": "online",
            "uptime": arcana_uptime,
            "activeChats": 12,
            "messagesProcessed": 1543,
            "avgResponseTime": "1.2s",
        },
        "myntrix": {
            "status": "online",
            "uptime": myntrix_uptime,
            "activeAgents": 8,
            "jobsCompleted": 234,
            "devicesConnected": 3,
        },
        "neosyntis": {
            "status": "online",
            "uptime": neosyntis_uptime,
            "activeWorkflows": 5,
            "datasetsManaged": 18,
            "searchQueriesProcessed": 892,
        },
        "cognisys": {
            "status": "online",
            "uptime": cognisys_uptime,
            "modelsActive": 12,
            "routingRules": 24,
            "requestsRouted": 3421,
        },
    }
    cache[cache_key] = {"data": response_data, "timestamp": datetime.now(timezone.utc)}
    return response_data

class MyntrixStatus(BaseModel):
    status: str
    uptime: str
    activeAgents: int
    jobsCompleted: int
    devicesConnected: int

class NeosyntisStatus(BaseModel):
    status: str
    uptime: str
    activeWorkflows: int
    datasetsManaged: int
    searchQueriesProcessed: int

class CognisysStatus(BaseModel):
    status: str
    uptime: str
    modelsActive: int
    routingRules: int
    requestsRouted: int

@app.get("/api/arcana/status", response_model=ArcanaStatus)
async def get_arcana_status():
    cache_key = "arcana_status"
    if cache_key in cache and (datetime.now(timezone.utc) - cache[cache_key]["timestamp"]).total_seconds() < CACHE_TTL_SECONDS:
        return cache[cache_key]["data"]

    current_time = datetime.now(timezone.utc)
    arcana_uptime = format_timedelta(current_time - module_startup_times["arcana"])
    response_data = {
        "status": "online",
        "uptime": arcana_uptime,
        "activeChats": 12,
        "messagesProcessed": 1543,
        "avgResponseTime": "1.2s",
    }
    cache[cache_key] = {"data": response_data, "timestamp": datetime.now(timezone.utc)}
    return response_data

@app.get("/api/myntrix/status", response_model=MyntrixStatus)
async def get_myntrix_status():
    cache_key = "myntrix_status"
    if cache_key in cache and (datetime.now(timezone.utc) - cache[cache_key]["timestamp"]).total_seconds() < CACHE_TTL_SECONDS:
        return cache[cache_key]["data"]

    current_time = datetime.now(timezone.utc)
    myntrix_uptime = format_timedelta(current_time - module_startup_times["myntrix"])
    response_data = {
        "status": "online",
        "uptime": myntrix_uptime,
        "activeAgents": 8,
        "jobsCompleted": 234,
        "devicesConnected": 3,
    }
    cache[cache_key] = {"data": response_data, "timestamp": datetime.now(timezone.utc)}
    return response_data

@app.get("/api/neosyntis/status", response_model=NeosyntisStatus)
async def get_neosyntis_status():
    cache_key = "neosyntis_status"
    if cache_key in cache and (datetime.now(timezone.utc) - cache[cache_key]["timestamp"]).total_seconds() < CACHE_TTL_SECONDS:
        return cache[cache_key]["data"]

    current_time = datetime.now(timezone.utc)
    neosyntis_uptime = format_timedelta(current_time - module_startup_times["neosyntis"])
    response_data = {
        "status": "online",
        "uptime": neosyntis_uptime,
        "activeWorkflows": 5,
        "datasetsManaged": 18,
        "searchQueriesProcessed": 892,
    }
    cache[cache_key] = {"data": response_data, "timestamp": datetime.now(timezone.utc)}
    return response_data

@app.get("/api/cognisys/status", response_model=CognisysStatus)
async def get_cognisys_status():
    cache_key = "cognisys_status"
    if cache_key in cache and (datetime.now(timezone.utc) - cache[cache_key]["timestamp"]).total_seconds() < CACHE_TTL_SECONDS:
        return cache[cache_key]["data"]

    current_time = datetime.now(timezone.utc)
    cognisys_uptime = format_timedelta(current_time - module_startup_times["cognisys"])
    response_data = {
        "status": "online",
        "uptime": cognisys_uptime,
        "modelsActive": 12,
        "routingRules": 24,
        "requestsRouted": 3421,
    }
    cache[cache_key] = {"data": response_data, "timestamp": datetime.now(timezone.utc)}
    return response_data

@app.post("/api/neosyntis/open-lab")
async def open_neosyntis_lab():
    logger.info("Quick action: Open Neosyntis Lab triggered.")
    # TODO: Implement actual logic for opening Neosyntis Lab
    if "neosyntis_status" in cache: del cache["neosyntis_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": "Neosyntis Lab opened successfully!"}

@app.post("/api/arcana/start-chat")
async def start_arcana_chat():
    logger.info("Quick action: Start Arcana Chat triggered.")
    # TODO: Implement actual logic for starting Arcana Chat
    if "arcana_status" in cache: del cache["arcana_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": "Arcana Chat started successfully!"}

@app.post("/api/myntrix/deploy-model")
async def deploy_model():
    logger.info("Quick action: Deploy Model triggered.")
    # TODO: Implement actual logic for deploying Myntrix Model
    if "myntrix_status" in cache: del cache["myntrix_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": "Model deployed successfully!"}

@app.post("/api/myntrix/manage-agents")
async def manage_agents():
    logger.info("Quick action: Manage Agents triggered.")
    # TODO: Implement actual logic for managing Myntrix Agents
    if "myntrix_status" in cache: del cache["myntrix_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": "Agents managed successfully!"}

# --- Chat Interface API ---
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat")
async def chat_with_llm(request: ChatRequest, current_user: User = Depends(get_current_user)):
    user_id = current_user.username # Use username as user_id for conversation history
    llm_response = await llm_service.get_openrouter_completion(user_id, request.message)
    return {"response": llm_response}

@app.post("/api/chat/demo")
async def chat_with_llm_demo(request: ChatRequest):
    user_id = "demo_user" # Hardcoded user_id for demo purposes
    llm_response = await llm_service.get_openrouter_completion(user_id, request.message)
    return {"response": llm_response}

@app.post("/api/chat/clear")
async def clear_chat_history(current_user: User = Depends(get_current_user)):
    user_id = current_user.username
    llm_service.clear_conversation_history(user_id)
    return {"message": "Chat history cleared."}

# Helper dependency to get the DBUser object from the current_user (Pydantic User)
def get_db_user_from_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == current_user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found in database")
    return db_user

@app.get("/api/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Retrieve the current authenticated user's profile.
    """
    return current_user

@app.put("/api/users/me", response_model=User)
async def update_users_me(user_update: UserUpdate, current_user: DBUser = Depends(get_db_user_from_current_user), db: Session = Depends(get_db)):
    """
    Update the current authenticated user's profile.
    """
    if user_update.username is not None and user_update.username != current_user.username:
        existing_user = get_user_from_db(db, user_update.username)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Username already taken")
        current_user.username = user_update.username

    if user_update.email is not None and user_update.email != current_user.email:
        existing_email_user = db.query(DBUser).filter(DBUser.email == user_update.email).first()
        if existing_email_user and existing_email_user.id != current_user.id:
            raise HTTPException(status_code=400, detail="Email already registered")
        current_user.email = user_update.email
        # If email changes, mark as unverified and generate new token
        current_user.is_verified = False
        current_user.verification_token = generate_verification_token()
        current_user.verification_token_expires_at = datetime.now(timezone.utc) + timedelta(minutes=VERIFICATION_TOKEN_EXPIRE_MINUTES)
        # TODO: Send new verification email

    if user_update.password is not None:
        current_user.hashed_password = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user

# Helper dependency to get the DBUser object from the current_user (Pydantic User)
def get_db_user_from_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == current_user.username).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found in database")
    return db_user

# --- WebSocket Endpoint for Interactive Shell ---
@app.websocket("/ws/shell/{chat_id}")
async def websocket_shell(
    websocket: WebSocket,
    chat_id: int,
    current_user: User = Depends(get_current_websocket_user) # Authenticate WebSocket
):
    logger.info(f"[WebSocket] Attempting to connect client {chat_id} to interactive shell for user {current_user.username}.")
    await websocket.accept()

    # Create a pseudo-terminal (pty)
    master_fd, slave_fd = pty.openpty()

    # Start a shell process (e.g., bash) in the pty
    shell_process = await asyncio.create_subprocess_exec(
        os.environ.get("SHELL", "/bin/bash"),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=project_root # Use project_root
    )

    # Get a non-blocking file-like object for the master end of the pty
    master_reader = os.fdopen(master_fd, 'rb', 0)

    async def forward_shell_to_client():
        """Reads from the shell's output and sends it to the WebSocket client."""
        try:
            while True:
                output = await asyncio.to_thread(master_reader.read, 1024)
                if not output:
                    logger.info(f"[WebSocket] Shell output stream for client {chat_id} ended (output was empty).")
                    break
                await websocket.send_text(output.decode(errors='ignore'))
        except (IOError, WebSocketDisconnect) as e:
            logger.info(f"[WebSocket] Shell output stream for client {chat_id} closed due to: {e}")
        except Exception as e:
            logger.error(f"[WebSocket] Unexpected error in forward_shell_to_client for client {chat_id}: {e}", exc_info=True)
        finally:
            # This task is only for forwarding. The main loop handles all cleanup.
            logger.info(f"[WebSocket] forward_shell_to_client task for client {chat_id} finishing.")

    client_task = asyncio.create_task(forward_shell_to_client(), name=f"shell_forwarder_{chat_id}")

    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"[WebSocket] Received data from client {chat_id}: {data[:100]}...") # Log first 100 chars
                # Check for resize command (sent as JSON from frontend)
                try:
                    data_json = json.loads(data)
                    if 'resize' in data_json:
                        cols, rows = data_json['resize']['cols'], data_json['resize']['rows']
                        logger.info(f"[WebSocket] Resizing PTY for client {chat_id} to {cols}x{rows}")
                        # fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
                        # The above line is commented out, which means resize commands are not being processed.
                        # This might not be the cause of the immediate close, but it's an issue.
                        continue # Skip writing resize command to shell
                except json.JSONDecodeError:
                    pass # It's regular user input, not a resize command

                # Forward user input to the shell
                os.write(master_fd, data.encode())
            except WebSocketDisconnect:
                logger.info(f"[WebSocket] Client {chat_id} disconnected gracefully.")
                break # Exit the loop on disconnect



    finally:
        logger.info(f"[WebSocket] Cleaning up resources for client {chat_id}.")
        # Clean up: terminate the shell process and cancel the reading task
        client_task.cancel()
        if shell_process.returncode is None:
            logger.info(f"[WebSocket] Terminating shell process for client {chat_id}.")
            shell_process.terminate()

        try:
            await shell_process.wait()
            logger.info(f"[WebSocket] Shell process for client {chat_id} exited with return code: {shell_process.returncode}")
        except asyncio.CancelledError:
            logger.info(f"Shell process cleanup for client {chat_id} was interrupted by server shutdown.")

        master_reader.close()
        try:
            os.close(slave_fd) # Explicitly close the slave file descriptor
        except OSError as e:
            logger.error(f"Error closing slave_fd for client {chat_id}: {e}")
        logger.info(f"[WebSocket] Resources cleaned up for client {chat_id}.")



# --- Static Files and Frontend Serving ---
# Determine the path to the frontend build directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) # This is /data/data/com.termux/files/home/VE/Vareon
frontend_build_dir = os.path.join(project_root, 'dist', 'public') # Corrected path for build output

# Mount the static files directory (e.g., assets, favicon, etc.)
# We are mounting the entire build directory, as assets seem to be directly under it.
app.mount("/assets", StaticFiles(directory=os.path.join(frontend_build_dir, "assets")), name="assets")
app.mount("/favicon.ico", StaticFiles(directory=frontend_build_dir), name="favicon") # For favicon directly in root
app.mount("/logo192.png", StaticFiles(directory=frontend_build_dir), name="logo192") # For logo directly in root
app.mount("/logo512.png", StaticFiles(directory=frontend_build_dir), name="logo512") # For logo directly in root
app.mount("/manifest.json", StaticFiles(directory=frontend_build_dir), name="manifest") # For manifest directly in root


@app.get("/{rest_of_path:path}")
async def serve_react_app(request: Request, rest_of_path: str):
    """
    Serves the React application.
    This endpoint catches all GET requests that were not handled by other routes.
    It serves the 'index.html' file, which is the entry point for the React app.
    The React router will then handle the specific path on the client-side.
    """
    index_path = os.path.join(frontend_build_dir, 'index.html')
    if os.path.exists(index_path):
        return FileResponse(index_path)
    else:
        logger.error(f"Frontend entry point not found: {index_path}")
        raise HTTPException(status_code=404, detail="Frontend not found. Please build the frontend first.")
