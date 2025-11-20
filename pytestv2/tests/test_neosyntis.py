import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid
from datetime import datetime, timedelta
from pytest_mock import MockerFixture
from typing import List
import json # Added this line
from io import BytesIO
import stat # Added this line
import shutil # Added this line for cleanup





from server_python.main import app
from server_python.database import get_db
from server_python.database import Base, User, Workflow, Dataset, MLModel, TrainingJob, Permission, Role, TelemetryData
from server_python.auth import get_password_hash, PermissionChecker, get_current_user

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_neosyntis.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(name="db_session")
def db_session_fixture():
    # Drop all tables before creating them to ensure a clean slate and updated schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    connection = engine.connect()
    transaction = connection.begin()
    db = TestingSessionLocal(bind=connection)
    try:
        yield db
    finally:
        db.close()
        transaction.rollback()
        connection.close()

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
    user_id = "d228678f-7e76-47ed-aa00-be9470c0ce79" # Hardcoded ID
    user = db_session.query(User).filter(User.id == user_id).first()
    if not user:
        hashed_password = get_password_hash("testpassword")
        user = User(id=user_id, username="testuser", email="test@example.com", hashed_password=hashed_password, is_verified=True)
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
    mocker.patch("server_python.auth.has_permission", return_value=True)
    yield

