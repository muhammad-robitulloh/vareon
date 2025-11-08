import os
from cryptography.fernet import Fernet

# Load Fernet key from environment variable
FERNET_KEY = os.getenv("FERNET_KEY")
if FERNET_KEY is None:
    # Generate a key if not found (for development/testing)
    # In production, this should be securely managed and loaded.
    FERNET_KEY = Fernet.generate_key().decode()
    print("WARNING: FERNET_KEY not found in environment. Generating a new one. "
          "This is INSECURE for production. Please set FERNET_KEY environment variable.")
    # Optionally, save it to .env for local development
    with open(".env", "a") as f:
        f.write(f"\nFERNET_KEY={FERNET_KEY}\n")

f = Fernet(FERNET_KEY)

def encrypt_api_key(api_key: str) -> str:
    return f.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: str) -> str:
    return f.decrypt(encrypted_api_key.encode()).decode()
