import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from server_python.database import get_db, User as DBUser
from server_python.auth import get_current_user
from server_python.encryption_utils import encrypt_api_key, decrypt_api_key
from . import schemas, service, crud # Import crud
from server_python.schemas import MessageResponse # Import MessageResponse

router = APIRouter()

# Load GitHub OAuth credentials from environment variables
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_REDIRECT_URI_BASE = os.getenv("GITHUB_REDIRECT_URI_BASE", "http://localhost:3000/auth/github/callback") # Unified callback URL
GITHUB_REDIRECT_URI = GITHUB_REDIRECT_URI_BASE # Use the unified base URL

if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    print("WARNING: GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not set. GitHub OAuth will not function.")

def get_git_service(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)) -> service.GitService:
    return service.GitService(db, current_user)

# --- GitHub OAuth Endpoints ---
@router.get("/github/authorize")
async def github_authorize(current_user: DBUser = Depends(get_current_user)):
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")
    
    # Store user ID in session or a temporary state for callback verification
    # For simplicity, we'll just redirect. In a real app, use a secure state parameter.
    
    authorize_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={GITHUB_REDIRECT_URI}&"
        f"scope=repo,workflow&" # Request necessary scopes
        f"state=git_connect" # Pass purpose as state
    )
    return RedirectResponse(authorize_url)

@router.get("/github/callback")
async def github_callback(
    code: str, 
    state: str, 
    current_user: DBUser = Depends(get_current_user), # Authenticate user for context
    db: Session = Depends(get_db)
):
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub Client ID or Secret not configured.")

    # Verify state parameter to prevent CSRF attacks
    if state != "git_connect": # Simple state verification
        raise HTTPException(status_code=400, detail="State mismatch. Possible CSRF attack.")

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_REDIRECT_URI,
    }

    response = requests.post(token_url, headers=headers, json=data)
    response.raise_for_status()
    token_data = response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="Failed to get access token from GitHub.")

    # Encrypt and store the access token
    encrypted_token = encrypt_api_key(access_token)
    
    # Update or create UserGitConfig
    db_config = crud.get_user_git_config(db, str(current_user.id))
    if db_config:
        db_config.github_pat_encrypted = encrypted_token
        db.commit()
        db.refresh(db_config)
    else:
        new_config_data = schemas.UserGitConfigCreate(
            github_pat=access_token, # Pass raw token for creation, it will be encrypted in crud
            default_author_name=current_user.username,
            default_author_email=current_user.email
        )
        crud.create_user_git_config(db, str(current_user.id), new_config_data)

    # Redirect back to the frontend with a success message
    return RedirectResponse(f"/dashboard/arcana?tab=git&github_auth_success=true")

# --- User Git Configuration Endpoints ---
@router.get("/config", response_model=schemas.UserGitConfigResponse)
def get_user_git_config(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_config = crud.get_user_git_config(db, str(current_user.id))
    if db_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Git configuration not found")
    # Mask PAT for security
    response_config = schemas.UserGitConfigResponse.from_orm(db_config)
    response_config.github_pat = "********" # Mask PAT
    return response_config

@router.post("/config", response_model=schemas.UserGitConfigResponse, status_code=status.HTTP_201_CREATED)
def create_user_git_config(config: schemas.UserGitConfigCreate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_config = crud.get_user_git_config(db, str(current_user.id))
    if db_config:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User Git configuration already exists. Use PUT to update.")
    
    new_config = crud.create_user_git_config(db, str(current_user.id), config)
    response_config = schemas.UserGitConfigResponse.from_orm(new_config)
    response_config.github_pat = "********" # Mask PAT
    return response_config

@router.put("/config", response_model=schemas.UserGitConfigResponse)
def update_user_git_config(config: schemas.UserGitConfigUpdate, current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    updated_config = crud.update_user_git_config(db, str(current_user.id), config)
    if updated_config is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Git configuration not found. Use POST to create.")
    
    response_config = schemas.UserGitConfigResponse.from_orm(updated_config)
    response_config.github_pat = "********" # Mask PAT
    return response_config

@router.post("/config/disconnect-github", response_model=MessageResponse)
def disconnect_github(current_user: DBUser = Depends(get_current_user), db: Session = Depends(get_db)):
    db_config = crud.get_user_git_config(db, str(current_user.id))
    if db_config:
        db_config.github_pat_encrypted = None # Clear the encrypted PAT
        db.commit()
        db.refresh(db_config)
        return {"message": "GitHub account disconnected successfully."}
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Git configuration not found.")

# --- Git Operations Endpoints ---
@router.post("/init", response_model=str)
def init_repo(request: schemas.GitInitRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.init_repo(request)

@router.post("/clone", response_model=str)
def clone_repo(request: schemas.GitCloneRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.clone_repo(request)

@router.get("/status", response_model=schemas.GitStatus)
def get_status(local_path: str, git_service: service.GitService = Depends(get_git_service)):
    return git_service.get_status(local_path)

@router.post("/add", response_model=str)
def add_files(local_path: str, request: schemas.GitAddRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.add_files(local_path, request)

@router.post("/commit", response_model=str)
def commit_changes(local_path: str, request: schemas.GitCommitRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.commit_changes(local_path, request)

@router.post("/push", response_model=str)
def push_changes(local_path: str, request: schemas.GitPushRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.push_changes(local_path, request)

@router.post("/pull", response_model=str)
def pull_changes(local_path: str, request: schemas.GitPullRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.pull_changes(local_path, request)

@router.post("/checkout", response_model=str)
def checkout_branch(local_path: str, request: schemas.GitCheckoutRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.checkout_branch(local_path, request)

@router.post("/branch", response_model=str)
def create_branch(local_path: str, request: schemas.GitCreateBranchRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.create_branch(local_path, request)

@router.post("/diff", response_model=schemas.GitDiffResponse)
def get_diff(local_path: str, request: schemas.GitDiffRequest, git_service: service.GitService = Depends(get_git_service)):
    return git_service.get_diff(local_path, request)

@router.get("/log", response_model=schemas.GitLogResponse)
def get_log(local_path: str, git_service: service.GitService = Depends(get_git_service)):
    return git_service.get_log(local_path)

@router.get("/branches", response_model=List[schemas.GitBranch])
def get_branches(local_path: str, git_service: service.GitService = Depends(get_git_service)):
    return git_service.get_branches(local_path)

@router.get("/file_content", response_model=str)
def read_file_content(local_path: str, file_path: str, git_service: service.GitService = Depends(get_git_service)):
    return git_service.read_file_content(local_path, file_path)

@router.post("/file_content", response_model=str)
def write_file_content(local_path: str, file_path: str, content: schemas.GitFileContent, git_service: service.GitService = Depends(get_git_service)):
    return git_service.write_file_content(local_path, file_path, content.content)