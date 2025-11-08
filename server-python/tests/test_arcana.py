import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid
from datetime import datetime, timedelta, timezone
from pytest_mock import MockerFixture
from typing import List, Dict, Any
import json

# Add the server-python directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from main import app, get_db, module_startup_times # Import app and get_db from main
from database import Base, User, Conversation, ChatMessage, ContextMemory, LLMProvider, LLMModel, UserLLMPreference, TerminalSession, TerminalCommandHistory, Permission, Role
from auth import get_password_hash, PermissionChecker, get_current_user

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(name="client")
def client_fixture(db_session):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

@pytest.fixture(name="test_user")
def test_user_fixture(db_session):
    hashed_password = get_password_hash("testpassword")
    user = User(id=str(uuid.uuid4()), username="testuser", email="test@example.com", hashed_password=hashed_password, is_verified=True)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(name="admin_user")
def admin_user_fixture(db_session):
    hashed_password = get_password_hash("adminpassword")
    admin = User(id=str(uuid.uuid4()), username="adminuser", email="admin@example.com", hashed_password=hashed_password, is_verified=True)
    db_session.add(admin) # Add admin first
    db_session.commit() # Commit admin to get an ID
    db_session.refresh(admin) # Refresh admin to ensure it's tracked

    # Create admin_access permission and admin role
    admin_permission = db_session.query(Permission).filter(Permission.name == "admin_access").first()
    if not admin_permission:
        admin_permission = Permission(id=str(uuid.uuid4()), name="admin_access")
        db_session.add(admin_permission)
        db_session.commit()
        db_session.refresh(admin_permission) # Refresh permission after commit

    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(id=str(uuid.uuid4()), name="admin")
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role) # Refresh role after commit
    
    # Establish relationships
    admin_role.permissions.append(admin_permission)
    admin.roles.append(admin_role)

    db_session.commit() # Commit changes to relationships
    db_session.refresh(admin) # Final refresh of admin to load relationships
    return admin

