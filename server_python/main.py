import logging
from datetime import datetime, timedelta, timezone
import os
import sys
import argparse
import time

import pty
import asyncio
import json
from typing import List, Dict, Any, Optional
import uuid # Import uuid
import psutil # Import psutil for system metrics
from fastapi import FastAPI, Depends, HTTPException, status, Request, Response, WebSocket, WebSocketDisconnect, Query
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from dotenv import load_dotenv # Import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the script's directory to sys.path for relative imports if run directly
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

# Now relative imports should work if main.py is run directly
from server_python.database import Base, engine, SessionLocal, setup_default_user, get_user_from_db, create_user_in_db, get_db, User as DBUser, get_user_by_username_or_email, Agent as DBAgent, HardwareDevice as DBHardwareDevice, Workflow as DBWorkflow, Dataset as DBDataset, RoutingRule as DBRoutingRule, Conversation as DBConversation, ChatMessage as DBChatMessage, ContextMemory as DBContextMemory, LLMProvider as DBLLMProvider, LLMModel as DBLLMModel, UserLLMPreference as DBUserLLMPreference, TerminalSession as DBTerminalSession, TerminalCommandHistory as DBTerminalCommandHistory, populate_initial_llm_data # Alias User from database to DBUser and other models
from server_python.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user, generate_verification_token, send_verification_email, PermissionChecker, VERIFICATION_TOKEN_EXPIRE_MINUTES, get_websocket_token, get_current_websocket_user
from server_python.schemas import Token, User, UserCreate, UserBase, Agent, AgentCreate, HardwareDevice, HardwareDeviceUpdate, Workflow, WorkflowCreate, Dataset, DatasetCreate, RoutingRule, RoutingRuleCreate, MessageResponse, UserUpdate, TelemetryData, ChatRequest, ChatResponse, ChatMessage, Conversation, ConversationCreate, ConversationUpdate, ContextMemory, ContextMemoryCreate, ContextMemoryUpdate, LLMProvider, LLMProviderCreate, LLMProviderUpdate, LLMModel, LLMModelCreate, LLMModelUpdate, UserLLMPreference, UserLLMPreferenceCreate, UserLLMPreferenceUpdate, TerminalSession, TerminalSessionCreate, TerminalSessionUpdate, TerminalCommandHistory, TerminalCommandHistoryCreate, SystemStatus
from server_python import llm_service # Import the new LLM service
from server_python.cognisys import api as cognisys_api # Import the cognisys API router
from server_python.myntrix import api as myntrix_api # Import the myntrix API router
from server_python.neosyntis import api as neosyntis_api # Import the neosyntis API router
from server_python.arcana import api as arcana_api # Import the arcana API router
from server_python.orchestrator import main as orchestrator_app # Import the orchestrator app
from server_python.context_memory import api as context_memory_api # Import the context_memory API router
from server_python.git_service import api as git_api # Import the git_service API router
from server_python import auth_oauth # Import the new auth_oauth router
from server_python import github_app # Import the new github_app router

app = FastAPI()

app.include_router(cognisys_api.router, prefix="/api/cognisys", tags=["Cognisys"])
app.include_router(myntrix_api.router, prefix="/api/myntrix", tags=["Myntrix"])
app.include_router(neosyntis_api.router, prefix="/api/neosyntis", tags=["Neosyntis"])
app.include_router(arcana_api.router, prefix="/api/arcana", tags=["Arcana"])
app.include_router(context_memory_api.router, prefix="/api/context_memory", tags=["Context Memory"])
app.include_router(git_api.router, prefix="/api/git", tags=["Git"])
app.include_router(auth_oauth.router, prefix="/api/auth", tags=["OAuth"]) # Include the OAuth router
app.include_router(github_app.router, prefix="/api/git", tags=["Git"]) # Include the GitHub App router
app.mount("/ws-api", orchestrator_app.app)

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
        populate_initial_llm_data(db) # Call the new function
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

# Simple in-memory cache
cache: Dict[str, Dict[str, Any]] = {}
CACHE_TTL_SECONDS = 5 # Cache validity in seconds









@app.post("/api/neosyntis/telemetry", response_model=MessageResponse)
async def receive_neosyntis_telemetry(telemetry_data: TelemetryData):
    logger.info(f"Received telemetry from {telemetry_data.source_type} (ID: {telemetry_data.source_id}): Metric='{telemetry_data.metric_name}', Value={telemetry_data.metric_value}, Timestamp={telemetry_data.timestamp}")
    # In a real system, this data would be stored in a time-series database or processed further.
    return {"message": "Telemetry data received successfully!"}

