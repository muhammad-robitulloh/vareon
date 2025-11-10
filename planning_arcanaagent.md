# Planning: Arcana Mode Agent Backend Architecture

This document outlines the backend architecture planning for the new "Arcana Mode Agent" tab within the Arcana dashboard. This feature aims to provide an interface for autonomous, agentic AI capabilities, specifically functioning as an **AI Agent Builder** or **Autonomous Fullstack Coding AI Builder**, akin to advanced systems like Replit AI Agent, Cursor AI, or Compyle AI. It will be deeply integrated with the Vareon ecosystem.

## 1. Overview of Arcana Mode Agent

The Arcana Mode Agent will empower users to define and launch highly autonomous AI agents capable of understanding high-level natural language goals and translating them into executable software development tasks. These agents will plan, generate code, execute, test, debug, and iterate on solutions across the full stack, leveraging the entire Vareon ecosystem.

**Key Capabilities:**
*   **Goal Interpretation**: Understand complex natural language descriptions of desired applications or features.
*   **Autonomous Planning**: Break down high-level goals into detailed, actionable steps, including architectural design, database schema, API definitions, and UI components.
*   **Code Generation**: Generate production-ready code for frontend, backend, and database layers in various programming languages and frameworks.
*   **Execution & Testing**: Execute generated code in sandboxed environments, run unit and integration tests, and perform end-to-end validation.
*   **Debugging & Refinement**: Analyze errors and test failures, identify root causes, and autonomously apply fixes and improvements.
*   **Iterative Development**: Continuously refine the codebase based on feedback, new requirements, or performance metrics.
*   **Ecosystem Integration**: Seamlessly interact with Vareon's Myntrix, Neosyntis, and Cognisys modules to achieve its objectives.

## 2. Core Architectural Components

To support this advanced Arcana Mode Agent, the following new or extended backend components are envisioned:

### 2.1. Autonomous Agent Service (New Module: `server-python/arcana_agent/`)

This will be a new, dedicated module responsible for orchestrating the complex operations of autonomous coding agents.

**Responsibilities:**
*   **Agent Lifecycle Management**: Create, read, update, delete, start, stop, pause, resume agents.
*   **Task Submission & Monitoring**: Receive high-level goals/tasks from the user, manage their decomposition into sub-tasks, and monitor their execution status.
*   **Agent State Management**: Persist and retrieve the current state of an agent, including its internal monologue, thought process, current code, project structure, and execution history.
*   **Tool Orchestration**: Dynamically manage and invoke "tools" (Vareon API endpoints, shell commands, code editors, version control) based on the agent's current plan.
*   **Logging & Auditing**: Record detailed agent actions, decisions, generated code, execution outputs, and errors for transparency, debugging, and learning.
*   **Safety & Guardrails**: Implement robust mechanisms to prevent harmful or unintended actions, including resource limits, code review/approval steps, and sandboxed execution environments.
*   **Feedback Loop Management**: Process feedback from execution, tests, or user input to guide agent's next steps.

### 2.2. Agent Definition & Configuration

Agents will require a comprehensive definition to guide their autonomous operation.

**Key Attributes of an Agent:**
*   `id`: Unique identifier.
*   `owner_id`: User who owns the agent.
*   `name`: Human-readable name (e.g., "FullstackDevBot", "BugFixer").
*   `description`: Purpose and specialized capabilities of the agent.
*   `goal`: The primary, high-level objective the agent is designed to achieve (e.g., "Build a simple e-commerce platform").
*   `status`: Current operational status (e.g., `idle`, `planning`, `coding`, `testing`, `deploying`, `paused`, `completed`, `failed`).
*   `configuration`: JSON field for agent-specific parameters:
    *   `llm_model_preferences`: Specific LLM models, temperature, top_p settings (via Arcana LLM Preferences).
    *   `memory_limits`: How much context memory the agent can utilize.
    *   `iteration_limits`: Maximum number of planning/execution cycles.
    *   `allowed_tools`: List of Vareon modules/APIs/shell commands the agent is explicitly allowed to use.
    *   `project_context`: Initial project setup, tech stack preferences, coding style guidelines.
    *   `code_generation_strategy`: (e.g., "test-driven development", "component-first").
