import sys
import os

# --- Path Setup ---
# Ensures the script looks for the database in the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
server_python_dir = os.path.join(project_root, 'server_python')
sys.path.insert(0, project_root)
os.chdir(server_python_dir)

from server_python.database import SessionLocal, LLMProvider

PROVIDER_NAME = "OpenRouter"

def verify_key():
    """
    Finds the 'OpenRouter' provider and prints its encrypted API key.
    """
    db = SessionLocal()
    try:
        provider = db.query(LLMProvider).filter(LLMProvider.name == PROVIDER_NAME).first()
        
        if not provider:
            print(f"VERIFICATION_FAILED: Provider '{PROVIDER_NAME}' not found.")
            return

        print(f"Found provider '{PROVIDER_NAME}'.")
        
        encrypted_key = provider.api_key_encrypted
        
        if not encrypted_key:
            print("VERIFICATION_FAILED: The 'api_key_encrypted' field is empty or null.")
        else:
            print(f"VERIFICATION_SUCCESS: Encrypted key found: {encrypted_key}")

    except Exception as e:
        print(f"An error occurred during verification: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify_key()
