# ImplementationV5: Addressing Mocked Backend Functions and Fallback Logic

This document outlines the plan for implementing the backend functions that are currently mocked or have incomplete "real" system interaction. It also includes instructions for implementing a robust fallback mechanism to ensure system stability even when certain functionalities are unavailable due to environmental constraints.

## 1. Functions Requiring Implementation/Integration

The following functions were identified as requiring further implementation or integration with external systems/hardware:

### Cognisys Module

*   **`POST /providers/{provider_id}/test-connection`**:
    *   **Current Status**: Placeholder.
    *   **Implementation Plan**: Implement actual logic to connect to the specified LLM provider using its `base_url` and `api_key`. This would involve making a small, test API call to the LLM provider to verify connectivity and authentication.
*   **`POST /chat`**:
    *   **Current Status**: Relies on external LLM providers; mocked during testing.
    *   **Implementation Plan**: Ensure `llm_interaction.call_llm_api` is robustly implemented to handle various LLM provider APIs (e.g., OpenAI, Google Gemini, custom local LLMs). This involves proper request formatting, error handling, and response parsing for each integrated provider.

### Myntrix Module

*   **`POST /agents/{agent_id}/start`, `stop`, `restart`**:
    *   **Current Status**: `TODO` for actual process control.
    *   **Implementation Plan**: Implement logic to interact with the underlying operating system or a container orchestration system (e.g., Docker, Kubernetes) to start, stop, or restart agent processes. This might involve shell commands, API calls to a container runtime, or direct process management.
*   **`POST /devices/{device_id}/connect`, `disconnect`, `command`, `upload`**:
    *   **Current Status**: `TODO` for actual device interaction logic.
    *   **Implementation Plan**: Implement specific drivers or communication protocols to interact with various types of devices (e.g., serial communication for `/dev/ttyUSB0`, network protocols for IP-based devices, MQTT, etc.). This will be highly dependent on the device types supported.
*   **WebSocket endpoint for telemetry: `ws/myntrix/telemetry/{deviceId}`**:
    *   **Current Status**: Placeholder.
    *   **Implementation Plan**: Implement a WebSocket server that can receive real-time telemetry data from devices and potentially push it to connected clients (e.g., frontend dashboards). This involves handling WebSocket connections, message parsing, and data routing.
*   **`GET /system-metrics`**:
    *   **Current Status**: Uses `psutil` to read system metrics. Mocked in tests due to potential `/proc` access restrictions in Termux.
    *   **Implementation Plan**: While `psutil` is the intended real implementation, a fallback mechanism (detailed below) will be crucial for environments where `/proc` access is denied.
*   **`POST /tasks/{task_id}/run`**:
    *   **Current Status**: `TODO` for actual task execution logic.
    *   **Implementation Plan**: Implement a task runner that can execute scheduled tasks. This might involve spawning subprocesses, calling external scripts, or executing internal Python functions based on the `action` payload of the `ScheduledTask`.

### Neosyntis Module

*   **`POST /workflows/{workflow_id}/trigger`**:
    *   **Current Status**: `TODO` for actual workflow execution logic.
    *   **Implementation Plan**: Implement a workflow engine that can interpret the `steps` of a workflow and execute them sequentially or in parallel. This could involve a state machine, a task queue (e.g., Celery), or a custom execution loop.
*   **`POST /datasets/upload`**:
    *   **Current Status**: Relies on `storage_service.save_dataset_file` which performs actual file system operations. Mocked in tests.
    *   **Implementation Plan**: Ensure `storage_service.save_dataset_file` correctly handles file uploads to the designated `DATASET_STORAGE_DIR`, including secure naming and error handling.
*   **`DELETE /datasets/{dataset_id}`**:
    *   **Current Status**: Relies on `storage_service.delete_dataset_file` which performs actual file system operations. Mocked in tests.
    *   **Implementation Plan**: Ensure `storage_service.delete_dataset_file` correctly deletes files from `DATASET_STORAGE_DIR` and handles cases where the file might not exist.
*   **`GET /datasets/{dataset_id}/download`**:
    *   **Current Status**: Relies on `os.path.exists`, `os.stat`, and `anyio.open_file` for file system operations. Mocked in tests.
    *   **Implementation Plan**: Ensure the function correctly serves the file from `DATASET_STORAGE_DIR`, handling file not found errors and streaming the file content efficiently.
*   **`POST /models/{model_id}/deploy`**:
    *   **Current Status**: `TODO` for actual ML model deployment logic.
    *   **Implementation Plan**: Implement logic to deploy ML models to a serving infrastructure (e.g., TensorFlow Serving, TorchServe, or a custom inference API). This might involve containerization, API calls to a model serving platform, or loading the model into memory for inference.
*   **`POST /models/{model_id}/train`**:
    *   **Current Status**: `TODO` for actual ML model training logic.
    *   **Implementation Plan**: Implement logic to initiate and monitor ML model training jobs. This could involve integrating with ML frameworks (e.g., scikit-learn, TensorFlow, PyTorch), managing training data, and tracking training progress.
*   **`GET /search`**:
    *   **Current Status**: Incomplete functionality, needs search for ML Models.
    *   **Implementation Plan**: Extend the search logic to include ML Models, querying their name, description, or other relevant metadata.

### Arcana Module (Core functionalities in `main.py` and `llm_service.py`)

*   **`POST /api/arcana/start-chat`**:
    *   **Current Status**: Placeholder with `TODO: Implement actual logic for starting Arcana Chat`.
    *   **Implementation Plan**: Implement the actual logic to initiate an Arcana chat session. This might involve setting up a new conversation, initializing LLM parameters, or preparing a specific context for the chat.
