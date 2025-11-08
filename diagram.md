# Vareon Ecosystem Interconnections Diagram

This document provides a high-level overview of the Vareon backend ecosystem, illustrating the relationships and data flow between its core modules: Arcana, Cognisys, Myntrix, and Neosyntis.

## 1. Core Modules and Their Responsibilities

*   **Core Application (`main.py`)**:
    *   Central API routing and entry point.
    *   User authentication and registration.
    *   Hosts Arcana's core functionalities.
    *   Provides global search across all modules.
*   **Arcana (Integrated into `main.py` and `llm_service.py`)**:
    *   **System Status**: Monitors the health and activity of all Vareon modules.
    *   **Context Memory**: Stores user-specific key-value pairs for contextual awareness.
    *   **LLM Preferences**: Manages user preferences for LLM interactions.
    *   **Terminal Management**: Provides interactive shell sessions.
    *   **Contextual Awareness (in `llm_service.py`)**: Dynamically injects relevant system/user context into LLM prompts.
*   **Cognisys Module**:
    *   **LLM Orchestration & Routing**: Manages LLM Providers and Models.
    *   **Routing Rules**: Implements rules to select the best LLM based on user intent or context.
    *   **Chat Interaction**: Handles user-LLM conversations.
*   **Myntrix Module**:
    *   **Agent & Device Management**: Provides CRUD for Agents and Devices.
    *   **Agent/Device Control**: Handles start/stop/restart of agents, connect/disconnect/command/upload for devices.
    *   **Task Scheduling & Job Monitoring**: Manages scheduled tasks and monitors job execution.
    *   **System Metrics**: Provides real-time system performance data.
*   **Neosyntis Module**:
    *   **Workflow Management**: Manages Workflows (creation, execution, status).
    *   **Dataset Management**: Handles Datasets (upload, download, CRUD).
    *   **Telemetry**: Ingests and retrieves telemetry data.
    *   **ML Model Management**: Manages ML Models (creation, deployment, training).
    *   **Search**: Provides search capabilities across workflows and datasets.

## 2. High-Level Interconnection Diagram

```mermaid
graph TD
    subgraph Core Application (main.py)
        A[User Auth/Reg] --> B(API Router)
        B --> C(Arcana Core)
        B --> D(Cognisys API)
        B --> E(Myntrix API)
        B --> F(Neosyntis API)
        B --> G(Global Search)
    end

    subgraph Arcana (in main.py & llm_service.py)
        C --> H(System Status)
        C --> I(Context Memory)
        C --> J(LLM Preferences)
        C --> K(Terminal Management)
        L(llm_service.py) --> M(Contextual Awareness)
    end

    subgraph Cognisys Module
        D --> N(LLM Providers/Models)
        D --> O(Routing Rules)
        D --> P(Chat Interaction)
    end

    subgraph Myntrix Module
        E --> Q(Agents/Devices CRUD)
        E --> R(Agent/Device Control)
        E --> S(Task Scheduling/Jobs)
        E --> T(System Metrics)
    end

    subgraph Neosyntis Module
        F --> U(Workflow Management)
        F --> V(Dataset Management)
        F --> W(Telemetry)
        F --> X(ML Model Management)
        F --> Y(Search)
    end

    subgraph Database
        DB[(Database)]
    end

    A -- Authenticates --> DB
    C -- Stores/Retrieves --> DB
    D -- Stores/Retrieves --> DB
    E -- Stores/Retrieves --> DB
    F -- Stores/Retrieves --> DB

    P -- Uses --> N
    P -- Applies --> O
    P -- Orchestrates --> R
    P -- Orchestrates --> U

    M -- Enriches Prompts --> P

    R -- Generates --> W
    U -- Controls --> R
    V -- Used by --> R
    V -- Used by --> X

    H -- Aggregates Data From --> N
    H -- Aggregates Data From --> Q
    H -- Aggregates Data From --> S
    H -- Aggregates Data From --> U
    H -- Aggregates Data From --> V
    H -- Aggregates Data From --> X

    G -- Queries --> DB
    G -- Queries --> Q
    G -- Queries --> U
    G -- Queries --> V
    G -- Queries --> O
```

## 3. Detailed Interconnections and Data Flow

### Authentication and Authorization
*   All API endpoints across Cognisys, Myntrix, and Neosyntis modules rely on the central authentication and authorization mechanisms provided by the **Core Application (`main.py`)**.
*   User data (including roles and permissions) is stored in the **Database**.

### Cognisys (LLM Orchestration)
*   **LLM Providers/Models (N)** and **Routing Rules (O)** are managed by Cognisys and stored in the **Database**.
*   **Chat Interaction (P)** uses configured LLM Providers/Models and applies Routing Rules to determine the optimal LLM for a given user query.
*   **Arcana's Contextual Awareness (M)** in `llm_service.py` can enrich the prompts sent by **Chat Interaction (P)** by injecting relevant user context, workflow status, or agent information.
*   **Chat Interaction (P)** can orchestrate actions in other modules, for example:
    *   Triggering **Agent/Device Control (R)** in Myntrix.
    *   Initiating **Workflow Management (U)** in Neosyntis.

### Myntrix (Agents & Devices)
*   **Agents/Devices CRUD (Q)** manages agents and devices, storing their configurations and statuses in the **Database**.
*   **Agent/Device Control (R)** handles real-time operations on agents and devices.
*   **Task Scheduling/Jobs (S)** manages background tasks and job execution, storing job details in the **Database**.
*   **System Metrics (T)** collects real-time performance data from the underlying system.
*   **Telemetry (W)** in Neosyntis can receive data generated by Myntrix agents or devices.

### Neosyntis (Workflows, Data & ML)
*   **Workflow Management (U)** defines and executes workflows, storing their steps and status in the **Database**.
*   **Dataset Management (V)** handles the storage and retrieval of datasets, with metadata stored in the **Database** and actual files on the file system (managed by `storage_service`).
*   **Telemetry (W)** ingests and stores telemetry data in the **Database**.
*   **ML Model Management (X)** handles the lifecycle of ML models (registration, training, deployment), storing metadata in the **Database**.
*   **Search (Y)** queries workflows and datasets stored in the **Database**.
*   **Workflow Management (U)** can control **Agent/Device Control (R)** in Myntrix or utilize **ML Model Management (X)** for training/deployment.

### Arcana (Core Services)
*   **System Status (H)** aggregates real-time data from **LLM Providers/Models (N)**, **Agents/Devices CRUD (Q)**, **Task Scheduling/Jobs (S)**, **Workflow Management (U)**, **Dataset Management (V)**, and **ML Model Management (X)** to provide a comprehensive system overview.
*   **Context Memory (I)** and **LLM Preferences (J)** are stored in the **Database** and used by **Arcana's Contextual Awareness (M)** and **Chat Interaction (P)**.
*   **Terminal Management (K)** interacts with the underlying operating system for shell access and stores command history in the **Database**.

### Global Search
*   The **Global Search (G)** endpoint in the Core Application queries various entities across Myntrix (Agents, Hardware Devices), Neosyntis (Workflows, Datasets), and Cognisys (Routing Rules) from the **Database**.

This diagram and explanation highlight the modular nature of Vareon, where each component has a clear responsibility, but they are tightly integrated through shared data (Database) and API calls to achieve complex functionalities like AI orchestration and system management.