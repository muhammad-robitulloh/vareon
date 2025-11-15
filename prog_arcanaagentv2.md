# Progress on Arcana CLI Agent Integration - Iteration 2

This document tracks the ongoing development of the Arcana CLI Agent, building upon the foundational backend and frontend work. This iteration focuses on transforming the conceptual CLI tool into a more robust, interactive, and feature-rich application, inspired by advanced CLI experiences like Cursor AI CLI and Gemini CLI.

## New Scope: Advanced CLI Features

The previous iteration established the backend API for CLI commands and API key management, along with a basic frontend for key generation. The next phase of development will focus on enhancing the CLI tool itself to provide a more interactive and user-friendly experience.

Key features to be developed for the CLI tool include:

1.  **Interactive/Rich Terminal UI**: Moving beyond a simple command-line script to a more dynamic and interactive terminal interface.
2.  **Error Log Toggle**: Implementing a mechanism (e.g., `Ctrl+O`) to open and close a dedicated error log display within the terminal UI.
3.  **Model Details Command (`/model`)**: A command to display details of the currently used model, based on the Cognisys configuration in the cloud. This requires new backend support.
4.  **Current Directory Indicator**: Displaying the user's current working directory within the CLI's interface.

## Detailed TODO List for Iteration 2

### 1. Backend Enhancements (for CLI Model Details)

-   [x] **New API Endpoint for Model Details**:
    -   Create a new endpoint (e.g., `GET /cognisys/cli/model-details` or `GET /arcana/cli-config/model-details`) that, given a `user_id` (from the API key), queries the Cognisys configuration to determine the currently active model and its relevant details (name, provider, type, etc.).
    -   This endpoint should leverage existing Cognisys CRUD operations or services to retrieve model information.
    -   Ensure proper authentication and authorization for this endpoint.

### 2. CLI Tool Enhancements (Node.js - Interactive UI)

-   [x] **Refactor CLI Project Setup**:
    -   Introduce a suitable Node.js library for building interactive terminal UIs (e.g., `Ink` for React-like components, or `blessed` for lower-level control).
    -   Restructure the existing `cli.js` into a more modular and component-based application to support the interactive UI.
-   [x] **Core Interactive UI Implementation**:
    -   Set up the main interactive loop and render the basic terminal layout.
    -   Implement a persistent command input area at the bottom of the screen.
    -   Design an area for displaying command output and conversation history.
-   [x] **Current Directory Indicator**:
    -   Integrate a component to display the current working directory, updating dynamically as the user navigates or commands change the directory.
-   [x] **`/model` Command Implementation**:
    -   Implement the `/model` command within the interactive CLI.
    -   This command should make an API call to the new backend endpoint (from Backend TODO) to fetch model details.
    -   Display the retrieved model information clearly within the interactive UI.
-   [x] **Error Log Toggle (`Ctrl+O`)**:
    -   Implement keyboard event listeners to detect `Ctrl+O`.
    -   Design a dedicated, collapsible area within the UI to display detailed error logs.
    -   Toggle the visibility of this error log area upon `Ctrl+O` press.
-   [x] **Enhanced Output Formatting**:
    -   Further improve output formatting within the interactive UI, including syntax highlighting for code, structured display of reasoning, and clear presentation of other command outputs.
-   [x] **Interactive Prompts**:
    -   Implement interactive prompts for commands that require complex inputs or confirmations, leveraging the chosen UI library.
-   [x] **Asynchronous Job Status Display**:
    -   For commands like `agent run` that return a job ID, implement a mechanism to display the status of these background jobs within the interactive UI, possibly with real-time updates.

### 3. Frontend Enhancements (Dashboard - Optional but Recommended)

-   [x] **CLI Configuration UI Expansion**:
    -   Expand the "CLI Configurations" section in the dashboard to allow users to manage more complex settings, potentially including default agents or preferred models, which the interactive CLI can then fetch.

This detailed TODO list will guide the next phase of development for the Arcana CLI Agent, focusing on delivering a highly interactive and integrated terminal experience.
