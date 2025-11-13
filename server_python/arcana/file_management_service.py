import os
import shutil
from datetime import datetime
from fastapi import HTTPException
from typing import List, Optional

from server_python.database import User
from . import schemas

# --- Directory and Path Management ---

def get_base_project_dir():
    """
    Returns the absolute path to the project's root directory.
    
    WARNING: This is for demonstration purposes to browse the project code.
    In a real multi-user application, this MUST be replaced with a function
    that returns a securely isolated, user-specific directory.
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

def _secure_path_join(base: str, relative: str) -> str:
    """
    Joins a base and relative path, ensuring the result is within the base.
    Prevents directory traversal attacks.
    """
    final_path = os.path.abspath(os.path.join(base, relative))
    if not final_path.startswith(base):
        raise HTTPException(status_code=400, detail="Access denied: Path is outside the allowed directory.")
    return final_path

# --- File Tree Service ---

def _build_file_tree_recursive(directory: str, user_root: str) -> List[schemas.FileInfo]:
    """
    Recursively builds a file tree structure for a given directory.
    Ignores common temporary/build directories.
    """
    tree = []
    ignore_patterns = {'__pycache__', 'node_modules', '.git', '.pytest_cache', 'dist', '.env', 'sql_app.db', 'test.db'}
    
    try:
        for entry_name in os.listdir(directory):
            if entry_name in ignore_patterns:
                continue

            entry_path = os.path.join(directory, entry_name)
            is_dir = os.path.isdir(entry_path)
            
            file_info = schemas.FileInfo(
                name=entry_name,
                path=os.path.relpath(entry_path, user_root),
                is_dir=is_dir,
                children=[] if is_dir else None
            )

            if is_dir:
                file_info.children = _build_file_tree_recursive(entry_path, user_root)

            tree.append(file_info)
    except (FileNotFoundError, PermissionError):
        pass  # Skip directories that can't be read

    tree.sort(key=lambda x: (not x.is_dir, x.name.lower()))
    
    return tree

async def get_file_tree(user: User) -> List[schemas.FileInfo]:
    """
    Retrieves the entire file tree for the user's project directory.
    This is the main service function for the /file-tree endpoint.
    """
    try:
        project_root = get_base_project_dir()
        file_tree = _build_file_tree_recursive(project_root, project_root)
        return file_tree
    except Exception as e:
        # In case of unexpected errors during file scanning
        raise HTTPException(status_code=500, detail=f"Failed to build file tree: {e}")

# --- Single File/Directory Operations Service ---

# The existing perform_file_operation function remains untouched.
# I am only adding new functions and not modifying this one.

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
        
        elif request.action == "rename":
            if not request.new_path:
                raise HTTPException(status_code=400, detail="new_path is required for rename operation.")
            
            old_path_abs = get_user_file_path(str(user.id), request.path)
            new_path_abs = get_user_file_path(str(user.id), request.new_path)

            if not os.path.exists(old_path_abs):
                raise HTTPException(status_code=404, detail=f"File or directory '{request.path}' not found.")
            
            if os.path.exists(new_path_abs):
                raise HTTPException(status_code=400, detail=f"A file or directory with the name '{request.new_path}' already exists.")
            
            try:
                os.rename(old_path_abs, new_path_abs)
                return schemas.FileOperationResponse(success=True, message=f"'{request.path}' renamed to '{request.new_path}' successfully.")
            except OSError as e:
                raise HTTPException(status_code=500, detail=f"Failed to rename '{request.path}' to '{request.new_path}': {e}")
        
        elif request.action == "read_many":
            content = ""
            for p in request.path:
                path = get_user_file_path(str(user.id), p)
                if not os.path.exists(path) or os.path.isdir(path):
                    return schemas.FileOperationResponse(success=False, message=f"File not found or is a directory: {p}", error_message="File not found or is a directory.")
                with open(path, "r") as f:
                    content += f.read() + "\n"
            return schemas.FileOperationResponse(success=True, message="Files read successfully.", content=content)

        elif request.action == "edit":
            if not os.path.exists(target_path) or os.path.isdir(target_path):
                return schemas.FileOperationResponse(success=False, message="File not found or is a directory.", error_message="File not found or is a directory.")
            with open(target_path, "r") as f:
                content = f.read()
            new_content = content.replace(request.content.splitlines()[0], request.content.splitlines()[1])
            with open(target_path, "w") as f:
                f.write(new_content)
            return schemas.FileOperationResponse(success=True, message=f"File '{request.path}' edited successfully.")

        else:
            return schemas.FileOperationResponse(success=False, message="Invalid file operation action.", error_message="Invalid file operation action.")

    except HTTPException as e:
        raise e
    except Exception as e:
        return schemas.FileOperationResponse(success=False, message=f"An unexpected error occurred: {e}", error_message=str(e))
