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

def assign_enterprise_plan_to_user(username: str, enterprise_plan_id: str):
    db = next(get_db())
    
    user = db.query(User).filter(User.username == username).first()
    if not user:
        print(f"User '{username}' not found.")
        return

    enterprise_plan = db.query(Plan).filter(Plan.id == enterprise_plan_id).first()
    if not enterprise_plan:
        print(f"Enterprise plan with ID '{enterprise_plan_id}' not found.")
        return

    # Deactivate any existing active subscriptions for the user
    existing_active_subscriptions = db.query(UserSubscription).filter(
        UserSubscription.user_id == user.id,
        UserSubscription.status == "active"
    ).all()

    for sub in existing_active_subscriptions:
        sub.status = "cancelled"
        sub.end_date = datetime.utcnow()
        db.add(sub)
    
    # Create a new UserSubscription for the Enterprise plan
    new_subscription = UserSubscription(
        id=str(uuid.uuid4()),
        user_id=user.id,
        plan_id=enterprise_plan.id,
        start_date=datetime.utcnow(),
        end_date=None, # Enterprise plans have no end date
        status="active"
    )
    db.add(new_subscription)
    
    # Update user's demo credits based on the new plan
    user.demo_credits = enterprise_plan.demo_credits if enterprise_plan.demo_credits is not None else 0

    db.commit()
    db.refresh(new_subscription)
    print(f"User '{username}' successfully subscribed to '{enterprise_plan.name}' plan.")
    db.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python assign_enterprise_plan.py <username> <enterprise_plan_id>")
        sys.exit(1)
    
    target_username = sys.argv[1]
    target_enterprise_plan_id = sys.argv[2]
    assign_enterprise_plan_to_user(target_username, target_enterprise_plan_id)
