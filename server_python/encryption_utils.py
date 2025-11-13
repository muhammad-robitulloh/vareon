import os
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional

# Load Fernet key from environment variable
FERNET_KEY = os.getenv("FERNET_KEY")
if FERNET_KEY is None:
    raise ValueError("FERNET_KEY environment variable not set. Please set it for encryption/decryption.")

f = Fernet(FERNET_KEY)

def encrypt_api_key(api_key: str) -> str:
    return f.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: Optional[str]) -> str:
    if not encrypted_api_key:
        return ""
    try:
        return f.decrypt(encrypted_api_key.encode()).decode()
    except InvalidToken:
        # Log the error or handle it as appropriate, for now return empty string
        return ""
