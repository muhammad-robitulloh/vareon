from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import sessionmaker, Session, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional, List

SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Association table for User-Role many-to-many relationship
user_roles = Table(
    'user_roles',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True)
)

# Association table for Role-Permission many-to-many relationship
role_permissions = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    permissions = relationship("Permission", secondary=role_permissions, backref="roles")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    verification_token_expires_at = Column(DateTime, nullable=True)
    roles = relationship("Role", secondary=user_roles, backref="users")


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

def create_user_in_db(db: Session, username: str, hashed_password: str, email: str, verification_token: str, verification_token_expires_at: datetime):
    db_user = User(username=username, hashed_password=hashed_password, email=email, verification_token=verification_token, verification_token_expires_at=verification_token_expires_at)
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

def get_permission_by_name(db: Session, name: str):
    return db.query(Permission).filter(Permission.name == name).first()

def create_permission(db: Session, name: str):
    db_permission = Permission(name=name)
    db.add(db_permission)
    db.commit()
    db.refresh(db_permission)
    return db_permission

def get_role_by_name(db: Session, name: str):
    return db.query(Role).filter(Role.name == name).first()

def create_role(db: Session, name: str, permission_names: List[str] = []):
    db_role = get_role_by_name(db, name)
    if db_role:
        return db_role
    
    db_role = Role(name=name)
    for perm_name in permission_names:
        permission = get_permission_by_name(db, perm_name)
        if not permission:
            permission = create_permission(db, perm_name)
        db_role.permissions.append(permission)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

# This function will be called to set up a default user for testing
def setup_default_user(db, get_password_hash_func):
    default_username = "testuser"
    default_password = "testpassword"
    default_email = "test@example.com"
    
    # Create default permissions if they don't exist
    admin_permission = get_permission_by_name(db, "admin_access") or create_permission(db, "admin_access")
    
    # Create default roles if they don't exist
    admin_role = get_role_by_name(db, "admin") or create_role(db, "admin", ["admin_access"])

    db_user = get_user_from_db(db, default_username)
    if not db_user:
        hashed_password = get_password_hash_func(default_password)
        db_user = User(username=default_username, hashed_password=hashed_password, email=default_email, is_verified=True, verification_token=None, verification_token_expires_at=None)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    
    # Assign admin role to default user if not already assigned
    if admin_role not in db_user.roles:
        db_user.roles.append(admin_role)
        db.commit()
        db.refresh(db_user)

    if not get_user_by_email(db, default_email):
        print(f"Default user '{default_username}' created with password '{default_password}'")