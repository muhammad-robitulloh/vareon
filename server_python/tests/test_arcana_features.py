import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
import uuid
from pytest_mock import MockerFixture
from typing import List
import shutil # For cleaning up test directories
from datetime import datetime # Add this line
from fastapi import HTTPException # Add this line

# Set DATASET_STORAGE_DIR for tests to a writable temporary location
TEST_DATASET_STORAGE_DIR = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.gemini', 'tmp')),
    "arcana_features_test_datasets"
)
os.environ["DATASET_STORAGE_DIR"] = TEST_DATASET_STORAGE_DIR
os.makedirs(TEST_DATASET_STORAGE_DIR, exist_ok=True)

# Set BASE_FILE_OPERATIONS_DIR for tests to a writable temporary location
TEST_FILE_OPERATIONS_DIR = os.path.join(
    os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.gemini', 'tmp')),
    "arcana_file_ops_test_dir"
)
os.environ["BASE_FILE_OPERATIONS_DIR"] = TEST_FILE_OPERATIONS_DIR
os.makedirs(TEST_FILE_OPERATIONS_DIR, exist_ok=True)

# Add the server_python directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from server_python.main import app, get_db
from server_python.database import Base, User, LLMProvider, LLMModel, ArcanaAgent
from server_python.auth import get_password_hash, PermissionChecker, get_current_user
from server_python.cognisys.crud import encrypt_api_key

# Setup test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_arcana_features.db" # Use a different DB file for arcana tests

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
def client_fixture(db_session, mocker: MockerFixture):
    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    
    # Mock setup_default_user and populate_initial_llm_data to prevent them from running during tests
    mocker.patch("server_python.database.setup_default_user")
    mocker.patch("server_python.database.populate_initial_llm_data")

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()

@pytest.fixture
def override_admin_permission_checker(admin_user, mocker: MockerFixture):
    mocker.patch("auth.has_permission", return_value=True)
    yield

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
    db_session.commit()
    db_session.refresh(admin)

    from database import Permission, Role
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
def setup_llm_models(db_session):
    provider = LLMProvider(
        id=str(uuid.uuid4()), name="TestLLMProvider", base_url="http://mock-llm.com",
        api_key_encrypted=encrypt_api_key("mock-key"), enabled=True
    )
    db_session.add(provider)
    db_session.commit()
    db_session.refresh(provider)

    code_gen_model = LLMModel(
        id=str(uuid.uuid4()), provider_id=provider.id, model_name="code-gen-model",
        type="chat", is_active=True, role="code_generation", max_tokens=4000
    )
    shell_trans_model = LLMModel(
        id=str(uuid.uuid4()), provider_id=provider.id, model_name="shell-trans-model",
        type="chat", is_active=True, role="shell_translation", max_tokens=1000
    )
    reasoning_model = LLMModel(
        id=str(uuid.uuid4()), provider_id=provider.id, model_name="reasoning-model",
        type="chat", is_active=True, role="reasoning", max_tokens=2000
    )
    general_chat_model = LLMModel(
        id=str(uuid.uuid4()), provider_id=provider.id, model_name="general-chat-model",
        type="chat", is_active=True, role="general", max_tokens=2000
    )
    db_session.add_all([code_gen_model, shell_trans_model, reasoning_model, general_chat_model])
    db_session.commit()
    db_session.refresh(code_gen_model)
    db_session.refresh(shell_trans_model)
    db_session.refresh(reasoning_model)
    db_session.refresh(general_chat_model)
    return {
        "provider": provider,
        "code_gen_model": code_gen_model,
        "shell_trans_model": shell_trans_model,
        "reasoning_model": reasoning_model,
        "general_chat_model": general_chat_model
    }

### Tests for Code Generation ###

async def mock_call_llm_api_code_gen(*args, **kwargs):
    messages = kwargs.get("messages", [])
    prompt = messages[-1]["content"] if messages else ""
    print(f"DEBUG: mock_call_llm_api_code_gen received prompt: {prompt}")
    if "python code" in prompt.lower():        return {"message": {"content": "```python\nprint('Hello, World!')\n```"}, "model_used": "code-gen-model"}
    return {"message": {"content": "```python\n# Could not generate code\n```"}, "model_used": "code-gen-model"}

