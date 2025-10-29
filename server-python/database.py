from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    otp_code = Column(String, nullable=True)
    otp_expires_at = Column(DateTime, nullable=True)


# --- Database Utility Functions ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_user_from_db(db, username: str):
    return db.query(User).filter(User.username == username).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user_in_db(db: Session, username: str, hashed_password: str, email: str, otp_code: str, otp_expires_at: datetime):
    db_user = User(username=username, hashed_password=hashed_password, email=email, otp_code=otp_code, otp_expires_at=otp_expires_at)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# This function will be called to set up a default user for testing
def get_user_by_username_or_email(db: Session, identifier: str):
    # Try to find by username first
    user = db.query(User).filter(User.username == identifier).first()
    if user:
        return user
    # If not found by username, try by email
    user = db.query(User).filter(User.email == identifier).first()
    return user

# This function will be called to set up a default user for testing
def setup_default_user(db, get_password_hash_func):
    default_username = "testuser"
    default_password = "testpassword"
    default_email = "test@example.com"
    if not get_user_from_db(db, default_username):
        hashed_password = get_password_hash_func(default_password)
        # For the default user, we can set is_verified to True and OTP fields to None
        db_user = User(username=default_username, hashed_password=hashed_password, email=default_email, is_verified=True, otp_code=None, otp_expires_at=None)
        db.add(db_user)
        db.commit()
    if not get_user_by_email(db, default_email):
        db.refresh(db_user)
        print(f"Default user '{default_username}' created with password '{default_password}'")