from sqlalchemy.orm import Session
from typing import List, Optional
import uuid
from datetime import datetime
import json
from server_python.encryption_utils import encrypt_api_key, decrypt_api_key

from server_python.database import UserGitConfig as DBUserGitConfig # Import the DB model
from .schemas import UserGitConfigCreate, UserGitConfigUpdate, GitRepoConfig # Import schemas

# --- UserGitConfig CRUD Operations ---

def get_user_git_config(db: Session, user_id: str, decrypt_pat: bool = False) -> Optional[DBUserGitConfig]:
    db_config = db.query(DBUserGitConfig).filter(DBUserGitConfig.user_id == user_id).first()
    if db_config and decrypt_pat and db_config.github_pat_encrypted:
        try:
            # Create a copy to avoid modifying the SQLAlchemy object directly for decrypted value
            # Or, more cleanly, add a @property to the DBUserGitConfig model for decrypted_pat
            # For now, we'll just add it as an attribute for this specific return
            db_config.github_pat = decrypt_api_key(db_config.github_pat_encrypted)
        except Exception as e:
            print(f"Error decrypting PAT for user {user_id}: {e}")
            db_config.github_pat = None # Ensure it's not used if decryption fails
    return db_config

def create_user_git_config(db: Session, user_id: str, config: UserGitConfigCreate) -> DBUserGitConfig:
    encrypted_pat = encrypt_api_key(config.github_pat) if config.github_pat else None
    db_config = DBUserGitConfig(
        id=str(uuid.uuid4()),
        user_id=user_id,
        github_pat_encrypted=encrypted_pat,
        default_author_name=config.default_author_name,
        default_author_email=config.default_author_email,
        default_repo_url=config.default_repo_url,
        default_local_path=config.default_local_path,
        default_branch=config.default_branch
    )
    db.add(db_config)
    db.commit()
    db.refresh(db_config)
    return db_config

def update_user_git_config(db: Session, user_id: str, config: UserGitConfigUpdate) -> Optional[DBUserGitConfig]:
    db_config = get_user_git_config(db, user_id)
    if db_config:
        if config.github_pat is not None:
            db_config.github_pat_encrypted = encrypt_api_key(config.github_pat) if config.github_pat else None
        if config.default_author_name is not None:
            db_config.default_author_name = config.default_author_name
        if config.default_author_email is not None:
            db_config.default_author_email = config.default_author_email
        if config.default_repo_url is not None:
            db_config.default_repo_url = config.default_repo_url
        if config.default_local_path is not None:
            db_config.default_local_path = config.default_local_path
        if config.default_branch is not None:
            db_config.default_branch = config.default_branch
        db_config.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_config)
    return db_config

def delete_user_git_config(db: Session, user_id: str) -> bool:
    db_config = get_user_git_config(db, user_id)
    if db_config:
        db.delete(db_config)
        db.commit()
        return True
    return False

# --- GitRepoConfig CRUD Operations (for managing multiple cloned repos by a user) ---
# (This would be more complex, involving a separate table for each cloned repo)
# For now, we'll assume a single default repo configured via UserGitConfig.
