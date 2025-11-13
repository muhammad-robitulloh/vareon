import os
import requests
from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta, timezone

from server_python.database import get_db, User as DBUser, get_user_by_username_or_email, create_user_in_db, UserGitConfig as DBUserGitConfig
from server_python.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_password_hash
from server_python.encryption_utils import encrypt_api_key
from server_python.git_service import crud as git_crud # Import git crud for UserGitConfig

router = APIRouter()

# --- Google OAuth Configuration ---
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:3000/auth/callback/google") # Frontend callback URL

GITHUB_REDIRECT_URI_BASE = os.getenv("GITHUB_REDIRECT_URI_BASE", "http://localhost:3000/auth/github/callback") # Unified callback URL

# --- GitHub OAuth Configuration (for login/signup) ---
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID") # Re-use from git_service.api
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET") # Re-use from git_service.api
# GITHUB_LOGIN_REDIRECT_URI is now unified with GITHUB_REDIRECT_URI_BASE
GITHUB_LOGIN_REDIRECT_URI = GITHUB_REDIRECT_URI_BASE

if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
    print("WARNING: GOOGLE_CLIENT_ID or GOOGLE_CLIENT_SECRET not set. Google OAuth will not function for login/signup.")
if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
    print("WARNING: GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not set. GitHub OAuth will not function for login/signup.")

# --- Helper to create or get user and generate token ---
async def _handle_oauth_user(db: Session, email: str, username: str, provider: str, provider_id: str, access_token: Optional[str] = None, redirect_path: str = "/auth") -> RedirectResponse:
    user = get_user_by_username_or_email(db, email)
    if not user:
        # Register new user
        hashed_password = get_password_hash(os.urandom(16).hex()) # Generate a random password
        user = create_user_in_db(db, username, hashed_password, email, None, None, is_verified=True)
        print(f"AUDIT: New user registered via {provider} OAuth: {user.username}")
    
    # Link provider ID if not already linked (future enhancement)
    # For now, we assume email is unique enough for login.

    # Generate access token for Vareon
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    vareon_access_token = create_access_token(
        data={"username": user.username}, expires_delta=access_token_expires
    )

    # Store provider-specific access token if provided (e.g., GitHub PAT)
    if provider == "github" and access_token:
        encrypted_token = encrypt_api_key(access_token)
        db_config = git_crud.get_user_git_config(db, str(user.id))
        if db_config:
            db_config.github_pat_encrypted = encrypted_token
            db.commit()
            db.refresh(db_config)
        else:
            new_config_data = git_crud.schemas.UserGitConfigCreate(
                github_pat=access_token, # Will be encrypted in crud
                default_author_name=username,
                default_author_email=email
            )
            git_crud.create_user_git_config(db, str(user.id), new_config_data)
        print(f"AUDIT: GitHub PAT stored for user {user.username}")

    # Redirect to frontend dashboard with Vareon access token
    return RedirectResponse(f"{redirect_path}?token={vareon_access_token}&oauth_success=true")

# --- Google OAuth Endpoints ---
@router.get("/google/authorize")
async def google_authorize():
    if not GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=500, detail="Google Client ID not configured.")
    
    authorize_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={GOOGLE_CLIENT_ID}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile&" # Request email and profile info
        f"redirect_uri={GOOGLE_REDIRECT_URI}&"
        f"access_type=offline&" # To get a refresh token
        f"prompt=consent" # To ensure refresh token is always returned
    )
    return RedirectResponse(authorize_url)

@router.get("/google/callback")
async def google_callback(
    code: str, 
    db: Session = Depends(get_db)
):
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google Client ID or Secret not configured.")

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": GOOGLE_CLIENT_ID,
        "client_secret": GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": GOOGLE_REDIRECT_URI,
    }

    response = requests.post(token_url, data=data)
    response.raise_for_status()
    token_data = response.json()

    access_token = token_data.get("access_token")
    id_token = token_data.get("id_token") # Contains user info
    if not access_token or not id_token:
        raise HTTPException(status_code=500, detail="Failed to get access or ID token from Google.")

    # Decode ID token to get user info
    import jwt # PyJWT
    try:
        # Google's public certificates are needed for full verification
        # For simplicity, we'll just decode without full signature verification for now
        # In production, use a library like google-auth to verify the ID token
        decoded_id_token = jwt.decode(id_token, options={"verify_signature": False})
        
        email = decoded_id_token.get("email")
        name = decoded_id_token.get("name")
        google_id = decoded_id_token.get("sub") # Unique Google user ID

        if not email or not name or not google_id:
            raise HTTPException(status_code=500, detail="Could not retrieve user info from Google ID token.")

        return await _handle_oauth_user(db, email, name, "google", google_id, access_token=access_token, redirect_path="/auth")

    except Exception as e:
        print(f"Error decoding Google ID token: {e}")
        raise HTTPException(status_code=500, detail=f"Error processing Google login: {e}")

# --- GitHub OAuth Endpoints (for login/signup) ---
@router.get("/github/login/authorize")
async def github_login_authorize():
    if not GITHUB_CLIENT_ID:
        raise HTTPException(status_code=500, detail="GitHub Client ID not configured.")
    
    authorize_url = (
        f"https://github.com/login/oauth/authorize?"
        f"client_id={GITHUB_CLIENT_ID}&"
        f"redirect_uri={GITHUB_LOGIN_REDIRECT_URI}&"
        f"scope=user:email,repo,workflow&" # Request email, repo, and workflow scopes
        f"state=login" # Indicate purpose is login
    )
    return RedirectResponse(authorize_url)

@router.get("/github/callback")
async def github_callback(
    code: str, 
    state: str, # Add state parameter
    db: Session = Depends(get_db)
):
    if not GITHUB_CLIENT_ID or not GITHUB_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="GitHub Client ID or Secret not configured.")

    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": GITHUB_CLIENT_ID,
        "client_secret": GITHUB_CLIENT_SECRET,
        "code": code,
        "redirect_uri": GITHUB_LOGIN_REDIRECT_URI,
    }

    response = requests.post(token_url, headers=headers, data=data) # Use data=data for x-www-form-urlencoded
    response.raise_for_status()
    token_data = response.json()

    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=500, detail="Failed to get access token from GitHub.")

    # Get user email from GitHub API
    user_email_url = "https://api.github.com/user/emails"
    user_email_headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    email_response = requests.get(user_email_url, headers=user_email_headers)
    email_response.raise_for_status()
    emails = email_response.json()
    
    primary_email = next((e for e in emails if e["primary"] and e["verified"]), None)
    if not primary_email:
        raise HTTPException(status_code=500, detail="No primary verified email found on GitHub account.")
    
    email = primary_email["email"]

    # Get user profile to get username
    user_profile_url = "https://api.github.com/user"
    user_profile_headers = {"Authorization": f"Bearer {access_token}", "Accept": "application/json"}
    profile_response = requests.get(user_profile_url, headers=user_profile_headers)
    profile_response.raise_for_status()
    profile_data = profile_response.json()
    
    username = profile_data.get("login") # GitHub username
    github_id = str(profile_data.get("id")) # GitHub user ID

    if not username:
        raise HTTPException(status_code=500, detail="Could not retrieve username from GitHub profile.")

    # Determine redirect path based on state
    redirect_path = "/auth"
    if state == "git_connect":
        redirect_path = "/dashboard/arcana?tab=git"
    elif state == "login":
        redirect_path = "/auth"
    
    return await _handle_oauth_user(db, email, username, "github", github_id, access_token=access_token, redirect_path=redirect_path)
