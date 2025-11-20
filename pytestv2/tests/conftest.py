import os
import pytest
import sys # Import sys

def pytest_configure(config):
    # Set DATASET_STORAGE_DIR for tests to a writable temporary location
    test_dataset_storage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '.gemini', 'tmp', "neosyntis_datasets_test"))
    os.environ["DATASET_STORAGE_DIR"] = test_dataset_storage_dir
    os.makedirs(test_dataset_storage_dir, exist_ok=True)

    # Add the project root to sys.path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)