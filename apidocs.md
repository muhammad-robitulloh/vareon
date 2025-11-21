# API Documentation

## Arcana Endpoints

#### `GET /version`
*   **Description**: Returns the current version of the Arcana backend.
*   **Method**: `GET`
*   **Function**: `get_backend_version`
*   **Response Model**: `{"version": "0.1.0-alpha"}`
*   **Authentication**: None

#### `GET /file-tree/`
*   **Description**: Retrieves the entire file tree for the user's sandboxed project directory. This provides a hierarchical view of all files and folders.
*   **Method**: `GET`
*   **Function**: `get_arcana_file_tree`
*   **Response Model**: `List[schemas.FileInfo]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /agents/`
*   **Description**: Create a new Arcana agent for the current user.
*   **Method**: `POST`
*   **Function**: `create_arcana_agent`
*   **Request Body**: `schemas.ArcanaAgentCreate`
*   **Response Model**: `schemas.ArcanaAgentResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /agents/`
*   **Description**: Retrieve all Arcana agents for the current user.
*   **Method**: `GET`
*   **Function**: `read_arcana_agents`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.ArcanaAgentResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /agents/{agent_id}`
*   **Description**: Retrieve a specific Arcana agent by its ID.
*   **Method**: `GET`
*   **Function**: `read_arcana_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Response Model**: `schemas.ArcanaAgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /agents/{agent_id}`
*   **Description**: Update an Arcana agent.
*   **Method**: `PUT`
*   **Function**: `update_arcana_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Request Body**: `schemas.ArcanaAgentUpdate`
*   **Response Model**: `schemas.ArcanaAgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /agents/{agent_id}`
*   **Description**: Delete an Arcana agent.
*   **Method**: `DELETE`
*   **Function**: `delete_arcana_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /generate-code`
*   **Description**: Generates code based on a natural language prompt.
*   **Method**: `POST`
*   **Function**: `generate_code_endpoint`
*   **Request Body**: `schemas.CodeGenerationRequest`
*   **Response Model**: `schemas.CodeGenerationResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /translate-shell-command`
*   **Description**: Translates a natural language instruction into a shell command.
*   **Method**: `POST`
*   **Function**: `translate_shell_command_endpoint`
*   **Request Body**: `schemas.ShellCommandTranslationRequest`
*   **Response Model**: `schemas.ShellCommandTranslationResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /generate-reasoning`
*   **Description**: Generates a detailed reasoning trace for a given task.
*   **Method**: `POST`
*   **Function**: `generate_reasoning_endpoint`
*   **Request Body**: `schemas.ReasoningRequest`
*   **Response Model**: `schemas.ReasoningResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /file-operations`
*   **Description**: Performs various file operations within the user's sandboxed directory.
*   **Method**: `POST`
*   **Function**: `file_operations_endpoint`
*   **Request Body**: `schemas.FileOperationRequest`
*   **Response Model**: `schemas.FileOperationResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /agents/{agent_id}/execute`
*   **Description**: Executes a task for a specific Arcana Agent as a background job.
*   **Method**: `POST`
*   **Function**: `execute_arcana_agent_task`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Request Body**: `schemas.AgentExecuteRequest`
*   **Response Model**: `schemas.ArcanaAgentJobResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /agents/{agent_id}/jobs/`
*   **Description**: Get all jobs for a specific agent.
*   **Method**: `GET`
*   **Function**: `get_agent_jobs`
*   **Parameters**:
    *   `agent_id`: `str` (path)
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 10)
*   **Response Model**: `List[schemas.ArcanaAgentJobResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /jobs/{job_id}`
*   **Description**: Get the status and details of a specific agent job.
*   **Method**: `GET`
*   **Function**: `get_agent_job`
*   **Parameters**:
    *   `job_id`: `str` (path)
*   **Response Model**: `schemas.ArcanaAgentJobResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /jobs/{job_id}/logs`
*   **Description**: Get the logs for a specific agent job.
*   **Method**: `GET`
*   **Function**: `get_agent_job_logs`
*   **Parameters**:
    *   `job_id`: `str` (path)
*   **Response Model**: `List[schemas.ArcanaAgentJobLogResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /jobs/{job_id}/submit_human_input`
*   **Description**: Submits human input to an agent job that is awaiting human input and resumes its execution.
*   **Method**: `POST`
*   **Function**: `submit_human_input`
*   **Parameters**:
    *   `job_id`: `str` (path)
*   **Request Body**: `schemas.HumanInputRequest`
*   **Response Model**: `schemas.ArcanaAgentJobResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /jobs/{job_id}/resume`
*   **Description**: Resume a job that is awaiting human input. This endpoint is now deprecated in favor of submit_human_input.
*   **Method**: `POST`
*   **Function**: `resume_agent_job`
*   **Parameters**:
    *   `job_id`: `str` (path)
*   **Response Model**: (Raises `HTTPException` with 400)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /cli/execute`
*   **Description**: Executes a command received from the Arcana CLI. This endpoint validates the API key and routes the command to the appropriate Arcana service.
*   **Method**: `POST`
*   **Function**: `execute_cli_command`
*   **Request Body**: `ArcanaCliCommandRequest` (imported from `server_python.schemas`)
*   **Response Model**: `ArcanaCliCommandResponse` (imported from `server_python.schemas`)
*   **Authentication**: API Key required (validated internally)

#### `POST /api-keys/`
*   **Description**: Generates a new Arcana API key for the current user.
*   **Method**: `POST`
*   **Function**: `create_arcana_api_key`
*   **Request Body**: `schemas.ArcanaApiKeyCreate`
*   **Response Model**: `ArcanaApiKeyResponse` (imported from `server_python.schemas`)
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /api-keys/`
*   **Description**: Retrieves all Arcana API keys for the current user.
*   **Method**: `GET`
*   **Function**: `get_arcana_api_keys`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[ArcanaApiKeyResponse]` (imported from `server_python.schemas`)
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /api-keys/{api_key_id}`
*   **Description**: Deactivates an Arcana API key for the current user.
*   **Method**: `DELETE`
*   **Function**: `deactivate_arcana_api_key`
*   **Parameters**:
    *   `api_key_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /api-keys/{api_key_id}/rotate`
*   **Description**: Rotates an Arcana API key: deactivates the old one and creates a new one.
*   **Method**: `POST`
*   **Function**: `rotate_arcana_api_key`
*   **Parameters**:
    *   `api_key_id`: `str` (path)
    *   `new_key_name`: `str` (body/form parameter, usually passed in request body)
*   **Response Model**: `ArcanaApiKeyResponse` (imported from `server_python.schemas`)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /cli-configs/`
*   **Description**: Creates a new CLI configuration setting or updates an existing one for the current user.
*   **Method**: `POST`
*   **Function**: `create_or_update_cli_config`
*   **Request Body**: `schemas.UserCliConfigCreate`
*   **Response Model**: `schemas.UserCliConfigResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /cli-configs/`
*   **Description**: Retrieves all CLI configuration settings for the current user.
*   **Method**: `GET`
*   **Function**: `get_all_cli_configs`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.UserCliConfigResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /cli-configs/{key}`
*   **Description**: Retrieves a specific CLI configuration setting for the current user by key.
*   **Method**: `GET`
*   **Function**: `get_cli_config`
*   **Parameters**:
    *   `key`: `str` (path)
*   **Response Model**: `schemas.UserCliConfigResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /cli-configs/{key}`
*   **Description**: Deletes a specific CLI configuration setting for the current user by key.
*   **Method**: `DELETE`
*   **Function**: `delete_cli_config`
*   **Parameters**:
    *   `key`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)


## Cognisys Endpoints

#### `POST /providers/`
*   **Description**: Creates a new LLM provider.
*   **Method**: `POST`
*   **Function**: `create_llm_provider`
*   **Request Body**: `schemas.LLMProviderCreate`
*   **Response Model**: `schemas.LLMProviderResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `GET /providers/`
*   **Description**: Reads LLM providers.
*   **Method**: `GET`
*   **Function**: `read_llm_providers`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.LLMProviderResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /providers/{provider_id}`
*   **Description**: Reads a specific LLM provider by ID.
*   **Method**: `GET`
*   **Function**: `read_llm_provider`
*   **Parameters**:
    *   `provider_id`: `str` (path)
*   **Response Model**: `schemas.LLMProviderResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /providers/{provider_id}`
*   **Description**: Updates an LLM provider.
*   **Method**: `PUT`
*   **Function**: `update_llm_provider`
*   **Parameters**:
    *   `provider_id`: `str` (path)
*   **Request Body**: `schemas.LLMProviderUpdate`
*   **Response Model**: `schemas.LLMProviderResponse`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `DELETE /providers/{provider_id}`
*   **Description**: Deletes an LLM provider.
*   **Method**: `DELETE`
*   **Function**: `delete_llm_provider`
*   **Parameters**:
    *   `provider_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `POST /providers/{provider_id}/test-connection`
*   **Description**: Tests connection for a specific LLM provider.
*   **Method**: `POST`
*   **Function**: `test_llm_provider_connection`
*   **Parameters**:
    *   `provider_id`: `str` (path)
*   **Response Model**: `{"message": str, "status": "success" | "failure"}`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /models/`
*   **Description**: Creates a new LLM model.
*   **Method**: `POST`
*   **Function**: `create_llm_model`
*   **Request Body**: `schemas.LLMModelCreate`
*   **Response Model**: `schemas.LLMModelResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `GET /models/`
*   **Description**: Reads LLM models.
*   **Method**: `GET`
*   **Function**: `read_llm_models`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.LLMModelResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /models/{model_id}`
*   **Description**: Reads a specific LLM model by ID.
*   **Method**: `GET`
*   **Function**: `read_llm_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Response Model**: `schemas.LLMModelResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /models/{model_id}`
*   **Description**: Updates an LLM model.
*   **Method**: `PUT`
*   **Function**: `update_llm_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Request Body**: `schemas.LLMModelUpdate`
*   **Response Model**: `schemas.LLMModelResponse`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `DELETE /models/{model_id}`
*   **Description**: Deletes an LLM model.
*   **Method**: `DELETE`
*   **Function**: `delete_llm_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `POST /routing-rules/`
*   **Description**: Creates a new routing rule.
*   **Method**: `POST`
*   **Function**: `create_routing_rule`
*   **Request Body**: `schemas.RoutingRuleCreate`
*   **Response Model**: `schemas.RoutingRuleResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /routing-rules/`
*   **Description**: Reads routing rules.
*   **Method**: `GET`
*   **Function**: `read_routing_rules`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.RoutingRuleResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /routing-rules/{rule_id}`
*   **Description**: Reads a specific routing rule by ID.
*   **Method**: `GET`
*   **Function**: `read_routing_rule`
*   **Parameters**:
    *   `rule_id`: `str` (path)
*   **Response Model**: `schemas.RoutingRuleResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /routing-rules/{rule_id}`
*   **Description**: Updates a routing rule.
*   **Method**: `PUT`
*   **Function**: `update_routing_rule`
*   **Parameters**:
    *   `rule_id`: `str` (path)
*   **Request Body**: `schemas.RoutingRuleUpdate`
*   **Response Model**: `schemas.RoutingRuleResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /routing-rules/{rule_id}`
*   **Description**: Deletes a routing rule.
*   **Method**: `DELETE`
*   **Function**: `delete_routing_rule`
*   **Parameters**:
    *   `rule_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /chat`
*   **Description**: Initiates a chat with Cognisys.
*   **Method**: `POST`
*   **Function**: `chat_with_cognisys`
*   **Request Body**: `schemas.ChatRequest`
*   **Response Model**: `schemas.ChatResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /detect-intent`
*   **Description**: Detects the intent of the user's prompt using an LLM.
*   **Method**: `POST`
*   **Function**: `detect_user_intent`
*   **Request Body**: `schemas.IntentDetectionRequest`
*   **Response Model**: `schemas.IntentDetectionResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /system-prompts/`
*   **Description**: Creates a new system prompt.
*   **Method**: `POST`
*   **Function**: `create_system_prompt`
*   **Request Body**: `schemas.SystemPromptCreate`
*   **Response Model**: `schemas.SystemPromptResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `GET /system-prompts/`
*   **Description**: Reads system prompts.
*   **Method**: `GET`
*   **Function**: `read_system_prompts`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.SystemPromptResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /system-prompts/{prompt_id}`
*   **Description**: Reads a specific system prompt by ID.
*   **Method**: `GET`
*   **Function**: `read_system_prompt`
*   **Parameters**:
    *   `prompt_id`: `str` (path)
*   **Response Model**: `schemas.SystemPromptResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /system-prompts/{prompt_id}`
*   **Description**: Updates a system prompt.
*   **Method**: `PUT`
*   **Function**: `update_system_prompt`
*   **Parameters**:
    *   `prompt_id`: `str` (path)
*   **Request Body**: `schemas.SystemPromptUpdate`
*   **Response Model**: `schemas.SystemPromptResponse`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `DELETE /system-prompts/{prompt_id}`
*   **Description**: Deletes a system prompt.
*   **Method**: `DELETE`
*   **Function**: `delete_system_prompt`
*   **Parameters**:
    *   `prompt_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (`PermissionChecker(["admin_access"])`)

#### `GET /cli/model-details`
*   **Description**: Retrieves details of the user's preferred LLM model for CLI usage.
*   **Method**: `GET`
*   **Function**: `get_cli_model_details`
*   **Response Model**: `schemas.CliModelDetailsResponse`
*   **Authentication**: Required (depends on `get_current_user`)


## Context Memory Endpoints

#### `GET /`
*   **Description**: Retrieve all categorized context memory for the current user.
*   **Method**: `GET`
*   **Function**: `get_full_user_context`
*   **Response Model**: `schemas.FullContextResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /item`
*   **Description**: Create a new context item of a specific type.
*   **Method**: `POST`
*   **Function**: `create_new_context_item`
*   **Request Body**: `CreateItemPayload`
    *   `type`: `str` (e.g., 'preference', 'project', or 'conversation')
    *   `key`: `str` (e.g., "Preferred Language")
    *   `value`: `Dict[str, Any]` (JSON object)
*   **Response Model**: `Dict[str, Any]` (returns the created item's value with ID)
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /item/{item_id}`
*   **Description**: Delete a specific context item by its ID.
*   **Method**: `DELETE`
*   **Function**: `delete_context_item`
*   **Parameters**:
    *   `item_id`: `str` (path)
*   **Response Model**: `{"ok": True}`
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /item/{item_id}`
*   **Description**: Update the value of a specific context item.
*   **Method**: `PUT`
*   **Function**: `update_context_item`
*   **Parameters**:
    *   `item_id`: `str` (path)
*   **Request Body**: `UpdateItemPayload`
    *   `value`: `Dict[str, Any]` (JSON object)
*   **Response Model**: `Dict[str, Any]` (returns the updated item's value with ID)
*   **Authentication**: Required (depends on `get_current_user`)


## Git Service Endpoints

#### `GET /config`
*   **Description**: Retrieves the user's Git configuration.
*   **Method**: `GET`
*   **Function**: `get_user_git_config`
*   **Response Model**: `schemas.UserGitConfigResponse` (with masked PAT)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /config`
*   **Description**: Creates a new user Git configuration.
*   **Method**: `POST`
*   **Function**: `create_user_git_config`
*   **Request Body**: `schemas.UserGitConfigCreate`
*   **Response Model**: `schemas.UserGitConfigResponse` (with masked PAT)
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /config`
*   **Description**: Updates an existing user Git configuration.
*   **Method**: `PUT`
*   **Function**: `update_user_git_config`
*   **Request Body**: `schemas.UserGitConfigUpdate`
*   **Response Model**: `schemas.UserGitConfigResponse` (with masked PAT)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /config/disconnect-github`
*   **Description**: Disconnects the user's GitHub account by clearing the encrypted PAT.
*   **Method**: `POST`
*   **Function**: `disconnect_github`
*   **Response Model**: `schemas.MessageResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /init`
*   **Description**: Initializes a new Git repository.
*   **Method**: `POST`
*   **Function**: `init_repo`
*   **Request Body**: `schemas.GitInitRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /clone`
*   **Description**: Clones a Git repository from a given URL to a local path.
*   **Method**: `POST`
*   **Function**: `clone_repo`
*   **Request Body**: `schemas.GitCloneRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `GET /status`
*   **Description**: Gets the current Git status of a repository.
*   **Method**: `GET`
*   **Function**: `get_status`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Response Model**: `schemas.GitStatus`
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /add`
*   **Description**: Adds files to the Git staging area.
*   **Method**: `POST`
*   **Function**: `add_files`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitAddRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /commit`
*   **Description**: Commits staged changes to the repository.
*   **Method**: `POST`
*   **Function**: `commit_changes`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitCommitRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /push`
*   **Description**: Pushes committed changes to a remote repository.
*   **Method**: `POST`
*   **Function**: `push_changes`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitPushRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /pull`
*   **Description**: Pulls changes from a remote repository.
*   **Method**: `POST`
*   **Function**: `pull_changes`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitPullRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /checkout`
*   **Description**: Switches to a specified Git branch.
*   **Method**: `POST`
*   **Function**: `checkout_branch`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitCheckoutRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /branch`
*   **Description**: Creates a new Git branch.
*   **Method**: `POST`
*   **Function**: `create_branch`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitCreateBranchRequest`
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /diff`
*   **Description**: Generates a diff of changes in the Git repository.
*   **Method**: `POST`
*   **Function**: `get_diff`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Request Body**: `schemas.GitDiffRequest`
*   **Response Model**: `schemas.GitDiffResponse`
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `GET /log`
*   **Description**: Gets the commit log of a repository.
*   **Method**: `GET`
*   **Function**: `get_log`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Response Model**: `schemas.GitLogResponse`
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `GET /branches`
*   **Description**: Gets a list of branches in a repository.
*   **Method**: `GET`
*   **Function**: `get_branches`
*   **Parameters**:
    *   `local_path`: `str` (query)
*   **Response Model**: `List[schemas.GitBranch]`
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `GET /file_content`
*   **Description**: Reads the content of a file within a Git repository.
*   **Method**: `GET`
*   **Function**: `read_file_content`
*   **Parameters**:
    *   `local_path`: `str` (query)
    *   `file_path`: `str` (query)
*   **Response Model**: `str` (file content)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `POST /file_content` (Corrected Method, was GET in source code)
*   **Description**: Writes content to a file within a Git repository.
*   **Method**: `POST`
*   **Function**: `write_file_content`
*   **Parameters**:
    *   `local_path`: `str` (query)
    *   `file_path`: `str` (query)
*   **Request Body**: `schemas.GitFileContent` (contains `content: str`)
*   **Response Model**: `str` (message indicating success)
*   **Authentication**: Required (depends on `get_current_user` via `get_git_service`)

#### `GET /github/repositories`
*   **Description**: Gets a list of GitHub repositories accessible by the installed GitHub App.
*   **Method**: `GET`
*   **Function**: `get_github_repositories`
*   **Response Model**: List of GitHub repository objects
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /github/repositories/{owner}/{repo}/branches`
*   **Description**: Gets a list of branches for a specific GitHub repository.
*   **Method**: `GET`
*   **Function**: `get_github_repository_branches`
*   **Parameters**:
    *   `owner`: `str` (path)
    *   `repo`: `str` (path)
*   **Response Model**: List of GitHub branch objects
*   **Authentication**: Required (depends on `get_current_user`)


## Myntrix Endpoints

#### `POST /agents/`
*   **Description**: Creates a new agent.
*   **Method**: `POST`
*   **Function**: `create_agent`
*   **Request Body**: `schemas.AgentCreate`
*   **Response Model**: `schemas.AgentResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /agents/`
*   **Description**: Reads all agents for the current user.
*   **Method**: `GET`
*   **Function**: `read_agents`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.AgentResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /agents/{agent_id}`
*   **Description**: Reads a specific agent by ID.
*   **Method**: `GET`
*   **Function**: `read_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Response Model**: `schemas.AgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /agents/{agent_id}`
*   **Description**: Updates an agent.
*   **Method**: `PUT`
*   **Function**: `update_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Request Body**: `schemas.AgentUpdate`
*   **Response Model**: `schemas.AgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /agents/{agent_id}/start`
*   **Description**: Simulates starting an agent process.
*   **Method**: `POST`
*   **Function**: `start_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Response Model**: `schemas.AgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /agents/{agent_id}/stop`
*   **Description**: Simulates stopping an agent process.
*   **Method**: `POST`
*   **Function**: `stop_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Response Model**: `schemas.AgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /agents/{agent_id}/restart`
*   **Description**: Simulates restarting an agent process.
*   **Method**: `POST`
*   **Function**: `restart_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Response Model**: `schemas.AgentResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /agents/{agent_id}`
*   **Description**: Deletes an agent.
*   **Method**: `DELETE`
*   **Function**: `delete_agent`
*   **Parameters**:
    *   `agent_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /devices/`
*   **Description**: Creates a new device.
*   **Method**: `POST`
*   **Function**: `create_device`
*   **Request Body**: `schemas.DeviceCreate`
*   **Response Model**: `schemas.DeviceResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /devices/`
*   **Description**: Reads all devices for the current user.
*   **Method**: `GET`
*   **Function**: `read_devices`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.DeviceResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /devices/{device_id}`
*   **Description**: Reads a specific device by ID.
*   **Method**: `GET`
*   **Function**: `read_device`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Response Model**: `schemas.DeviceResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /devices/{device_id}`
*   **Description**: Updates a device.
*   **Method**: `PUT`
*   **Function**: `update_device`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Request Body**: `schemas.DeviceUpdate`
*   **Response Model**: `schemas.DeviceResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /devices/{device_id}`
*   **Description**: Deletes a device.
*   **Method**: `DELETE`
*   **Function**: `delete_device`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /devices/{device_id}/connect`
*   **Description**: Simulates connecting to a device.
*   **Method**: `POST`
*   **Function**: `connect_device`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Response Model**: `schemas.DeviceResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /devices/{device_id}/disconnect`
*   **Description**: Simulates disconnecting from a device.
*   **Method**: `POST`
*   **Function**: `disconnect_device`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Response Model**: `schemas.DeviceResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /devices/{device_id}/command`
*   **Description**: Sends a command to a device (placeholder).
*   **Method**: `POST`
*   **Function**: `send_device_command`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Request Body**: `Dict[str, str]` (expected to contain a 'command' key)
*   **Response Model**: `Dict[str, str]` (message indicating command sent)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /devices/{device_id}/upload`
*   **Description**: Uploads a file to a device (placeholder).
*   **Method**: `POST`
*   **Function**: `upload_file_to_device`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Request Body**: `UploadFile` (file to upload)
*   **Response Model**: `Dict[str, str]` (message indicating file uploaded)
*   **Authentication**: Required (depends on `get_current_user`)

#### `WS /ws/myntrix/telemetry/{device_id}`
*   **Description**: WebSocket endpoint for receiving and sending telemetry data to/from a device.
*   **Method**: `WebSocket`
*   **Function**: `websocket_telemetry_endpoint`
*   **Parameters**:
    *   `device_id`: `str` (path)
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /system-metrics`
*   **Description**: Retrieves system resource metrics (CPU, memory). Falls back to mock data if permissions are denied or in mock mode.
*   **Method**: `GET`
*   **Function**: `get_system_metrics`
*   **Response Model**: `Dict[str, Any]` (contains `cpu_percent`, `memory_percent`, `memory_total`, `memory_available`, `timestamp`, `mocked` (optional), `reason` (optional))
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /jobs/`
*   **Description**: Reads all jobs for the current user.
*   **Method**: `GET`
*   **Function**: `read_jobs`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.JobResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /tasks/`
*   **Description**: Creates a new scheduled task.
*   **Method**: `POST`
*   **Function**: `create_scheduled_task`
*   **Request Body**: `schemas.ScheduledTaskCreate`
*   **Response Model**: `schemas.ScheduledTaskResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /tasks/`
*   **Description**: Reads all scheduled tasks for the current user.
*   **Method**: `GET`
*   **Function**: `read_scheduled_tasks`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.ScheduledTaskResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /tasks/{task_id}`
*   **Description**: Reads a specific scheduled task by ID.
*   **Method**: `GET`
*   **Function**: `read_scheduled_task`
*   **Parameters**:
    *   `task_id`: `str` (path)
*   **Response Model**: `schemas.ScheduledTaskResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /tasks/{task_id}`
*   **Description**: Updates a scheduled task.
*   **Method**: `PUT`
*   **Function**: `update_scheduled_task`
*   **Parameters**:
    *   `task_id`: `str` (path)
*   **Request Body**: `schemas.ScheduledTaskUpdate`
*   **Response Model**: `schemas.ScheduledTaskResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /tasks/{task_id}`
*   **Description**: Deletes a scheduled task.
*   **Method**: `DELETE`
*   **Function**: `delete_scheduled_task`
*   **Parameters**:
    *   `task_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /tasks/{task_id}/run`
*   **Description**: Simulates running a scheduled task.
*   **Method**: `POST`
*   **Function**: `run_scheduled_task`
*   **Parameters**:
    *   `task_id`: `str` (path)
*   **Response Model**: `schemas.TaskRunResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /tasks/history/{task_id}`
*   **Description**: Retrieves the history of runs for a specific scheduled task.
*   **Method**: `GET`
*   **Function**: `get_task_history`
*   **Parameters**:
    *   `task_id`: `str` (path)
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.TaskRunResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /visualization-data`
*   **Description**: Retrieves aggregated data for 3D visualization, including agents and devices.
*   **Method**: `GET`
*   **Function**: `get_visualization_data`
*   **Response Model**: `Dict[str, Any]` (contains lists of agent and device data)
*   **Authentication**: Required (depends on `get_current_user`)


## Neosyntis Endpoints

#### `POST /workflows/`
*   **Description**: Creates a new workflow.
*   **Method**: `POST`
*   **Function**: `create_workflow`
*   **Request Body**: `schemas.WorkflowCreate`
*   **Response Model**: `schemas.WorkflowResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /workflows/`
*   **Description**: Reads all workflows for the current user.
*   **Method**: `GET`
*   **Function**: `read_workflows`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.WorkflowResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /workflows/{workflow_id}`
*   **Description**: Reads a specific workflow by ID.
*   **Method**: `GET`
*   **Function**: `read_workflow`
*   **Parameters**:
    *   `workflow_id`: `str` (path)
*   **Response Model**: `schemas.WorkflowResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /workflows/{workflow_id}`
*   **Description**: Updates a workflow.
*   **Method**: `PUT`
*   **Function**: `update_workflow`
*   **Parameters**:
    *   `workflow_id`: `str` (path)
*   **Request Body**: `schemas.WorkflowUpdate`
*   **Response Model**: `schemas.WorkflowResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /workflows/{workflow_id}`
*   **Description**: Deletes a workflow.
*   **Method**: `DELETE`
*   **Function**: `delete_workflow`
*   **Parameters**:
    *   `workflow_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /workflows/{workflow_id}/trigger`
*   **Description**: Simulates triggering a workflow execution.
*   **Method**: `POST`
*   **Function**: `trigger_workflow`
*   **Parameters**:
    *   `workflow_id`: `str` (path)
*   **Response Model**: `schemas.WorkflowResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /workflows/{workflow_id}/status`
*   **Description**: Retrieves the status of a specific workflow.
*   **Method**: `GET`
*   **Function**: `get_workflow_status`
*   **Parameters**:
    *   `workflow_id`: `str` (path)
*   **Response Model**: `schemas.WorkflowResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /datasets/upload`
*   **Description**: Uploads a new dataset.
*   **Method**: `POST`
*   **Function**: `upload_dataset`
*   **Parameters**:
    *   `name`: `str` (form field)
    *   `format`: `str` (form field)
    *   `file`: `UploadFile` (file upload)
    *   `description`: `Optional[str]` (form field)
*   **Response Model**: `schemas.DatasetResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /datasets/`
*   **Description**: Reads all datasets for the current user.
*   **Method**: `GET`
*   **Function**: `read_datasets`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.DatasetResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /datasets/{dataset_id}`
*   **Description**: Reads a specific dataset by ID.
*   **Method**: `GET`
*   **Function**: `read_dataset`
*   **Parameters**:
    *   `dataset_id`: `str` (path)
*   **Response Model**: `schemas.DatasetResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /datasets/{dataset_id}`
*   **Description**: Updates a dataset.
*   **Method**: `PUT`
*   **Function**: `update_dataset`
*   **Parameters**:
    *   `dataset_id`: `str` (path)
*   **Request Body**: `schemas.DatasetUpdate`
*   **Response Model**: `schemas.DatasetResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /datasets/{dataset_id}`
*   **Description**: Deletes a dataset.
*   **Method**: `DELETE`
*   **Function**: `delete_dataset`
*   **Parameters**:
    *   `dataset_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /datasets/{dataset_id}/download`
*   **Description**: Downloads a specific dataset file.
*   **Method**: `GET`
*   **Function**: `download_dataset`
*   **Parameters**:
    *   `dataset_id`: `str` (path)
*   **Response Model**: `FileResponse` (downloads the file)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /telemetry/ingest`
*   **Description**: Ingests telemetry data.
*   **Method**: `POST`
*   **Function**: `ingest_telemetry`
*   **Request Body**: `schemas.TelemetryDataCreate`
*   **Response Model**: `schemas.TelemetryDataResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /telemetry/`
*   **Description**: Retrieves telemetry data.
*   **Method**: `GET`
*   **Function**: `get_telemetry`
*   **Parameters**:
    *   `metric_name`: `Optional[str]` (query)
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.TelemetryDataResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /search`
*   **Description**: Searches Neosyntis entities (workflows, datasets, ML models).
*   **Method**: `GET`
*   **Function**: `search_neosyntis_entities`
*   **Parameters**:
    *   `query`: `str` (query)
    *   `entity_type`: `Optional[str]` (query, e.g., "workflows", "datasets", "ml_models")
*   **Response Model**: `List[Dict[str, Any]]` (list of search results)
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /models/`
*   **Description**: Creates a new ML model.
*   **Method**: `POST`
*   **Function**: `create_ml_model`
*   **Request Body**: `schemas.MLModelCreate`
*   **Response Model**: `schemas.MLModelResponse`
*   **Status Code**: `201 Created`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /models/`
*   **Description**: Reads all ML models for the current user.
*   **Method**: `GET`
*   **Function**: `read_ml_models`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.MLModelResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /models/{model_id}`
*   **Description**: Reads a specific ML model by ID.
*   **Method**: `GET`
*   **Function**: `read_ml_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Response Model**: `schemas.MLModelResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `PUT /models/{model_id}`
*   **Description**: Updates an ML model.
*   **Method**: `PUT`
*   **Function**: `update_ml_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Request Body**: `schemas.MLModelUpdate`
*   **Response Model**: `schemas.MLModelResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `DELETE /models/{model_id}`
*   **Description**: Deletes an ML model.
*   **Method**: `DELETE`
*   **Function**: `delete_ml_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Status Code**: `204 No Content`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /models/{model_id}/deploy`
*   **Description**: Simulates deploying an ML model.
*   **Method**: `POST`
*   **Function**: `deploy_ml_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Response Model**: `schemas.MLModelResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `POST /models/{model_id}/train`
*   **Description**: Simulates initiating training for an ML model.
*   **Method**: `POST`
*   **Function**: `train_ml_model`
*   **Parameters**:
    *   `model_id`: `str` (path)
*   **Response Model**: `schemas.TrainingJobResponse`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /training-jobs/`
*   **Description**: Reads all training jobs for the current user.
*   **Method**: `GET`
*   **Function**: `read_training_jobs`
*   **Parameters**:
    *   `skip`: `int` (query, default: 0)
    *   `limit`: `int` (query, default: 100)
*   **Response Model**: `List[schemas.TrainingJobResponse]`
*   **Authentication**: Required (depends on `get_current_user`)

#### `GET /training-jobs/{job_id}`
*   **Description**: Reads a specific training job by ID.
*   **Method**: `GET`
*   **Function**: `read_training_job`
*   **Parameters**:
    *   `job_id`: `str` (path)
*   **Response Model**: `schemas.TrainingJobResponse`
*   **Authentication**: Required (depends on `get_current_user`)