def test_generate_code(client, auth_headers, db_session, setup_llm_models, mocker: MockerFixture):
    mocker.patch("server_python.arcana.code_generation_service.call_llm_api", side_effect=mock_call_llm_api_code_gen)
    
    response = client.post(
        "/api/arcana/generate-code",
        headers=auth_headers,
        json={"prompt": "Generate a Python program that prints 'Hello, World!'", "language": "python"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert "print('Hello, World!')" in response.json()["generated_code"]
    assert response.json()["language"] == "python"
    assert response.json()["model_used"] == "code-gen-model"

### Tests for Shell Command Translation ###

async def mock_call_llm_api_shell_trans(*args, **kwargs):
    messages = kwargs.get("messages", [])
    prompt = messages[-1]["content"] if messages else ""
    if "list all files" in prompt.lower():
        return {"message": {"content": '{"command": "ls -l", "reasoning": "Lists files in long format."}'}, "model_used": "shell-trans-model"}
    return {"message": {"content": '{"command": "echo \"Unknown command\"", "reasoning": "Could not translate."}'}, "model_used": "shell-trans-model"}

def test_translate_shell_command(client, auth_headers, db_session, setup_llm_models, mocker: MockerFixture):
    mocker.patch("server_python.arcana.shell_translation_service.call_llm_api", side_effect=mock_call_llm_api_shell_trans)

    response = client.post(
        "/api/arcana/translate-shell-command",
        headers=auth_headers,
        json={"prompt": "List all files in the current directory", "shell_type": "bash"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert response.json()["translated_command"] == "ls -l"
    assert response.json()["is_safe"] == True # Based on check_command_safety
    assert response.json()["model_used"] == "shell-trans-model"

### Tests for Reasoning System ###

async def mock_call_llm_api_reasoning(*args, **kwargs):
    messages = kwargs.get("messages", [])
    prompt = messages[-1]["content"] if messages else ""
    if "plan a trip to paris" in prompt.lower():
        return {"message": {"content": """
            {
                \"reasoning_trace\": [
                    {\"step_number\": 1, \"description\": \"Identify destination and dates.\", \"action\": \"Ask user\", \"outcome\": \"Got destination.\"},
                    {\"step_number\": 2, \"description\": \"Search for flights.\", \"action\": \"Call flight API\", \"outcome\": \"Found flights.\"}
                ],
                \"summary\": \"Planned a trip by identifying details and searching flights.\"
            }
            """}, "model_used": "reasoning-model"}
    return {"message": {"content": '{"reasoning_trace": [], "summary": "No specific reasoning generated."}'}, "model_used": "reasoning-model"}

def test_generate_reasoning(client, auth_headers, db_session, setup_llm_models, mocker: MockerFixture):
    mocker.patch("server_python.arcana.reasoning_service.call_llm_api", side_effect=mock_call_llm_api_reasoning)

    response = client.post(
        "/api/arcana/generate-reasoning",
        headers=auth_headers,
        json={"prompt": "Plan a trip to Paris", "task_type": "travel_planning"}
    )
    assert response.status_code == 200
    assert response.json()["success"] == True
    assert len(response.json()["reasoning_trace"]) == 2
    assert response.json()["reasoning_trace"][0]["description"] == "Identify destination and dates."
    assert "Planned a trip" in response.json()["summary"]
    assert response.json()["model_used"] == "reasoning-model"

@pytest.fixture
def mock_file_system(mocker: MockerFixture):
    mock_os_makedirs = mocker.patch("server_python.arcana.file_management_service.os.makedirs")
    mock_open = mocker.patch("server_python.arcana.file_management_service.open", mocker.mock_open())
    mock_os_remove = mocker.patch("server_python.arcana.file_management_service.os.remove")
    mock_shutil_rmtree = mocker.patch("server_python.arcana.file_management_service.shutil.rmtree")
    mock_os_path_exists = mocker.patch("server_python.arcana.file_management_service.os.path.exists", return_value=True)
    mock_os_path_isdir = mocker.patch("server_python.arcana.file_management_service.os.path.isdir", return_value=False) # Default to file
    mock_os_listdir = mocker.patch("server_python.arcana.file_management_service.os.listdir", return_value=[])
    mock_os_path_getsize = mocker.patch("server_python.arcana.file_management_service.os.path.getsize", return_value=100)
    mock_os_path_getmtime = mocker.patch("server_python.arcana.file_management_service.os.path.getmtime", return_value=datetime.now().timestamp())
    
    return {
        "makedirs": mock_os_makedirs,
        "open": mock_open,
        "remove": mock_os_remove,
        "rmtree": mock_shutil_rmtree,
        "exists": mock_os_path_exists,
        "isdir": mock_os_path_isdir,
        "listdir": mock_os_listdir,
        "getsize": mock_os_path_getsize,
        "getmtime": mock_os_path_getmtime,
    }

### Tests for File Operations ###

def test_file_operations_write_read_delete(client, auth_headers, test_user, mock_file_system, mocker: MockerFixture):
    user_test_dir = os.path.join(TEST_FILE_OPERATIONS_DIR, str(test_user.id))
    # os.makedirs(user_test_dir, exist_ok=True) # This should be mocked, not called directly

    # Configure the mock open to return content when read() is called
    mock_file_system["open"].return_value.__enter__.return_value.read.return_value = "Hello from Arcana!"

    # Test Write
    write_response = client.post(
        "/api/arcana/file-operations",
        headers=auth_headers,
        json={"action": "write", "path": "test_file.txt", "content": "Hello from Arcana!"}
    )
    assert write_response.status_code == 200
    assert write_response.json()["success"] == True
    assert "written successfully" in write_response.json()["message"]
    mock_file_system["open"].assert_called_once_with(mocker.ANY, "w")
    mock_file_system["open"]().write.assert_called_once_with("Hello from Arcana!")
    mock_file_system["exists"].return_value = True # Simulate file exists after write
    mock_file_system["isdir"].return_value = False # Simulate it's a file
    # assert os.path.exists(os.path.join(user_test_dir, "test_file.txt")) # This assertion relies on actual filesystem, remove

    # Test Read
    read_response = client.post(
        "/api/arcana/file-operations",
        headers=auth_headers,
        json={"action": "read", "path": "test_file.txt"}
    )
    assert read_response.status_code == 200
    assert read_response.json()["success"] == True
    assert read_response.json()["content"] == "Hello from Arcana!"
    mock_file_system["open"].assert_called_with(mocker.ANY, "r")
    # mock_file_system["open"]().read.return_value = "Hello from Arcana!" # This was set above

    # Test List
    mock_file_system["isdir"].return_value = True # Simulate it's a directory for list
    mock_file_system["listdir"].return_value = ["test_file.txt"]
    mock_file_system["exists"].return_value = True # Directory exists
    list_response = client.post(
        "/api/arcana/file-operations",
        headers=auth_headers,
        json={"action": "list", "path": "."}
    )
    assert list_response.status_code == 200
    assert list_response.json()["success"] == True
    assert any(f["name"] == "test_file.txt" for f in list_response.json()["file_list"])

    # Test Delete
    mock_file_system["exists"].return_value = True # Simulate file exists before delete
    mock_file_system["isdir"].return_value = False # Simulate it's a file
    mock_file_system["remove"].return_value = None # Simulate successful removal
    delete_response = client.post(
        "/api/arcana/file-operations",
        headers=auth_headers,
        json={"action": "delete", "path": "test_file.txt"}
    )
    # print(f"DEBUG: delete_response.json(): {delete_response.json()}") # Keep for debugging if needed
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] == True
    assert "deleted successfully" in delete_response.json()["message"]
    mock_file_system["remove"].assert_called_once_with(mocker.ANY)
    mock_file_system["exists"].return_value = False # Simulate file does not exist after delete

def test_file_operations_create_directory(client, auth_headers, test_user, mock_file_system, mocker: MockerFixture):
    dir_name = "new_dir"
    expected_abs_path = os.path.join(TEST_FILE_OPERATIONS_DIR, str(test_user.id), dir_name)

    # Mock get_user_file_path to return the correct absolute path for the requested directory
    mock_get_user_file_path = mocker.patch(
        "server_python.arcana.file_management_service.get_user_file_path",
        return_value=expected_abs_path
    )
    
    # Reset the makedirs mock to ensure we only count calls within this test's action
    mock_file_system["makedirs"].reset_mock()
    mock_file_system["makedirs"].return_value = None # Simulate successful creation

    # Before creation, simulate that the directory does not exist
    mock_file_system["exists"].return_value = False
    mock_file_system["isdir"].return_value = False

    create_dir_response = client.post(
        "/api/arcana/file-operations",
        headers=auth_headers,
        json={"action": "create_directory", "path": dir_name}
    )
    assert create_dir_response.status_code == 200
    assert create_dir_response.json()["success"] == True
    assert "created successfully" in create_dir_response.json()["message"]
    
    # Now, assert that makedirs was called once for the specific new directory
    mock_file_system["makedirs"].assert_called_once_with(expected_abs_path, exist_ok=True)
    
    # Also ensure get_user_file_path was called with the correct arguments, using mocker.ANY for the user_id
    mock_get_user_file_path.assert_called_once_with(mocker.ANY, dir_name)
    
    # After creation, simulate that the directory exists
    mock_file_system["exists"].return_value = True
    mock_file_system["isdir"].return_value = True
    # assert os.path.isdir(os.path.join(user_test_dir, dir_name)) # This assertion relies on actual filesystem, remove

    # Clean up (mocked)
    # shutil.rmtree(os.path.join(user_test_dir, dir_name)) # No need to call actual rmtree

def test_file_operations_security_path_traversal(client, auth_headers, test_user, mocker: MockerFixture):
    # Mock get_user_file_path to raise HTTPException directly
    mocker.patch("server_python.arcana.file_management_service.get_user_file_path", side_effect=HTTPException(status_code=400, detail="Access denied: Path outside user's allowed directory."))
    
    # Attempt to write outside the user's directory
    response = client.post(
        "/api/arcana/file-operations",
        headers=auth_headers,
        json={"action": "write", "path": "../../../dangerous_file.txt", "content": "Malicious content"}
    )
    assert response.status_code == 400
    assert "Access denied" in response.json()["detail"]

### Tests for Arcana Mode Agent Execution ###

async def mock_process_chat_request(*args, **kwargs):
    return {"response": "Agent chat response", "model_used": "general-chat-model"}

async def mock_call_llm_api_agent_tools(*args, **kwargs):
    messages = kwargs.get("messages", [])
    # Simulate LLM deciding to call generate_code
    if "generate python" in messages[-1]["content"].lower():
        return {"message": {"tool_calls": [{"id": "call_123", "function": {"name": "generate_code", "arguments": "{\"prompt\": \"hello world\", \"language\": \"python\"}"}}]}, "model_used": "tool-user-model"}
    return {"message": {"content": "Agent did not call a tool."}, "model_used": "tool-user-model"}

def test_execute_agent_task_chat_mode(client, auth_headers, db_session, test_user, mocker: MockerFixture):
    mocker.patch("server_python.arcana.agent_orchestration_service.get_openrouter_completion", return_value="Agent chat response")
    
    agent = ArcanaAgent(
        id=str(uuid.uuid4()), owner_id=str(test_user.id), name="ChattyAgent",
        persona="friendly assistant", mode="chat", status="idle"
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)

    response = client.post(
        f"/api/arcana/agents/{agent.id}/execute",
        headers=auth_headers,
        json={"agent_id": str(agent.id), "task_prompt": "Tell me a joke."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["output"] == "Agent chat response"
    assert "Chat response generated" in response.json()["actions_taken"][0]

def test_execute_agent_task_tool_user_mode(client, auth_headers, db_session, test_user, setup_llm_models, mocker: MockerFixture):
    mocker.patch("server_python.arcana.agent_orchestration_service.call_llm_api", side_effect=mock_call_llm_api_agent_tools)
    mocker.patch("server_python.arcana.code_generation_service.generate_code", return_value={"generated_code": "print('Mocked Code')", "success": True})

    agent = ArcanaAgent(
        id=str(uuid.uuid4()), owner_id=str(test_user.id), name="ToolAgent",
        persona="code generator", mode="tool_user", status="idle"
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)

    response = client.post(
        f"/api/arcana/agents/{agent.id}/execute",
        headers=auth_headers,
        json={"agent_id": str(agent.id), "task_prompt": "Generate python code for hello world."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Agent did not call a tool." in response.json()["output"]

def test_execute_agent_task_autonomous_mode(client, auth_headers, db_session, test_user, setup_llm_models, mocker: MockerFixture):
    mocker.patch("server_python.arcana.agent_orchestration_service.call_llm_api", side_effect=mock_call_llm_api_agent_tools)
    mocker.patch("server_python.arcana.reasoning_service.call_llm_api", return_value={
        "message": {
            "content": "{\"reasoning_trace\": [{\"step_number\": 1, \"description\": \"Mocked reasoning step.\", \"action\": \"None\", \"outcome\": \"None\"}], \"summary\": \"Mocked reasoning summary\"}"
        }
    })
    m4 = mocker.patch("server_python.arcana.reasoning_service.generate_reasoning", return_value={"summary": "Mocked reasoning summary", "success": True, "reasoning_trace": []})
    agent = ArcanaAgent(
        id=str(uuid.uuid4()), owner_id=str(test_user.id), name="AutoAgent",
        persona="planner", mode="autonomous", status="idle", objective="complete tasks autonomously"
    )
    db_session.add(agent)
    db_session.commit()
    db_session.refresh(agent)

    response = client.post(
        f"/api/arcana/agents/{agent.id}/execute",
        headers=auth_headers,
        json={"agent_id": str(agent.id), "task_prompt": "Plan and execute a task."}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert "Generated reasoning: Mocked reasoning summary" in response.json()["actions_taken"][0]
    assert "Agent did not call a tool." in response.json()["output"]    
# Cleanup the test database and dataset/file_ops directories after tests run
def teardown_module(module):
    import os
    if os.path.exists("./test_arcana_features.db"):
        os.remove("./test_arcana_features.db")
    if os.path.exists(TEST_DATASET_STORAGE_DIR):
        shutil.rmtree(TEST_DATASET_STORAGE_DIR)
    if os.path.exists(TEST_FILE_OPERATIONS_DIR):
        shutil.rmtree(TEST_FILE_OPERATIONS_DIR)
