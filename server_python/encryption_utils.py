import os
from cryptography.fernet import Fernet, InvalidToken
from typing import Optional
import logging

logger = logging.getLogger(__name__)

def get_fernet_suite() -> Optional[Fernet]:
    """
    Initializes and returns a Fernet suite from the environment variable.
    Returns None if the key is not set.
    """
    fernet_key = os.getenv("FERNET_KEY")
    if not fernet_key:
        logger.error("CRITICAL: FERNET_KEY environment variable not set or is empty.")
        return None
    try:
        return Fernet(fernet_key.encode())
    except (ValueError, TypeError):
        logger.error("CRITICAL: FERNET_KEY is invalid and cannot be used to initialize Fernet suite.")
        return None

def encrypt_api_key(api_key: str) -> str:
    """Encrypts an API key using the application's FERNET_KEY."""
    if not api_key:
        return ""
    f = get_fernet_suite()
    if not f:
        # This will cause encryption to fail if the key is not set, which is intended.
        raise ValueError("Cannot encrypt: Fernet suite could not be initialized.")
    return f.encrypt(api_key.encode()).decode()

def decrypt_api_key(encrypted_api_key: Optional[str]) -> str:
    """Decrypts an API key using the application's FERNET_KEY."""
    if not encrypted_api_key:
        return ""
    
    f = get_fernet_suite()
    if not f:
        # If the key is not set, decryption is impossible.
        return ""
        
    try:
        return f.decrypt(encrypted_api_key.encode()).decode()
    except InvalidToken:
        # This is a critical error, indicating a key mismatch or corrupt data.
        logger.error(
            "CRITICAL DECRYPTION ERROR: InvalidToken. "
            "This means the data was encrypted with a DIFFERENT FERNET_KEY. "
            "The key in your .env file does not match the key used for encryption."
        )
        return ""
    except Exception as e:
        logger.error(f"An unexpected decryption error occurred: {e}")
        return ""
