# Backend Realization V1: Cognisys Dashboard

**Goal:** Replace all mock data and mock functionalities in the Cognisys Dashboard with a fully functional backend implementation. This document outlines the roadmap and a detailed checklist for the first phase of backend implementation, focusing exclusively on the Cognisys Dashboard components.

---

## Phase 1: Cognisys Dashboard Backend Implementation

### Roadmap:

1.  **Core Infrastructure & Setup:**
    *   Establish a robust API framework (e.g., FastAPI, Express.js) within the `server-python/` directory.
    *   Implement database connection and an Object-Relational Mapper (ORM) (e.g., Drizzle, SQLAlchemy).
    *   Set up basic error handling and logging mechanisms.
    *   Configure environment variables for sensitive data such as API keys and database credentials.

2.  **LLM Provider Management (`provider-settings-tab.tsx`):**
    *   **Objective:** Enable users to configure and manage their LLM provider settings, including API keys, securely.
    *   **API Endpoints:**
        *   `GET /api/cognisys/providers`: Retrieve a list of all configured LLM providers. This endpoint should *not* expose sensitive API keys to the frontend.
        *   `POST /api/cognisys/providers`: Create a new LLM provider configuration.
        *   `PUT /api/cognisys/providers/{id}`: Update an existing LLM provider's configuration (e.g., enable/disable status, base URL, API key, organization ID).
        *   `DELETE /api/cognisys/providers/{id}`: Remove an LLM provider configuration.
        *   `POST /api/cognisys/providers/{id}/test-connection`: An endpoint to test the connectivity and authentication with a specific LLM provider using the stored credentials.
    *   **Database Schema:**
        *   A `providers` table with fields: `id` (primary key), `name` (string), `baseUrl` (string), `enabled` (boolean), `encryptedApiKey` (string, for secure storage), `organizationId` (string, nullable).
    *   **Security Considerations:**
        *   API keys must be encrypted before being stored in the database and decrypted only when needed for backend operations (e.g., testing connection, making LLM calls).
        *   Ensure secure handling of API keys in transit and at rest.
        *   Implement appropriate authentication and authorization for these API endpoints.

3.  **AI Model Mapping (`model-map-tab.tsx`):**
    *   **Objective:** Provide the frontend with a list of available AI models and their current status for visualization and selection.
    *   **API Endpoint:**
        *   `GET /api/cognisys/models`: Retrieve a list of AI models, including their associated provider, type, and active status.
    *   **Database Schema:**
        *   A `models` table with fields: `id` (primary key), `name` (string), `providerId` (foreign key to `providers` table), `type` (string), `isActive` (boolean), `reasoning` (boolean), `role` (string, nullable).
    *   **Business Logic:**
        *   Consider mechanisms to dynamically discover or update model availability from integrated LLM providers, or manage them manually.

4.  **Routing Rules Management (`routing-rules-tab.tsx`):**
    *   **Objective:** Allow users to define and manage rules that dictate how incoming requests are routed to different AI models based on intent and conditions.
    *   **API Endpoints:**
        *   `GET /api/cognisys/routing-rules`: Fetch all defined routing rules.
        *   `POST /api/cognisys/routing-rules`: Create a new routing rule.
        *   `PUT /api/cognisys/routing-rules/{id}`: Update an existing routing rule.
        *   `DELETE /api/cognisys/routing-rules/{id}`: Delete a routing rule.
    *   **Database Schema:**
        *   A `routing_rules` table with fields: `id` (primary key), `intent` (string), `condition` (string, e.g., a mini-language for conditions), `targetModelId` (foreign key to `models` table), `priority` (integer).

5.  **Test Console & AI Interaction (`test-console-tab.tsx`):**
    *   **Objective:** Enable users to test prompts, observe LLM responses, and visualize the routing decisions made by Cognisys.
    *   **API Endpoint:**
        *   `POST /api/cognisys/chat`: The central endpoint for processing user prompts. It will handle intent detection, rule-based routing, LLM interaction, and response generation.
    *   **Business Logic:**
        *   **Intent Detection:** Implement logic to analyze the user's `prompt` and determine its underlying `intent`. This could range from simple keyword matching to more advanced LLM-based classification.
        *   **Rule Evaluation:** Develop an engine to evaluate the defined `routing_rules` against the detected `intent` and `prompt` content. The highest priority matching rule should determine the `targetModel`.
        *   **LLM Integration:** Implement a layer to interact with various LLM providers (OpenAI, Anthropic, Google, etc.) using their respective APIs. This layer will use the decrypted API keys and base URLs from the `providers` configuration.
        *   **Response Handling:** Process and format the responses received from the LLMs.
        *   **Token Counting:** Accurately track and report token usage for each LLM interaction.
        *   **Visualization Data Generation:** Generate the `nodes` and `edges` data required by the `react-flow` component to visually represent the routing path and decision-making process for each query.
    *   **Database (Optional):**
        *   A `chat_history` table for logging and auditing purposes, including fields like `id`, `userId`, `prompt`, `response`, `modelUsed`, `tokensUsed`, `timestamp`.

