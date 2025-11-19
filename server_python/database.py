from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Table, Text, Float, UniqueConstraint
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List
import uuid # Import uuid
from .encryption_utils import encrypt_api_key

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for User-Role many-to-many relationship
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', String(36), ForeignKey('users.id'), primary_key=True),
    Column('role_id', String(36), ForeignKey('roles.id'), primary_key=True)
)

# Association table for Role-Permission many-to-many relationship
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', String(36), ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', String(36), ForeignKey('permissions.id'), primary_key=True)
)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)

class Role(Base):
    __tablename__ = "roles"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    permissions = relationship("Permission", secondary=role_permissions, backref="roles")

class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    roles = relationship("Role", secondary=user_roles, backref="users")
    arcana_api_keys = relationship("ArcanaApiKey", back_populates="user")
    
    # Subscription-related fields
    demo_credits = Column(Integer, default=0)
    subscriptions = relationship("UserSubscription", back_populates="user")

class Plan(Base):
    __tablename__ = "plans"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    price_monthly = Column(Integer, nullable=False)
    price_yearly = Column(Integer, nullable=False)
    max_users = Column(Integer, default=1)
    features = Column(Text, nullable=True) # Storing as JSON string
    demo_credits = Column(Integer, nullable=True)

class UserSubscription(Base):
    __tablename__ = "user_subscriptions"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    plan_id = Column(String(36), ForeignKey('plans.id'), nullable=False)
    start_date = Column(DateTime, default=datetime.utcnow)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default="active") # e.g., active, cancelled, expired
    
    user = relationship("User", back_populates="subscriptions")
    plan = relationship("Plan")


class ArcanaApiKey(Base):
    __tablename__ = "arcana_api_keys"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, nullable=False) # Encrypted API key
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, nullable=False) # User-defined name for the key
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    user = relationship("User", back_populates="arcana_api_keys")

class UserCliConfig(Base):
    __tablename__ = "user_cli_configs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    key = Column(String, nullable=False, index=True)
    value = Column(Text, nullable=False) # Storing as JSON string or plain text
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="cli_configs")

    __table_args__ = (
        UniqueConstraint('user_id', 'key', name='uq_user_id_key'),
    )

class Agent(Base):
    __tablename__ = "agents"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False) # New field
    status = Column(String, nullable=False)
    health = Column(Integer, default=100) # New field
    last_run = Column(DateTime, nullable=True) # New field
    configuration = Column(Text, nullable=True) # New field, storing as JSON string
    owner = relationship("User", backref="agents")

class Device(Base):
    __tablename__ = "devices"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)
    connection_string = Column(String, nullable=False)
    status = Column(String, default="disconnected")
    last_seen = Column(DateTime, nullable=True)
    firmware_version = Column(String, nullable=True)
    configuration = Column(Text, nullable=True)
    owner = relationship("User", backref="devices")

class Job(Base):
    __tablename__ = "jobs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    progress = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    logs = Column(Text, nullable=True)
    details = Column(Text, nullable=True) # Storing as JSON string
    owner = relationship("User", backref="jobs")

class ScheduledTask(Base):
    __tablename__ = "scheduled_tasks"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    schedule = Column(String, nullable=False) # Cron expression
    action = Column(Text, nullable=False) # JSON string for action payload
    enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", backref="scheduled_tasks")

class TaskRun(Base):
    __tablename__ = "task_runs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    task_id = Column(String(36), ForeignKey('scheduled_tasks.id'), nullable=False)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, nullable=False) # e.g., 'pending', 'running', 'success', 'failed'
    logs = Column(Text, nullable=True)
    scheduled_task = relationship("ScheduledTask", backref="task_runs")

