import sys
import os
from dotenv import load_dotenv

# --- Path Setup ---
# Ensures the script looks for the database and .env file in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
server_python_dir = os.path.join(project_root, 'server_python')

# Load the .env file from the server_python directory
dotenv_path = os.path.join(server_python_dir, '.env')
if os.path.exists(dotenv_path):
    print(f"Loading environment variables from {dotenv_path}")
    load_dotenv(dotenv_path)
else:
    print(f"Warning: .env file not found at {dotenv_path}")

# Add the project root to the Python path for imports
sys.path.insert(0, project_root)

# Change CWD so the relative database path is resolved correctly
os.chdir(server_python_dir)

from server_python.database import SessionLocal, LLMProvider
from server_python.encryption_utils import encrypt_api_key

# The API key provided by the user
NEW_API_KEY = "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"
PROVIDER_NAME = "OpenRouter"

def update_key():
    """
    Finds the 'OpenRouter' provider and updates its API key.
    """
    db = SessionLocal()
    try:
        provider = db.query(LLMProvider).filter(LLMProvider.name == PROVIDER_NAME).first()
        
        if not provider:
            print(f"ERROR: LLM Provider '{PROVIDER_NAME}' not found in the database.")
            return

        print(f"Found provider '{PROVIDER_NAME}'. Updating API key...")
        
        # Encrypt and update the key
        provider.api_key_encrypted = encrypt_api_key(NEW_API_KEY)
        
        db.commit()
        
        print(f"Successfully updated the API key for '{PROVIDER_NAME}'.")

    except Exception as e:
        print(f"An error occurred: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    update_key()
