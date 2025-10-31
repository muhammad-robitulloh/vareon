import os
import hashlib
import random
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from typing import Optional

from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from schemas import TokenData # Changed from relative to absolute import
from database import get_user_from_db, get_db, User # Changed from relative to absolute import

load_dotenv()

# --- Configuration ---
SECRET_KEY = os.getenv("SECRET_KEY", "your-super-secret-key")  # CHANGE THIS IN PRODUCTION!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

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
def generate_otp():
    return str(random.randint(100000, 999999))

def send_verification_email(email: str, otp: str):
    msg = MIMEText(f"Your OTP for Vareon email verification is: {otp}")
    msg['Subject'] = "Vareon Email Verification"
    msg['From'] = SENDER_EMAIL
    msg['To'] = email

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        print(f"Verification email sent to {email}")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Error sending verification email to {email}: SMTP Authentication Error - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send verification email: Authentication failed. Check SMTP credentials.")
    except smtplib.SMTPServerDisconnected as e:
        print(f"Error sending verification email to {email}: SMTP Server Disconnected - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send verification email: SMTP server disconnected unexpectedly.")
    except smtplib.SMTPException as e:
        print(f"Error sending verification email to {email}: SMTP Error - {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send verification email: SMTP error occurred.")
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

async def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email not verified. Please check your email for a verification code."
        )
    return user