class TelemetryData(Base):
    __tablename__ = "telemetry_data"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metric_name = Column(String, nullable=False, index=True)
    value = Column(Float, nullable=False)
    workflow_id = Column(String(36), ForeignKey('workflows.id'), nullable=True)
    dataset_id = Column(String(36), ForeignKey('datasets.id'), nullable=True)
    device_id = Column(String(36), ForeignKey('devices.id'), nullable=True)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False) # To track who generated the telemetry
    workflow = relationship("Workflow", backref="telemetry_data")
    dataset = relationship("Dataset", backref="telemetry_data")
    device = relationship("Device", backref="telemetry_data")
    owner = relationship("User", backref="telemetry_data")

class MLModel(Base):
    __tablename__ = "ml_models"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    version = Column(String, nullable=False)
    status = Column(String, default="registered") # e.g., registered, training, deployed, failed
    path_to_artifact = Column(String, nullable=True)
    training_dataset_id = Column(String(36), ForeignKey('datasets.id'), nullable=True)
    deployed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", backref="ml_models")
    training_dataset = relationship("Dataset", foreign_keys=[training_dataset_id])

class TrainingJob(Base):
    __tablename__ = "training_jobs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    model_id = Column(String(36), ForeignKey('ml_models.id'), nullable=False)
    status = Column(String, nullable=False) # e.g., pending, running, completed, failed
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    metrics = Column(Text, nullable=True) # Storing as JSON string
    logs = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", backref="training_jobs")
    ml_model = relationship("MLModel", backref="training_jobs")

class HardwareDevice(Base):
    __tablename__ = "hardware_devices"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    device_type = Column(String, nullable=False)
    status = Column(String, nullable=False)
    owner = relationship("User", backref="hardware_devices")

class Workflow(Base):
    __tablename__ = "workflows"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True) # New field
    status = Column(String, nullable=False)
    steps = Column(Text, nullable=False) # Storing steps as JSON string
    created_at = Column(DateTime, default=datetime.utcnow) # New field
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow) # New field
    owner = relationship("User", backref="workflows")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True) # New field
    file_path = Column(String, nullable=True) # New field
    size_bytes = Column(Integer, nullable=True) # New field
    format = Column(String, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow) # New field
    owner = relationship("User", backref="datasets")

class RoutingRule(Base):
    __tablename__ = "routing_rules"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    condition = Column(Text, nullable=False)
    target_model = Column(String, nullable=False)
    priority = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", backref="routing_rules")

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="conversations")

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String(36), ForeignKey('conversations.id'), nullable=False)
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False) # Redundant but useful for direct query
    sender = Column(String, nullable=False) # "user" or "llm"
    message_content = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    conversation = relationship("Conversation", backref="messages")
    user = relationship("User", backref="chat_messages")

class ContextMemory(Base):
    __tablename__ = "context_memory"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    key = Column(String, index=True, nullable=False)
    value = Column(Text, nullable=False) # Storing as JSON/text
    last_accessed = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="context_memories")

class LLMProvider(Base):
    __tablename__ = "llm_providers"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    base_url = Column(String, nullable=False)
    enabled = Column(Boolean, default=True) # New field
    api_key_encrypted = Column(String, nullable=False) # Encrypted API key
    organization_id = Column(String, nullable=True) # New field, nullable
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class LLMModel(Base):
    __tablename__ = "llm_models"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    provider_id = Column(String(36), ForeignKey('llm_providers.id'), nullable=False)
    model_name = Column(String, nullable=False)
    type = Column(String, nullable=True) # New field
    is_active = Column(Boolean, default=True) # New field
    reasoning = Column(Boolean, default=False) # New field
    role = Column(String, nullable=True) # New field, nullable
    max_tokens = Column(Integer, nullable=True)
    cost_per_token = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    provider = relationship("LLMProvider", backref="models")

class UserLLMPreference(Base):
    __tablename__ = "user_llm_preferences"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    default_model_id = Column(String(36), ForeignKey('llm_models.id'), nullable=True)
    temperature = Column(Float, default=0.7)
    top_p = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="llm_preference", uselist=False)
    default_model = relationship("LLMModel")

