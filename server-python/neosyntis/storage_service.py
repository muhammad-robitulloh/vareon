import os
from fastapi import UploadFile
from typing import Optional

# Configure the base directory for dataset storage
# This should ideally be configurable via environment variables
DATASET_STORAGE_DIR = os.getenv("DATASET_STORAGE_DIR", "/tmp/neosyntis_datasets")

# Ensure the storage directory exists
os.makedirs(DATASET_STORAGE_DIR, exist_ok=True)

async def save_dataset_file(file: UploadFile, dataset_id: str) -> str:
    """
    Saves an uploaded file to the local filesystem.
    Returns the full path to the saved file.
    """
    file_extension = file.filename.split(".")[-1] if "." in file.filename else "bin"
    file_name = f"{dataset_id}.{file_extension}"
    file_path = os.path.join(DATASET_STORAGE_DIR, file_name)

    try:
        with open(file_path, "wb") as buffer:
            while True:
                chunk = await file.read(1024 * 1024)  # Read in 1MB chunks
                if not chunk:
                    break
                buffer.write(chunk)
        return file_path
    except IOError as e:
        print(f"Error saving file {file_path}: {e}")
        raise Exception(f"Failed to save dataset file: {e}")
    except Exception as e:
        print(f"An unexpected error occurred while saving file {file_path}: {e}")
        raise Exception(f"An unexpected error occurred: {e}")

def get_dataset_file_path(dataset_id: str, file_extension: str) -> str:
    """
    Constructs the expected file path for a dataset.
    """
    file_name = f"{dataset_id}.{file_extension}"
    return os.path.join(DATASET_STORAGE_DIR, file_name)

def delete_dataset_file(file_path: str) -> bool:
    """
    Deletes a dataset file from the local filesystem.
    Returns True if successful, False otherwise.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"Error deleting file {file_path}: {e}")
        return False