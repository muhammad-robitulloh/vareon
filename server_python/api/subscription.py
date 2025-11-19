
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, timedelta
from pydantic import BaseModel
import uuid

from server_python import database, schemas
from server_python.auth import get_current_user
from sqlalchemy.orm import joinedload # Add this import

logger = logging.getLogger(__name__)
router = APIRouter(
    prefix="/api/subscriptions",
    tags=["Subscriptions"],
    responses={404: {"description": "Not found"}},
)

class PlanSelectRequest(BaseModel):
    plan_id: uuid.UUID

@router.get("/plans", response_model=List[schemas.Plan])
def get_all_plans(db: Session = Depends(database.get_db)):
    """
    Get a list of all available subscription plans.
    """
    logger.info("Fetching all available subscription plans.")
    plans = db.query(database.Plan).order_by(database.Plan.price_monthly).all()
    return plans

@router.get("/my-plan", response_model=schemas.UserSubscription)
def get_my_subscription(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Get the current user's active subscription plan.
    """
    logger.info(f"Fetching current subscription for user {current_user.id}.")
    
    # Find the most recent active subscription
    subscription = db.query(database.UserSubscription).filter(
        database.UserSubscription.user_id == str(current_user.id),
        database.UserSubscription.status == "active"
    ).order_by(database.UserSubscription.start_date.desc()).first()

    if not subscription:
        logger.warning(f"No active subscription found for user {current_user.id}. Defaulting to Free Trial.")
        # If no subscription, create a "Free Trial" one for them
        free_plan = db.query(database.Plan).filter(database.Plan.name == "Free Trial").first()
        if not free_plan:
            logger.error("CRITICAL: 'Free Trial' plan not found in database.")
            raise HTTPException(status_code=500, detail="Default plan configuration is missing.")
        
        subscription = database.UserSubscription(
            user_id=str(current_user.id),
            plan_id=str(free_plan.id),
            status="active"
        )
        db.add(subscription)
        
        # Also update the user's demo credits
        user_db = db.query(database.User).filter(database.User.id == str(current_user.id)).first()
        if user_db:
            user_db.demo_credits = free_plan.demo_credits
        
        db.commit()
        db.refresh(subscription)

    return subscription

@router.post("/select-plan", response_model=schemas.UserSubscription)
def select_plan(
    request: PlanSelectRequest,
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Select a new subscription plan for the current user.
    This is a mock endpoint and does not process payments.
    """
    logger.info(f"User {current_user.id} is selecting plan {request.plan_id}.")
    
    plan_to_assign = db.query(database.Plan).filter(database.Plan.id == str(request.plan_id)).first()
    if not plan_to_assign:
        logger.error(f"User {current_user.id} tried to select non-existent plan {request.plan_id}.")
        raise HTTPException(status_code=404, detail="Plan not found.")

    # Deactivate any existing active subscriptions
    existing_subs = db.query(database.UserSubscription).filter(
        database.UserSubscription.user_id == str(current_user.id),
        database.UserSubscription.status == "active"
    )
    for sub in existing_subs:
        logger.info(f"Deactivating old subscription {sub.id} for user {current_user.id}.")
        sub.status = "cancelled"
        sub.end_date = datetime.utcnow()

    # Create the new subscription
    new_subscription = database.UserSubscription(
        user_id=str(current_user.id),
        plan_id=str(plan_to_assign.id),
        status="active",
        # Set an end date for non-enterprise plans for this example
        end_date=datetime.utcnow() + timedelta(days=30) if plan_to_assign.name != "Enterprise" else None
    )
    db.add(new_subscription)
    
    user_db = db.query(database.User).options(joinedload(database.User.roles)).filter(database.User.id == str(current_user.id)).first()
    if user_db:
        user_db.demo_credits = plan_to_assign.demo_credits if plan_to_assign.demo_credits is not None else 0

        # --- Role Assignment Logic ---
        admin_role = db.query(database.Role).filter(database.Role.name == "admin").first()
        if not admin_role:
            logger.warning("Admin role not found in database. Creating it.")
            admin_role = database.Role(name="admin")
            db.add(admin_role)
            db.flush() # Flush to get the ID for the new role

            # Ensure 'admin_access' permission exists and assign it to the admin role
            admin_access_perm = db.query(database.Permission).filter(database.Permission.name == "admin_access").first()
            if not admin_access_perm:
                logger.warning("Admin access permission not found in database. Creating it.")
                admin_access_perm = database.Permission(name="admin_access")
                db.add(admin_access_perm)
                db.flush() # Flush to get the ID for the new permission

            if admin_access_perm not in admin_role.permissions:
                admin_role.permissions.append(admin_access_perm)
                logger.info("Assigned 'admin_access' permission to 'admin' role.")

        if plan_to_assign.name == "Enterprise":
            if admin_role not in user_db.roles:
                user_db.roles.append(admin_role)
                logger.info(f"Assigned 'admin' role to user {current_user.id} due to Enterprise plan.")
        else:
            if admin_role in user_db.roles:
                user_db.roles.remove(admin_role)
                logger.info(f"Removed 'admin' role from user {current_user.id} due to non-Enterprise plan.")
        # --- End Role Assignment Logic ---

    db.commit()
    db.refresh(new_subscription)
    logger.info(f"Successfully subscribed user {current_user.id} to plan '{plan_to_assign.name}'.")
    
    return new_subscription

@router.post("/skip", response_model=schemas.UserSubscription)
def skip_plan_selection(
    current_user: schemas.User = Depends(get_current_user),
    db: Session = Depends(database.get_db)
):
    """
    Skips plan selection and assigns the default 'Free Trial' plan.
    """
    logger.info(f"User {current_user.id} skipped plan selection. Assigning Free Trial.")
    
    free_plan = db.query(database.Plan).filter(database.Plan.name == "Free Trial").first()
    if not free_plan:
        logger.error("CRITICAL: 'Free Trial' plan not found in database during skip.")
        raise HTTPException(status_code=500, detail="Default plan configuration is missing.")

    # Check if user already has an active subscription
    existing_sub = db.query(database.UserSubscription).filter(
        database.UserSubscription.user_id == str(current_user.id),
        database.UserSubscription.status == "active"
    ).first()

    if existing_sub:
        logger.info(f"User {current_user.id} already has an active subscription. No action taken on skip.")
        return existing_sub

    # Assign the free trial plan
    trial_subscription = database.UserSubscription(
        user_id=str(current_user.id),
        plan_id=str(free_plan.id),
        status="active"
    )
    db.add(trial_subscription)
    
    user_db = db.query(database.User).filter(database.User.id == str(current_user.id)).first()
    if user_db:
        user_db.demo_credits = free_plan.demo_credits
    
    db.commit()
    db.refresh(trial_subscription)
    logger.info(f"Successfully assigned Free Trial plan to user {current_user.id}.")

    return trial_subscription