*   `current_task_id`: Reference to the currently executing `AgentTask`.
*   `created_at`, `updated_at`.

### 2.3. Agent Task Management

When a user submits a goal to an agent, it initiates an `AgentTask` that tracks the entire development process.

**Key Attributes of an AgentTask:**
*   `id`: Unique identifier.
*   `agent_id`: The agent assigned to this task.
*   `user_id`: User who submitted the task.
*   `goal_description`: Detailed natural language description of the task's goal.
*   `status`: `pending`, `planning`, `coding`, `testing`, `debugging`, `deploying`, `completed`, `failed`, `cancelled`.
*   `start_time`, `end_time`.
*   `current_step`: Description of the current step being executed by the agent (e.g., "Designing database schema", "Writing user authentication API").
*   `plan`: JSON representation of the agent's current execution plan.
*   `code_changes`: History of code modifications made by the agent.
*   `test_results`: Outcomes of tests run by the agent.
*   `deployment_status`: Status of any deployments initiated by the agent.
*   `logs`: Accumulated detailed logs/output from the agent's execution, including LLM interactions, tool calls, and system outputs.
*   `results`: Final output, generated code, deployment URLs, or summary of the task.

### 2.4. Agent Tools / Capabilities

Autonomous agents operate by using "tools" to interact with their environment and perform coding tasks. In Vareon, these tools will be a rich set of functionalities exposed by the ecosystem.

**Implementation Strategy:**
*   **Tool Registry**: A dynamic mechanism to register and describe available tools. Each tool will have:
    *   `name`: Unique identifier (e.g., `cognisys_llm_chat`, `myntrix_agent_control`, `neosyntis_workflow_trigger`, `arcana_terminal_execute`).
    *   `description`: Natural language description for LLM to understand its purpose.
    *   `parameters`: JSON schema defining required and optional input parameters.
    *   `invocation_method`: Internal function or API endpoint to call.
*   **Dynamic Tool Invocation**: The agent orchestration service will dynamically invoke these tools based on the agent's LLM-driven planning and reasoning. This might involve:
    *   Making HTTP requests to Vareon's own API endpoints (e.g., to create a Myntrix agent, trigger a Neosyntis workflow).
    *   Executing shell commands (via the Arcana Terminal Management service, in a sandboxed and monitored environment) for file system operations, running build tools, or executing tests.
    *   Interacting with the Cognisys LLM service for further reasoning, code generation, or natural language processing.
    *   Direct file system manipulation (e.g., creating/modifying source code files).
    *   Version control operations (e.g., `git clone`, `git commit`).

## 3. Enhanced Integration with Existing Vareon Ecosystem

The Arcana Mode Agent will be deeply integrated with and act as a super-orchestrator for the existing modules:

*   **Cognisys**:
    *   **Primary Reasoning Engine**: Agents will heavily rely on Cognisys's LLM routing capabilities for:
        *   **Planning**: Generating step-by-step plans from high-level goals.
        *   **Code Generation**: Translating design into code snippets, functions, or entire files.
        *   **Natural Language to Code**: Converting user instructions into executable code.
        *   **Error Analysis**: Understanding and debugging error messages from execution.
        *   **Self-Correction**: Proposing and implementing fixes based on feedback.
*   **Myntrix**:
    *   **Deployment & Environment Management**: Agents can use Myntrix APIs to:
        *   Deploy generated backend services as new Myntrix agents.
        *   Provision and manage development/testing environments (e.g., spin up containers).
        *   Control and monitor Myntrix agents/devices that are part of the developed application.
    *   **Task Automation**: Agents can schedule and monitor automated tasks (e.g., CI/CD pipelines) via Myntrix.
*   **Neosyntis**:
    *   **Workflow Automation**: Agents can create, trigger, monitor, or modify Neosyntis workflows to automate deployment pipelines, data processing, or ML model retraining.
    *   **Data Management**: Agents can upload, download, or analyze datasets (e.g., for populating test databases, training ML models).
    *   **ML Model Lifecycle**: Agents can initiate ML model training or deployment processes managed by Neosyntis.
