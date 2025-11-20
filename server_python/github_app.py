import os
import time
import jwt
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from server_python.database import get_db, User as DBUser, get_user_by_username_or_email, UserGitConfig as DBUserGitConfig
from server_python.auth import get_current_user, decode_access_token
from server_python.git_service import crud as git_crud
from server_python.git_service.schemas import UserGitConfigCreate

router = APIRouter()

# --- GitHub App Configuration ---
GITHUB_APP_ID = os.getenv("GITHUB_APP_ID")
GITHUB_APP_PRIVATE_KEY = os.getenv("GITHUB_APP_PRIVATE_KEY")
GITHUB_APP_INSTALLATION_URL = "https://github.com/apps/connect-to-arcana"

if not GITHUB_APP_ID or not GITHUB_APP_PRIVATE_KEY:
    print("WARNING: GITHUB_APP_ID or GITHUB_APP_PRIVATE_KEY not set. GitHub App integration will not function.")

def generate_jwt_token():
    """Generates a JWT token for GitHub App authentication."""
    if not GITHUB_APP_ID or not GITHUB_APP_PRIVATE_KEY:
        raise HTTPException(status_code=500, detail="GitHub App not configured.")

    payload = {
        "iat": int(time.time()) - 60,  # 1 minute in the past to allow for clock skew
        "exp": int(time.time()) + (10 * 60),  # 10 minutes
        "iss": GITHUB_APP_ID,
    }
    return jwt.encode(payload, GITHUB_APP_PRIVATE_KEY, algorithm="RS256")

async def get_installation_access_token(installation_id: int):
    """Generates an installation access token for a given installation ID."""
    jwt_token = generate_jwt_token()
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    url = f"https://api.github.com/app/installations/{installation_id}/access_tokens"
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()["token"]

@router.get("/github/app/install", tags=["git"])
async def install_github_app(
    token: str = Query(..., description="Vareon access token for authentication"),
    db: Session = Depends(get_db)
):
    """Redirects the user to the GitHub App installation page."""
    try:
        payload = decode_access_token(token)
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
        
        user = get_user_by_username_or_email(db, username) # Get DBUser from username
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        if not GITHUB_APP_INSTALLATION_URL:
            raise HTTPException(status_code=500, detail="GitHub App installation URL not configured.")
        
        redirect_to_github_url = f"{GITHUB_APP_INSTALLATION_URL}/installations/new?state={token}"
        return RedirectResponse(redirect_to_github_url)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed during GitHub App installation redirect: {e}")

@router.get("/github/app/callback", tags=["git"])
async def github_app_callback(
    installation_id: int,
    state: str = Query(..., description="Vareon access token passed as state parameter"),
    db: Session = Depends(get_db),
):
    """Handles the callback from the GitHub App installation."""
    try:
        payload = decode_access_token(state) # Decode the state parameter (which is our token)
        username = payload.get("username")
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload in state")
        
        current_user = get_user_by_username_or_email(db, username) # Get DBUser from username
        if not current_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found from token in state")

        db_config = git_crud.get_user_git_config(db, str(current_user.id))
        if db_config:
            db_config.github_app_installation_id = installation_id
            db.commit()
            db.refresh(db_config)
        else:
            new_config_data = UserGitConfigCreate(
                github_app_installation_id=installation_id,
                default_author_name=current_user.username,
                default_author_email=current_user.email
            )
            git_crud.create_user_git_config(db, str(current_user.id), new_config_data)

        # The 'state' parameter contains the Vareon access token
        vareon_access_token = state # The state parameter IS the token

        return RedirectResponse(f"/dashboard/profile?github_app_installed=true&token={vareon_access_token}&oauth_success=true")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Authentication failed during GitHub App callback: {e}")

@router.post("/github/app/disconnect", tags=["git"])
async def disconnect_github_app(
    db: Session = Depends(get_db),
    current_user: DBUser = Depends(get_current_user),
):
    """Disconnects the GitHub App for the current user."""
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    db_config = git_crud.get_user_git_config(db, str(current_user.id))
    if db_config:
        db_config.github_app_installation_id = None
        db.commit()
        db.refresh(db_config)

    return {"message": "GitHub App disconnected successfully."}

