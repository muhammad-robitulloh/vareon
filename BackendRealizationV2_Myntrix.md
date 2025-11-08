# Backend Realization V2: Myntrix Dashboard

**Goal:** Implement the full backend for the Myntrix Dashboard, moving all mock data and mock functionalities to a live, production-ready backend. This document outlines the roadmap and a detailed checklist for the second phase of backend implementation, focusing exclusively on the Myntrix Dashboard components.

---

## Phase 2: Myntrix Dashboard Backend Implementation

### Roadmap:

1.  **Core Infrastructure & Setup:** (Assuming this is already established from V1 Cognisys)
    *   Continue utilizing the existing API framework (e.g., FastAPI, Express.js) and database connection/ORM.
    *   Ensure proper modularization for Myntrix-specific functionalities within the backend project.

2.  **Agent Management (`agent-manager-tab.tsx`):**
    *   **Objective:** Provide full CRUD (Create, Read, Update, Delete) functionality for AI agents, and enable control over their lifecycle (start, stop, restart).
    *   **API Endpoints:**
        *   `GET /api/myntrix/agents`: Retrieve a comprehensive list of all AI agents, including their current status, health metrics, and last execution timestamp.
        *   `POST /api/myntrix/agents`: Facilitate the creation of a new AI agent, accepting initial configuration parameters.
        *   `POST /api/myntrix/agents/{id}/start`: Issue a command to initiate the execution of a specific agent.
        *   `POST /api/myntrix/agents/{id}/stop`: Issue a command to gracefully cease the execution of a specific agent.
        *   `POST /api/myntrix/agents/{id}/restart`: Issue a command to stop and then restart a specific agent's process.
        *   `DELETE /api/myntrix/agents/{id}`: Enable the permanent removal of an AI agent and its associated data.
    *   **Database Schema:**
        *   A `agents` table should store agent configurations and their dynamic state. Fields: `id` (primary key), `name` (string), `type` (string), `status` (string, e.g., 'running', 'stopped', 'error'), `health` (integer 0-100), `lastRun` (datetime, nullable), `configuration` (JSON/TEXT field for agent-specific settings).
    *   **Business Logic:**
        *   Implement robust process management logic for starting, stopping, and restarting agents (e.g., spawning child processes, integration with a container orchestration system like Docker/Kubernetes).
        *   Develop mechanisms for continuous health monitoring to update an agent's `status` and `health` in near real-time.

3.  **Device Control (`device-control-tab.tsx`):**
    *   **Objective:** Empower users to establish and terminate connections with physical devices, dispatch commands, upload files, and receive real-time telemetry data.
    *   **API Endpoints:**
        *   `GET /api/myntrix/devices`: Retrieve a list of all configured devices and their current connection status.
        *   `POST /api/myntrix/devices/{id}/connect`: Initiate a connection to a specified physical device.
        *   `POST /api/myntrix/devices/{id}/disconnect`: Terminate an active connection with a specific device.
        *   `POST /api/myntrix/devices/{id}/command`: Transmit a command string to a connected device, expecting a response or confirmation.
        *   `POST /api/myntrix/devices/{id}/upload`: Handle the secure upload of files (e.g., firmware, G-code) to a connected device.
    *   **WebSocket Endpoint:**
        *   `ws/myntrix/telemetry/{deviceId}`: Establish a WebSocket connection to provide a real-time stream of telemetry data and operational logs from the designated device.
    *   **Database Schema:**
        *   A `devices` table to persist device configurations: `id` (primary key), `name` (string), `type` (string), `connectionString` (string, e.g., serial port path, IP address), `status` (string, dynamic), `lastSeen` (datetime, dynamic), `firmwareVersion` (string, nullable), `configuration` (JSON/TEXT for device-specific settings).
    *   **Business Logic:**
        *   Implement device-specific communication protocols (e.g., serial communication, TCP/IP sockets for network-connected devices).
        *   Develop secure file transfer mechanisms to devices.
        *   Manage WebSocket connections for reliable real-time data streaming.

4.  **Resource Monitoring (`resource-monitor-tab.tsx`):**
    *   **Objective:** Provide a real-time overview of system resource utilization (CPU, Memory) and display the status of all active (running/pending) jobs.
    *   **API Endpoints:**
        *   `GET /api/myntrix/system-metrics`: Deliver current and potentially historical data on CPU and Memory usage.
        *   `GET /api/myntrix/jobs`: Furnish a list of all active (running/pending) and recently completed or failed jobs, including their progress.
    *   **Database Schema:**
        *   A `jobs` table to track job lifecycle: `id` (primary key), `name` (string), `type` (string), `status` (string: 'running', 'pending', 'completed', 'failed'), `progress` (integer 0-100), `createdAt` (datetime), `updatedAt` (datetime), `logs` (TEXT, nullable), `details` (JSON/TEXT, nullable).
        *   (Optional, for historical data) A `system_metrics_history` table for long-term storage of resource usage, or integration with a specialized time-series database.
    *   **Business Logic:**
        *   Implement server-side monitoring tools to continuously collect CPU and Memory usage data from the host system.
        *   Integrate seamlessly with the task scheduling system (from `task-scheduler-tab`) to accurately list and track job statuses and progress.