*   **Arcana Core (Context Memory, Terminal)**:
    *   **Persistent Knowledge**: Agents will extensively use Arcana's Context Memory to:
        *   Store project specifications, architectural decisions, and design patterns.
        *   Maintain a long-term memory of past projects, successful strategies, and common pitfalls.
        *   Retrieve user preferences and coding styles.
    *   **Sandboxed Execution**: Agents will execute shell commands and run generated code within a sandboxed environment provided by Arcana's Terminal Management. This allows for:
        *   File system interaction (creating/modifying files, navigating directories).
        *   Running build commands, compilers, interpreters.
        *   Executing tests and capturing their output.
        *   Interacting with version control systems (e.g., `git`).

## 4. Backend API Endpoints (Proposed Additions/Refinements)

The previously proposed endpoints remain relevant, with potential for additional parameters or response details to support the coding agent's needs.

### `POST /api/arcana/agents/` (Refined)

*   **Request Body**: `AgentCreateSchema` (e.g., `name`, `description`, `goal`, `configuration`, `tools_enabled`, `initial_project_template_id`).
*   **Response**: `AgentResponseSchema`.

### `POST /api/arcana/agents/{agent_id}/run` (Refined)

*   **Description**: Submits a task/goal to an autonomous agent for execution, initiating a full development cycle.
*   **Request Body**: `AgentTaskCreateSchema` (e.g., `goal_description`, `target_repository_url`, `initial_files`).
*   **Response**: `AgentTaskResponseSchema`.

### `GET /api/arcana/agents/{agent_id}/tasks/{task_id}/code-changes`

*   **Description**: Retrieves a history of code changes made by the agent for a specific task.
*   **Response**: `List[CodeChangeSchema]` (e.g., `file_path`, `diff`, `timestamp`, `agent_reasoning`).

### `GET /api/arcana/agents/{agent_id}/tasks/{task_id}/test-results`

*   **Description**: Retrieves the results of tests run by the agent for a specific task.
*   **Response**: `TestResultsSchema` (e.g., `passed_count`, `failed_count`, `details`).

### `POST /api/arcana/agents/{agent_id}/tasks/{task_id}/approve-step`

*   **Description**: Allows a user to approve a critical step or code change proposed by the agent (Human-in-the-Loop).
*   **Request Body**: `ApprovalSchema` (e.g., `step_id`, `approved: bool`, `feedback: str`).
*   **Response**: `MessageResponse`.

## 5. Frontend Considerations

The frontend for the "Arcana Mode Agent" tab will need a sophisticated interface to manage and interact with these coding agents:
*   **Agent Dashboard**: List agents, their current status, and high-level goals.
*   **Agent Creation/Configuration Form**: Detailed form to define agent parameters, goals, and allowed tools.
*   **Interactive Project View**: A file explorer, integrated code editor, and diff viewer to inspect generated code and changes.
*   **Real-time Activity Feed**: Display agent's internal monologue, planning steps, tool calls, code generation, execution outputs, and errors in real-time.
*   **Task Submission & Monitoring**: Interface to submit new development tasks and track their progress through various stages (planning, coding, testing, deploying).
*   **Human-in-the-Loop Controls**: Buttons/prompts for user approval of critical agent actions or code changes.
*   **Result Visualization**: Display generated application previews, deployment URLs, or test reports.

## 6. Future Enhancements

*   **Advanced Agent Templates**: Pre-configured agents for specific development tasks (e.g., "React Component Builder", "FastAPI Endpoint Creator").
*   **Multi-Agent Collaboration**: Agents working together on larger projects.
*   **Learning & Adaptation**: Agents learning from successful and failed attempts to improve their coding strategies.
*   **Cost Optimization**: Intelligent management of LLM calls and compute resources.
*   **Integrated Development Environment (IDE) Features**: More advanced code editing, refactoring, and debugging capabilities within the agent's environment.

This updated planning document provides a more detailed roadmap for developing the Arcana Mode Agent as a powerful, autonomous coding AI builder within the Vareon ecosystem.