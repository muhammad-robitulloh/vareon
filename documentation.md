# Vareon Backend API Documentation

This document provides comprehensive API documentation for the Vareon backend, designed to facilitate frontend integration and general API usage.

## Table of Contents

1.  [Introduction](#1-introduction)
2.  [Authentication](#2-authentication)
3.  [Common Models](#3-common-models)
4.  [Global Endpoints](#4-global-endpoints)
5.  [Arcana API](#5-arcana-api)
6.  [Cognisys API](#6-cognisys-api)
7.  [Myntrix API](#7-myntrix-api)
8.  [Neosyntis API](#8-neosyntis-api)

---

## 1. Introduction

The Vareon backend is built with FastAPI, providing a robust and scalable API for managing various aspects of the Vareon ecosystem, including AI orchestration, agent and device management, workflow automation, and machine learning models. This documentation details the available endpoints, their functionalities, request/response formats, and authentication requirements.

## 2. Authentication

Vareon uses OAuth2 with Bearer tokens for API authentication.

### `POST /api/token`

*   **Description**: Authenticates a user and returns an access token.
*   **Authentication Required**: No
*   **Request Body**: `application/x-www-form-urlencoded`
    *   `username` (string, required): User's username or email.
    *   `password` (string, required): User's password.
*   **Response (200 OK)**: `Token`
    ```json
    {
      "access_token": "your_jwt_access_token",
      "token_type": "bearer"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Incorrect username or password.
    *   `403 Forbidden`: Email not verified.

### Using the Access Token

Once you have an `access_token`, include it in the `Authorization` header of subsequent requests:

`Authorization: Bearer <your_jwt_access_token>`

## 3. Common Models

### `MessageResponse`

*   **Description**: A generic response model for simple messages.
    ```json
    {
      "message": "string"
    }
    ```

### `Token`

*   **Description**: Model for authentication tokens.
    ```json
    {
      "access_token": "string",
      "token_type": "string"
    }
    ```

### `User`

*   **Description**: User profile model.
    ```json
    {
      "email": "user@example.com",
      "username": "username",
      "id": "uuid_string",
      "is_active": true,
      "is_verified": true,
      "verification_token": "string_or_null",
      "verification_token_expires_at": "datetime_string_or_null",
      "roles": [
        {
          "name": "string",
          "id": "uuid_string",
          "permissions": [
            {
              "name": "string",
              "id": "uuid_string"
            }
          ]
        }
      ]
    }
    ```

### `UserCreate`

*   **Description**: Model for creating a new user.
    ```json
    {
      "email": "user@example.com",
      "username": "username",
      "password": "password"
    }
    ```

### `UserUpdate`

*   **Description**: Model for updating an existing user's profile.
    ```json
    {
      "username": "new_username",
      "email": "new_email@example.com",
      "password": "new_password"
    }
    ```

---

## 4. Global Endpoints (from `main.py`)

These endpoints are directly defined in `main.py` and provide core application functionalities.

### `GET /health`

*   **Description**: Checks the health status of the backend server.
*   **Authentication Required**: No
*   **Response (200 OK)**:
    ```json
    {
      "status": "ok"
    }
    ```

### `POST /api/register`

*   **Description**: Registers a new user account.
*   **Authentication Required**: No
*   **Request Body**: `UserCreate`
    ```json
    {
      "email": "new_user@example.com",
      "username": "new_user",
      "password": "secure_password"
    }
    ```
*   **Response (200 OK)**: `MessageResponse`
    ```json
    {
      "message": "Registration successful. Please check your email to verify your account."
    }
    ```
*   **Error Responses**:
    *   `400 Bad Request`: Username or email already registered.
    *   `500 Internal Server Error`: Failed to send verification email.

### `POST /api/verify-email`

*   **Description**: Verifies a user's email address using a token.
*   **Authentication Required**: No
*   **Request Body**: `VerifyEmailRequest`
    ```json
    {
      "email": "user@example.com",
      "token": "verification_token_string"
    }
    ```
*   **Response (200 OK)**: `MessageResponse`
    ```json
    {
      "message": "Email verified successfully!",
      "status": "success"
    }
    ```
*   **Error Responses**:
    *   `404 Not Found`: User not found.
    *   `400 Bad Request`: Invalid verification token or token expired.
    *   `500 Internal Server Error`: Unexpected error during email verification.

### `GET /api/dashboard`

*   **Description**: Retrieves the current user's dashboard information. (Requires `admin_access` permission).
*   **Authentication Required**: Yes (Admin Access)
*   **Response (200 OK)**: `User`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.

### `GET /api/system/status`

*   **Description**: Provides a comprehensive status overview of all Vareon modules.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `SystemStatus`
    ```json
    {
      "arcana": {
        "status": "online",
        "uptime": "string",
        "activeChats": 0,
        "messagesProcessed": 0,
        "avgResponseTime": "string",
        "activeAgents": 0,
        "jobsCompleted": 0,
        "devicesConnected": 0,
        "activeWorkflows": 0,
        "datasetsManaged": 0,
        "searchQueriesProcessed": 0,
        "modelsActive": 0,
        "routingRules": 0,
        "requestsRouted": 0
      },
      "myntrix": {
        "status": "online",
        "uptime": "string",
        "activeAgents": 0,
        "jobsCompleted": 0,
        "devicesConnected": 0,
        "activeChats": 0,
        "messagesProcessed": 0,
        "avgResponseTime": "string",
        "activeWorkflows": 0,
        "datasetsManaged": 0,
        "searchQueriesProcessed": 0,
        "modelsActive": 0,
        "routingRules": 0,
        "requestsRouted": 0
      },
      "neosyntis": {
        "status": "online",
        "uptime": "string",
        "activeWorkflows": 0,
        "datasetsManaged": 0,
        "searchQueriesProcessed": 0,
        "activeChats": 0,
        "messagesProcessed": 0,
        "avgResponseTime": "string",
        "activeAgents": 0,
        "jobsCompleted": 0,
        "devicesConnected": 0,
        "modelsActive": 0,
        "routingRules": 0,
        "requestsRouted": 0
      },
      "cognisys": {
        "status": "online",
        "uptime": "string",
        "modelsActive": 0,
        "routingRules": 0,
        "requestsRouted": 0,
        "activeChats": 0,
        "messagesProcessed": 0,
        "avgResponseTime": "string",
        "activeAgents": 0,
        "jobsCompleted": 0,
        "devicesConnected": 0,
        "activeWorkflows": 0,
        "datasetsManaged": 0,
        "searchQueriesProcessed": 0
      }
    }
    ```

### `GET /api/users/me`

*   **Description**: Retrieves the profile of the current authenticated user.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `User`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: User not found in database.

### `PUT /api/users/me`

*   **Description**: Updates the profile of the current authenticated user.
*   **Authentication Required**: Yes
*   **Request Body**: `UserUpdate`
*   **Response (200 OK)**: `User`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: User not found in database.
    *   `400 Bad Request`: Username or email already taken.

### `GET /api/search`

*   **Description**: Performs a global search across various Vareon entities (Workflows, Datasets, Agents, Hardware Devices, Routing Rules).
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `query` (string, required): The search term.
*   **Response (200 OK)**: `List[Dict[str, Any]]` - A list of dictionaries, where each dictionary represents a search result with `type`, `id`, `name`, and other relevant fields.
    ```json
    [
      {
        "type": "workflow",
        "id": "uuid_string",
        "name": "string",
        "status": "string"
      },
      {
        "type": "dataset",
        "id": "uuid_string",
        "name": "string",
        "format": "string"
      },
      {
        "type": "agent",
        "id": "uuid_string",
        "name": "string",
        "status": "string"
      },
      {
        "type": "hardware_device",
        "id": "uuid_string",
        "name": "string",
        "device_type": "string"
      },
      {
        "type": "routing_rule",
        "id": "uuid_string",
        "name": "string",
        "target_model": "string"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `POST /api/chat`

*   **Description**: Initiates or continues a chat conversation with an LLM, potentially orchestrating other services.
*   **Authentication Required**: Yes
*   **Request Body**: `ChatRequest`
    ```json
    {
      "message": "string",
      "conversation_id": "uuid_string_or_null"
    }
    ```
*   **Response (200 OK)**: `ChatResponse`
    ```json
    {
      "response": "string",
      "conversation_id": "uuid_string",
      "message_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Conversation not found.
    *   `500 Internal Server Error`: LLM API request failed or other orchestration error.

### `GET /api/chat/history/{conversation_id}`

*   **Description**: Retrieves the chat history for a specific conversation.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `conversation_id` (UUID, required): The ID of the conversation.
*   **Response (200 OK)**: `List[ChatMessage]`
    ```json
    [
      {
        "id": "uuid_string",
        "conversation_id": "uuid_string",
        "user_id": "uuid_string",
        "sender": "user_or_llm",
        "message_content": "string",
        "timestamp": "datetime_string"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Conversation not found.

### `GET /api/chat/conversations`

*   **Description**: Lists all chat conversations for the current user.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `List[Conversation]`
    ```json
    [
      {
        "title": "string_or_null",
        "id": "uuid_string",
        "user_id": "uuid_string",
        "created_at": "datetime_string",
        "updated_at": "datetime_string"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `POST /api/chat/conversations`

*   **Description**: Creates a new chat conversation.
*   **Authentication Required**: Yes
*   **Request Body**: `ConversationCreate`
    ```json
    {
      "title": "string_or_null"
    }
    ```
*   **Response (200 OK)**: `Conversation`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `PUT /api/chat/conversations/{conversation_id}`

*   **Description**: Updates an existing chat conversation.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `conversation_id` (UUID, required): The ID of the conversation to update.
*   **Request Body**: `ConversationUpdate`
    ```json
    {
      "title": "new_title_string_or_null"
    }
    ```
*   **Response (200 OK)**: `Conversation`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Conversation not found.

### `DELETE /api/chat/conversations/{conversation_id}`

*   **Description**: Deletes a specific chat conversation and all its messages.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `conversation_id` (UUID, required): The ID of the conversation to delete.
*   **Response (200 OK)**: `MessageResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Conversation not found.

### `POST /api/chat/clear`

*   **Description**: Clears chat history for the current user. Can clear a specific conversation or all conversations.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `conversation_id` (UUID, optional): If provided, clears history for this specific conversation. If not provided, clears all conversations for the user.
*   **Response (200 OK)**: `MessageResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Conversation not found (if `conversation_id` is provided).

---

## 5. Arcana API

Arcana provides foundational AI and system intelligence services.

### `GET /api/arcana/status`

*   **Description**: Retrieves the status of the Arcana module.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `ArcanaStatus`
    ```json
    {
      "status": "online",
      "uptime": "string",
      "activeChats": 12,
      "messagesProcessed": 1543,
      "avgResponseTime": "1.2s"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `POST /api/arcana/start-chat`

*   **Description**: Triggers the start of an Arcana Chat. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `MessageResponse`
    ```json
    {
      "message": "Arcana Chat started successfully!"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/arcana/context-memory`

*   **Description**: Retrieves all context memories for the current user.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `List[ContextMemory]`
    ```json
    [
      {
        "key": "string",
        "value": "json_string_or_plain_text",
        "id": "uuid_string",
        "user_id": "uuid_string",
        "last_accessed": "datetime_string",
        "created_at": "datetime_string",
        "updated_at": "datetime_string"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/arcana/context-memory/{key}`

*   **Description**: Retrieves a specific context memory by its key for the current user.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `key` (string, required): The key of the context memory.
*   **Response (200 OK)**: `ContextMemory`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Context memory not found.

### `POST /api/arcana/context-memory`

*   **Description**: Creates a new context memory or updates an existing one for the current user.
*   **Authentication Required**: Yes
*   **Request Body**: `ContextMemoryCreate`
    ```json
    {
      "key": "string",
      "value": "json_string_or_plain_text"
    }
    ```
*   **Response (200 OK)**: `ContextMemory`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `DELETE /api/arcana/context-memory/{key}`

*   **Description**: Deletes a specific context memory by its key for the current user.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `key` (string, required): The key of the context memory to delete.
*   **Response (200 OK)**: `MessageResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Context memory not found.

### `GET /api/arcana/llm/preferences`

*   **Description**: Retrieves the current user's LLM preferences. Creates default preferences if none exist.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `UserLLMPreference`
    ```json
    {
      "default_model_id": "uuid_string_or_null",
      "temperature": 0.7,
      "top_p": 1.0,
      "id": "uuid_string",
      "user_id": "uuid_string",
      "created_at": "datetime_string",
      "updated_at": "datetime_string",
      "default_model": {
        "provider_id": "uuid_string",
        "model_name": "string",
        "max_tokens": 0,
        "cost_per_token": 0,
        "id": "uuid_string",
        "created_at": "datetime_string",
        "updated_at": "datetime_string",
        "provider": {
          "name": "string",
          "base_url": "string",
          "id": "uuid_string",
          "created_at": "datetime_string",
          "updated_at": "datetime_string"
        }
      }
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `PUT /api/arcana/llm/preferences`

*   **Description**: Updates the current user's LLM preferences.
*   **Authentication Required**: Yes
*   **Request Body**: `UserLLMPreferenceUpdate`
    ```json
    {
      "default_model_id": "uuid_string_or_null",
      "temperature": 0.5,
      "top_p": 0.8
    }
    ```
*   **Response (200 OK)**: `UserLLMPreference`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Default LLM Model not found (if `default_model_id` is provided and invalid).

### `GET /api/arcana/terminal/sessions`

*   **Description**: Lists all terminal sessions for the current user.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `List[TerminalSession]`
    ```json
    [
      {
        "status": "active_or_closed",
        "last_command": "string_or_null",
        "id": "uuid_string",
        "user_id": "uuid_string",
        "started_at": "datetime_string",
        "ended_at": "datetime_string_or_null"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/arcana/terminal/sessions/{session_id}/history`

*   **Description**: Retrieves the command history for a specific terminal session.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `session_id` (UUID, required): The ID of the terminal session.
*   **Response (200 OK)**: `List[TerminalCommandHistory]`
    ```json
    [
      {
        "session_id": "uuid_string",
        "command": "string",
        "output": "string_or_null",
        "id": "uuid_string",
        "timestamp": "datetime_string"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Terminal session not found.

### `POST /api/arcana/terminal/sessions/{session_id}/close`

*   **Description**: Closes a specific terminal session.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `session_id` (UUID, required): The ID of the terminal session to close.
*   **Response (200 OK)**: `MessageResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Terminal session not found.

### `WebSocket /ws/shell/{session_id}`

*   **Description**: Establishes an interactive WebSocket connection to a shell session.
*   **Authentication Required**: Yes (via `token` query parameter)
*   **Path Parameters**:
    *   `session_id` (UUID, required): The ID of the terminal session.
*   **Query Parameters**:
    *   `token` (string, required): JWT access token.
*   **Messages**:
    *   **Client to Server**: Text messages representing shell input or JSON messages for control (e.g., `{"resize": {"cols": 80, "rows": 24}}`).
    *   **Server to Client**: Text messages representing shell output.
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Terminal session not found.

---

## 6. Cognisys API

Cognisys focuses on LLM orchestration and routing.

### `POST /api/cognisys/providers/`

*   **Description**: Creates a new LLM provider.
*   **Authentication Required**: Yes (`admin_access` permission)
*   **Request Body**: `LLMProviderCreate`
    ```json
    {
      "name": "string",
      "base_url": "string",
      "api_key": "string"
    }
    ```
*   **Response (201 Created)**: `LLMProvider`
    ```json
    {
      "name": "string",
      "base_url": "string",
      "id": "uuid_string",
      "created_at": "datetime_string",
      "updated_at": "datetime_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.

### `GET /api/cognisys/providers/`

*   **Description**: Retrieves a list of all LLM providers.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[LLMProvider]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/cognisys/providers/{provider_id}`

*   **Description**: Retrieves a specific LLM provider by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `provider_id` (string, required): The ID of the LLM provider.
*   **Response (200 OK)**: `LLMProvider`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: LLM Provider not found.

### `PUT /api/cognisys/providers/{provider_id}`

*   **Description**: Updates an existing LLM provider.
*   **Authentication Required**: Yes (`admin_access` permission)
*   **Path Parameters**:
    *   `provider_id` (string, required): The ID of the LLM provider to update.
*   **Request Body**: `LLMProviderUpdate`
    ```json
    {
      "name": "string_or_null",
      "base_url": "string_or_null",
      "api_key": "string_or_null"
    }
    ```
*   **Response (200 OK)**: `LLMProvider`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.
    *   `404 Not Found`: LLM Provider not found.

### `DELETE /api/cognisys/providers/{provider_id}`

*   **Description**: Deletes a specific LLM provider.
*   **Authentication Required**: Yes (`admin_access` permission)
*   **Path Parameters**:
    *   `provider_id` (string, required): The ID of the LLM provider to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.
    *   `404 Not Found`: LLM Provider not found.

### `POST /api/cognisys/providers/{provider_id}/test-connection`

*   **Description**: Tests the connection to a specific LLM provider. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `provider_id` (string, required): The ID of the LLM provider to test.
*   **Response (200 OK)**:
    ```json
    {
      "message": "string",
      "status": "success_or_failure"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: LLM Provider not found.

### `POST /api/cognisys/models/`

*   **Description**: Creates a new LLM model.
*   **Authentication Required**: Yes (`admin_access` permission)
*   **Request Body**: `LLMModelCreate`
    ```json
    {
      "provider_id": "uuid_string",
      "model_name": "string",
      "max_tokens": 0,
      "cost_per_token": 0
    }
    ```
*   **Response (201 Created)**: `LLMModel`
    ```json
    {
      "provider_id": "uuid_string",
      "model_name": "string",
      "max_tokens": 0,
      "cost_per_token": 0,
      "id": "uuid_string",
      "created_at": "datetime_string",
      "updated_at": "datetime_string",
      "provider": {
        "name": "string",
        "base_url": "string",
        "id": "uuid_string",
        "created_at": "datetime_string",
        "updated_at": "datetime_string"
      }
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.

### `GET /api/cognisys/models/`

*   **Description**: Retrieves a list of all LLM models.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[LLMModel]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/cognisys/models/{model_id}`

*   **Description**: Retrieves a specific LLM model by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the LLM model.
*   **Response (200 OK)**: `LLMModel`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: LLM Model not found.

### `PUT /api/cognisys/models/{model_id}`

*   **Description**: Updates an existing LLM model.
*   **Authentication Required**: Yes (`admin_access` permission)
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the LLM model to update.
*   **Request Body**: `LLMModelUpdate`
    ```json
    {
      "provider_id": "uuid_string_or_null",
      "model_name": "string_or_null"
    }
    ```
*   **Response (200 OK)**: `LLMModel`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.
    *   `404 Not Found`: LLM Model not found.

### `DELETE /api/cognisys/models/{model_id}`

*   **Description**: Deletes a specific LLM model.
*   **Authentication Required**: Yes (`admin_access` permission)
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the LLM model to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `403 Forbidden`: Not enough permissions.
    *   `404 Not Found`: LLM Model not found.

### `POST /api/cognisys/routing-rules`

*   **Description**: Creates a new LLM routing rule.
*   **Authentication Required**: Yes
*   **Request Body**: `RoutingRuleCreate`
    ```json
    {
      "name": "string",
      "condition": "string",
      "target_model": "string",
      "priority": 0
    }
    ```
*   **Response (201 Created)**: `RoutingRule`
    ```json
    {
      "name": "string",
      "condition": "string",
      "target_model": "string",
      "priority": 0,
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/cognisys/routing-rules`

*   **Description**: Retrieves a list of all LLM routing rules for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[RoutingRule]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/cognisys/routing-rules/{rule_id}`

*   **Description**: Retrieves a specific LLM routing rule by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `rule_id` (string, required): The ID of the routing rule.
*   **Response (200 OK)**: `RoutingRule`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Routing Rule not found.

### `PUT /api/cognisys/routing-rules/{rule_id}`

*   **Description**: Updates an existing LLM routing rule.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `rule_id` (string, required): The ID of the routing rule to update.
*   **Request Body**: `RoutingRuleUpdate`
    ```json
    {
      "name": "string_or_null",
      "condition": "string_or_null",
      "target_model": "string_or_null",
      "priority": 0
    }
    ```
*   **Response (200 OK)**: `RoutingRule`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Routing Rule not found.

### `DELETE /api/cognisys/routing-rules/{rule_id}`

*   **Description**: Deletes a specific LLM routing rule.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `rule_id` (string, required): The ID of the routing rule to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Routing Rule not found.

---

## 7. Myntrix API

Myntrix manages agents and devices.

### `POST /api/myntrix/agents/`

*   **Description**: Creates a new agent.
*   **Authentication Required**: Yes
*   **Request Body**: `AgentCreate`
    ```json
    {
      "name": "string",
      "type": "string",
      "status": "string",
      "health": 0,
      "configuration": {}
    }
    ```
*   **Response (201 Created)**: `Agent`
    ```json
    {
      "id": "uuid_string",
      "owner_id": "uuid_string",
      "name": "string",
      "type": "string",
      "status": "string",
      "health": 0,
      "last_run": "datetime_string_or_null",
      "configuration": {}
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/myntrix/agents/`

*   **Description**: Retrieves a list of all agents for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[Agent]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/myntrix/agents/{agent_id}`

*   **Description**: Retrieves a specific agent by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `agent_id` (string, required): The ID of the agent.
*   **Response (200 OK)**: `Agent`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Agent not found.

### `PUT /api/myntrix/agents/{agent_id}`

*   **Description**: Updates an existing agent.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `agent_id` (string, required): The ID of the agent to update.
*   **Request Body**: `AgentUpdate`
    ```json
    {
      "name": "string_or_null",
      "type": "string_or_null",
      "status": "string_or_null",
      "health": 0,
      "last_run": "datetime_string_or_null",
      "configuration": {}
    }
    ```
*   **Response (200 OK)**: `Agent`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Agent not found.

### `POST /api/myntrix/agents/{agent_id}/start`

*   **Description**: Starts a specific agent. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `agent_id` (string, required): The ID of the agent to start.
*   **Response (200 OK)**: `Agent`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Agent not found.

### `POST /api/myntrix/agents/{agent_id}/stop`

*   **Description**: Stops a specific agent. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `agent_id` (string, required): The ID of the agent to stop.
*   **Response (200 OK)**: `Agent`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Agent not found.

### `POST /api/myntrix/agents/{agent_id}/restart`

*   **Description**: Restarts a specific agent. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `agent_id` (string, required): The ID of the agent to restart.
*   **Response (200 OK)**: `Agent`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Agent not found.

### `DELETE /api/myntrix/agents/{agent_id}`

*   **Description**: Deletes a specific agent.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `agent_id` (string, required): The ID of the agent to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Agent not found.

### `POST /api/myntrix/devices/`

*   **Description**: Creates a new device.
*   **Authentication Required**: Yes
*   **Request Body**: `DeviceCreate`
    ```json
    {
      "name": "string",
      "type": "string",
      "connection_string": "string",
      "status": "string",
      "firmware_version": "string_or_null",
      "configuration": {}
    }
    ```
*   **Response (201 Created)**: `Device`
    ```json
    {
      "id": "uuid_string",
      "owner_id": "uuid_string",
      "name": "string",
      "type": "string",
      "connection_string": "string",
      "status": "string",
      "last_seen": "datetime_string_or_null",
      "firmware_version": "string_or_null",
      "configuration": {}
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/myntrix/devices/`

*   **Description**: Retrieves a list of all devices for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[Device]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/myntrix/devices/{device_id}`

*   **Description**: Retrieves a specific device by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device.
*   **Response (200 OK)**: `Device`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `PUT /api/myntrix/devices/{device_id}`

*   **Description**: Updates an existing device.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device to update.
*   **Request Body**: `DeviceUpdate`
    ```json
    {
      "name": "string_or_null",
      "type": "string_or_null",
      "connection_string": "string_or_null",
      "status": "string_or_null",
      "last_seen": "datetime_string_or_null",
      "firmware_version": "string_or_null",
      "configuration": {}
    }
    ```
*   **Response (200 OK)**: `Device`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `DELETE /api/myntrix/devices/{device_id}`

*   **Description**: Deletes a specific device.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `POST /api/myntrix/devices/{device_id}/connect`

*   **Description**: Connects to a specific device. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device to connect.
*   **Response (200 OK)**: `Device`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `POST /api/myntrix/devices/{device_id}/disconnect`

*   **Description**: Disconnects from a specific device. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device to disconnect.
*   **Response (200 OK)**: `Device`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `POST /api/myntrix/devices/{device_id}/command`

*   **Description**: Sends a command to a specific device. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device to send the command to.
*   **Request Body**:
    ```json
    {
      "command": "string"
    }
    ```
*   **Response (200 OK)**: `Dict[str, str]`
    ```json
    {
      "message": "string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `POST /api/myntrix/devices/{device_id}/upload`

*   **Description**: Uploads a file to a specific device. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `device_id` (string, required): The ID of the device to upload the file to.
*   **Request Body**: `multipart/form-data`
    *   `file` (file, required): The file to upload.
*   **Response (200 OK)**: `Dict[str, str]`
    ```json
    {
      "message": "string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Device not found.

### `GET /api/myntrix/system-metrics`

*   **Description**: Retrieves real-time system metrics (CPU, memory).
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `Dict[str, Any]`
    ```json
    {
      "cpu_percent": 0,
      "memory_percent": 0,
      "memory_total": 0,
      "memory_available": 0,
      "timestamp": "datetime_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `500 Internal Server Error`: Failed to get system metrics (e.g., PermissionError).

### `GET /api/myntrix/jobs/`

*   **Description**: Retrieves a list of all jobs for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[JobResponse]`
    ```json
    [
      {
        "name": "string",
        "type": "string",
        "status": "string",
        "progress": 0,
        "created_at": "datetime_string_or_null",
        "updated_at": "datetime_string_or_null",
        "logs": "string_or_null",
        "details": {},
        "id": "uuid_string",
        "owner_id": "uuid_string"
      }
    ]
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `POST /api/myntrix/tasks/`

*   **Description**: Creates a new scheduled task.
*   **Authentication Required**: Yes
*   **Request Body**: `ScheduledTaskCreate`
    ```json
    {
      "name": "string",
      "schedule": "string",
      "action": {},
      "enabled": true
    }
    ```
*   **Response (201 Created)**: `ScheduledTaskResponse`
    ```json
    {
      "name": "string",
      "schedule": "string",
      "action": {},
      "enabled": true,
      "created_at": "datetime_string_or_null",
      "updated_at": "datetime_string_or_null",
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/myntrix/tasks/`

*   **Description**: Retrieves a list of all scheduled tasks for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[ScheduledTaskResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/myntrix/tasks/{task_id}`

*   **Description**: Retrieves a specific scheduled task by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `task_id` (string, required): The ID of the scheduled task.
*   **Response (200 OK)**: `ScheduledTaskResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Scheduled Task not found.

### `PUT /api/myntrix/tasks/{task_id}`

*   **Description**: Updates an existing scheduled task.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `task_id` (string, required): The ID of the scheduled task to update.
*   **Request Body**: `ScheduledTaskUpdate`
    ```json
    {
      "name": "string_or_null",
      "schedule": "string_or_null",
      "action": {},
      "enabled": true
    }
    ```
*   **Response (200 OK)**: `ScheduledTaskResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Scheduled Task not found.

### `DELETE /api/myntrix/tasks/{task_id}`

*   **Description**: Deletes a specific scheduled task.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `task_id` (string, required): The ID of the scheduled task to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Scheduled Task not found.

### `POST /api/myntrix/tasks/{task_id}/run`

*   **Description**: Runs a specific scheduled task immediately. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `task_id` (string, required): The ID of the scheduled task to run.
*   **Response (200 OK)**: `TaskRunResponse`
    ```json
    {
      "task_id": "uuid_string",
      "start_time": "datetime_string_or_null",
      "end_time": "datetime_string_or_null",
      "status": "string",
      "logs": "string_or_null",
      "id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Scheduled Task not found.

### `GET /api/myntrix/tasks/history/{task_id}`

*   **Description**: Retrieves the run history for a specific scheduled task.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `task_id` (string, required): The ID of the scheduled task.
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[TaskRunResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Scheduled Task not found.

### `GET /api/myntrix/visualization-data`

*   **Description**: Aggregates data from agents and devices for 3D visualization.
*   **Authentication Required**: Yes
*   **Response (200 OK)**: `Dict[str, Any]`
    ```json
    {
      "agents": [
        {
          "id": "uuid_string",
          "name": "string",
          "type": "string",
          "status": "string",
          "health": 0,
          "last_run": "datetime_string_or_null",
          "configuration": {}
        }
      ],
      "devices": [
        {
          "id": "uuid_string",
          "name": "string",
          "type": "string",
          "connection_string": "string",
          "status": "string",
          "last_seen": "datetime_string_or_null",
          "firmware_version": "string_or_null",
          "configuration": {}
        }
      ],
      "timestamp": "datetime_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

---

## 8. Neosyntis API

Neosyntis focuses on data, workflows, and ML models.

### `POST /api/neosyntis/workflows/`

*   **Description**: Creates a new workflow.
*   **Authentication Required**: Yes
*   **Request Body**: `WorkflowCreate`
    ```json
    {
      "name": "string",
      "description": "string_or_null",
      "status": "string",
      "steps": "json_string"
    }
    ```
*   **Response (201 Created)**: `WorkflowResponse`
    ```json
    {
      "name": "string",
      "description": "string_or_null",
      "status": "string",
      "steps": "json_string",
      "created_at": "datetime_string_or_null",
      "updated_at": "datetime_string_or_null",
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/workflows/`

*   **Description**: Retrieves a list of all workflows for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[WorkflowResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/workflows/{workflow_id}`

*   **Description**: Retrieves a specific workflow by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `workflow_id` (string, required): The ID of the workflow.
*   **Response (200 OK)**: `WorkflowResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Workflow not found.

### `PUT /api/neosyntis/workflows/{workflow_id}`

*   **Description**: Updates an existing workflow.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `workflow_id` (string, required): The ID of the workflow to update.
*   **Request Body**: `WorkflowUpdate`
    ```json
    {
      "name": "string_or_null",
      "description": "string_or_null",
      "status": "string_or_null",
      "steps": "json_string_or_null"
    }
    ```
*   **Response (200 OK)**: `WorkflowResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Workflow not found.

### `DELETE /api/neosyntis/workflows/{workflow_id}`

*   **Description**: Deletes a specific workflow.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `workflow_id` (string, required): The ID of the workflow to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Workflow not found.

### `POST /api/neosyntis/workflows/{workflow_id}/trigger`

*   **Description**: Triggers the execution of a specific workflow. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `workflow_id` (string, required): The ID of the workflow to trigger.
*   **Response (200 OK)**: `WorkflowResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Workflow not found.

### `GET /api/neosyntis/workflows/{workflow_id}/status`

*   **Description**: Retrieves the status of a specific workflow.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `workflow_id` (string, required): The ID of the workflow.
*   **Response (200 OK)**: `WorkflowResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Workflow not found.

### `POST /api/neosyntis/datasets/upload`

*   **Description**: Uploads a new dataset.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `name` (string, required): The name of the dataset.
    *   `format` (string, required): The format of the dataset (e.g., "csv", "json").
    *   `description` (string, optional): A description of the dataset.
*   **Request Body**: `multipart/form-data`
    *   `file` (file, required): The dataset file to upload.
*   **Response (201 Created)**: `DatasetResponse`
    ```json
    {
      "name": "string",
      "description": "string_or_null",
      "file_path": "string_or_null",
      "size_bytes": 0,
      "format": "string",
      "uploaded_at": "datetime_string_or_null",
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/datasets/`

*   **Description**: Retrieves a list of all datasets for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[DatasetResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/datasets/{dataset_id}`

*   **Description**: Retrieves a specific dataset by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `dataset_id` (string, required): The ID of the dataset.
*   **Response (200 OK)**: `DatasetResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Dataset not found.

### `PUT /api/neosyntis/datasets/{dataset_id}`

*   **Description**: Updates an existing dataset.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `dataset_id` (string, required): The ID of the dataset to update.
*   **Request Body**: `DatasetUpdate`
    ```json
    {
      "name": "string_or_null",
      "description": "string_or_null",
      "file_path": "string_or_null",
      "size_bytes": 0,
      "format": "string_or_null",
      "uploaded_at": "datetime_string_or_null"
    }
    ```
*   **Response (200 OK)**: `DatasetResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Dataset not found.

### `DELETE /api/neosyntis/datasets/{dataset_id}`

*   **Description**: Deletes a specific dataset.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `dataset_id` (string, required): The ID of the dataset to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Dataset not found.

### `GET /api/neosyntis/datasets/{dataset_id}/download`

*   **Description**: Downloads a specific dataset file.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `dataset_id` (string, required): The ID of the dataset to download.
*   **Response (200 OK)**: `FileResponse` (binary file content)
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Dataset or dataset file not found.

### `POST /api/neosyntis/telemetry/ingest`

*   **Description**: Ingests telemetry data.
*   **Authentication Required**: Yes
*   **Request Body**: `TelemetryDataCreate`
    ```json
    {
      "timestamp": "datetime_string_or_null",
      "metric_name": "string",
      "value": 0,
      "workflow_id": "uuid_string_or_null",
      "dataset_id": "uuid_string_or_null",
      "device_id": "uuid_string_or_null"
    }
    ```
*   **Response (201 Created)**: `TelemetryDataResponse`
    ```json
    {
      "timestamp": "datetime_string_or_null",
      "metric_name": "string",
      "value": 0,
      "workflow_id": "uuid_string_or_null",
      "dataset_id": "uuid_string_or_null",
      "device_id": "uuid_string_or_null",
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/telemetry/`

*   **Description**: Retrieves telemetry data for the current user, optionally filtered by metric name.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `metric_name` (string, optional): Filter telemetry data by metric name.
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[TelemetryDataResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `POST /api/neosyntis/models/`

*   **Description**: Creates a new ML model.
*   **Authentication Required**: Yes
*   **Request Body**: `MLModelCreate`
    ```json
    {
      "name": "string",
      "version": "string",
      "status": "string",
      "path_to_artifact": "string_or_null",
      "training_dataset_id": "uuid_string_or_null",
      "deployed_at": "datetime_string_or_null"
    }
    ```
*   **Response (201 Created)**: `MLModelResponse`
    ```json
    {
      "name": "string",
      "version": "string",
      "status": "string",
      "path_to_artifact": "string_or_null",
      "training_dataset_id": "uuid_string_or_null",
      "deployed_at": "datetime_string_or_null",
      "created_at": "datetime_string_or_null",
      "updated_at": "datetime_string_or_null",
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/models/`

*   **Description**: Retrieves a list of all ML models for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[MLModelResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/models/{model_id}`

*   **Description**: Retrieves a specific ML model by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the ML model.
*   **Response (200 OK)**: `MLModelResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: ML Model not found.

### `PUT /api/neosyntis/models/{model_id}`

*   **Description**: Updates an existing ML model.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the ML model to update.
*   **Request Body**: `MLModelUpdate`
    ```json
    {
      "name": "string_or_null",
      "version": "string_or_null",
      "status": "string_or_null",
      "path_to_artifact": "string_or_null",
      "training_dataset_id": "uuid_string_or_null",
      "deployed_at": "datetime_string_or_null"
    }
    ```
*   **Response (200 OK)**: `MLModelResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: ML Model not found.

### `DELETE /api/neosyntis/models/{model_id}`

*   **Description**: Deletes a specific ML model.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the ML model to delete.
*   **Response (204 No Content)**: `{"ok": true}`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: ML Model not found.

### `POST /api/neosyntis/models/{model_id}/deploy`

*   **Description**: Deploys a specific ML model. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the ML model to deploy.
*   **Response (200 OK)**: `MLModelResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: ML Model not found.

### `POST /api/neosyntis/models/{model_id}/train`

*   **Description**: Initiates training for a specific ML model. (Currently a placeholder).
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `model_id` (string, required): The ID of the ML model to train.
*   **Response (200 OK)**: `TrainingJobResponse`
    ```json
    {
      "model_id": "uuid_string",
      "status": "string",
      "start_time": "datetime_string_or_null",
      "end_time": "datetime_string_or_null",
      "metrics": {},
      "logs": "string_or_null",
      "created_at": "datetime_string_or_null",
      "updated_at": "datetime_string_or_null",
      "id": "uuid_string",
      "owner_id": "uuid_string"
    }
    ```
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: ML Model not found.

### `GET /api/neosyntis/training-jobs/`

*   **Description**: Retrieves a list of all training jobs for the current user.
*   **Authentication Required**: Yes
*   **Query Parameters**:
    *   `skip` (integer, optional, default: 0): Number of items to skip.
    *   `limit` (integer, optional, default: 100): Maximum number of items to return.
*   **Response (200 OK)**: `List[TrainingJobResponse]`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.

### `GET /api/neosyntis/training-jobs/{job_id}`

*   **Description**: Retrieves a specific training job by ID.
*   **Authentication Required**: Yes
*   **Path Parameters**:
    *   `job_id` (string, required): The ID of the training job.
*   **Response (200 OK)**: `TrainingJobResponse`
*   **Error Responses**:
    *   `401 Unauthorized`: Invalid or missing token.
    *   `404 Not Found`: Training Job not found.