5.  **Task Scheduling (`task-scheduler-tab.tsx`):**
    *   **Objective:** Enable users to define, schedule, and manage automated tasks using cron expressions, and to review their detailed execution history, and even rerun them.
    *   **API Endpoints:**
        *   `GET /api/myntrix/tasks`: Retrieve all currently configured scheduled tasks.
        *   `GET /api/myntrix/tasks/history`: Fetch the complete execution history for all tasks.
        *   `POST /api/myntrix/tasks`: Create and register a new scheduled task.
        *   `POST /api/myntrix/tasks/{id}/run`: Manually trigger the immediate execution of a specific scheduled task, bypassing its cron schedule.
        *   `PUT /api/myntrix/tasks/{id}`: Update the parameters of an existing scheduled task (e.g., modify its `schedule`, `action`, or `enabled` status).
        *   `DELETE /api/myntrix/tasks/{id}`: Permanently remove a scheduled task from the system.
    *   **Database Schema:**
        *   A `scheduled_tasks` table: `id` (primary key), `name` (string), `schedule` (string, storing the cron expression), `action` (string, defining the task's payload, e.g., 'workflow', 'script', 'agent', 'api'), `enabled` (boolean), `createdAt` (datetime), `updatedAt` (datetime).
        *   A `task_runs` table: `id` (primary key), `taskId` (foreign key to `scheduled_tasks.id`), `startTime` (datetime), `endTime` (datetime, nullable), `status` (string, e.g., 'pending', 'running', 'success', 'failed'), `logs` (TEXT, nullable).
    *   **Business Logic:**
        *   Implement a robust, persistent task scheduler (e.g., using a Python library like `APScheduler` or a dedicated scheduler service) capable of parsing cron expressions and triggering tasks at the specified times.
        *   Define and integrate various task "actions" that scheduled jobs can perform (e.g., triggering an agent via its API, running a local script on the backend server, making an external API call).
        *   Develop comprehensive logging and management of `task_runs` and their associated `logs`.

6.  **3D Visualization (`ThreeDVisualizationTab.tsx`):**
    *   **Objective:** Dynamically provide data to populate the 3D representation of agents and devices based on their real-time status and configurations.
    *   **API Endpoint:**
        *   `GET /api/myntrix/visualization-data`: A unified endpoint that consolidates and delivers real-time data about agents and devices in a structured format optimized for the 3D scene (e.g., current positions, operational status, and other visualization-specific parameters).
    *   **Business Logic:**
        *   Actively aggregate and process data from the Agent Management and Device Control modules to construct the visualization payload.
        *   Implement algorithms to compute dynamic visual properties such as positions, status-driven color changes, or movement patterns for 3D elements based on underlying operational data.
        *   Consider mechanisms for real-time updates to the visualization data (e.g., leveraging WebSockets or Server-Sent Events (SSE) for highly dynamic scenarios) if the current data polling mechanism proves insufficient for fluidity.

---

### Checklist for Backend Realization V2: Myntrix Dashboard

#### **General:**
*   [ ] Review and confirm that the existing backend infrastructure (API framework, database, authentication, logging) can adequately support the new Myntrix dashboard features.
*   [ ] Define and implement any shared utility functions or helper modules specific for Myntrix functionalities within the backend.

#### **Agent Management:**
*   **Database:**
    *   [ ] Create `agents` table with columns: `id` (UUID/PK), `name` (TEXT), `type` (TEXT), `status` (TEXT), `health` (INTEGER), `lastRun` (DATETIME, nullable), `configuration` (JSONB/TEXT).
*   **API Endpoints:**
    *   [ ] Implement `GET /api/myntrix/agents` to fetch all agents.
    *   [ ] Implement `POST /api/myntrix/agents` to create a new agent.
    *   [ ] Implement `POST /api/myntrix/agents/{id}/start` to start an agent.
        *   [ ] Develop logic to spawn/manage agent processes (e.g., `subprocess` module, Docker API).
    *   [ ] Implement `POST /api/myntrix/agents/{id}/stop` to stop an agent.
        *   [ ] Develop logic to gracefully terminate agent processes.
    *   [ ] Implement `POST /api/myntrix/agents/{id}/restart` to restart an agent.
    *   [ ] Implement `DELETE /api/myntrix/agents/{id}` to delete an agent.
*   **Business Logic:**
    *   [ ] Implement robust agent lifecycle management (start/stop/restart).
    *   [ ] Develop real-time health monitoring for agents (e.g., a periodic background task to check agent process status and resource usage).

#### **Device Control:**
*   **Database:**
    *   [ ] Create `devices` table with columns: `id` (UUID/PK), `name` (TEXT), `type` (TEXT), `connectionString` (TEXT), `status` (TEXT, dynamic), `lastSeen` (DATETIME, dynamic), `firmwareVersion` (TEXT, nullable), `configuration` (JSONB/TEXT).
*   **API Endpoints:**
    *   [ ] Implement `GET /api/myntrix/devices` to fetch all configured devices.
    *   [ ] Implement `POST /api/myntrix/devices/{id}/connect` to connect to a device.
        *   [ ] Include logic to establish physical or network connection.
    *   [ ] Implement `POST /api/myntrix/devices/{id}/disconnect` to disconnect from a device.
        *   [ ] Include logic to gracefully close connection.
    *   [ ] Implement `POST /api/myntrix/devices/{id}/command` to send a command to a device.
        *   [ ] Develop device communication interface.
    *   [ ] Implement `POST /api/myntrix/devices/{id}/upload` to upload a file.
        *   [ ] Handle multipart/form-data.
        *   [ ] Implement secure file transfer to the device.
*   **WebSocket Endpoint:**
    *   [ ] Implement `ws/myntrix/telemetry/{deviceId}` for real-time telemetry streaming.
        *   [ ] Logic to collect telemetry from the device.
        *   [ ] Logic to stream data via WebSocket.

#### **Resource Monitoring:**
*   **Database:**
    *   [ ] Create `jobs` table: `id` (UUID/PK), `name` (TEXT), `type` (TEXT), `status` (TEXT), `progress` (INTEGER), `createdAt` (DATETIME), `updatedAt` (DATETIME), `logs` (TEXT, nullable), `details` (JSONB/TEXT, nullable).
    *   [ ] (Optional) Implement `system_metrics_history` table or integrate with a time-series database for long-term metric storage.
*   **API Endpoints:**
    *   [ ] Implement `GET /api/myntrix/system-metrics` to provide CPU/Memory usage.
        *   [ ] Develop server-side logic to collect real-time system metrics (e.g., `psutil` in Python).
    *   [ ] Implement `GET /api/myntrix/jobs` to provide job activity data.
        *   [ ] Integrate with the Task Scheduling service to retrieve and filter relevant job statuses.

#### **Task Scheduling:**
*   **Database:**
    *   [ ] Create `scheduled_tasks` table: `id` (UUID/PK), `name` (TEXT), `schedule` (TEXT, cron expression), `action` (TEXT), `enabled` (BOOLEAN), `createdAt` (DATETIME), `updatedAt` (DATETIME).
    *   [ ] Create `task_runs` table: `id` (UUID/PK), `taskId` (FK), `startTime` (DATETIME), `endTime` (DATETIME, nullable), `status` (TEXT), `logs` (TEXT, nullable).
*   **API Endpoints:**
    *   [ ] Implement `GET /api/myntrix/tasks` to fetch all scheduled tasks.
    *   [ ] Implement `GET /api/myntrix/tasks/history` to fetch task execution history.
    *   [ ] Implement `POST /api/myntrix/tasks` to create a new task.
        *   [ ] Include validation for cron expressions.
    *   [ ] Implement `POST /api/myntrix/tasks/{id}/run` to manually run a task.
    *   [ ] Implement `PUT /api/myntrix/tasks/{id}` to update a task.
    *   [ ] Implement `DELETE /api/myntrix/tasks/{id}` to delete a task.
*   **Business Logic:**
    *   [ ] Implement a robust background task scheduler process (e.g., using `APScheduler` or similar).
    *   [ ] Develop the logic to execute tasks based on their `action` type (e.g., trigger other APIs, run shell commands).
    *   [ ] Implement mechanisms to record `task_runs` and capture execution `logs`.

#### **3D Visualization:**
*   **API Endpoint:**
    *   [ ] Implement `GET /api/myntrix/visualization-data` to provide a consolidated, real-time data payload for the 3D scene.
*   **Business Logic:**
    *   [ ] Aggregate data from agents and devices to dynamically create the visualization payload.
    *   [ ] Develop logic to compute dynamic properties (e.g., positions, status-driven colors, animation states) for the 3D elements based on the collected operational data.
    *   [ ] (Consider) Explore WebSockets or SSE for pushing real-time visualization updates to the frontend if high-frequency data changes are required.
