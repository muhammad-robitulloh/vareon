import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server_python.database import Base, User, Role, Permission # Import your models

SQLALCHEMY_DATABASE_URL = "sqlite:///./server_python/sql_app.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def assign_admin_role_to_user(username: str):
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()
    admin_role = db.query(Role).filter(Role.name == "admin").first()

    if not user:
        print(f"User '{username}' not found.")
        return
    if not admin_role:
        print("Admin role not found. Please ensure it exists in the database.")
        return

    if admin_role not in user.roles:
        user.roles.append(admin_role)
        db.commit()
        print(f"Admin role assigned to user '{username}'.")
    else:
        print(f"User '{username}' already has the admin role.")
    
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python assign_admin_role.py <username>")
        sys.exit(1)
    
    target_username = sys.argv[1]
    assign_admin_role_to_user(target_username)
