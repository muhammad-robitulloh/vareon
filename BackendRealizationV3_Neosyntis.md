# Backend Realization V3: Neosyntis Dashboard

This document outlines the roadmap and checklist for implementing the full backend functionality for the Neosyntis Dashboard. The current frontend components for Neosyntis are using mock data, and the goal of this phase is to replace that with a robust, database-backed backend.

## Roadmap Overview

The realization of the Neosyntis Dashboard backend will proceed in several key stages:

1.  **Database Integration for Core Entities**: Transitioning `Workflow` and `Dataset` entities from in-memory storage to persistent database storage.
2.  **API Endpoint Enhancement**: Expanding existing Neosyntis API endpoints and creating new ones to support CRUD (Create, Read, Update, Delete) operations and advanced functionalities for Workflows, Datasets, and other Neosyntis-specific features.
3.  **Business Logic Implementation**: Developing the core logic for workflow execution, dataset processing, model deployment, and telemetry data handling.
4.  **Integration with Other Modules**: Ensuring seamless interaction with Myntrix (for hardware/agents), Cognisys (for routing), and Arcana (for chat/LLM).
5.  **Telemetry and Monitoring**: Implementing real-time data collection and aggregation for the Neosyntis Telemetry tab.
6.  **Search Functionality**: Developing a backend search service for Neosyntis resources.

## Stage 1: Database Integration for Core Entities (Workflows & Datasets)

This stage focuses on replacing the in-memory `simulated_workflows` and `simulated_datasets` with proper database models and operations.

### Checklist:

#### 1. Workflows
*   **Database Model (`database.py` / `models.py`)**:
    *   Define SQLAlchemy model for `Workflow` with fields: `id` (UUID), `name` (string), `description` (optional string), `status` (enum: `pending`, `running`, `completed`, `failed`), `steps` (JSON/array of strings), `created_at` (datetime), `updated_at` (datetime), `owner_id` (foreign key to User).
    *   Consider a separate `WorkflowStep` model if steps require more complex attributes (e.g., status per step, parameters).
*   **Pydantic Schemas (`schemas.py`)**:
    *   Update `Workflow` schema to reflect database model.
    *   Create `WorkflowCreate` schema for new workflow creation.
    *   Create `WorkflowUpdate` schema for updating existing workflows.
*   **CRUD API Endpoints (`main.py`)**:
    *   `POST /api/neosyntis/workflows`: Create a new workflow.
        *   Input: `WorkflowCreate` schema.
        *   Output: Created `Workflow` object.
        *   Logic: Store in DB, assign owner.
    *   `GET /api/neosyntis/workflows`: List all workflows (with optional filtering/pagination).
        *   Output: List of `Workflow` objects.
        *   Logic: Fetch from DB.
    *   `GET /api/neosyntis/workflows/{workflow_id}`: Get a specific workflow by ID.
        *   Output: `Workflow` object.
        *   Logic: Fetch from DB.
    *   `PUT /api/neosyntis/workflows/{workflow_id}`: Update an existing workflow.
        *   Input: `WorkflowUpdate` schema.
        *   Output: Updated `Workflow` object.
        *   Logic: Update in DB.
    *   `DELETE /api/neosyntis/workflows/{workflow_id}`: Delete a workflow.
        *   Logic: Delete from DB.
    *   `POST /api/neosyntis/workflows/{workflow_id}/trigger`: Trigger workflow execution.
        *   Logic: Update workflow status to `running`, initiate background task for execution (placeholder for now).
    *   `GET /api/neosyntis/workflows/{workflow_id}/status`: Get workflow execution status.
        *   Logic: Fetch status from DB.
*   **Business Logic (New module, e.g., `neosyntis_service.py`)**:
    *   Placeholder for workflow execution logic (e.g., a function `execute_workflow(workflow_id)` that simulates steps and updates status).

#### 2. Datasets
*   **Database Model (`database.py` / `models.py`)**:
    *   Define SQLAlchemy model for `Dataset` with fields: `id` (UUID), `name` (string), `description` (optional string), `file_path` (string, path to stored file), `size_bytes` (integer), `format` (string), `uploaded_at` (datetime), `owner_id` (foreign key to User).
    *   Consider fields for metadata, tags, access control.
*   **Pydantic Schemas (`schemas.py`)**:
    *   Update `Dataset` schema to reflect database model.
    *   Create `DatasetCreate` schema for new dataset creation (might include file upload details).
    *   Create `DatasetUpdate` schema for updating dataset metadata.
*   **CRUD API Endpoints (`main.py`)**:
    *   `POST /api/neosyntis/datasets/upload`: Upload a new dataset.
        *   Input: `DatasetCreate` schema + actual file upload (using `UploadFile` from FastAPI).
        *   Output: Created `Dataset` object.
        *   Logic: Save file to a designated storage location, store metadata in DB, assign owner.
    *   `GET /api/neosyntis/datasets`: List all datasets (with optional filtering/pagination).
        *   Output: List of `Dataset` objects.
        *   Logic: Fetch from DB.
    *   `GET /api/neosyntis/datasets/{dataset_id}`: Get a specific dataset by ID.
        *   Output: `Dataset` object.
        *   Logic: Fetch from DB.
    *   `PUT /api/neosyntis/datasets/{dataset_id}`: Update dataset metadata.
        *   Input: `DatasetUpdate` schema.
        *   Output: Updated `Dataset` object.
        *   Logic: Update metadata in DB.
    *   `DELETE /api/neosyntis/datasets/{dataset_id}`: Delete a dataset.
        *   Logic: Delete file from storage, delete metadata from DB.
    *   `GET /api/neosyntis/datasets/{dataset_id}/download`: Download a dataset.
        *   Output: File stream.
        *   Logic: Retrieve file from storage and stream it.
