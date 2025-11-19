import sys
import os
import uuid
from dotenv import load_dotenv

# --- Path Setup ---
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
server_python_dir = os.path.join(project_root, 'server_python')
dotenv_path = os.path.join(server_python_dir, '.env')

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path=dotenv_path)

sys.path.insert(0, project_root)
os.chdir(server_python_dir)

from server_python.database import SessionLocal, LLMModel, LLMProvider, User, UserLLMPreference

NEW_DEFAULT_MODEL_NAME = "mistralai/mistral-7b-instruct:free"
PROVIDER_NAME = "OpenRouter"
USER_NAME = "testuser"

def change_default_model():
    """
    Adds the new default model if it doesn't exist and sets it as the
    preference for the specified user.
    """
    db = SessionLocal()
    try:
        # 1. Get the OpenRouter provider
        provider = db.query(LLMProvider).filter(LLMProvider.name == PROVIDER_NAME).first()
        if not provider:
            print(f"ERROR: Provider '{PROVIDER_NAME}' not found.")
            return

        # 2. Find or create the new default model
        new_model = db.query(LLMModel).filter(LLMModel.model_name == NEW_DEFAULT_MODEL_NAME).first()
        if not new_model:
            print(f"Model '{NEW_DEFAULT_MODEL_NAME}' not found. Creating it...")
            new_model = LLMModel(
                id=str(uuid.uuid4()),
                provider_id=provider.id,
                model_name=NEW_DEFAULT_MODEL_NAME,
                type="chat",
                is_active=True,
                reasoning=True,
                role="general"
            )
            db.add(new_model)
            db.commit()
            db.refresh(new_model)
            print(f"Successfully created new model with ID: {new_model.id}")
        else:
            print(f"Model '{NEW_DEFAULT_MODEL_NAME}' already exists with ID: {new_model.id}")

        # 3. Get the user
        user = db.query(User).filter(User.username == USER_NAME).first()
        if not user:
            print(f"ERROR: User '{USER_NAME}' not found.")
            return

        # 4. Find or create the user's preferences and update the default model
        user_prefs = db.query(UserLLMPreference).filter(UserLLMPreference.user_id == str(user.id)).first()
        if not user_prefs:
            print(f"No preferences found for '{USER_NAME}'. Creating new preference entry.")
            user_prefs = UserLLMPreference(user_id=str(user.id))
            db.add(user_prefs)
        
        user_prefs.default_model_id = new_model.id
        db.commit()
        
        print(f"\nSUCCESS: Successfully set '{NEW_DEFAULT_MODEL_NAME}' as the default model for user '{USER_NAME}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    change_default_model()
