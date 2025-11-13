from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from server_python.database import get_db, User as DBUser
from ..auth import get_current_user
from . import crud, schemas

router = APIRouter()

@router.get("/", response_model=schemas.FullContextResponse)
def get_full_user_context(
    current_user: DBUser = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    """
    Retrieve all categorized context memory for the current user.
    """
    user_id = str(current_user.id)
    all_context = crud.get_all_context_for_user(db, user_id=user_id)
    return all_context

class CreateItemPayload(BaseModel):
    type: str # 'preference', 'project', or 'conversation'
    key: str # e.g., "Preferred Language"
    value: Dict[str, Any]

@router.post("/item", status_code=status.HTTP_201_CREATED)
def create_new_context_item(
    payload: CreateItemPayload,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new context item of a specific type.
    """
    user_id = str(current_user.id)
    prefix = crud.CONTEXT_KEY_PREFIXES.get(payload.type)
    if not prefix:
        raise HTTPException(status_code=400, detail="Invalid context type specified.")
    
    # The 'key' from payload is the human-readable part. The DB key is prefix + readable key.
    db_key = f"{prefix}{payload.key}"
    
    # The value from payload is the JSON object itself.
    db_item = crud.create_context_item(db, user_id=user_id, key=db_key, value=payload.value)
    
    # Return the created object, adding the id back to the value dict for the response
    response_value = payload.value.copy()
    response_value['id'] = db_item.id
    return response_value

@router.delete("/item/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_context_item(
    item_id: str,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete a specific context item by its ID.
    """
    user_id = str(current_user.id)
    success = crud.delete_context_item(db, item_id=item_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Context item not found.")
    return {"ok": True}

class UpdateItemPayload(BaseModel):
    value: Dict[str, Any]

@router.put("/item/{item_id}")
def update_context_item(
    item_id: str,
    payload: UpdateItemPayload,
    current_user: DBUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update the value of a specific context item.
    """
    user_id = str(current_user.id)
    updated_item = crud.update_context_item(db, item_id=item_id, user_id=user_id, value=payload.value)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Context item not found.")
    
    response_value = payload.value.copy()
    response_value['id'] = updated_item.id
    return response_value