class TerminalSession(Base):
    __tablename__ = "terminal_sessions"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    status = Column(String, default="active") # "active", "closed"
    last_command = Column(Text, nullable=True)
    user = relationship("User", backref="terminal_sessions")

class TerminalCommandHistory(Base):
    __tablename__ = "terminal_command_history"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey('terminal_sessions.id'), nullable=False)
    command = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    output = Column(Text, nullable=True) # Truncated output
    session = relationship("TerminalSession", backref="command_history")

class UserGitConfig(Base):
    __tablename__ = "user_git_configs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey('users.id'), nullable=False, unique=True)
    github_pat_encrypted = Column(String, nullable=True)
    github_app_installation_id = Column(Integer, nullable=True) # New column for GitHub App Installation ID
    default_author_name = Column(String, nullable=True)
    default_author_email = Column(String, nullable=True)
    default_repo_url = Column(String, nullable=True)
    default_local_path = Column(String, nullable=True)
    default_branch = Column(String, default="main")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", backref="git_config", uselist=False)

class ArcanaAgent(Base):
    __tablename__ = "arcana_agents"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    name = Column(String, index=True, nullable=False)
    persona = Column(String, default="default")
    mode = Column(String, default="chat")
    objective = Column(Text, nullable=True)
    status = Column(String, default="idle")
    configuration = Column(Text, nullable=True) # Storing as JSON string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", backref="arcana_agents")

class ArcanaAgentJob(Base):
    __tablename__ = "arcana_agent_jobs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String(36), ForeignKey('arcana_agents.id'), nullable=False)
    owner_id = Column(String(36), ForeignKey('users.id'), nullable=False)
    status = Column(String, default="starting") # e.g., starting, planning, coding, testing, awaiting_human_input, completed, failed
    goal = Column(Text, nullable=False)
    message_history = Column(Text, nullable=True) # New: Stores JSON of LLM messages
    original_request = Column(Text, nullable=True) # New: Stores JSON of original AgentExecuteRequest
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ended_at = Column(DateTime, nullable=True)
    final_output = Column(Text, nullable=True)

    # New column for parent-child relationship
    parent_job_id = Column(String(36), ForeignKey("arcana_agent_jobs.id"), nullable=True)

    # Relationships
    agent = relationship("ArcanaAgent", backref="jobs")
    owner = relationship("User", backref="arcana_agent_jobs")
    logs = relationship("ArcanaAgentJobLog", back_populates="job", cascade="all, delete-orphan")

    # New relationships for hierarchical jobs
    parent_job = relationship("ArcanaAgentJob", remote_side=[id], back_populates="child_jobs")
    child_jobs = relationship("ArcanaAgentJob", back_populates="parent_job", cascade="all, delete-orphan")

class ArcanaAgentJobLog(Base):
    __tablename__ = "arcana_agent_job_logs"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    job_id = Column(String(36), ForeignKey('arcana_agent_jobs.id'), nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    log_type = Column(String, nullable=False) # e.g., 'thought', 'command', 'output', 'human_input_needed', 'error'
    content = Column(Text, nullable=False)
    job = relationship("ArcanaAgentJob", back_populates="logs")


class SystemPrompt(Base):
    __tablename__ = "system_prompts"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, nullable=False)
    content = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# --- Database Utility Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_db(db, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user_in_db(db: Session, username: str, hashed_password: str, email: str, verification_token: str, verification_token_expires_at: datetime):
    db_user = User(id=str(uuid.uuid4()), username=username, hashed_password=hashed_password, email=email, verification_token=verification_token, verification_token_expires_at=verification_token_expires_at)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# This function will be called to set up a default user for testing
def get_user_by_username_or_email(db: Session, identifier: str):
    # Try to find by username first
    user = db.query(User).filter(User.username == identifier).first()
    if user:
        return user
    # If not found by username, try by email
    user = db.query(User).filter(User.email == identifier).first()
    return user

def get_permission_by_name(db: Session, name: str):
    return db.query(Permission).filter(Permission.name == name).first()

