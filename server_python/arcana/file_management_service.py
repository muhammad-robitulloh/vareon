import os
import shutil
from datetime import datetime
from fastapi import HTTPException
from typing import List

from server_python.database import User
from . import schemas

# Define a base directory for user-specific file operations
# This should be configurable and ideally isolated per user in a production environment
# For now, we'll use a subdirectory within the project's temporary directory
# In a real app, this would be more robust, e.g., /data/users/{user_id}/files
def get_base_file_operations_dir():
    base_dir = os.getenv("BASE_FILE_OPERATIONS_DIR", os.path.join(
        os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '.gemini', 'tmp')),
        "arcana_user_files_default"
    ))
    print(f"DEBUG: BASE_FILE_OPERATIONS_DIR: {base_dir}")
    return base_dir

# Ensure the base directory exists (for default case, if env var not set)
os.makedirs(get_base_file_operations_dir(), exist_ok=True)

def get_user_file_path(user_id: str, relative_path: str) -> str:
    """Constructs a safe absolute path within the user's designated directory."""
    base_dir = get_base_file_operations_dir()
    user_dir = os.path.join(base_dir, user_id)
    os.makedirs(user_dir, exist_ok=True) # Ensure user's directory exists

    # Resolve the path to prevent directory traversal
    abs_path = os.path.abspath(os.path.join(user_dir, relative_path))

    # Ensure the resolved path is still within the user's directory
    if not abs_path.startswith(user_dir):
        raise HTTPException(status_code=400, detail="Access denied: Path outside user's allowed directory.")
    
    print(f"DEBUG: user_id: {user_id}, relative_path: {relative_path}")
    print(f"DEBUG: user_dir: {user_dir}")
    print(f"DEBUG: abs_path: {abs_path}")
    
    return abs_path

async def perform_file_operation(user: User, request: schemas.FileOperationRequest) -> schemas.FileOperationResponse:
    """
    Performs file operations (read, write, delete, list, create_directory) within a user's sandboxed directory.
    """
    try:
        target_path = get_user_file_path(str(user.id), request.path)

        if request.action == "read":
            if not os.path.exists(target_path) or os.path.isdir(target_path):
                return schemas.FileOperationResponse(success=False, message="File not found or is a directory.", error_message="File not found or is a directory.")
            with open(target_path, "r") as f:
                content = f.read()
            return schemas.FileOperationResponse(success=True, message=f"File '{request.path}' read successfully.", content=content)

        elif request.action == "write":
            if os.path.isdir(target_path):
                return schemas.FileOperationResponse(success=False, message="Cannot write to a directory.", error_message="Cannot write to a directory.")
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)
            
            with open(target_path, "w") as f:
                f.write(request.content or "")
            return schemas.FileOperationResponse(success=True, message=f"File '{request.path}' written successfully.")

        elif request.action == "delete":
            if not os.path.exists(target_path):
                raise HTTPException(status_code=404, detail=f"File or directory '{request.path}' not found.")
            if os.path.isdir(target_path):
                if request.recursive:
                    shutil.rmtree(target_path)
                    return schemas.FileOperationResponse(success=True, message=f"Directory '{request.path}' and its contents deleted successfully.")
                else:
                    raise HTTPException(status_code=400, detail=f"Cannot delete directory '{request.path}'. Use recursive=true to delete non-empty directories.")
            else:
                os.remove(target_path)
                return schemas.FileOperationResponse(success=True, message=f"File '{request.path}' deleted successfully.")

        elif request.action == "list":
            if not os.path.exists(target_path) or not os.path.isdir(target_path):
                return schemas.FileOperationResponse(success=False, message="Directory not found.", error_message="Directory not found.")
            
            file_list: List[schemas.FileInfo] = []
            for entry_name in os.listdir(target_path):
                entry_path = os.path.join(target_path, entry_name)
                is_dir = os.path.isdir(entry_path)
                size = os.path.getsize(entry_path) if not is_dir else None
                last_mod = datetime.fromtimestamp(os.path.getmtime(entry_path))
                file_list.append(schemas.FileInfo(
                    name=entry_name,
                    path=os.path.relpath(entry_path, get_user_file_path(str(user.id), "")), # Relative to user's root
                    is_directory=is_dir,
                    size=size,
                    last_modified=last_mod
                ))
            return schemas.FileOperationResponse(success=True, message=f"Contents of '{request.path}' listed successfully.", file_list=file_list)

        elif request.action == "create_directory":
            if os.path.exists(target_path) and not os.path.isdir(target_path):
                return schemas.FileOperationResponse(success=False, message="A file with that name already exists.", error_message="A file with that name already exists.")
            os.makedirs(target_path, exist_ok=True)
            return schemas.FileOperationResponse(success=True, message=f"Directory '{request.path}' created successfully.")
        
        else:
            return schemas.FileOperationResponse(success=False, message="Invalid file operation action.", error_message="Invalid file operation action.")

    except HTTPException as e:
        raise e
    except Exception as e:
        return schemas.FileOperationResponse(success=False, message=f"An unexpected error occurred: {e}", error_message=str(e))
