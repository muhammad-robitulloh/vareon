import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from main import app, get_db
from server_python.database import Base

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


def test_read_main(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

# Test user registration
def test_register_user(client):
    response = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"
    assert response.json()["email"] == "test@example.com"


# Test duplicate user registration
def test_register_duplicate_user(client):
    client.post(
        "/api/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    response = client.post(
        "/api/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"


# Test user login
def test_login_for_access_token(client):
    client.post(
        "/api/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword",
        },
    )
    response = client.post(
        "/api/token",
        data={
            "username": "testuser",
            "password": "testpassword",
        },
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


# Test quick action: Open Neosyntis Lab
def test_open_neosyntis_lab(client):
    response = client.post("/api/neosyntis/open-lab")
    assert response.status_code == 200
    assert response.json() == {"message": "Neosyntis Lab opened successfully!"}


# Test quick action: Start Arcana Chat
def test_start_arcana_chat(client):
    response = client.post("/api/arcana/start-chat")
    assert response.status_code == 200
    assert response.json() == {"message": "Arcana Chat started successfully!"}


# Test quick action: Deploy Myntrix Model
def test_deploy_myntrix_model(client):
    response = client.post("/api/myntrix/deploy-model")
    assert response.status_code == 200
    assert response.json() == {"message": "Model deployed successfully!"}


# Test quick action: Manage Myntrix Agents
def test_manage_myntrix_agents(client):
    response = client.post("/api/myntrix/manage-agents")
    assert response.status_code == 200
    assert response.json() == {"message": "Agents managed successfully!"}


# Test agent listing
def test_list_myntrix_agents(client):
    response = client.get("/api/myntrix/agents")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "name" in response.json()[0]


# Test hardware listing
def test_list_myntrix_hardware(client):
    response = client.get("/api/myntrix/hardware")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "name" in response.json()[0]


# Test hardware status update
def test_update_myntrix_hardware_status(client):
    device_id = "device-1"
    response = client.post(
        f"/api/myntrix/hardware/{device_id}/status", json={"status": "disconnected"}
    )
    assert response.status_code == 200
    assert response.json() == {"message": f"Device {device_id} status updated to disconnected"}


# Test workflow listing
def test_list_neosyntis_workflows(client):
    response = client.get("/api/neosyntis/workflows")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "name" in response.json()[0]


# Test workflow trigger
def test_trigger_neosyntis_workflow(client):
    workflow_id = "workflow-1"
    response = client.post(f"/api/neosyntis/workflows/{workflow_id}/trigger")
    assert response.status_code == 200
    assert response.json() == {"message": f"Workflow {workflow_id} triggered successfully!"}


# Test workflow status
def test_get_neosyntis_workflow_status(client):
    workflow_id = "workflow-1"
    # First trigger to set status
    client.post(f"/api/neosyntis/workflows/{workflow_id}/trigger")
    response = client.get(f"/api/neosyntis/workflows/{workflow_id}/status")
    assert response.status_code == 200
    assert response.json() == {"status": "running"}


# Test dataset listing
def test_list_neosyntis_datasets(client):
    response = client.get("/api/neosyntis/datasets")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "name" in response.json()[0]


# Test dataset upload
def test_upload_neosyntis_dataset(client):
    response = client.post(
        "/api/neosyntis/datasets/upload",
        json={
            "name": "New Test Dataset",
            "size_mb": 50.0,
            "format": "json",
        },
    )
    assert response.status_code == 200
    assert "dataset_id" in response.json()
    assert response.json()["message"] == "Dataset {dataset_id} uploaded successfully!".format(dataset_id=response.json()["dataset_id"])


# Test dataset download
def test_download_neosyntis_dataset(client):
    # First upload a dataset to ensure it exists
    upload_response = client.post(
        "/api/neosyntis/datasets/upload",
        json={
            "name": "Downloadable Dataset",
            "size_mb": 20.0,
            "format": "txt",
        },
    )
    dataset_id = upload_response.json()["dataset_id"]

    response = client.get(f"/api/neosyntis/datasets/{dataset_id}/download")
    assert response.status_code == 200
    assert response.json() == {"message": f"Dataset {dataset_id} downloaded successfully!", "dataset_name": "Downloadable Dataset"}


# Test routing rule listing
def test_list_cognisys_routing_rules(client):
    response = client.get("/api/cognisys/routing-rules")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert "id" in response.json()[0]
    assert "name" in response.json()[0]


# Test create routing rule
def test_create_cognisys_routing_rule(client):
    initial_rules_count = len(client.get("/api/cognisys/routing-rules").json())
    response = client.post(
        "/api/cognisys/routing-rules",
        json={
            "name": "New Rule",
            "condition": "user.country == 'CA'",
            "target_model": "gpt-3.5",
            "priority": 5,
        },
    )
    assert response.status_code == 200
    assert response.json()["name"] == "New Rule"
    assert len(client.get("/api/cognisys/routing-rules").json()) == initial_rules_count + 1


# Test update routing rule
def test_update_cognisys_routing_rule(client):
    # Create a rule first
    create_response = client.post(
        "/api/cognisys/routing-rules",
        json={
            "name": "Rule to Update",
            "condition": "user.age > 60",
            "target_model": "old_model",
            "priority": 2,
        },
    )
    rule_id = create_response.json()["id"]

    update_response = client.put(
        f"/api/cognisys/routing-rules/{rule_id}",
        json={
            "name": "Updated Rule",
            "condition": "user.age < 18",
            "target_model": "new_model",
            "priority": 8,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Rule"
    assert update_response.json()["target_model"] == "new_model"


# Test delete routing rule
def test_delete_cognisys_routing_rule(client):
    # Create a rule first
    create_response = client.post(
        "/api/cognisys/routing-rules",
        json={
            "name": "Rule to Delete",
            "condition": "always true",
            "target_model": "any",
            "priority": 1,
        },
    )
    rule_id = create_response.json()["id"]

    initial_rules_count = len(client.get("/api/cognisys/routing-rules").json())
    delete_response = client.delete(f"/api/cognisys/routing-rules/{rule_id}")

    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": f"Routing rule {rule_id} deleted successfully!"}
    assert len(client.get("/api/cognisys/routing-rules").json()) == initial_rules_count - 1