*   **Storage Logic (New module, e.g., `storage_service.py`)**:
    *   Functions for saving, retrieving, and deleting files from a configured storage location (e.g., local filesystem, S3, etc.).

## Stage 2: Advanced Neosyntis Features

This stage focuses on implementing the backend for the remaining Neosyntis Dashboard tabs.

### Checklist:

#### 1. Telemetry
*   **Database Model (`database.py` / `models.py`)**:
    *   Define `TelemetryData` model (e.g., `timestamp`, `metric_name`, `value`, `workflow_id`/`dataset_id`/`device_id` for context).
*   **API Endpoints (`main.py`)**:
    *   `GET /api/neosyntis/telemetry`: Retrieve aggregated telemetry data (e.g., for charts).
        *   Input: Query parameters for time range, metric type, aggregation level.
        *   Output: Aggregated telemetry data.
    *   `POST /api/neosyntis/telemetry/ingest`: Endpoint for internal services/agents to push telemetry data.
*   **Business Logic (`neosyntis_service.py` / `telemetry_service.py`)**:
    *   Logic for aggregating and querying telemetry data efficiently.

#### 2. Search Engine
*   **API Endpoint (`main.py`)**:
    *   `GET /api/neosyntis/search`: Search across Neosyntis entities (workflows, datasets, models).
        *   Input: `query` string, `entity_type` filter.
        *   Output: List of search results.
*   **Business Logic (`search_service.py`)**:
    *   Integration with a search engine (e.g., Elasticsearch, or simple LIKE queries for initial implementation).
    *   Indexing logic for workflows, datasets, and models.

#### 3. Model Deployment & Machine Learning
*   **Database Model (`database.py` / `models.py`)**:
    *   Define `MLModel` model (e.g., `id`, `name`, `version`, `status`, `path_to_model_artifact`, `training_dataset_id`, `deployed_at`, `owner_id`).
    *   Define `TrainingJob` model (e.g., `id`, `model_id`, `status`, `start_time`, `end_time`, `metrics`).
*   **Pydantic Schemas (`schemas.py`)**:
    *   `MLModel`, `MLModelCreate`, `MLModelUpdate`.
    *   `TrainingJob`, `TrainingJobCreate`.
*   **API Endpoints (`main.py`)**:
    *   `POST /api/neosyntis/models`: Upload/register a new ML model.
    *   `GET /api/neosyntis/models`: List all ML models.
    *   `GET /api/neosyntis/models/{model_id}`: Get model details.
    *   `POST /api/neosyntis/models/{model_id}/deploy`: Deploy a model to an inference endpoint.
    *   `POST /api/neosyntis/models/{model_id}/train`: Start a training job for a model.
    *   `GET /api/neosyntis/training-jobs`: List training jobs.
    *   `GET /api/neosyntis/training-jobs/{job_id}`: Get training job details.
*   **Business Logic (`ml_service.py`)**:
    *   Integration with ML frameworks/platforms (e.g., MLflow, Kubeflow, or custom inference server).
    *   Logic for model versioning, deployment, and monitoring.
    *   Logic for managing training jobs.

#### 4. Ecosystem Builder & Device Settings
*   **Ecosystem Builder**: This is highly dependent on its intended functionality. If it's about connecting different Vareon modules or external services, it would involve:
    *   **Database Model**: `Integration` or `ServiceConnection` model.
    *   **API Endpoints**: CRUD for integrations.
    *   **Business Logic**: Logic for establishing and managing connections.
*   **Device Settings**: If distinct from Myntrix hardware:
    *   **Database Model**: `NeosyntisDevice` model (if specific to Neosyntis).
    *   **API Endpoints**: CRUD for Neosyntis devices.
    *   **Business Logic**: Device configuration management.

#### 5. Cognisys Configuration
*   The existing `/api/cognisys/routing-rules` endpoints are already quite comprehensive.
*   **Enhancement**: Ensure these endpoints are backed by a database and not just in-memory storage.
    *   **Database Model**: Define `RoutingRule` model in `database.py` (if not already done).
    *   **API Endpoints**: Modify existing endpoints to interact with the database.

## General Considerations for All Stages:

*   **Authentication and Authorization**: Ensure all new and updated endpoints are protected by appropriate authentication (`Depends(get_current_user)`) and authorization (`PermissionChecker`) as per existing patterns.
*   **Error Handling**: Implement robust error handling for database operations, file operations, and external service calls.
*   **Logging**: Ensure comprehensive logging for all critical operations and errors.
*   **Testing**: Write unit and integration tests for all new database models, services, and API endpoints.
*   **Scalability**: Design with scalability in mind, especially for data-intensive operations like dataset processing and workflow execution (e.g., using background tasks, message queues).
*   **Configuration**: Externalize sensitive information and configurable parameters (e.g., storage paths, external service URLs) using environment variables or a configuration management system.
*   **Documentation**: Update API documentation (e.g., OpenAPI/Swagger generated by FastAPI) as new endpoints are added.

This roadmap and checklist provide a structured approach to fully implementing the Neosyntis Dashboard backend, moving from mock data to a production-ready system.