def create_permission(db: Session, name: str):
    db_permission = Permission(id=str(uuid.uuid4()), name=name)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()

def create_role(db: Session, name: str, permission_names: List[str] = []):
    db_role = get_role_by_name(db, name)
    if db_role:
        return db_role
    
    db_role = Role(id=str(uuid.uuid4()), name=name)
    for perm_name in permission_names:
        permission = get_permission_by_name(db, perm_name)
        if not permission:
            permission = create_permission(db, perm_name)
        db_role.permissions.append(permission)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# This function will be called to set up a default user for testing
def setup_default_user(db, get_password_hash_func):
    default_username = "testuser"
    default_password = "testpassword"
    default_email = "test@example.com"
    
    # Create default permissions if they don't exist
    admin_permission = get_permission_by_name(db, "admin_access") or create_permission(db, "admin_access")
    
    # Create default roles if they don't exist
    admin_role = get_role_by_name(db, "admin") or create_role(db, "admin", ["admin_access"])

    db_user = get_user_from_db(db, default_username)
    if not db_user:
        hashed_password = get_password_hash_func(default_password)
        db_user = User(id=str(uuid.uuid4()), username=default_username, hashed_password=hashed_password, email=default_email, is_verified=True, verification_token=None, verification_token_expires_at=None)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # Assign admin role to default user if not already assigned
    if admin_role not in db_user.roles:
        db_user.roles.append(admin_role)
        db.commit()
        db.refresh(db_user)

    if not get_user_by_email(db, default_email):
        print(f"Default user '{default_username}' created with password '{default_password}'")

def seed_initial_plans(db: Session):
    import json

    plans_to_seed = {
        "Free Trial": {
            "price_monthly": 0, "price_yearly": 0, "max_users": 1, "demo_credits": 100,
            "features": json.dumps([
                "Basic Access to Core Modules",
                "100 Demo Credits for Advanced Modules",
                "Community Forum Support"
            ])
        },
        "Student": {
            "price_monthly": 15000, "price_yearly": 150000, "max_users": 1, "demo_credits": 500,
            "features": json.dumps([
                "Full Access to Core Modules",
                "500 Demo Credits for Advanced Modules",
                "Requires Student Verification",
                "Community Forum Support"
            ])
        },
        "Individual": {
            "price_monthly": 75000, "price_yearly": 750000, "max_users": 1, "demo_credits": 1000,
            "features": json.dumps([
                "Full Access to Core Modules",
                "1000 Demo Credits for Advanced Modules",
                "Standard Email Support"
            ])
        },
        "Professional": {
            "price_monthly": 250000, "price_yearly": 2500000, "max_users": 5, "demo_credits": None,
            "features": json.dumps([
                "Unlimited Access to All Modules",
                "Up to 5 Users in Workspace",
                "Premium Model Access",
                "Priority Email Support"
            ])
        },
        "Enterprise": {
            "price_monthly": -1, "price_yearly": -1, "max_users": -1, "demo_credits": None, # -1 indicates "Custom"
            "features": json.dumps([
                "Unlimited Access & Custom Models",
                "Custom User Seat Count",
                "Custom Admin Configuration",
                "Dedicated Support Manager"
            ])
        }
    }

    for plan_name, details in plans_to_seed.items():
        plan = db.query(Plan).filter(Plan.name == plan_name).first()
        if not plan:
            new_plan = Plan(
                id=str(uuid.uuid4()),
                name=plan_name,
                price_monthly=details["price_monthly"],
                price_yearly=details["price_yearly"],
                max_users=details["max_users"],
                demo_credits=details["demo_credits"],
                features=details["features"]
            )
            db.add(new_plan)
            print(f"Created subscription plan: {plan_name}")
        else: # Update existing plans
            plan.price_monthly = details["price_monthly"]
            plan.price_yearly = details["price_yearly"]
            plan.max_users = details["max_users"]
            plan.demo_credits = details["demo_credits"]
            plan.features = details["features"]
            print(f"Updated subscription plan: {plan_name}")
            
    db.commit()