*   **Context Memory API (`/api/arcana/context-memory`)**:
    *   **Current Status**: Fully implemented CRUD operations interacting with `DBContextMemory`.
    *   **Implementation Plan**: These functions are already functional. No further implementation is required beyond ensuring robust error handling and data validation.
*   **LLM Configuration API (`/api/arcana/llm/preferences`)**:
    *   **Current Status**: Fully implemented CRUD operations interacting with `DBUserLLMPreference`.
    *   **Implementation Plan**: These functions are already functional. No further implementation is required beyond ensuring robust error handling and data validation.
*   **Terminal Session Management API (`/api/arcana/terminal/sessions`, `/ws/shell/{session_id}`)**:
    *   **Current Status**: CRUD operations are implemented. The WebSocket endpoint for interactive shell is implemented using `pty` and `asyncio`.
    *   **Implementation Plan**: The core CRUD for sessions and history is functional. For the WebSocket, ensure robust handling of `pty` interactions, shell process management, and client disconnections. Consider adding features like terminal resizing and more sophisticated command logging/output processing.
*   **Contextual Awareness within `llm_service.py`**:
    *   **Current Status**: Implemented to dynamically inject workflow and agent status into LLM prompts based on keywords.
    *   **Implementation Plan**: This functionality is already present. Future enhancements could include more sophisticated context extraction, integration with other data sources, and configurable context injection rules.

## 2. Fallback Logic for Restricted System Access (e.g., `/proc` in Termux)

For functions that interact directly with the operating system, such as `GET /system-metrics` which uses `psutil` to access `/proc`, a fallback mechanism is essential for environments with restricted access (like Termux without root).

**Proposed Fallback Strategy:**

1.  **Environment Variable Flag**: Introduce an environment variable, e.g., `VAREON_MOCK_SYSTEM_METRICS=true`. If this variable is set to `true`, the system will automatically switch to a mock mode for specific functions.
2.  **Conditional Implementation**: Modify the affected backend functions to check for this environment variable.
3.  **Mocking Library Integration**: When in mock mode, use a simple in-memory mock or a predefined set of dummy data instead of attempting actual system calls.

### Example: Fallback for `GET /system-metrics` (Myntrix Module)

**`server-python/myntrix/api.py` (Modified `get_system_metrics` function):**

```python
import os
import psutil
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime

# ... (other imports) ...

router = APIRouter()

# ... (other endpoints) ...

@router.get("/system-metrics", response_model=Dict[str, Any])
async def get_system_metrics(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    # TODO: Add authentication/authorization

    # Check for mock mode environment variable
    if os.getenv("VAREON_MOCK_SYSTEM_METRICS", "false").lower() == "true":
        # Fallback to mock data
        return {
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "memory_total": 8 * 1024 * 1024 * 1024, # 8 GB
            "memory_available": 5 * 1024 * 1024 * 1024, # 5 GB
            "timestamp": datetime.utcnow().isoformat(),
            "mocked": True
        }

    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory_info.percent,
            "memory_total": memory_info.total,
            "memory_available": memory_info.available,
            "timestamp": datetime.utcnow().isoformat()
        }
    except PermissionError:
        # If PermissionError occurs, log it and fall back to mock data
        print("WARNING: Permission denied to access system metrics. Falling back to mock data.")
        return {
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "memory_total": 8 * 1024 * 1024 * 1024, # 8 GB
            "memory_available": 5 * 1024 * 1024 * 1024, # 5 GB
            "timestamp": datetime.utcnow().isoformat(),
            "mocked": True,
            "reason": "PermissionError accessing system metrics"
        }
    except Exception as e:
        # Catch any other unexpected errors and fall back to mock data
        print(f"ERROR: Failed to get system metrics: {e}. Falling back to mock data.")
        return {
            "cpu_percent": 10.0,
            "memory_percent": 30.0,
            "memory_total": 8 * 1024 * 1024 * 1024, # 8 GB
            "memory_available": 5 * 1024 * 1024 * 1024, # 5 GB
            "timestamp": datetime.utcnow().isoformat(),
            "mocked": True,
            "reason": f"Unexpected error: {e}"
        }
```

**Instructions for Implementation:**

1.  **Identify Critical System-Dependent Functions**: Review all backend functions that directly interact with the operating system (e.g., `psutil` for system metrics, file system operations, process management).
2.  **Define Environment Variable**: For each such function, decide if a mock fallback is necessary. If so, define a clear environment variable (e.g., `VAREON_MOCK_FUNCTION_NAME=true`).
3.  **Implement Conditional Logic**: Within the function, add an `if` statement to check the environment variable.
4.  **Provide Mock Data**: If the environment variable is set, return sensible mock data. This mock data should mimic the structure and types of the real data to avoid breaking downstream consumers.
5.  **Error Handling with Fallback**: Implement `try-except` blocks around the real system interaction logic. If a `PermissionError` or other relevant system-level error occurs, log the error and then fall back to returning the mock data. This ensures graceful degradation rather than a server crash.
6.  **Document Mocked Behavior**: Clearly document in the API responses (e.g., using an additional field like `"mocked": True`) when mock data is being returned, so clients can be aware of the operational mode.

By following this approach, the Vareon backend can maintain stability and provide a consistent (albeit mocked) experience even in environments where full system access is not available, while still allowing for full functionality when deployed in a less restricted setting.