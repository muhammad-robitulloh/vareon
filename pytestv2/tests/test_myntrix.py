import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid
from datetime import datetime, timedelta
from pytest_mock import MockerFixture





from server_python.main import app
from server_python.database import get_db
from server_python.database import Base, User, Agent, Device, Job, ScheduledTask, TaskRun, Permission, Role
from server_python.auth import get_password_hash, PermissionChecker, get_current_user

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_myntrix.db"

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
    db_session.add(admin)
    
    # Create admin_access permission and admin role
    admin_permission = db_session.query(Permission).filter(Permission.name == "admin_access").first()
    if not admin_permission:
        admin_permission = Permission(id=str(uuid.uuid4()), name="admin_access")
        db_session.add(admin_permission)
        db_session.commit()
        db_session.refresh(admin_permission)

    admin_role = db_session.query(Role).filter(Role.name == "admin").first()
    if not admin_role:
        admin_role = Role(id=str(uuid.uuid4()), name="admin")
        db_session.add(admin_role)
        db_session.commit()
        db_session.refresh(admin_role)
    
    admin_role.permissions.append(admin_permission)
    admin.roles.append(admin_role)

    db_session.commit()
    db_session.refresh(admin)
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

### Tests for Agent Management ###

def test_create_agent(client, auth_headers, test_user):
    response = client.post(
        "/api/myntrix/agents/",
        headers=auth_headers,
        json={
            "name": "TestAgent",
            "type": "LLM",
            "status": "offline",
            "health": 100,
            "configuration": {"model": "gpt-3.5"}
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "TestAgent"
    assert response.json()["owner_id"] == test_user.id

def test_read_agents(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent1", type="Sensor",
        status="running", health=90, configuration='{"sensor_type": "temp"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.get("/api/myntrix/agents/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Agent1"

def test_read_agent(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent2", type="Actuator",
        status="stopped", health=100, configuration='{"action": "move"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.get(f"/api/myntrix/agents/{agent.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Agent2"

def test_update_agent(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent3", type="LLM",
        status="offline", health=100, configuration='{"model": "gpt-4"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.put(
        f"/api/myntrix/agents/{agent.id}",
        headers=auth_headers,
        json={"name": "UpdatedAgent3", "status": "running", "health": 80}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedAgent3"
    assert response.json()["status"] == "running"

def test_start_agent(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent4", type="LLM",
        status="offline", health=100, configuration='{"model": "claude"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.post(f"/api/myntrix/agents/{agent.id}/start", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_stop_agent(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent5", type="LLM",
        status="running", health=100, configuration='{"model": "llama"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.post(f"/api/myntrix/agents/{agent.id}/stop", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "stopped"

def test_restart_agent(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent6", type="LLM",
        status="stopped", health=100, configuration='{"model": "falcon"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.post(f"/api/myntrix/agents/{agent.id}/restart", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "restarting" # Placeholder status

def test_delete_agent(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Agent7", type="LLM",
        status="offline", health=100, configuration='{"model": "mistral"}'
    )
    db_session.add(agent)
    db_session.commit()

    response = client.delete(f"/api/myntrix/agents/{agent.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/myntrix/agents/{agent.id}", headers=auth_headers)
    assert get_response.status_code == 404

### Tests for Device Control ###

def test_create_device(client, auth_headers, test_user):
    response = client.post(
        "/api/myntrix/devices/",
        headers=auth_headers,
        json={
            "name": "TestDevice",
            "type": "Sensor",
            "connection_string": "/dev/ttyUSB0",
            "status": "disconnected",
            "firmware_version": "1.0.0",
            "configuration": {"baud_rate": 9600}
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "TestDevice"
    assert response.json()["owner_id"] == test_user.id

def test_read_devices(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device1", type="Actuator",
        connection_string="192.168.1.100", status="connected", firmware_version="1.1.0"
    )
    db_session.add(device)
    db_session.commit()

    response = client.get("/api/myntrix/devices/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Device1"

def test_read_device(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device2", type="Sensor",
        connection_string="/dev/ttyACM0", status="disconnected", firmware_version="1.0.1"
    )
    db_session.add(device)
    db_session.commit()

    response = client.get(f"/api/myntrix/devices/{device.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "Device2"

def test_update_device(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device3", type="Actuator",
        connection_string="192.168.1.101", status="connected", firmware_version="1.2.0"
    )
    db_session.add(device)
    db_session.commit()

    response = client.put(
        f"/api/myntrix/devices/{device.id}",
        headers=auth_headers,
        json={"name": "UpdatedDevice3", "status": "disconnected"}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedDevice3"
    assert response.json()["status"] == "disconnected"

def test_delete_device(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device4", type="Sensor",
        connection_string="/dev/ttyUSB1", status="connected", firmware_version="1.0.2"
    )
    db_session.add(device)
    db_session.commit()

    response = client.delete(f"/api/myntrix/devices/{device.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/myntrix/devices/{device.id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_connect_device(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device5", type="Actuator",
        connection_string="192.168.1.102", status="disconnected", firmware_version="1.3.0"
    )
    db_session.add(device)
    db_session.commit()

    response = client.post(f"/api/myntrix/devices/{device.id}/connect", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "connected"

def test_disconnect_device(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device6", type="Sensor",
        connection_string="/dev/ttyUSB2", status="connected", firmware_version="1.0.3"
    )
    db_session.add(device)
    db_session.commit()

    response = client.post(f"/api/myntrix/devices/{device.id}/disconnect", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["status"] == "disconnected"

def test_send_device_command(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device7", type="Actuator",
        connection_string="192.168.1.103", status="connected", firmware_version="1.4.0"
    )
    db_session.add(device)
    db_session.commit()

    response = client.post(
        f"/api/myntrix/devices/{device.id}/command",
        headers=auth_headers,
        json={"command": "G0 X10 Y10"}
    )
    assert response.status_code == 200
    assert "message" in response.json()

def test_upload_file_to_device(client, auth_headers, db_session, test_user):
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Device8", type="Controller",
        connection_string="usb-port", status="connected", firmware_version="2.0.0"
    )
    db_session.add(device)
    db_session.commit()

    # Create a dummy file for upload
    file_content = b"This is a test file content."
    files = {"file": ("test_file.txt", file_content, "text/plain")}

    response = client.post(
        f"/api/myntrix/devices/{device.id}/upload",
        headers=auth_headers,
        files=files
    )
    assert response.status_code == 200
    assert "message" in response.json()
    assert "test_file.txt" in response.json()["message"]

### Tests for Resource Monitoring ###

def test_get_system_metrics(client, auth_headers, mocker: MockerFixture):
    mocker.patch("psutil.cpu_percent", return_value=25.5)
    mocker.patch("psutil.virtual_memory", return_value=mocker.Mock(percent=50.0, total=1000000000, available=500000000))
    response = client.get("/api/myntrix/system-metrics", headers=auth_headers)
    assert response.status_code == 200
    assert "cpu_percent" in response.json()
    assert "memory_percent" in response.json()

def test_read_jobs(client, auth_headers, db_session, test_user):
    job = Job(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="Job1", type="Training",
        status="running", progress=50, logs="Starting training..."
    )
    db_session.add(job)
    db_session.commit()

    response = client.get("/api/myntrix/jobs/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "Job1"

### Tests for Task Scheduling ###

def test_create_scheduled_task(client, auth_headers, test_user):
    response = client.post(
        "/api/myntrix/tasks/",
        headers=auth_headers,
        json={
            "name": "DailyBackup",
            "schedule": "0 0 * * *",
            "action": {"type": "script", "path": "/scripts/backup.sh"},
            "enabled": True
        }
    )
    assert response.status_code == 201
    assert response.json()["name"] == "DailyBackup"
    assert response.json()["owner_id"] == test_user.id

def test_read_scheduled_tasks(client, auth_headers, db_session, test_user):
    task = ScheduledTask(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="HourlyReport",
        schedule="0 * * * *", action='{"type": "report"}', enabled=True
    )
    db_session.add(task)
    db_session.commit()

    response = client.get("/api/myntrix/tasks/", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert response.json()[0]["name"] == "HourlyReport"

def test_read_scheduled_task(client, auth_headers, db_session, test_user):
    task = ScheduledTask(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="WeeklyCleanup",
        schedule="0 0 * * 0", action='{"type": "cleanup"}', enabled=True
    )
    db_session.add(task)
    db_session.commit()

    response = client.get(f"/api/myntrix/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["name"] == "WeeklyCleanup"

def test_update_scheduled_task(client, auth_headers, db_session, test_user):
    task = ScheduledTask(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="MonthlySync",
        schedule="0 0 1 * *", action='{"type": "sync"}', enabled=True
    )
    db_session.add(task)
    db_session.commit()

    response = client.put(
        f"/api/myntrix/tasks/{task.id}",
        headers=auth_headers,
        json={"name": "UpdatedMonthlySync", "enabled": False}
    )
    assert response.status_code == 200
    assert response.json()["name"] == "UpdatedMonthlySync"
    assert response.json()["enabled"] == False

def test_delete_scheduled_task(client, auth_headers, db_session, test_user):
    task = ScheduledTask(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="DailyCheck",
        schedule="0 1 * * *", action='{"type": "check"}', enabled=True
    )
    db_session.add(task)
    db_session.commit()

    response = client.delete(f"/api/myntrix/tasks/{task.id}", headers=auth_headers)
    assert response.status_code == 204

    get_response = client.get(f"/api/myntrix/tasks/{task.id}", headers=auth_headers)
    assert get_response.status_code == 404

def test_run_scheduled_task(client, auth_headers, db_session, test_user):
    task = ScheduledTask(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="ManualRun",
        schedule="0 0 * * *", action='{"type": "manual"}', enabled=True
    )
    db_session.add(task)
    db_session.commit()

    response = client.post(f"/api/myntrix/tasks/{task.id}/run", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["task_id"] == task.id
    assert response.json()["status"] == "completed"

def test_get_task_history(client, auth_headers, db_session, test_user):
    task = ScheduledTask(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="HistoryTask",
        schedule="0 0 * * *", action='{"type": "history"}', enabled=True
    )
    db_session.add(task)
    db_session.commit()

    run1 = TaskRun(id=str(uuid.uuid4()), task_id=task.id, status="success", start_time=datetime.utcnow() - timedelta(hours=1))
    run2 = TaskRun(id=str(uuid.uuid4()), task_id=task.id, status="failed", start_time=datetime.utcnow())
    db_session.add_all([run1, run2])
    db_session.commit()

    response = client.get(f"/api/myntrix/tasks/history/{task.id}", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["status"] == "success" or response.json()[1]["status"] == "success"

### Tests for 3D Visualization ###

def test_get_visualization_data(client, auth_headers, db_session, test_user):
    agent = Agent(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="VisAgent", type="LLM",
        status="running", health=95, configuration='{"model": "visual"}'
    )
    device = Device(
        id=str(uuid.uuid4()), owner_id=test_user.id, name="VisDevice", type="Sensor",
        connection_string="virtual", status="connected", firmware_version="1.0.0"
    )
    db_session.add_all([agent, device])
    db_session.commit()

    response = client.get("/api/myntrix/visualization-data", headers=auth_headers)
    assert response.status_code == 200
    assert "agents" in response.json()
    assert "devices" in response.json()
    assert len(response.json()["agents"]) > 0
    assert len(response.json()["devices"]) > 0
    assert response.json()["agents"][0]["name"] == "VisAgent"
    assert response.json()["devices"][0]["name"] == "VisDevice"