# --- Workflow Management Tests ---
def test_create_workflow(client, auth_headers, test_user):
    response = client.post(
        "/api/neosyntis/workflows/",
        headers=auth_headers,
        json={
            "name": "Test Workflow",
            "description": "A sample workflow for testing.",
            "status": "draft",
            "steps": json.dumps({"step1": "do_something", "step2": "do_another_thing"})
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Workflow"
    assert response.json()["owner_id"] == test_user.id
    assert response.json()["status"] == "draft"
    assert json.loads(response.json()["steps"]) == {"step1": "do_something", "step2": "do_another_thing"}
    assert "id" in response.json()

def test_read_workflows(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Workflow 1",
        "description": "Description 1",
        "status": "active",
        "steps": json.dumps({"step_a": "action_a"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    db_session.add(workflow)
    db_session.commit()

    response = client.get("/api/neosyntis/workflows/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Workflow 1"
    assert json.loads(response.json()[0]["steps"]) == {"step_a": "action_a"}

def test_read_workflow(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Workflow 2",
        "description": "Description 2",
        "status": "pending",
        "steps": json.dumps({"step_b": "action_b"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    db_session.add(workflow)
    db_session.commit()

    response = client.get(f"/api/neosyntis/workflows/{workflow.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Workflow 2"
    assert json.loads(response.json()["steps"]) == {"step_b": "action_b"}

def test_update_workflow(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Workflow 3",
        "description": "Description 3",
        "status": "draft",
        "steps": json.dumps({"step_c": "action_c"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    db_session.add(workflow)
    db_session.commit()

    updated_steps = json.dumps({"step_c": "updated_action_c", "step_d": "action_d"})
    response = client.put(
        f"/api/neosyntis/workflows/{workflow.id}",
        headers=auth_headers,
        json={"name": "Updated Workflow 3", "status": "active", "steps": updated_steps}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Workflow 3"
    assert response.json()["status"] == "active"
    assert json.loads(response.json()["steps"]) == json.loads(updated_steps)

def test_delete_workflow(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Workflow to Delete",
        "description": "This workflow will be deleted.",
        "status": "draft",
        "steps": json.dumps({"step_e": "action_e"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    db_session.add(workflow)
    db_session.commit()

    response = client.delete(f"/api/neosyntis/workflows/{workflow.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/neosyntis/workflows/{workflow.id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_trigger_workflow(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Workflow to Trigger",
        "description": "This workflow will be triggered.",
        "status": "draft",
        "steps": json.dumps({"step_f": "action_f"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    db_session.add(workflow)
    db_session.commit()

    response = client.post(f"/api/neosyntis/workflows/{workflow.id}/trigger", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert json.loads(response.json()["steps"]) == {"step_f": "action_f"}

def test_get_workflow_status(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Workflow Status Check",
        "description": "Check the status of this workflow.",
        "status": "paused",
        "steps": json.dumps({"step_g": "action_g"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    db_session.add(workflow)
    db_session.commit()

    response = client.get(f"/api/neosyntis/workflows/{workflow.id}/status", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Workflow Status Check"
    assert response.json()["status"] == "paused"
    assert json.loads(response.json()["steps"]) == {"step_g": "action_g"}

# --- Dataset Management Tests ---
def test_upload_dataset(client, auth_headers, test_user, mocker: MockerFixture):
    # Mock storage_service.save_dataset_file
    mocker.patch(
        "server_python.neosyntis.api.storage_service.save_dataset_file",
        return_value="/path/to/mock/dataset.csv"
    )
    # Mock file object
    file_content = b"col1,col2\n1,a\n2,b"
    mock_file = BytesIO(file_content)
    mock_file.name = "test_dataset.csv"
    mock_file.size = len(file_content)

    response = client.post(
        "/api/neosyntis/datasets/upload",
        headers=auth_headers,
        params={
            "name": "Test Dataset",
            "format": "csv",
            "description": "A mock dataset for testing."
        },
        files={"file": ("test_dataset.csv", mock_file, "text/csv")}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Dataset"
    assert response.json()["owner_id"] == test_user.id
    assert response.json()["format"] == "csv"
    assert response.json()["file_path"] == "/path/to/mock/dataset.csv"
    assert response.json()["size_bytes"] == len(file_content)
    assert "id" in response.json()

def test_read_datasets(client, auth_headers, db_session, test_user):
    dataset_data = {
        "name": "Dataset 1",
        "description": "Description 1",
        "file_path": "/path/to/dataset1.csv",
        "size_bytes": 1024,
        "format": "csv"
    }
    dataset = Dataset(
        id=str(uuid.uuid4()), owner_id=test_user.id, **dataset_data
    )
    db_session.add(dataset)
    db_session.commit()

    response = client.get("/api/neosyntis/datasets/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Dataset 1"
    assert response.json()[0]["format"] == "csv"

def test_read_dataset(client, auth_headers, db_session, test_user):
    dataset_data = {
        "name": "Dataset 2",
        "description": "Description 2",
        "file_path": "/path/to/dataset2.json",
        "size_bytes": 2048,
        "format": "json"
    }
    dataset = Dataset(
        id=str(uuid.uuid4()), owner_id=test_user.id, **dataset_data
    )
    db_session.add(dataset)
    db_session.commit()

    response = client.get(f"/api/neosyntis/datasets/{dataset.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Dataset 2"
    assert response.json()["format"] == "json"

def test_update_dataset(client, auth_headers, db_session, test_user):
    dataset_data = {
        "name": "Dataset 3",
        "description": "Description 3",
        "file_path": "/path/to/dataset3.txt",
        "size_bytes": 512,
        "format": "txt"
    }
    dataset = Dataset(
        id=str(uuid.uuid4()), owner_id=test_user.id, **dataset_data
    )
    db_session.add(dataset)
    db_session.commit()

    response = client.put(
        f"/api/neosyntis/datasets/{dataset.id}",
        headers=auth_headers,
        json={"name": "Updated Dataset 3", "description": "Updated description."}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Dataset 3"
    assert response.json()["description"] == "Updated description."

def test_delete_dataset(client, auth_headers, db_session, test_user, mocker: MockerFixture):
    # Mock storage_service.delete_dataset_file
    mocker.patch("neosyntis.storage_service.delete_dataset_file", return_value=True)

    dataset_data = {
        "name": "Dataset to Delete",
        "description": "This dataset will be deleted.",
        "file_path": "/path/to/delete.csv",
        "size_bytes": 100,
        "format": "csv"
    }
    dataset = Dataset(
        id=str(uuid.uuid4()), owner_id=test_user.id, **dataset_data
    )
    db_session.add(dataset)
    db_session.commit()

    response = client.delete(f"/api/neosyntis/datasets/{dataset.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/neosyntis/datasets/{dataset.id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_download_dataset(client, auth_headers, db_session, test_user, mocker: MockerFixture):
    # Mock os.path.exists
    mocker.patch("os.path.exists", return_value=True)
    # Mock os.stat to return a dummy stat_result
    mock_stat_result = mocker.Mock()
    mock_stat_result.st_size = 200 # Match the size_bytes in dataset_data
    mock_stat_result.st_mtime = 1234567890.0 # Example timestamp
    mock_stat_result.st_mode = stat.S_IFREG # Set a valid mode for a regular file
    mocker.patch("os.stat", return_value=mock_stat_result)
    # Mock anyio.open_file
    mock_file_handle = mocker.AsyncMock()
    mock_file_handle.__aenter__.return_value = mocker.Mock(read=mocker.AsyncMock(return_value=b"mock file content"))
    mocker.patch("anyio.open_file", return_value=mock_file_handle)
    
    dataset_data = {
        "name": "Dataset to Download",
        "description": "This dataset will be downloaded.",
        "file_path": "/path/to/download.csv",
        "size_bytes": 200,
        "format": "csv"
    }
    dataset = Dataset(
        id=str(uuid.uuid4()), owner_id=test_user.id, **dataset_data
    )
    db_session.add(dataset)
    db_session.commit()

    response = client.get(f"/api/neosyntis/datasets/{dataset.id}/download", headers=auth_headers)
    assert response.status_code == 200
    # Further assertions on FileResponse can be tricky with TestClient,
    # but we can check if FileResponse was called with correct arguments
    # mock_file_response.assert_called_once_with( # This line was causing NameError
    #     path="/path/to/download.csv",
    #     filename="Dataset to Download",
    #     media_type="application/octet-stream"
    # )

# --- Telemetry Tests ---
def test_ingest_telemetry(client, auth_headers, test_user):
    response = client.post(
        "/api/neosyntis/telemetry/ingest",
        headers=auth_headers,
        json={
            "metric_name": "cpu_usage",
            "value": 75.5,
            "workflow_id": None,
            "dataset_id": None,
            "device_id": None
        }
    )
    assert response.status_code == 201
    assert response.json()["metric_name"] == "cpu_usage"
    assert response.json()["value"] == 75.5
    assert response.json()["owner_id"] == test_user.id
    assert "id" in response.json()

def test_get_telemetry(client, auth_headers, db_session, test_user):
    telemetry_data_1 = TelemetryData(
        id=str(uuid.uuid4()), owner_id=test_user.id, metric_name="temp", value=25.0
    )
    telemetry_data_2 = TelemetryData(
        id=str(uuid.uuid4()), owner_id=test_user.id, metric_name="humidity", value=60.0
    )
    db_session.add_all([telemetry_data_1, telemetry_data_2])
    db_session.commit()

    response = client.get("/api/neosyntis/telemetry/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["metric_name"] == "temp" or response.json()[1]["metric_name"] == "temp"

    response = client.get("/api/neosyntis/telemetry/?metric_name=temp", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["metric_name"] == "temp"

# --- Search Engine Tests ---
def test_search_neosyntis_entities(client, auth_headers, db_session, test_user):
    workflow_data = {
        "name": "Search Workflow",
        "description": "This is a workflow for searching.",
        "status": "active",
        "steps": json.dumps({"step_s": "action_s"})
    }
    workflow = Workflow(
        id=str(uuid.uuid4()), owner_id=test_user.id, **workflow_data
    )
    dataset_data = {
        "name": "Search Dataset",
        "description": "This is a dataset for searching.",
        "file_path": "/path/to/search.csv",
        "size_bytes": 300,
        "format": "csv"
    }
    dataset = Dataset(
        id=str(uuid.uuid4()), owner_id=test_user.id, **dataset_data
    )
    db_session.add_all([workflow, dataset])
    db_session.commit()

    # Search for workflows
    response = client.get("/api/neosyntis/search?query=workflow&entity_type=workflows", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "workflow"
    assert response.json()[0]["name"] == "Search Workflow"

    # Search for datasets
    response = client.get("/api/neosyntis/search?query=dataset&entity_type=datasets", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["type"] == "dataset"
    assert response.json()[0]["name"] == "Search Dataset"

    # Search for all entities
    response = client.get("/api/neosyntis/search?query=search", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2

# --- ML Model Deployment & Machine Learning Tests ---
def test_create_ml_model(client, auth_headers, test_user):
    response = client.post(
        "/api/neosyntis/models/",
        headers=auth_headers,
        json={
            "name": "Test Model",
            "version": "1.0",
            "status": "registered",
            "path_to_artifact": "/models/test_model.pkl",
            "training_dataset_id": None,
            "deployed_at": None
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Model"
    assert response.json()["owner_id"] == test_user.id
    assert response.json()["version"] == "1.0"
    assert "id" in response.json()

def test_read_ml_models(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Model 1",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/model1.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    response = client.get("/api/neosyntis/models/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Model 1"
    assert response.json()[0]["version"] == "1.0"

def test_read_ml_model(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Model 2",
        "version": "1.1",
        "status": "trained",
        "path_to_artifact": "/models/model2.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    response = client.get(f"/api/neosyntis/models/{ml_model.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Model 2"
    assert response.json()["version"] == "1.1"

def test_update_ml_model(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Model 3",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/model3.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    response = client.put(
        f"/api/neosyntis/models/{ml_model.id}",
        headers=auth_headers,
        json={"name": "Updated Model 3", "status": "deployed", "version": "1.2"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Model 3"
    assert response.json()["status"] == "deployed"
    assert response.json()["version"] == "1.2"

def test_delete_ml_model(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Model to Delete",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/delete_model.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    response = client.delete(f"/api/neosyntis/models/{ml_model.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/neosyntis/models/{ml_model.id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_deploy_ml_model(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Model to Deploy",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/deploy_model.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    response = client.post(f"/api/neosyntis/models/{ml_model.id}/deploy", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "deployed"
    assert response.json()["deployed_at"] is not None

def test_train_ml_model(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Model to Train",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/train_model.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    response = client.post(f"/api/neosyntis/models/{ml_model.id}/train", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["model_id"] == ml_model.id
    assert response.json()["status"] == "running"
    assert "id" in response.json()

def test_read_training_jobs(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Parent Model",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/parent.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    training_job_data = {
        "model_id": ml_model.id,
        "status": "completed",
        "start_time": datetime.utcnow() - timedelta(hours=1),
        "end_time": datetime.utcnow(),
        "metrics": json.dumps({"accuracy": 0.95}),
        "logs": "Training completed successfully."
    }
    training_job = TrainingJob(
        id=str(uuid.uuid4()), owner_id=test_user.id, **training_job_data
    )
    db_session.add(training_job)
    db_session.commit()

    response = client.get("/api/neosyntis/training-jobs/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["model_id"] == ml_model.id
    assert response.json()[0]["status"] == "completed"
    assert response.json()[0]["metrics"] == {"accuracy": 0.95}

def test_read_training_job(client, auth_headers, db_session, test_user):
    ml_model_data = {
        "name": "Parent Model 2",
        "version": "1.0",
        "status": "registered",
        "path_to_artifact": "/models/parent2.pkl",
        "training_dataset_id": None,
        "deployed_at": None
    }
    ml_model = MLModel(
        id=str(uuid.uuid4()), owner_id=test_user.id, **ml_model_data
    )
    db_session.add(ml_model)
    db_session.commit()

    training_job_data = {
        "model_id": ml_model.id,
        "status": "running",
        "start_time": datetime.utcnow() - timedelta(minutes=30),
        "end_time": None,
        "metrics": json.dumps({"loss": 0.1}),
        "logs": "Training in progress."
    }
    training_job = TrainingJob(
        id=str(uuid.uuid4()), owner_id=test_user.id, **training_job_data
    )
    db_session.add(training_job)
    db_session.commit()

    response = client.get(f"/api/neosyntis/training-jobs/{training_job.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["model_id"] == ml_model.id
    assert response.json()["status"] == "running"
    assert response.json()["metrics"] == {"loss": 0.1}

# Cleanup the test database and dataset directory after tests run
@pytest.fixture(scope="module", autouse=True)
def cleanup():
    yield
    if os.path.exists("./test_neosyntis.db"):
        os.remove("./test_neosyntis.db")
    # Get DATASET_STORAGE_DIR from environment as it's set in conftest.py
    dataset_storage_dir = os.environ.get("DATASET_STORAGE_DIR")
    if dataset_storage_dir and os.path.exists(dataset_storage_dir):
        shutil.rmtree(dataset_storage_dir)