def populate_initial_llm_data(db: Session):
    # Check for and create default LLM Provider (e.g., OpenRouter)
    openrouter_provider = db.query(LLMProvider).filter(LLMProvider.name == "OpenRouter").first()
    if not openrouter_provider:
        openrouter_provider = LLMProvider(
            id=str(uuid.uuid4()),
            name="OpenRouter",
            api_key_encrypted=encrypt_api_key(""), # API key will be set via dashboard
            base_url="https://openrouter.ai/api/v1",
            enabled=True,
            organization_id=None
        )
        db.add(openrouter_provider)
        db.commit()
        db.refresh(openrouter_provider)
        print("Created default LLM Provider: OpenRouter")

    # Check for and create a default model linked to the provider
    default_model_name = "kwaipilot/kat-coder-pro:free"
    default_model = db.query(LLMModel).filter(LLMModel.model_name == default_model_name).first()
    if not default_model:
        default_model = LLMModel(
            id=str(uuid.uuid4()),
            provider_id=openrouter_provider.id,
            model_name=default_model_name,
            type="chat",
            is_active=True,
            reasoning=True,
            role="general"
        )
        db.add(default_model)
        db.commit()
        db.refresh(default_model)
        print(f"Created default LLM Model: {default_model_name}")

    # Set the new model as the default for 'testuser'
    test_user = db.query(User).filter(User.username == 'testuser').first()
    if test_user:
        user_prefs = db.query(UserLLMPreference).filter(UserLLMPreference.user_id == str(test_user.id)).first()
        if not user_prefs:
            user_prefs = UserLLMPreference(user_id=str(test_user.id))
            db.add(user_prefs)
        
        if user_prefs.default_model_id != default_model.id:
            user_prefs.default_model_id = default_model.id
            db.commit()
            print(f"Set '{default_model_name}' as the default model for 'testuser'.")


    # Create default intent detection system prompt
    intent_prompt_name = "intent_detection_prompt"
    default_intent_prompt = db.query(SystemPrompt).filter(SystemPrompt.name == intent_prompt_name).first()
    if not default_intent_prompt:
        default_intent_prompt_content = """You are an AI intent detection system. Your task is to classify user prompts into one of the following categories:
- 'shell_command': The user wants to execute a command in a terminal or get a shell command.
- 'code_generation': The user wants to generate code, get code examples, or debug code.
- 'file_operation': The user wants to perform operations on files (create, read, write, delete, list, move, etc.).
- 'conversation': The user is engaging in a general conversation, asking questions, or seeking information.
- 'arcana_agent_management': The user is asking to create, list, update, or delete Arcana agents.
- 'unknown': The intent cannot be clearly determined from the provided categories.

Provide your response in a JSON format with the following keys:
- 'intent': The detected intent category.
- 'confidence': A float between 0.0 and 1.0 indicating your confidence in the detection.
- 'reasoning': A brief explanation of why you chose this intent.

Example JSON output:
{"intent": "shell_command", "confidence": 0.95, "reasoning": "The prompt explicitly asks to 'run a command'."}
{"intent": "code_generation", "confidence": 0.88, "reasoning": "The prompt mentions 'Python code' and 'function'."}
{"intent": "conversation", "confidence": 0.70, "reasoning": "The prompt is a general greeting."}
{"intent": "file_operation", "confidence": 0.90, "reasoning": "The prompt asks to 'create a new file'."}
{"intent": "arcana_agent_management", "confidence": 0.92, "reasoning": "The prompt asks to 'list my agents'."}
"""
        db_default_intent_prompt = SystemPrompt(
            id=str(uuid.uuid4()),
            name=intent_prompt_name,
            content=default_intent_prompt_content,
            description="Default system prompt for LLM-based intent detection."
        )
        db.add(db_default_intent_prompt)
        db.commit()
        db.refresh(db_default_intent_prompt)
        print(f"Created default System Prompt: {intent_prompt_name}")