# --- Multimodel Routing API ---
# These endpoints are now handled by the cognisys router
@app.post("/api/cognisys/routing-rules", response_model=RoutingRule)
async def create_cognisys_routing_rule(rule: RoutingRuleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = DBRoutingRule(owner_id=str(current_user.id), name=rule.name, condition=rule.condition, target_model=rule.target_model, priority=rule.priority)
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    logger.info(f"AUDIT: Routing rule created. User ID: {current_user.id}, Rule ID: {db_rule.id}, Name: {db_rule.name}")
    if "cognisys_status" in cache: del cache["cognisys_status"]
    if "system_status" in cache: del cache["system_status"]
    return db_rule

@app.get("/api/cognisys/routing-rules", response_model=List[RoutingRule])
async def list_cognisys_routing_rules(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"AUDIT: Routing rules listed. User ID: {current_user.id}")
    return db.query(DBRoutingRule).filter(DBRoutingRule.owner_id == str(current_user.id)).all()

@app.get("/api/cognisys/routing-rules/{rule_id}", response_model=RoutingRule)
async def get_cognisys_routing_rule(rule_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = db.query(DBRoutingRule).filter(DBRoutingRule.id == rule_id, DBRoutingRule.owner_id == str(current_user.id)).first()
    if db_rule is None:
        logger.warning(f"AUDIT: Routing rule not found for get. User ID: {current_user.id}, Rule ID: {rule_id}")
        raise HTTPException(status_code=404, detail="Routing rule not found")
    logger.info(f"AUDIT: Routing rule retrieved. User ID: {current_user.id}, Rule ID: {db_rule.id}")
    return db_rule

@app.put("/api/cognisys/routing-rules/{rule_id}", response_model=RoutingRule)
async def update_cognisys_routing_rule(rule_id: str, rule_update: RoutingRuleCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = db.query(DBRoutingRule).filter(DBRoutingRule.id == rule_id, DBRoutingRule.owner_id == str(current_user.id)).first()
    if db_rule is None:
        logger.warning(f"AUDIT: Routing rule not found for update. User ID: {current_user.id}, Rule ID: {rule_id}")
        raise HTTPException(status_code=404, detail="Routing rule not found")
    
    db_rule.name = rule_update.name
    if rule_update.condition is not None:
        db_rule.condition = rule_update.condition
    if rule_update.target_model is not None:
        db_rule.target_model = rule_update.target_model
    if rule_update.priority is not None:
        db_rule.priority = rule_update.priority
    db_rule.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_rule)
    logger.info(f"AUDIT: Routing rule updated. User ID: {current_user.id}, Rule ID: {db_rule.id}, Name: {db_rule.name}")
    if "cognisys_status" in cache: del cache["cognisys_status"]
    if "system_status" in cache: del cache["system_status"]
    return db_rule

@app.delete("/api/cognisys/routing-rules/{rule_id}", response_model=MessageResponse)
async def delete_cognisys_routing_rule(rule_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    db_rule = db.query(DBRoutingRule).filter(DBRoutingRule.id == rule_id, DBRoutingRule.owner_id == str(current_user.id)).first()
    if db_rule is None:
        logger.warning(f"AUDIT: Routing rule not found for delete. User ID: {current_user.id}, Rule ID: {rule_id}")
        raise HTTPException(status_code=404, detail="Routing rule not found")
    db.delete(db_rule)
    db.commit()
    logger.info(f"AUDIT: Routing rule deleted. User ID: {current_user.id}, Rule ID: {rule_id}")
    if "cognisys_status" in cache: del cache["cognisys_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": "Routing rule deleted successfully"}

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
        logger.info(f"AUDIT: User registered and verification email sent. User ID: {new_user.id}, Email: {new_user.email}")
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
            logger.warning(f"AUDIT: Email verification failed - User not found. Email: {request.email}")
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")

        if user.is_verified:
            logger.info(f"AUDIT: Email already verified. User ID: {user.id}, Email: {user.email}")
            return {"message": "Email already verified.", "status": "success"}

        if not user.verification_token or user.verification_token != request.token:
            logger.warning(f"AUDIT: Email verification failed - Invalid token. User ID: {user.id}, Email: {user.email}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification token.")

        if user.verification_token_expires_at:
            # Make user.verification_token_expires_at timezone-aware (UTC) for comparison
            # Assuming it was stored as UTC but retrieved as naive
            aware_expiration_time = user.verification_token_expires_at.replace(tzinfo=timezone.utc)
            if aware_expiration_time < datetime.now(timezone.utc):
                logger.warning(f"AUDIT: Email verification failed - Token expired. User ID: {user.id}, Email: {user.email}")
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token expired.")

        user.is_verified = True
        user.verification_token = None
        user.verification_token_expires_at = None
        db.commit()
        db.refresh(user)
        logger.info(f"AUDIT: Email verified successfully. User ID: {user.id}, Email: {user.email}")
        return {"message": "Email verified successfully!", "status": "success"}
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"AUDIT: Unexpected error during email verification. Email: {request.email}, Error: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An unexpected error occurred during email verification.")

@app.post("/api/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = get_user_by_username_or_email(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"AUDIT: Login failed - Incorrect credentials. Username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_verified:
        logger.warning(f"AUDIT: Login failed - Email not verified. Username: {form_data.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for a verification link."
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )
    logger.info(f"AUDIT: User logged in successfully. User ID: {user.id}, Username: {user.username}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/dashboard", response_model=User)
async def read_dashboard(current_user: User = Depends(PermissionChecker(["admin_access"]))):
    return current_user

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
async def get_system_status(current_user: Optional[User] = Depends(get_current_user, use_cache=False), db: Session = Depends(get_db)):
    # Fetch system metrics using psutil with fallback
    cpu_percent = 0.0
    memory_percent = 0.0
    memory_total = 0
    memory_available = 0
    system_metrics_mocked = False
    system_metrics_reason = ""

    try:
        cpu_percent = psutil.cpu_percent(interval=0.1) # Short interval for quick check
        memory_info = psutil.virtual_memory()
        memory_percent = memory_info.percent
        memory_total = memory_info.total
        memory_available = memory_info.available
    except PermissionError:
        logger.warning("Permission denied to access system metrics via psutil. Falling back to mock data.")
        cpu_percent = 10.0
        memory_percent = 30.0
        memory_total = 8 * 1024 * 1024 * 1024 # 8 GB
        memory_available = 5 * 1024 * 1024 * 1024 # 5 GB
        system_metrics_mocked = True
        system_metrics_reason = "PermissionError accessing system metrics"
    except Exception as e:
        logger.error(f"Failed to get system metrics via psutil: {e}. Falling back to mock data.", exc_info=True)
        cpu_percent = 10.0
        memory_percent = 30.0
        memory_total = 8 * 1024 * 1024 * 1024 # 8 GB
        memory_available = 5 * 1024 * 1024 * 1024 # 5 GB
        system_metrics_mocked = True
        system_metrics_reason = f"Unexpected error: {e}"

    # Check for mock mode environment variable or if user is not authenticated
    if os.getenv("VAREON_MOCK_SYSTEM_STATUS", "false").lower() == "true" or current_user is None:
        mock_time = datetime.utcnow().isoformat()
        return_data = {
            "arcana": {
                "status": "offline",
                "uptime": "0s",
                "activeChats": 0,
                "messagesProcessed": 0,
                "avgResponseTime": "0s",
                "activeAgents": 0,
                "jobsCompleted": 0,
                "devicesConnected": 0,
                "activeWorkflows": 0,
                "datasetsManaged": 0,
                "searchQueriesProcessed": 0,
                "modelsActive": 0,
                "routingRules": 0,
                "requestsRouted": 0,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_total": memory_total,
                "memory_available": memory_available,
                "system_metrics_mocked": system_metrics_mocked,
                "system_metrics_reason": system_metrics_reason,
            },
            "myntrix": {
                "status": "offline",
                "uptime": "0s",
                "activeAgents": 0,
                "jobsCompleted": 0,
                "devicesConnected": 0,
                "activeChats": 0,
                "messagesProcessed": 0,
                "avgResponseTime": "0s",
                "activeWorkflows": 0,
                "datasetsManaged": 0,
                "searchQueriesProcessed": 0,
                "modelsActive": 0,
                "routingRules": 0,
                "requestsRouted": 0,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_total": memory_total,
                "memory_available": memory_available,
                "system_metrics_mocked": system_metrics_mocked,
                "system_metrics_reason": system_metrics_reason,
            },
            "neosyntis": {
                "status": "offline",
                "uptime": "0s",
                "activeWorkflows": 0,
                "datasetsManaged": 0,
                "searchQueriesProcessed": 0,
                "activeChats": 0,
                "messagesProcessed": 0,
                "avgResponseTime": "0s",
                "activeAgents": 0,
                "jobsCompleted": 0,
                "devicesConnected": 0,
                "modelsActive": 0,
                "routingRules": 0,
                "requestsRouted": 0,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_total": memory_total,
                "memory_available": memory_available,
                "system_metrics_mocked": system_metrics_mocked,
                "system_metrics_reason": system_metrics_reason,
            },
            "cognisys": {
                "status": "offline",
                "uptime": "0s",
                "modelsActive": 0,
                "routingRules": 0,
                "requestsRouted": 0,
                "activeChats": 0,
                "messagesProcessed": 0,
                "avgResponseTime": "0s",
                "activeAgents": 0,
                "jobsCompleted": 0,
                "devicesConnected": 0,
                "activeWorkflows": 0,
                "datasetsManaged": 0,
                "searchQueriesProcessed": 0,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_total": memory_total,
                "memory_available": memory_available,
                "system_metrics_mocked": system_metrics_mocked,
                "system_metrics_reason": system_metrics_reason,
            },
            "mocked": True,
            "reason": "Mocked due to environment variable or unauthenticated access"
        }
        logger.info(f"Returning mocked system status: {json.dumps(return_data, indent=2)}")
        return return_data

    cache_key = "system_status"
    if cache_key in cache and (datetime.now(timezone.utc) - cache[cache_key]["timestamp"]).total_seconds() < CACHE_TTL_SECONDS:
        return cache[cache_key]["data"]

    current_time = datetime.now(timezone.utc)

    arcana_uptime = format_timedelta(current_time - module_startup_times["arcana"])
    myntrix_uptime = format_timedelta(current_time - module_startup_times["myntrix"])
    neosyntis_uptime = format_timedelta(current_time - module_startup_times["neosyntis"])
    cognisys_uptime = format_timedelta(current_time - module_startup_times["cognisys"])

    # Fetch real data from the database
    active_agents_count = db.query(DBAgent).filter(DBAgent.owner_id == str(current_user.id), DBAgent.status == "online").count()
    total_agents_count = db.query(DBAgent).filter(DBAgent.owner_id == str(current_user.id)).count()
    
    active_workflows_count = db.query(DBWorkflow).filter(DBWorkflow.owner_id == str(current_user.id), DBWorkflow.status == "running").count()
    total_workflows_count = db.query(DBWorkflow).filter(DBWorkflow.owner_id == str(current_user.id)).count()

    datasets_managed_count = db.query(DBDataset).filter(DBDataset.owner_id == str(current_user.id)).count()

    routing_rules_count = db.query(DBRoutingRule).filter(DBRoutingRule.owner_id == str(current_user.id)).count()
    
    devices_connected_count = db.query(DBHardwareDevice).filter(DBHardwareDevice.owner_id == str(current_user.id), DBHardwareDevice.status == "connected").count()
    total_devices_count = db.query(DBHardwareDevice).filter(DBHardwareDevice.owner_id == str(current_user.id)).count()

    # Fetch Arcana specific data
    active_chats_count = db.query(DBConversation).filter(DBConversation.user_id == str(current_user.id)).count()
    messages_processed_count = db.query(DBChatMessage).filter(DBChatMessage.user_id == str(current_user.id)).count()

    response_data = {
        "arcana": {
            "status": "online",
            "uptime": arcana_uptime,
            "activeChats": active_chats_count,
            "messagesProcessed": messages_processed_count,
            "avgResponseTime": "1.2s", # Still simulated
            "activeAgents": 0, # Explicitly set to 0 or fetch if applicable
            "jobsCompleted": 0,
            "devicesConnected": 0,
            "activeWorkflows": 0,
            "datasetsManaged": 0,
            "searchQueriesProcessed": 0,
            "modelsActive": 0,
            "routingRules": 0,
            "requestsRouted": 0,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_total": memory_total,
            "memory_available": memory_available,
            "system_metrics_mocked": system_metrics_mocked,
            "system_metrics_reason": system_metrics_reason,
        },
        "myntrix": {
            "status": "online",
            "uptime": myntrix_uptime,
            "activeAgents": active_agents_count,
            "jobsCompleted": 234, # Still simulated
            "devicesConnected": devices_connected_count,
            "activeChats": 0,
            "messagesProcessed": 0,
            "avgResponseTime": "0s",
            "activeWorkflows": 0,
            "datasetsManaged": 0,
            "searchQueriesProcessed": 0,
            "modelsActive": 0,
            "routingRules": 0,
            "requestsRouted": 0,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_total": memory_total,
            "memory_available": memory_available,
            "system_metrics_mocked": system_metrics_mocked,
            "system_metrics_reason": system_metrics_reason,
        },
        "neosyntis": {
            "status": "online",
            "uptime": neosyntis_uptime,
            "activeWorkflows": active_workflows_count,
            "datasetsManaged": datasets_managed_count,
            "searchQueriesProcessed": 892, # Still simulated
            "activeChats": 0,
            "messagesProcessed": 0,
            "avgResponseTime": "0s",
            "activeAgents": 0,
            "jobsCompleted": 0,
            "devicesConnected": 0,
            "modelsActive": 0,
            "routingRules": 0,
            "requestsRouted": 0,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_total": memory_total,
            "memory_available": memory_available,
            "system_metrics_mocked": system_metrics_mocked,
            "system_metrics_reason": system_metrics_reason,
        },
        "cognisys": {
            "status": "online",
            "uptime": cognisys_uptime,
            "modelsActive": 12, # Still simulated
            "routingRules": routing_rules_count,
            "requestsRouted": 3421, # Still simulated
            "activeChats": 0,
            "messagesProcessed": 0,
            "avgResponseTime": "0s",
            "activeAgents": 0,
            "jobsCompleted": 0,
            "devicesConnected": 0,
            "activeWorkflows": 0,
            "datasetsManaged": 0,
            "searchQueriesProcessed": 0,
            "cpu_percent": cpu_percent,
            "memory_percent": memory_percent,
            "memory_total": memory_total,
            "memory_available": memory_available,
            "system_metrics_mocked": system_metrics_mocked,
            "system_metrics_reason": system_metrics_reason,
        },
        "mocked": False, # This will be set to True if any module is mocked
        "reason": None,
    }
    # If any module had mocked system metrics, set the top-level mocked and reason
    if system_metrics_mocked:
        response_data["mocked"] = True
        response_data["reason"] = system_metrics_reason

    cache[cache_key] = {"data": response_data, "timestamp": datetime.now(timezone.utc)}
    return response_data

@app.post("/api/neosyntis/open-lab")
async def open_neosyntis_lab():
    logger.info("Quick action: Open Neosyntis Lab triggered.")
    # TODO: Implement actual logic for opening Neosyntis Lab
    if "neosyntis_status" in cache: del cache["neosyntis_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": "Neosyntis Lab opened successfully!"}

@app.post("/api/arcana/start-chat", response_model=MessageResponse)
async def start_arcana_chat(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    logger.info(f"Quick action: Start Arcana Chat triggered by user {current_user.id}.")
    # Implement actual logic for starting Arcana Chat
    # This could involve:
    # 1. Creating a new conversation in the database
    # 2. Initializing LLM parameters for the user/conversation
    # 3. Preparing a specific context for the chat
    
    # For now, we'll simulate creating a new conversation
    user_id = str(current_user.id)
    new_conversation = DBConversation(user_id=user_id, title=f"Arcana Chat - {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
    db.add(new_conversation)
    db.commit()
    db.refresh(new_conversation)
    
    logger.info(f"Arcana Chat session started. New conversation ID: {new_conversation.id}")
    
    if "arcana_status" in cache: del cache["arcana_status"]
    if "system_status" in cache: del cache["system_status"]
    return {"message": f"Arcana Chat started successfully! Conversation ID: {new_conversation.id}"}

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

@app.get("/api/search", response_model=List[Dict[str, Any]])
async def global_search(query: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = []
    search_pattern = f"%{query}%"

    # Search Workflows
    workflows = db.query(DBWorkflow).filter(DBWorkflow.owner_id == str(current_user.id), DBWorkflow.name.ilike(search_pattern)).all()
    for wf in workflows:
        results.append({"type": "workflow", "id": wf.id, "name": wf.name, "status": wf.status})

    # Search Datasets
    datasets = db.query(DBDataset).filter(DBDataset.owner_id == str(current_user.id), DBDataset.name.ilike(search_pattern)).all()
    for ds in datasets:
        results.append({"type": "dataset", "id": ds.id, "name": ds.name, "format": ds.format})

    # Search Agents
    agents = db.query(DBAgent).filter(DBAgent.owner_id == str(current_user.id), DBAgent.name.ilike(search_pattern)).all()
    for agent in agents:
        results.append({"type": "agent", "id": agent.id, "name": agent.name, "status": agent.status})

    # Search Hardware Devices
    hardware_devices = db.query(DBHardwareDevice).filter(DBHardwareDevice.owner_id == str(current_user.id), DBHardwareDevice.name.ilike(search_pattern)).all()
    for hd in hardware_devices:
        results.append({"type": "hardware_device", "id": hd.id, "name": hd.name, "device_type": hd.device_type})

    # Search Routing Rules
    routing_rules = db.query(DBRoutingRule).filter(DBRoutingRule.owner_id == str(current_user.id), DBRoutingRule.name.ilike(search_pattern)).all()
    for rr in routing_rules:
        results.append({"type": "routing_rule", "id": rr.id, "name": rr.name, "target_model": rr.target_model})

    return results

# --- Chat Interface API ---
class ChatRequest(BaseModel):
    message: str

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_llm(request: ChatRequest, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)

    # 1. Determine conversation_id
    if request.conversation_id:
        conversation = db.query(DBConversation).filter(DBConversation.id == str(request.conversation_id), DBConversation.user_id == user_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
    else:
        conversation = DBConversation(user_id=user_id, title=request.message[:50]) # Auto-generate title from first message
        db.add(conversation)
        db.commit()
        db.refresh(conversation)
        logger.info(f"AUDIT: New conversation created. User ID: {user_id}, Conversation ID: {conversation.id}")

    # 2. Save user's message
    user_chat_message = DBChatMessage(
        conversation_id=conversation.id,
        user_id=user_id,
        sender="user",
        message_content=request.message
    )
    db.add(user_chat_message)
    db.commit()
    db.refresh(user_chat_message)
    logger.info(f"AUDIT: User message saved. User ID: {user_id}, Conversation ID: {conversation.id}, Message ID: {user_chat_message.id}")

    # Implement Dynamic LLM Routing
    routing_rules = db.query(DBRoutingRule).filter(DBRoutingRule.owner_id == user_id).order_by(DBRoutingRule.priority.desc()).all()

    selected_model = None
    for rule in routing_rules:
        if rule.condition == "true" or (rule.condition == "user.id == current_user.id" and rule.owner_id == user_id):
            selected_model = rule.target_model
            break
    
    if not selected_model:
        selected_model = "gemini-pro"

    logger.info(f"User {user_id} chat request routed to: {selected_model}")

    llm_response_content = ""
    # Service Orchestration: Check if the selected_model indicates a service to orchestrate
    if selected_model.startswith("myntrix_agent:"):
        agent_id = selected_model.split(":")[1]
        task_details = {"request_message": request.message}
        success = await trigger_myntrix_agent_task(agent_id, task_details, user_id, db)
        if success:
            llm_response_content = f"Myntrix Agent {agent_id} triggered with message: {request.message}"
        else:
            raise HTTPException(status_code=500, detail=f"Failed to trigger Myntrix Agent {agent_id}")
    elif selected_model.startswith("neosyntis_workflow:"):
        workflow_id = selected_model.split(":")[1]
        db_workflow = db.query(DBWorkflow).filter(DBWorkflow.id == workflow_id, DBWorkflow.owner_id == user_id).first()
        if db_workflow is None:
            raise HTTPException(status_code=404, detail=f"Neosyntis Workflow {workflow_id} not found")
        
        try:
            workflow_steps = json.loads(db_workflow.steps)
            logger.info(f"Orchestrating workflow {workflow_id} steps: {workflow_steps}")
            
            for step in workflow_steps:
                if step.get("action") == "trigger_agent":
                    agent_id = step.get("agent_id")
                    task_details = step.get("task_details", {})
                    if agent_id:
                        success = await trigger_myntrix_agent_task(agent_id, task_details, user_id, db)
                        if not success:
                            raise HTTPException(status_code=400, detail=f"Failed to trigger agent {agent_id} from orchestrated workflow")
                    else:
                        logger.warning(f"Orchestrated workflow {workflow_id} step missing agent_id for 'trigger_agent' action: {step}")
                elif step.get("action") == "utilize_llm":
                    llm_task = step.get("llm_task")
                    input_data = step.get("input_data", "")
                    if llm_task:
                        llm_response_content = await utilize_arcana_llm_task(llm_task, input_data, user_id, db)
                        logger.info(f"Arcana LLM responded from orchestrated workflow: {llm_response_content}")
                    else:
                        logger.warning(f"Orchestrated workflow {workflow_id} step missing llm_task for 'utilize_llm' action: {step}")
                elif step.get("action") == "manage_model":
                    model_id = step.get("model_id")
                    operation = step.get("operation")
                    if model_id and operation:
                        success = await manage_myntrix_model_task(model_id, operation, user_id, db)
                        if not success:
                            raise HTTPException(status_code=400, detail=f"Failed to manage model {model_id} with operation {operation} from orchestrated workflow")
                    else:
                        logger.warning(f"Orchestrated workflow {workflow_id} step missing model_id or operation for 'manage_model' action: {step}")
                else:
                    logger.info(f"Unknown or unsupported orchestrated workflow step action: {step.get('action')}. Skipping.")

            db_workflow.status = "completed"
            db.commit()
            db.refresh(db_workflow)
            logger.info(f"Orchestrated workflow {workflow_id} completed.")
            llm_response_content = f"Neosyntis Workflow {workflow_id} orchestrated successfully with message: {request.message}"

        except json.JSONDecodeError:
            logger.error(f"Orchestrated workflow {workflow_id} has invalid JSON steps: {db_workflow.steps}")
            db_workflow.status = "failed"
            db.commit()
            db.refresh(db_workflow)
            raise HTTPException(status_code=400, detail="Orchestrated workflow steps are not valid JSON.")
        except Exception as e:
            logger.error(f"Error orchestrating workflow {workflow_id}: {e}", exc_info=True)
            db_workflow.status = "failed"
            db.commit()
            db.refresh(db_workflow)
            raise HTTPException(status_code=500, detail="Error orchestrating workflow.")
    else:
        # If not a service orchestration, proceed with LLM completion
        llm_response_content = await llm_service.get_openrouter_completion(user_id, request.message, model_name=selected_model, db=db, owner_id=user_id)
    
    # 3. Save LLM's response
    llm_chat_message = DBChatMessage(
        conversation_id=conversation.id,
        user_id=user_id,
        sender="llm",
        message_content=llm_response_content
    )
    db.add(llm_chat_message)
    db.commit()
    db.refresh(llm_chat_message)
    logger.info(f"AUDIT: LLM response saved. User ID: {user_id}, Conversation ID: {conversation.id}, Message ID: {llm_chat_message.id}")

    return ChatResponse(response=llm_response_content, conversation_id=conversation.id, message_id=llm_chat_message.id)

@app.get("/api/chat/history/{conversation_id}", response_model=List[ChatMessage])
async def get_chat_history(conversation_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    conversation = db.query(DBConversation).filter(DBConversation.id == str(conversation_id), DBConversation.user_id == user_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    messages = db.query(DBChatMessage).filter(DBChatMessage.conversation_id == str(conversation_id)).order_by(DBChatMessage.timestamp).all()
    logger.info(f"AUDIT: Chat history retrieved. User ID: {user_id}, Conversation ID: {conversation_id}")
    return messages

@app.get("/api/chat/conversations", response_model=List[Conversation])
async def list_conversations(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    conversations = db.query(DBConversation).filter(DBConversation.user_id == user_id).order_by(DBConversation.updated_at.desc()).all()
    logger.info(f"AUDIT: Conversations listed. User ID: {user_id}")
    return conversations

@app.post("/api/chat/conversations", response_model=Conversation)
async def create_conversation(conversation_create: ConversationCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    conversation = DBConversation(user_id=user_id, title=conversation_create.title)
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    logger.info(f"AUDIT: Conversation created. User ID: {user_id}, Conversation ID: {conversation.id}, Title: {conversation.title}")
    return conversation

@app.put("/api/chat/conversations/{conversation_id}", response_model=Conversation)
async def update_conversation(conversation_id: uuid.UUID, conversation_update: ConversationUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    conversation = db.query(DBConversation).filter(DBConversation.id == str(conversation_id), DBConversation.user_id == user_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    if conversation_update.title is not None:
        conversation.title = conversation_update.title
    conversation.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(conversation)
    logger.info(f"AUDIT: Conversation updated. User ID: {user_id}, Conversation ID: {conversation.id}, New Title: {conversation.title}")
    return conversation

@app.delete("/api/chat/conversations/{conversation_id}", response_model=MessageResponse)
async def delete_conversation(conversation_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    conversation = db.query(DBConversation).filter(DBConversation.id == str(conversation_id), DBConversation.user_id == user_id).first()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    db.query(DBChatMessage).filter(DBChatMessage.conversation_id == str(conversation_id)).delete()
    db.delete(conversation)
    db.commit()
    logger.info(f"AUDIT: Conversation and its messages deleted. User ID: {user_id}, Conversation ID: {conversation_id}")
    return {"message": "Conversation and its messages deleted successfully."}

@app.post("/api/chat/clear", response_model=MessageResponse)
async def clear_chat_history(current_user: User = Depends(get_current_user), db: Session = Depends(get_db), conversation_id: Optional[uuid.UUID] = Query(None)):
    user_id = str(current_user.id)
    if conversation_id:
        conversation = db.query(DBConversation).filter(DBConversation.id == str(conversation_id), DBConversation.user_id == user_id).first()
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        db.query(DBChatMessage).filter(DBChatMessage.conversation_id == str(conversation_id)).delete()
        db.commit()
        logger.info(f"AUDIT: Chat history cleared for conversation. User ID: {user_id}, Conversation ID: {conversation_id}")
        return {"message": f"Chat history cleared for conversation {conversation_id}."}
    else:
        # Clear all conversations and messages for the user
        conversations = db.query(DBConversation).filter(DBConversation.user_id == user_id).all()
        for conv in conversations:
            db.query(DBChatMessage).filter(DBChatMessage.conversation_id == str(conv.id)).delete()
            db.delete(conv)
        db.commit()
        logger.info(f"AUDIT: All chat history cleared for user. User ID: {user_id}")
        return {"message": "All chat history cleared."}

# --- Context Memory API ---
@app.get("/api/arcana/context-memory", response_model=List[ContextMemory])
async def get_all_context_memory(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    context_memories = db.query(DBContextMemory).filter(DBContextMemory.user_id == user_id).all()
    logger.info(f"AUDIT: All context memories retrieved. User ID: {user_id}")
    return context_memories

@app.get("/api/arcana/context-memory/{key}", response_model=ContextMemory)
async def get_context_memory_by_key(key: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    context_memory = db.query(DBContextMemory).filter(DBContextMemory.user_id == user_id, DBContextMemory.key == key).first()
    if not context_memory:
        raise HTTPException(status_code=404, detail="Context memory not found")
    logger.info(f"AUDIT: Context memory retrieved by key. User ID: {user_id}, Key: {key}")
    return context_memory

@app.post("/api/arcana/context-memory", response_model=ContextMemory)
async def create_or_update_context_memory(context_data: ContextMemoryCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    context_memory = db.query(DBContextMemory).filter(DBContextMemory.user_id == user_id, DBContextMemory.key == context_data.key).first()
    if context_memory:
        context_memory.value = context_data.value
        context_memory.updated_at = datetime.utcnow()
        logger.info(f"AUDIT: Context memory updated. User ID: {user_id}, Key: {context_data.key}")
    else:
        context_memory = DBContextMemory(user_id=user_id, key=context_data.key, value=context_data.value)
        db.add(context_memory)
        logger.info(f"AUDIT: Context memory created. User ID: {user_id}, Key: {context_data.key}")
    db.commit()
    db.refresh(context_memory)
    return context_memory

@app.delete("/api/arcana/context-memory/{key}", response_model=MessageResponse)
async def delete_context_memory_by_key(key: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    context_memory = db.query(DBContextMemory).filter(DBContextMemory.user_id == user_id, DBContextMemory.key == key).first()
    if not context_memory:
        raise HTTPException(status_code=404, detail="Context memory not found")
    db.delete(context_memory)
    db.commit()
    logger.info(f"AUDIT: Context memory deleted. User ID: {user_id}, Key: {key}")
    return {"message": "Context memory deleted successfully"}

# --- LLM Configuration API ---




@app.get("/api/arcana/llm/preferences", response_model=UserLLMPreference)
async def get_user_llm_preferences(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    preferences = db.query(DBUserLLMPreference).filter(DBUserLLMPreference.user_id == user_id).first()
    if not preferences:
        # Create default preferences if none exist
        preferences = DBUserLLMPreference(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
        logger.info(f"AUDIT: Default LLM preferences created for user. User ID: {user_id}")
    logger.info(f"AUDIT: User LLM preferences retrieved. User ID: {user_id}")
    return preferences

@app.put("/api/arcana/llm/preferences", response_model=UserLLMPreference)
async def update_user_llm_preferences(preference_update: UserLLMPreferenceUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    preferences = db.query(DBUserLLMPreference).filter(DBUserLLMPreference.user_id == user_id).first()
    if not preferences:
        preferences = DBUserLLMPreference(user_id=user_id)
        db.add(preferences)
        db.commit()
        db.refresh(preferences)
    
    if preference_update.default_model_id is not None:
        # Validate if the model exists
        model = db.query(DBLLMModel).filter(DBLLMModel.id == str(preference_update.default_model_id)).first()
        if not model:
            raise HTTPException(status_code=404, detail="Default LLM Model not found")
        preferences.default_model_id = str(preference_update.default_model_id)
    if preference_update.temperature is not None:
        preferences.temperature = preference_update.temperature
    if preference_update.top_p is not None:
        preferences.top_p = preference_update.top_p
    
    db.commit()
    db.refresh(preferences)
    return preferences

# --- Terminal Session Management API ---
@app.get("/api/arcana/terminal/sessions", response_model=List[TerminalSession])
async def list_terminal_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    sessions = db.query(DBTerminalSession).filter(DBTerminalSession.user_id == user_id).order_by(DBTerminalSession.started_at.desc()).all()
    logger.info(f"AUDIT: Terminal sessions listed. User ID: {user_id}")
    return sessions

@app.get("/api/arcana/terminal/sessions/{session_id}/history", response_model=List[TerminalCommandHistory])
async def get_terminal_session_history(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    session = db.query(DBTerminalSession).filter(DBTerminalSession.id == str(session_id), DBTerminalSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Terminal session not found")
    
    history = db.query(DBTerminalCommandHistory).filter(DBTerminalCommandHistory.session_id == str(session_id)).order_by(DBTerminalCommandHistory.timestamp).all()
    logger.info(f"AUDIT: Terminal session history retrieved. User ID: {user_id}, Session ID: {session_id}")
    return history

@app.post("/api/arcana/terminal/sessions/{session_id}/close", response_model=MessageResponse)
async def close_terminal_session(session_id: uuid.UUID, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    user_id = str(current_user.id)
    session = db.query(DBTerminalSession).filter(DBTerminalSession.id == str(session_id), DBTerminalSession.user_id == user_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Terminal session not found")
    
    session.status = "closed"
    session.ended_at = datetime.utcnow()
    db.commit()
    db.refresh(session)
    logger.info(f"AUDIT: Terminal session closed. User ID: {user_id}, Session ID: {session_id}")
    return {"message": "Terminal session closed successfully"}

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
@app.websocket("/ws/shell/{session_id}")
async def websocket_shell(
    websocket: WebSocket,
    session_id: uuid.UUID, # Renamed from chat_id to session_id
    current_user: User = Depends(get_current_websocket_user), # Authenticate WebSocket
    db: Session = Depends(get_db) # Inject DB session
):
    logger.info(f"[WebSocket] Entering websocket_shell function for session {session_id}.")
    user_id = str(current_user.id)
    logger.info(f"[WebSocket] Attempting to connect client {session_id} to interactive shell for user {user_id}.")
    
    # Create a new TerminalSession entry
    terminal_session = DBTerminalSession(id=str(session_id), user_id=user_id, status="active")
    db.add(terminal_session)
    db.commit()
    db.refresh(terminal_session)
    logger.info(f"AUDIT: Terminal session started. User ID: {user_id}, Session ID: {session_id}")

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
                    logger.info(f"[WebSocket] Shell output stream for client {session_id} ended (output was empty).")
                    break
                await websocket.send_text(output.decode(errors='ignore'))
        except (IOError, WebSocketDisconnect) as e:
            logger.info(f"[WebSocket] Shell output stream for client {session_id} closed due to: {e}")
        except Exception as e:
            logger.error(f"[WebSocket] Unexpected error in forward_shell_to_client for client {session_id}: {e}", exc_info=True)
        finally:
            logger.info(f"[WebSocket] forward_shell_to_client task for client {session_id} finishing.")

    client_task = asyncio.create_task(forward_shell_to_client(), name=f"shell_forwarder_{session_id}")

    try:
        while True:
            try:
                data = await websocket.receive_text()
                logger.debug(f"[WebSocket] Received data from client {session_id}: {data[:100]}...") # Log first 100 chars
                
                # Check for resize command (sent as JSON from frontend)
                try:
                    data_json = json.loads(data)
                    if 'resize' in data_json:
                        cols, rows = data_json['resize']['cols'], data_json['resize']['rows']
                        logger.info(f"[WebSocket] Resizing PTY for client {session_id} to {cols}x{rows}")
                        # To fully implement terminal resizing, uncomment the line below and ensure
                        # 'termios' and 'struct' are imported at the top of the file.
                        # import fcntl
                        # import termios
                        # import struct
                        # fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
                        # The above line is commented out, which means resize commands are not being processed.
                        # This might not be the cause of the immediate close, but it's an issue.
                        continue # Skip writing resize command to shell
                except json.JSONDecodeError:
                    pass # It's regular user input, not a resize command

                # Log command to history
                command_history_entry = DBTerminalCommandHistory(
                    session_id=str(session_id),
                    command=data,
                    output="" # Output will be captured later if needed
                )
                db.add(command_history_entry)
                db.commit()
                db.refresh(command_history_entry)
                terminal_session.last_command = data # Update last command in session
                db.commit()

                # Forward user input to the shell
                os.write(master_fd, data.encode())
            except WebSocketDisconnect:
                logger.info(f"[WebSocket] Client {session_id} disconnected gracefully.")
                break # Exit the loop on disconnect

    finally:
        logger.info(f"[WebSocket] Cleaning up resources for client {session_id}.")
        # Update TerminalSession status on disconnect
        terminal_session.status = "closed"
        terminal_session.ended_at = datetime.utcnow()
        db.commit()
        logger.info(f"AUDIT: Terminal session closed. User ID: {user_id}, Session ID: {session_id}")

        # Clean up: terminate the shell process and cancel the reading task
        client_task.cancel()
        if shell_process.returncode is None:
            logger.info(f"[WebSocket] Terminating shell process for client {session_id}.")
            shell_process.terminate()

        try:
            await shell_process.wait()
            logger.info(f"[WebSocket] Shell process for client {session_id} exited with return code: {shell_process.returncode}")
        except asyncio.CancelledError:
            logger.info(f"Shell process cleanup for client {session_id} was interrupted by server shutdown.")

        master_reader.close()
        try:
            os.close(slave_fd) # Explicitly close the slave file descriptor
        except OSError as e:
            logger.error(f"Error closing slave_fd for client {session_id}: {e}")
        logger.info(f"[WebSocket] Resources cleaned up for client {session_id}.")



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
