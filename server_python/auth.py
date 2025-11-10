import os
import hashlib
import random
import httpx
from datetime import datetime, timedelta
from typing import Optional, List
import secrets # Import secrets module for token generation
import logging

logger = logging.getLogger(__name__)

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status, WebSocket
from schemas import TokenData
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
import os

# load_dotenv(os.path.join(os.path.dirname(__file__), '.env')) # Removed, now handled in run.py

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")  # CHANGE THIS IN PRODUCTION!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440
VERIFICATION_TOKEN_EXPIRE_MINUTES = 1440 # 24 hours

# Email Configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "vareon.co@gmail.com")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "vareon.co@gmail.com")

# PBKDF2 Hashing parameters
SALT_SIZE = 16
ITERATIONS = 100000 # Can be adjusted for performance vs security
KEY_LENGTH = 32

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/token")

# --- Password Hashing (using PBKDF2) ---
def get_hexdigest(salt, password):
    return hashlib.pbkdf2_hmac(
        'sha256', # The hash algorithm to use
        password.encode('utf-8'), # Convert password to bytes
        salt, # Salt as bytes
        ITERATIONS, # Number of iterations
        dklen=KEY_LENGTH # Length of the derived key
    ).hex()

def verify_password(plain_password, stored_password_info):
    # stored_password_info format: "salt$hexdigest"
    salt_hex, hexdigest = stored_password_info.split('$')
    salt = bytes.fromhex(salt_hex)
    return get_hexdigest(salt, plain_password) == hexdigest

def get_password_hash(password):
    salt = os.urandom(SALT_SIZE) # Generate a random salt
    hexdigest = get_hexdigest(salt, password)
    return f"{salt.hex()}${hexdigest}"

# --- Email Verification ---
def generate_verification_token():
    return secrets.token_urlsafe(32) # Generate a URL-safe text string

def get_email_verification_html(verification_link: str) -> str:
    # This function will return the HTML content for the verification email.
    # For now, it's a placeholder. We will create a separate HTML file for this.
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Email Verification</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
            .container {{ width: 80%; margin: 20px auto; padding: 20px; border: 1px solid #ddd; border-radius: 8px; background-color: #f9f9f9; }}
            .header {{ background-color: #0056b3; color: white; padding: 10px 20px; text-align: center; border-radius: 8px 8px 0 0; }}
            .content {{ padding: 20px; }}
            .button {{ display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }}
            .footer {{ margin-top: 20px; font-size: 0.8em; color: #777; text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Vareon Email Verification</h2>
            </div>
            <div class="content">
                <p>Dear User,</p>
                <p>Thank you for registering with Vareon. To complete your registration, please verify your email address by clicking the button below:</p>
                <p style="text-align: center;">
                    <a href="{verification_link}" class="button">Verify Email Address</a>
                </p>
                <p>If the button above does not work, please copy and paste the following link into your web browser:</p>
                <p><a href="{verification_link}">{verification_link}</a></p>
                <p>This link will expire in 24 hours.</p>
                <p>If you did not register for a Vareon account, please disregard this email.</p>
                <p>Best regards,</p>
                <p>The Vareon Team</p>
            </div>
            <div class="footer">
                <p>&copy; {datetime.now().year} Vareon. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """

def send_verification_email(email: str, verification_link: str):
    # setup credentials from environment
    consumerKey = SMTP_USERNAME
    consumerSecret = SMTP_PASSWORD

    # setup body.
    html_content = get_email_verification_html(verification_link)
    data = {
        'from': SENDER_EMAIL,
        'to': email,
        'subject': 'Verify Your Vareon Email Address',
        'content': f"Please verify your email address by clicking on this link: {verification_link}",
        'html_content': html_content
    }

    # setup headers
    headers = {
            'Accept': 'application/json',
            'Consumerkey': consumerKey,
            'Consumersecret': consumerSecret,
            'Content-Type': 'application/json',
    }

    # Setup URL
    url = 'https://api.turbo-smtp.com/api/v2/mail/send'

    try:
        with httpx.Client() as client:
            response = client.post(url, json=data, headers=headers)
            response.raise_for_status()  # Raises an exception for 4XX/5XX responses

        print(f"Verification email sent to {email} via TurboSMTP API. Response: {response.text}")

    except httpx.HTTPStatusError as e:
        print(f"Error sending verification email to {email} via API: HTTP Status Error - {e.response.status_code} - {e.response.text}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to send verification email: API error {e.response.status_code}")
    except Exception as e:
        print(f"Error sending verification email to {email}: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send verification email due to an unexpected error.")

# --- JWT Token Management ---
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

import database # Import the database module
from database import get_user_from_db, User # Keep other necessary imports

# ... (rest of the file) ...

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    logger.info(f"get_current_user received token: {token[:10]}...") # Log first 10 chars for security
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        logger.info(f"JWT decoded payload: {payload}")
        username: str = payload.get("username")
        if username is None:
            logger.warning("Username not found in JWT payload, raising credentials_exception.")
            raise credentials_exception
        token_data = TokenData(username=username)
        logger.info(f"Username from token: {token_data.username}")
    except JWTError as e:
        logger.warning(f"JWT decoding error: {e}, raising credentials_exception.")
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        logger.warning(f"User {token_data.username} not found in database, raising credentials_exception.")
        raise credentials_exception
    # Temporarily bypass email verification for testing
    # if not user.is_verified:
    #     logger.warning(f"User {user.username} email not verified (is_verified: {user.is_verified}), raising 403 Forbidden.")
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Email not verified. Please check your email for a verification code."
    #     )
    logger.info(f"User {user.username} successfully authenticated.")
    return user

async def get_websocket_token(websocket: WebSocket) -> str:
    token = websocket.query_params.get("token")
    if not token:
        logger.warning("WebSocket connection attempt without token.")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token missing in WebSocket URL")
    logger.info(f"WebSocket token extracted: {token[:10]}...") # Log first 10 chars for security
    return token

async def get_current_websocket_user(ws_token: str = Depends(get_websocket_token), db: Session = Depends(database.get_db)):
    return await get_current_user(ws_token, db)

def has_role(user: User, role_name: str) -> bool:
    for role in user.roles:
        if role.name == role_name:
            return True
    return False

def has_permission(user: User, permission_name: str) -> bool:
    for role in user.roles:
        # Assuming role.permissions is List[str] as per schemas.py
        if permission_name in role.permissions:
            return True
    return False

class RoleChecker:
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not any(has_role(current_user, role) for role in self.allowed_roles):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user

class PermissionChecker:
    def __init__(self, required_permissions: List[str]):
        self.required_permissions = required_permissions

    def __call__(self, current_user: User = Depends(get_current_user)):
        if not all(has_permission(current_user, perm) for perm in self.required_permissions):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
        return current_user