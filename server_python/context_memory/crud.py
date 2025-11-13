import json
from sqlalchemy.orm import Session
from typing import List, Dict, Any
import uuid

from server_python.database import ContextMemory as DBContextMemory
from . import schemas

CONTEXT_KEY_PREFIXES = {
    "preference": "pref:",
    "project": "proj:",
    "conversation": "conv:",
}

def get_all_context_for_user(db: Session, user_id: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Retrieves all context for a user and categorizes it.
    """
    db_items = db.query(DBContextMemory).filter(DBContextMemory.user_id == user_id).all()
    
    categorized_context = {
        "userPreferences": [],
        "projectKnowledge": [],
        "conversationSnippets": [],
    }

    for item in db_items:
        try:
            value_dict = json.loads(item.value)
            value_dict['id'] = item.id # Add the DB id to the object
            
            if item.key.startswith(CONTEXT_KEY_PREFIXES["preference"]):
                categorized_context["userPreferences"].append(value_dict)
            elif item.key.startswith(CONTEXT_KEY_PREFIXES["project"]):
                categorized_context["projectKnowledge"].append(value_dict)
            elif item.key.startswith(CONTEXT_KEY_PREFIXES["conversation"]):
                categorized_context["conversationSnippets"].append(value_dict)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON for context item {item.id}")
            continue
            
    return categorized_context

def create_context_item(db: Session, user_id: str, key: str, value: Dict[str, Any]) -> DBContextMemory:
    """
    Creates a new context item.
    """
    db_item = DBContextMemory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        key=key,
        value=json.dumps(value)
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

def delete_context_item(db: Session, item_id: str, user_id: str) -> bool:
    """
    Deletes a context item by its ID.
    """
    db_item = db.query(DBContextMemory).filter(DBContextMemory.id == item_id, DBContextMemory.user_id == user_id).first()
    if db_item:
        db.delete(db_item)
        db.commit()
        return True
    return False

def update_context_item(db: Session, item_id: str, user_id: str, value: Dict[str, Any]) -> DBContextMemory:
    """
    Updates a context item's value.
    """
    db_item = db.query(DBContextMemory).filter(DBContextMemory.id == item_id, DBContextMemory.user_id == user_id).first()
    if db_item:
        db_item.value = json.dumps(value)
        db.commit()
        db.refresh(db_item)
        return db_item
    return None