@pytest.fixture(name="auth_headers")
def auth_headers_fixture(client, test_user):
    response = client.post(
        "/api/token",
        data={"username": test_user.username, "password": "testpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture(name="admin_auth_headers")
def admin_auth_headers_fixture(client, admin_user):
    response = client.post(
        "/api/token",
        data={"username": admin_user.username, "password": "adminpassword"}
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def override_admin_permission_checker(admin_user, mocker: MockerFixture):
    # Mock has_permission to always return True for admin_access
    mocker.patch("auth.has_permission", return_value=True)
    yield

# --- Arcana Unit Tests ---
# Test GET /api/arcana/status
def test_get_arcana_status(client, auth_headers, db_session):
    # Ensure module_startup_times is set for arcana
    module_startup_times["arcana"] = datetime.now(timezone.utc) - timedelta(minutes=5)

    response = client.get("/api/arcana/status", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "online"
    assert "uptime" in response.json()
    assert response.json()["activeChats"] == 12 # Hardcoded in main.py
    assert response.json()["messagesProcessed"] == 1543 # Hardcoded in main.py
    assert response.json()["avgResponseTime"] == "1.2s" # Hardcoded in main.py

# Test POST /api/arcana/start-chat
def test_start_arcana_chat(client, auth_headers):
    # Ensure module_startup_times is set for arcana
    module_startup_times["arcana"] = datetime.now(timezone.utc) - timedelta(minutes=5)

    response = client.post("/api/arcana/start-chat", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Arcana Chat started successfully!"
    # Verify cache invalidation (optional, as cache is in-memory and not directly accessible from test)

# Test POST /api/arcana/context-memory (create_or_update_context_memory)
def test_create_context_memory(client, auth_headers, test_user):
    context_data = {
        "key": "favorite_color",
        "value": json.dumps({"color": "blue"})
    }
    response = client.post(
        "/api/arcana/context-memory",
        headers=auth_headers,
        json=context_data
    )
    assert response.status_code == 200
    assert response.json()["key"] == "favorite_color"
    assert json.loads(response.json()["value"]) == {"color": "blue"}
    assert response.json()["user_id"] == str(test_user.id)
    assert "id" in response.json()

    # Test update context memory
    updated_context_data = {
        "key": "favorite_color",
        "value": json.dumps({"color": "green"})
    }
    response = client.post(
        "/api/arcana/context-memory",
        headers=auth_headers,
        json=updated_context_data
    )
    assert response.status_code == 200
    assert response.json()["key"] == "favorite_color"
    assert json.loads(response.json()["value"]) == {"color": "green"}
    assert response.json()["user_id"] == str(test_user.id)

# Test GET /api/arcana/context-memory/{key}
def test_get_context_memory_by_key(client, auth_headers, db_session, test_user):
    context_memory = ContextMemory(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        key="favorite_food",
        value=json.dumps({"food": "pizza"})
    )
    db_session.add(context_memory)
    db_session.commit()

    response = client.get(f"/api/arcana/context-memory/{context_memory.key}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["key"] == "favorite_food"
    assert json.loads(response.json()["value"]) == {"food": "pizza"}
    assert response.json()["user_id"] == str(test_user.id)

# Test GET /api/arcana/context-memory
def test_get_all_context_memory(client, auth_headers, db_session, test_user):
    context_memory_1 = ContextMemory(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        key="setting_1",
        value=json.dumps({"theme": "dark"})
    )
    context_memory_2 = ContextMemory(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        key="setting_2",
        value=json.dumps({"notifications": True})
    )
    db_session.add_all([context_memory_1, context_memory_2])
    db_session.commit()

    response = client.get("/api/arcana/context-memory", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["key"] == "setting_1" or response.json()[1]["key"] == "setting_1"
    assert response.json()[0]["user_id"] == str(test_user.id) or response.json()[1]["user_id"] == str(test_user.id)

# Test DELETE /api/arcana/context-memory/{key}
def test_delete_context_memory_by_key(client, auth_headers, db_session, test_user):
    context_memory = ContextMemory(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        key="temp_setting",
        value=json.dumps({"temp": 25})
    )
    db_session.add(context_memory)
    db_session.commit()

    response = client.delete(f"/api/arcana/context-memory/{context_memory.key}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Context memory deleted successfully"

    get_response = client.get(f"/api/arcana/context-memory/{context_memory.key}", headers=auth_headers)
    assert get_response.status_code == 404

# Test GET /api/arcana/llm/preferences
def test_get_user_llm_preferences(client, auth_headers, db_session, test_user):
    # Test default preferences creation
    response = client.get("/api/arcana/llm/preferences", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["user_id"] == str(test_user.id)
    assert response.json()["temperature"] == 0.7
    assert response.json()["top_p"] == 1.0
    assert "id" in response.json()

# Test PUT /api/arcana/llm/preferences
def test_update_user_llm_preferences(client, auth_headers, db_session, test_user):
    # Ensure default preferences exist
    client.get("/api/arcana/llm/preferences", headers=auth_headers)

    # Create a dummy LLMProvider for default_model_id
    llm_provider = LLMProvider(
        id=str(uuid.uuid4()),
        name="Test Provider",
        base_url="http://test.com",
        api_key_encrypted="dummy_key"
    )
    db_session.add(llm_provider)
    db_session.commit()

    llm_model = LLMModel(
        id=str(uuid.uuid4()),
        provider_id=str(llm_provider.id), # Link to the dummy provider
        model_name="test-model",
        max_tokens=1000,
        cost_per_token=0.001
    )
    db_session.add(llm_model)
    db_session.commit()

    update_data = {
        "default_model_id": str(llm_model.id),
        "temperature": 0.5,
        "top_p": 0.8
    }
    response = client.put(
        "/api/arcana/llm/preferences",
        headers=auth_headers,
        json=update_data
    )
    assert response.status_code == 200
    assert response.json()["user_id"] == str(test_user.id)
    assert response.json()["default_model_id"] == str(llm_model.id)
    assert response.json()["temperature"] == 0.5
    assert response.json()["top_p"] == 0.8

# Test GET /api/arcana/terminal/sessions
def test_list_terminal_sessions(client, auth_headers, db_session, test_user):
    session_1 = TerminalSession(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        status="active",
        started_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    session_2 = TerminalSession(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        status="closed",
        started_at=datetime.now(timezone.utc) - timedelta(minutes=30),
        ended_at=datetime.now(timezone.utc) - timedelta(minutes=10)
    )
    db_session.add_all([session_1, session_2])
    db_session.commit()

    response = client.get("/api/arcana/terminal/sessions", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["user_id"] == str(test_user.id) or response.json()[1]["user_id"] == str(test_user.id)

# Test GET /api/arcana/terminal/sessions/{session_id}/history
def test_get_terminal_session_history(client, auth_headers, db_session, test_user):
    session = TerminalSession(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        status="active",
        started_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(session)
    db_session.commit()

    command_1 = TerminalCommandHistory(
        id=str(uuid.uuid4()),
        session_id=str(session.id),
        command="ls -l",
        output="total 0",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    command_2 = TerminalCommandHistory(
        id=str(uuid.uuid4()),
        session_id=str(session.id),
        command="pwd",
        output="/home/user",
        timestamp=datetime.now(timezone.utc) - timedelta(minutes=4)
    )
    db_session.add_all([command_1, command_2])
    db_session.commit()

    response = client.get(f"/api/arcana/terminal/sessions/{session.id}/history", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["session_id"] == str(session.id) or response.json()[1]["session_id"] == str(session.id)
    assert response.json()[0]["command"] == "ls -l" or response.json()[1]["command"] == "ls -l"

# Test POST /api/arcana/terminal/sessions/{session_id}/close
def test_close_terminal_session(client, auth_headers, db_session, test_user):
    session = TerminalSession(
        id=str(uuid.uuid4()),
        user_id=str(test_user.id),
        status="active",
        started_at=datetime.now(timezone.utc) - timedelta(hours=1)
    )
    db_session.add(session)
    db_session.commit()

    response = client.post(f"/api/arcana/terminal/sessions/{session.id}/close", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Terminal session closed successfully"

    closed_session = db_session.query(TerminalSession).filter(TerminalSession.id == str(session.id)).first()
    assert closed_session.status == "closed"
    assert closed_session.ended_at is not None
