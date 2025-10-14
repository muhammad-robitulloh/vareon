import asyncio
import json
import logging
import pty
import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Dict, Any, Literal

from . import config
from .utils import file_utils, shell_utils, telegram_utils
from .ai_core import ai_core_instance

# --- Logging ---
logger = logging.getLogger(__name__)

# --- Pydantic Models for API Data Validation ---
class ChatRequest(BaseModel):
    chat_id: int
    message: str
    attached_file_path: str | None = None

class AutoDebugRequest(BaseModel):
    request_id: str

class FileRequest(BaseModel):
    path: str

class FileWriteRequest(FileRequest):
    content: str

class SettingsUpdateRequest(BaseModel):
    key: str
    value: str

class FileOperationRequest(BaseModel):
    file_path: str

class TelegramSettings(BaseModel):
    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str

# --- FastAPI Application Setup ---

app = FastAPI(
    title="Cognitive Shell Backend API",
    description="API to power the NeuroNet AI Cognitive Shell web interface.",
    version="2.0.0"
)

# --- CORS Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], # Standard React dev ports
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"], # Allows all headers
)

# --- Application Lifecycle Events ---
@app.on_event("startup")
async def startup_event():
    if config.TELEGRAM_ENABLED:
        asyncio.create_task(telegram_utils.start_telegram_bot())

@app.on_event("shutdown")
async def shutdown_event():
    await telegram_utils.stop_telegram_bot()

# --- Standard REST API Endpoints ---

@app.get("/api/system_info")
def get_system_info():
    return config.SYSTEM_INFO

@app.get("/api/history/{history_type}")
def get_history(history_type: Literal['chat', 'shell']):
    return file_utils.get_history(history_type)

@app.post("/api/history/clear")
def clear_history():
    result = file_utils.clear_all_history()
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["message"])
    return result