---

### Checklist for Backend Realization V1: Cognisys Dashboard

#### **General:**

*   [ ] Set up the backend project structure within `server-python/cognisys/`.
*   [ ] Configure the database connection (e.g., PostgreSQL, SQLite).
*   [ ] Implement basic authentication middleware for all Cognisys API endpoints (e.g., token-based authentication).
*   [ ] Implement centralized error handling for API responses.
*   [ ] Implement comprehensive logging for API requests and LLM interactions.

#### **LLM Provider Management:**

*   **Database:**
    *   [ ] Create `providers` table with columns: `id` (UUID/PK), `name` (TEXT), `baseUrl` (TEXT), `enabled` (BOOLEAN), `encryptedApiKey` (TEXT), `organizationId` (TEXT, nullable).
*   **API Endpoints:**
    *   [ ] Implement `GET /api/cognisys/providers` to fetch all providers (ensure `encryptedApiKey` is excluded from response).
    *   [ ] Implement `POST /api/cognisys/providers` to create a new provider.
        *   [ ] Integrate API key encryption before saving to DB.
    *   [ ] Implement `PUT /api/cognisys/providers/{id}` to update provider settings.
        *   [ ] Handle `apiKey` updates: encrypt new key if provided.
    *   [ ] Implement `DELETE /api/cognisys/providers/{id}` to delete a provider.
    *   [ ] Implement `POST /api/cognisys/providers/{id}/test-connection` for connection testing.
        *   [ ] Decrypt API key for use in the test.
        *   [ ] Return clear success/failure status and messages.

#### **AI Model Mapping:**

*   **Database:**
    *   [ ] Create `models` table with columns: `id` (UUID/PK), `name` (TEXT), `providerId` (FK to `providers.id`), `type` (TEXT), `isActive` (BOOLEAN), `reasoning` (BOOLEAN), `role` (TEXT, nullable).
*   **API Endpoint:**
    *   [ ] Implement `GET /api/cognisys/models` to fetch all models, including joined provider information.
*   **Initial Data:**
    *   [ ] Populate the `models` table with initial AI model data.

#### **Routing Rules Management:**

*   **Database:**
    *   [ ] Create `routing_rules` table with columns: `id` (UUID/PK), `intent` (TEXT), `condition` (TEXT), `targetModelId` (FK to `models.id`), `priority` (INTEGER).
*   **API Endpoints:**
    *   [ ] Implement `GET /api/cognisys/routing-rules` to fetch all routing rules.
    *   [ ] Implement `POST /api/cognisys/routing-rules` to create a new routing rule.
    *   [ ] Implement `PUT /api/cognisys/routing-rules/{id}` to update an existing routing rule.
    *   [ ] Implement `DELETE /api/cognisys/routing-rules/{id}` to delete a routing rule.

#### **Test Console & AI Interaction:**

*   **API Endpoint:**
    *   [ ] Implement `POST /api/cognisys/chat` for processing chat requests.
*   **Business Logic:**
    *   [ ] Implement `intent` detection logic (e.g., keyword matching, regex, or a small LLM call).
    *   [ ] Implement `routing_rules` evaluation logic to select the optimal `targetModel` based on intent and conditions.
    *   [ ] Implement an LLM integration layer to interact with various configured providers.
        *   [ ] Ensure secure decryption of API keys for LLM calls.
    *   [ ] Implement accurate token counting for each LLM interaction.
    *   [ ] Implement logic to generate `react-flow` visualization data (`nodes`, `edges`) based on the actual routing path taken for each query.
*   **Database (Optional):**
    *   [ ] Create `chat_history` table with columns: `id` (UUID/PK), `userId` (FK), `prompt` (TEXT), `response` (TEXT), `modelUsed` (TEXT), `tokensUsed` (INTEGER), `timestamp` (DATETIME).
