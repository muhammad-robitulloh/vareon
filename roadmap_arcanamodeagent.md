# Arcana Mode Agent Development Roadmap

This roadmap outlines the planned enhancements for the Arcana Mode Agent, drawing inspiration from advanced AI development environments like Compyle AI, Cursor AI, and Replit AI Agent. The goal is to evolve Arcana into a highly interactive, transparent, and capable autonomous development assistant.

## Current State (Implemented Features)

*   **Agent Creation & Management**: Users can create, view, and edit Arcana Agents with configurable `name`, `persona`, `mode`, `objective`, `target_repo_path`, `target_branch`, and a `default_model_id` (LLM).
*   **Agent Task Submission**: Users can submit natural language tasks to selected agents.
*   **Agent Job Monitoring**: Display of agent jobs with status and detailed logs (thoughts, commands, outputs, errors).
*   **Human-in-the-Loop (Basic)**: Agents can request human input/clarification, pause execution, and resume upon user submission.
*   **File Tree Navigation**: Interactive display of the repository's file structure.
*   **File Editing**: View and edit file content directly within the UI.
*   **Git Operations**: Basic Git commands (status, add, commit, push, pull, checkout, branch) via a dedicated panel.
*   **GitHub OAuth Integration**: Seamless connection to GitHub for authenticated Git operations.

## Phase 1: Foundational Enhancements (UI/UX & Core Interaction)

This phase focuses on improving the core interaction with code and files, providing a more robust and intuitive developer experience.

### 1. Rich Code Editor Integration (Frontend)
*   **Goal**: Replace the basic `Textarea` in `FileEditor.tsx` with a full-featured code editor.
*   **Features**:
    *   Syntax highlighting for various programming languages.
    *   Line numbers.
    *   Basic code completion/suggestions.
    *   Improved scrolling and navigation.
*   **Impact**: Significantly enhances the experience of viewing and editing code, making the agent's proposed changes or generated code easier to review and modify.

### 2. Direct File Operations in UI (Frontend)
*   **Goal**: Enable users to perform common file system operations directly from the `FileTree` component.
*   **Features**:
    *   Context menus (right-click) or dedicated buttons in `FileTree` for:
        *   "New File"
        *   "New Folder"
        *   "Delete File/Folder"
        *   "Rename File/Folder"
    *   These actions will call the backend's `/api/arcana/file-operations` endpoint with appropriate `action` types.
*   **Impact**: Provides users with direct control over the agent's working directory, facilitating setup, cleanup, and manual adjustments.

## Phase 2: Advanced Agent Control & Transparency

This phase focuses on making the agent's execution more transparent and allowing for richer human-agent collaboration.

### 1. Real-time, Streaming Output/Logs (Frontend & Backend)
*   **Goal**: Provide immediate, live feedback on the agent's progress.
*   **Features**:
    *   Implement WebSocket-based streaming for agent job logs.
    *   Backend (`agent_orchestration_service.py`) will push log entries over WebSocket as they occur.
    *   Frontend (`ArcanaAgentTab.tsx`) will consume these WebSocket messages to update the log display in real-time.
*   **Impact**: Users will see the agent's thoughts and actions unfold live, significantly improving transparency and engagement.

### 2. Enhanced Human-in-the-Loop (Frontend & Backend)
*   **Goal**: Make the agent's requests for human input more contextual and actionable.
*   **Features**:
    *   When `awaiting_human_input`, the UI will display not just the agent's message, but also relevant context (e.g., the last few log entries, a diff of proposed changes, or the code snippet the agent is asking about).
    *   Backend (`agent_orchestration_service.py`) will need to store/pass more context when requesting human input.
    *   Frontend will render this context alongside the input field.
*   **Impact**: Users can provide more informed and precise input, leading to more effective agent guidance.

### 3. Agent State & Progress Visualization (Frontend)
*   **Goal**: Provide a clear, high-level overview of what the agent is currently doing.
*   **Features**:
    *   Prominent display of the agent's current status (e.g., "Planning...", "Executing Tool: generate_code", "Awaiting Human Input").
    *   Potentially a simple visual workflow indicator (e.g., a progress bar or step-by-step visualization).
*   **Impact**: Users can quickly grasp the agent's current activity and overall progress.

## Phase 3: Deeper Integration & Automation

This phase introduces more sophisticated capabilities for code quality, verification, and automated workflows.

### 1. Code Review & Diff Application (Frontend & Backend)
*   **Goal**: Allow agents to propose code changes that users can review and apply.
*   **Features**:
    *   Agent generates a diff/patch for proposed changes.
    *   Frontend displays the diff in a user-friendly format (side-by-side or unified).
    *   User can approve/reject the diff, and the agent applies it (or reverts).
*   **Impact**: Enables agents to make significant code modifications with human oversight, reducing risk.

### 2. Automated Testing & Verification (Backend & Frontend)
*   **Goal**: Empower agents to validate their own work.
*   **Features**:
    *   Agent can run existing test suites within the `target_repo_path`.
    *   Agent can generate new tests for its code.
    *   Frontend displays test results (pass/fail, coverage).
*   **Impact**: Increases confidence in agent-generated code and automates quality assurance.

### 3. Enhanced Context Management (Backend)
*   **Goal**: Improve the agent's ability to leverage and manage long-term context.
*   **Features**:
    *   Integration with the `ContextMemory` module for storing and retrieving relevant information across tasks and sessions.
    *   Agent can explicitly store/retrieve information from its context memory.
*   **Impact**: Agents become more intelligent and efficient by learning from past experiences and accessing relevant knowledge.

## Future Considerations

*   **Multi-Agent Collaboration**: Orchestrating multiple Arcana agents to work together on complex tasks.
*   **Custom Tool Definition**: Allowing users to define and integrate their own custom tools for agents.
*   **Version Control Branching/Merging UI**: More advanced Git UI for visual branching, merging, and conflict resolution.
*   **Deployment Automation**: Agents assisting with deployment pipelines.

This roadmap provides a structured approach to evolving the Arcana Mode Agent into a powerful and intuitive development companion.
