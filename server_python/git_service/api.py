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

def get_git_service(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)) -> service.GitService:
    return service.GitService(db, current_user)

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
async def clone_repo(request: schemas.GitCloneRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.clone_repo(request)

@router.get("/status", response_model=schemas.GitStatus)
async def get_status(local_path: str, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.get_status(local_path)

@router.post("/add", response_model=str)
async def add_files(local_path: str, request: schemas.GitAddRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.add_files(local_path, request)

@router.post("/commit", response_model=str)
async def commit_changes(local_path: str, request: schemas.GitCommitRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.commit_changes(local_path, request)

@router.post("/push", response_model=str)
async def push_changes(local_path: str, request: schemas.GitPushRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.push_changes(local_path, request)

@router.post("/pull", response_model=str)
async def pull_changes(local_path: str, request: schemas.GitPullRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.pull_changes(local_path, request)

@router.post("/checkout", response_model=str)
async def checkout_branch(local_path: str, request: schemas.GitCheckoutRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.checkout_branch(local_path, request)

@router.post("/branch", response_model=str)
async def create_branch(local_path: str, request: schemas.GitCreateBranchRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.create_branch(local_path, request)

@router.post("/diff", response_model=schemas.GitDiffResponse)
async def get_diff(local_path: str, request: schemas.GitDiffRequest, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.get_diff(local_path, request)

@router.get("/log", response_model=schemas.GitLogResponse)
async def get_log(local_path: str, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.get_log(local_path)

@router.get("/branches", response_model=List[schemas.GitBranch])
async def get_branches(local_path: str, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.get_branches(local_path)

@router.get("/file_content", response_model=str)
async def read_file_content(local_path: str, file_path: str, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.read_file_content(local_path, file_path)

@router.post("/file_content", response_model=str)
async def write_file_content(local_path: str, file_path: str, content: schemas.GitFileContent, git_service: service.GitService = Depends(get_git_service)):
    return await git_service.write_file_content(local_path, file_path, content.content)