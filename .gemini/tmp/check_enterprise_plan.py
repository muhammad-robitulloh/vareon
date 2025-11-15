import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from server_python.database import Base, User, Role, Permission, Plan, UserSubscription # Import your models
import uuid
from datetime import datetime

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

def check_enterprise_plan():
    db = next(get_db())
    enterprise_plan = db.query(Plan).filter(Plan.name == "Enterprise").first()
    
    if enterprise_plan:
        print(f"Enterprise Plan Found:")
        print(f"  ID: {enterprise_plan.id}")
        print(f"  Name: {enterprise_plan.name}")
        print(f"  Price Monthly: {enterprise_plan.price_monthly}")
        print(f"  Price Yearly: {enterprise_plan.price_yearly}")
        print(f"  Max Users: {enterprise_plan.max_users}")
        print(f"  Features: {enterprise_plan.features}")
        print(f"  Demo Credits: {enterprise_plan.demo_credits}")
        return enterprise_plan.id
    else:
        print("Enterprise Plan Not Found.")
        return None
    db.close()

if __name__ == "__main__":
    check_enterprise_plan()
