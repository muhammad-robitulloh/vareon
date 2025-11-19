import sys
import os
import uuid

# Add the project root to the Python path to allow for absolute imports
sys.path.insert(0, os.getcwd())

from server_python.database import SessionLocal, ArcanaAgent, User, Base, engine, setup_default_user
from server_python.auth import get_password_hash

def initialize_database():
    """Ensures all tables are created in the database."""
    print("Initializing database... Ensuring all tables exist.")
    Base.metadata.create_all(bind=engine)
    print("Database initialization complete.")

def ensure_agent_exists():
    """
    Checks if any ArcanaAgent exists. If not, creates a default one for 'testuser'.
    Prints the ID of the found or created agent.
    """
    db = SessionLocal()
    try:
        # Ensure the default user exists first
        print("Ensuring default user 'testuser' exists...")
        setup_default_user(db, get_password_hash)
        print("Default user check complete.")

        owner = db.query(User).filter(User.username == 'testuser').first()
        if not owner:
            print("ERROR: Default user 'testuser' could not be found or created. Cannot proceed.")
            return

        agent = db.query(ArcanaAgent).filter(ArcanaAgent.owner_id == str(owner.id)).first()
        
        if agent:
            print(f"AGENT_ID={agent.id}")
            return

        # If no agent exists for the user, create one
        print("No Arcana agent found for 'testuser'. Creating a default worker agent...")
        
        new_agent_id = str(uuid.uuid4())
        new_agent = ArcanaAgent(
            id=new_agent_id,
            owner_id=str(owner.id),
            name="Default Worker Agent",
            persona="A reliable worker agent that executes tasks.",
            mode="tool_user", # Must be 'tool_user' or 'autonomous' to use tools
            status="idle"
        )
        
        db.add(new_agent)
        db.commit()
        
        print(f"AGENT_ID={new_agent.id}")

    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()
    ensure_agent_exists()