# --- File System API ---
@app.post("/api/fs/list")
def list_files_fs(request: FileRequest):
    # This endpoint is for general file system browsing, not specific generated/uploaded files
    result = file_utils.list_files_in_path(request.path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/fs/read")
def read_file_fs(request: FileRequest):
    result = file_utils.read_file(request.path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/fs/write")
def write_file_fs(request: FileWriteRequest):
    result = file_utils.write_file(request.path, request.content)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/fs/delete")
async def delete_file_fs(request: FileRequest):
    result = file_utils.delete_file(request.path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result

# --- Settings API ---
@app.get("/api/settings/llm_config")
def get_llm_config():
    # Return relevant LLM config from config.py
    return {
        "CODE_GEN_MODEL": config.CODE_GEN_MODEL,
        "ERROR_FIX_MODEL": config.ERROR_FIX_MODEL,
        "CONVERSATION_MODEL": config.CONVERSATION_MODEL,
        "COMMAND_CONVERSION_MODEL": config.COMMAND_CONVERSION_MODEL,
        "FILENAME_GEN_MODEL": config.FILENAME_GEN_MODEL,
        "INTENT_DETECTION_MODEL": config.INTENT_DETECTION_MODEL,
        "REASONING_ENABLED": config.REASONING_ENABLED,
        "REASONING_MODEL": config.REASONING_MODEL,
        "REASONING_MAX_TOKENS": config.REASONING_MAX_TOKENS,
        "REASONING_TEMPERATURE": config.REASONING_TEMPERATURE,
        "REASONING_APPLY_TO_MODELS": config.REASONING_APPLY_TO_MODELS,
    }

@app.put("/api/settings/llm_config")
def update_llm_config(request: Dict[str, Any]):
    for key, value in request.items():
        # Special handling for REASONING_APPLY_TO_MODELS (list to comma-separated string)
        if key == "REASONING_APPLY_TO_MODELS":
            value = ",".join(value) # Convert list back to comma-separated string
        result = file_utils.update_env_variable(key, str(value))
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["message"])
    return {"status": "success", "message": "LLM configuration updated."}

@app.get("/api/settings/api_key")
def get_api_key():
    return {"api_key": config.OPENROUTER_API_KEY}

@app.put("/api/settings/api_key")
def update_api_key(request: SettingsUpdateRequest):
    result = file_utils.update_env_variable("OPENROUTER_API_KEY", request.value)
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["message"])
    return {"status": "success", "message": "API Key updated."}

@app.get("/api/settings/llm_base_url")
def get_llm_base_url():
    return {"llm_base_url": config.LLM_BASE_URL}

@app.put("/api/settings/llm_base_url")
def update_llm_base_url(request: SettingsUpdateRequest):
    result = file_utils.update_env_variable("LLM_BASE_URL", request.value)
    if result.get("error"):
        raise HTTPException(status_code=500, detail=result["message"])
    return {"status": "success", "message": "LLM Base URL updated."}

@app.get("/api/settings/telegram_bot")
def get_telegram_settings():
    return {
        "telegram_enabled": config.TELEGRAM_ENABLED,
        "telegram_bot_token": config.TELEGRAM_BOT_TOKEN,
        "telegram_chat_id": config.TELEGRAM_CHAT_ID,
    }

@app.put("/api/settings/telegram_bot")
async def update_telegram_settings(request: TelegramSettings):
    # Stop bot if it's currently running and being disabled or token is changing
    if telegram_utils.telegram_application and telegram_utils.telegram_application.running and \
       (config.TELEGRAM_ENABLED and not request.telegram_enabled or \
        config.TELEGRAM_BOT_TOKEN != request.telegram_bot_token):
        await telegram_utils.stop_telegram_bot()

    # Update environment variables
    file_utils.update_env_variable("TELEGRAM_ENABLED", str(request.telegram_enabled))
    file_utils.update_env_variable("TELEGRAM_BOT_TOKEN", request.telegram_bot_token)
    file_utils.update_env_variable("TELEGRAM_CHAT_ID", request.telegram_chat_id)

    # Reload config to reflect new values immediately
    config.load_dotenv(override=True, dotenv_path=config.ENV_PATH)

    # Start bot if it's enabled and not already running
    if config.TELEGRAM_ENABLED and not (telegram_utils.telegram_application and telegram_utils.telegram_application.running):
        asyncio.create_task(telegram_utils.start_telegram_bot())

    return {"status": "success", "message": "Telegram bot settings updated."}

@app.get("/api/files")
def get_files():
    # List all files, categorized by type
    categorized_files = file_utils.list_all_files_categorized()
    return categorized_files

@app.post("/api/files/read")
def read_any_file(request: FileOperationRequest):
    # file_utils.read_file now handles path validation
    result = file_utils.read_file(request.file_path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return {"file_path": request.file_path, "content": result["content"]}

@app.delete("/api/files/delete")
def delete_any_file(request: FileOperationRequest):
    # file_utils.delete_file now handles path validation
    result = file_utils.delete_file(request.file_path)
    if result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return {"status": "success", "message": f"File {request.file_path} deleted."}

@app.post("/api/files/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        result = file_utils.save_uploaded_file(file.filename, content)
        if result.get("error"):
            raise HTTPException(status_code=500, detail=result["message"])
        return {"status": "success", "message": f"File {file.filename} uploaded successfully.", "path": result["path"]}
    except Exception as e:
        logger.error(f"Failed to upload file: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {e}")

# --- Analytics API ---
@app.get("/api/analytics/token_usage")
def get_token_usage():
    return {"token_usage": file_utils.get_token_usage_data()}

# --- Streaming API Endpoints ---

@app.post("/api/chat")
def chat_stream(request: ChatRequest):
    """Handles a chat message and streams the AI's response back."""
    return StreamingResponse(ai_core_instance.process_chat_stream(request.chat_id, request.message, request.attached_file_path), media_type="application/x-ndjson")

@app.post("/api/auto_debug")
def auto_debug_stream(request: AutoDebugRequest):
    """Handles an auto-debug request and streams the AI's process back."""
    # This endpoint needs to be implemented in ai_core.py if it's to be used.
    # For now, it's a placeholder.
    raise HTTPException(status_code=501, detail="Auto-debug not yet implemented.")

# --- WebSocket Endpoint for Interactive Shell ---

@app.websocket("/ws/shell/{chat_id}")
async def websocket_shell(websocket: WebSocket, chat_id: str):
    await websocket.accept()
    
    # Create a pseudo-terminal (pty)
    master_fd, slave_fd = pty.openpty()
    
    # Start a shell process (e.g., bash) in the pty
    shell_process = await asyncio.create_subprocess_exec(
        os.environ.get("SHELL", "/bin/bash"),
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        cwd=config.PROJECT_ROOT # Use config.PROJECT_ROOT
    )

    # Get a non-blocking file-like object for the master end of the pty
    master_reader = os.fdopen(master_fd, 'rb', 0)

    async def forward_shell_to_client():
        """Reads from the shell's output and sends it to the WebSocket client."""
        try:
            while True:
                output = await asyncio.to_thread(master_reader.read, 1024)
                if not output:
                    break
                await websocket.send_text(output.decode(errors='ignore'))
        except (IOError, WebSocketDisconnect):
            pass
        finally:
            logger.info(f"Shell for client {chat_id} has closed.")
            if websocket.client_state != WebSocketDisconnect:
                 await websocket.close()

    client_task = asyncio.create_task(forward_shell_to_client())

    try:
        while True:
            # Wait for data from the client
            data = await websocket.receive_text()
            # Check for resize command (sent as JSON from frontend)
            try:
                data_json = json.loads(data)
                if 'resize' in data_json:
                    import fcntl, termios, struct
                    cols, rows = data_json['resize']['cols'], data_json['resize']['rows']
                    fcntl.ioctl(master_fd, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
                    continue # Skip writing resize command to shell
            except json.JSONDecodeError:
                pass # It's regular user input, not a resize command

            # Forward user input to the shell
            os.write(master_fd, data.encode())

    except WebSocketDisconnect:
        logger.info(f"Client {chat_id} disconnected.")
    finally:
        # Clean up: terminate the shell process and cancel the reading task
        client_task.cancel()
        if shell_process.returncode is None:
            shell_process.terminate()
        await shell_process.wait()
        master_reader.close()
        logger.info(f"Cleaned up resources for client {chat_id}.")

# --- Static Files and Frontend Serving ---

# Define the path to the frontend build directory
frontend_build_dir = os.path.abspath(os.path.join(config.PROJECT_ROOT, 'ai_web_dashboard', 'frontend', 'build'))

# Mount the 'static' directory from the build folder
app.mount("/static", StaticFiles(directory=os.path.join(frontend_build_dir, "static")), name="static")

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