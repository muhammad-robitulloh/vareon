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

def check_user_permissions(username: str):
    db = next(get_db())
    user = db.query(User).filter(User.username == username).first()

    if user:
        print(f"User: {user.username}")
        if user.roles:
            print("Roles:")
            for role in user.roles:
                print(f"  - {role.name}")
                if role.permissions:
                    print("    Permissions:")
                    for permission in role.permissions:
                        print(f"      - {permission.name}")
                else:
                    print("    No permissions assigned to this role.")
        else:
            print("No roles assigned to this user.")
    else:
        print(f"User '{username}' not found.")

if __name__ == "__main__":
    check_user_permissions("mrbtlhh")
