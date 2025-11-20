import sys
import os
import shutil
import uuid
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from server_python.main import app 
from server_python.database import Base, get_db, User
from server_python.auth import get_current_user


# --- Test Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_arcana.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session", scope="function")
def db_session_fixture():
    Base.metadata.drop_all(bind=engine) # Drop all tables
    Base.metadata.create_all(bind=engine) # Create all tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(name="client")
def client_fixture(db_session):
    # Override get_db to use the fixture's session
    app.dependency_overrides[get_db] = lambda: db_session
    # Override get_current_user to return a mock user that exists in the current session
    mock_user = User(id=str(uuid.uuid4()), email="test@example.com", username="testuser", is_active=True)
    db_session.add(mock_user) # Add mock user to the session
    db_session.commit() # Commit the mock user to the test database
    db_session.refresh(mock_user)

    app.dependency_overrides[get_current_user] = lambda: mock_user

    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

# --- Tests ---

# This test should also take the client fixture
def test_create_and_manage_arcana_agent(client: TestClient, db_session: Session): # Removed db_session argument from function
    # Test Create
    response = client.post(
        "/api/arcana/agents/",
        json={"name": "Test Agent", "persona": "tester", "mode": "test_mode"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Agent"
    assert "id" in data
    agent_id = data["id"]

    # Test Read
    get_response = client.get(f"/api/arcana/agents/{agent_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Test Agent"

    # Test Update
    update_response = client.put(
        f"/api/arcana/agents/{agent_id}",
        json={"name": "Updated Test Agent", "status": "running"}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Test Agent"
    assert update_response.json()["status"] == "running"

    # Test Delete
    delete_response = client.delete(f"/api/arcana/agents/{agent_id}")
    assert delete_response.status_code == 204

    # Verify Delete
    get_after_delete_response = client.get(f"/api/arcana/agents/{agent_id}")
    assert get_after_delete_response.status_code == 404

def test_read_arcana_agents(client: TestClient, db_session: Session): # Removed db_session argument from function
    response = client.get("/api/arcana/agents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Cleanup the test database and dataset directory after tests run
@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    if os.path.exists("./test_arcana.db"):
        os.remove("./test_arcana.db")
    # Get DATASET_STORAGE_DIR from environment as it's set in conftest.py
    dataset_storage_dir = os.environ.get("DATASET_STORAGE_DIR")
    if dataset_storage_dir and os.path.exists(dataset_storage_dir):
        shutil.rmtree(dataset_storage_dir)