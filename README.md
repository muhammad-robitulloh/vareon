# Vareon Backend

This repository contains the backend services for the Vareon project, built with FastAPI and Python. It provides various functionalities for AI orchestration, agent and device management, workflow automation, and machine learning models.

## Table of Contents

1.  [Features](#1-features)
2.  [Installation](#2-installation)
3.  [Running the Backend](#3-running-the-backend)
4.  [API Documentation](#4-api-documentation)
5.  [Ecosystem Overview](#5-ecosystem-overview)
6.  [Implementation Details](#6-implementation-details)
7.  [Libraries Used](#7-libraries-used)
8.  [Testing](#8-testing)

---

## 1. Features

*   **User Authentication & Authorization**: Secure user management with JWT.
*   **Arcana Core Services**: System status, context memory, LLM preferences, and interactive terminal management.
*   **Cognisys Module**: LLM provider management, model routing, and chat interaction.
*   **Myntrix Module**: Agent and device management, task scheduling, job monitoring, and system metrics.
*   **Neosyntis Module**: Workflow management, dataset management, telemetry ingestion, and ML model lifecycle management.
*   **Global Search**: Search across various entities in the Vareon ecosystem.

## 2. Installation

### Prerequisites

*   Python 3.8+
*   Node.js (for frontend development, if applicable)
*   npm or yarn (for frontend development, if applicable)

### Backend Setup

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/your-repo/vareon.git
    cd vareon/server-python
    ```
2.  **Create a virtual environment**:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
3.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Environment Variables**:
    Create a `.env` file in the `server-python/` directory based on `.env.example` and fill in the necessary values (e.g., `SECRET_KEY`, `OPENROUTER_API_KEY`, `SMTP_PASSWORD`).

## 3. Running the Backend

### Development Mode

To run the backend in development mode with Uvicorn:

```bash
python run.py --dev
```

If you also want to build and serve the frontend (assuming it's in `../client`):

```bash
python run.py --dev --with-frontend
```

### Production Mode

To run the backend in production mode with Gunicorn:

```bash
python run.py --prod --workers 4
```

## 4. API Documentation

Detailed API documentation, including all available endpoints, request/response models, and authentication requirements, can be found in:

*   [API Documentation](documentation.md)

## 5. Ecosystem Overview

For a high-level understanding of the interconnections and data flow between the different modules in the Vareon ecosystem, refer to:

*   [Ecosystem Diagram](diagram.md)

## 6. Implementation Details

For a detailed plan on implementing currently mocked backend functions and strategies for fallback logic in restricted environments, refer to:

*   [Implementation Details V5](ImplementationV5.md)

## 7. Libraries Used

### Python Backend Libraries (from `requirements.txt`)

*   `fastapi`: Web framework for building APIs.
*   `uvicorn`: ASGI server for running FastAPI applications.
*   `gunicorn`: WSGI HTTP server for Unix (used in production).
*   `python-jose[cryptography]`: JOSE (JSON Object Signing and Encryption) for JWT.
*   `python-multipart`: For handling form data, especially file uploads.
*   `SQLAlchemy`: SQL toolkit and Object-Relational Mapper (ORM).
*   `python-dotenv`: Reads key-value pairs from a `.env` file.
*   `httpx`: A fully featured HTTP client for Python.
*   `email-validator`: For email address validation.
*   `cryptography`: Cryptographic recipes and primitives.
*   `psutil`: Cross-platform library for retrieving process and system utilization.

### Frontend/Shared Libraries (from `package.json` - selected key libraries)

*   `react`, `react-dom`: JavaScript library for building user interfaces.
*   `typescript`: Superset of JavaScript that compiles to plain JavaScript.
*   `vite`: Next generation frontend tooling.
*   `tailwindcss`: A utility-first CSS framework.
*   `drizzle-orm`, `drizzle-kit`: TypeScript ORM for SQL databases.
*   `@tanstack/react-query`: Hooks for fetching, caching and updating asynchronous data in React.
*   `zustand`: A small, fast, and scalable bearbones state-management solution.
*   `@monaco-editor/react`: Monaco Editor for React.
*   `@xterm/xterm`, `@xterm/addon-web-links`: Terminal emulator for the web.
*   `@xyflow/react`: Library for building interactive node-based editors.
*   `three`, `@react-three/fiber`, `@react-three/drei`: For 3D graphics.
*   `lucide-react`: Beautifully simple and consistent icon toolkit.
*   `framer-motion`: A production-ready motion library for React.
*   `zod`: TypeScript-first schema declaration and validation library.

## 8. Testing

Unit and integration tests are written using `pytest`.

To run the tests for a specific module (e.g., Cognisys):

```bash
DATASET_STORAGE_DIR=/data/data/com.termux/files/home/VE/V/VE/Vareon/server-python/data/neosyntis_datasets pytest server-python/tests/test_cognisys.py
```

Replace `test_cognisys.py` with `test_myntrix.py`, `test_neosyntis.py`, or `test_arcana.py` to run tests for other modules.