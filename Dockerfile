# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder

# Set the working directory inside the container
WORKDIR /app
# Copy package.json and package-lock.json from the host's client directory
# to the container's /app/client directory.
# The source path is relative to the build context (project root).
# The destination path is relative to the WORKDIR (/app).
COPY package.json ./client/package.json
COPY package-lock.json ./client/package-lock.json

# Change to the client directory for npm commands
WORKDIR /app/client

# Install frontend dependencies
RUN npm install

WORKDIR /app

COPY server ./server

WORKDIR /app/server
# Build the React application
RUN npm run build

# Stage 2: Serve the Python backend and static frontend files
FROM python:3.10-slim-buster

WORKDIR /app

# Install Python dependencies
COPY server-python/requirements.txt ./server-python/
RUN pip install --no-cache-dir -r server-python/requirements.txt

# Copy the built frontend from the previous stage
COPY --from=frontend-builder /app/client/dist ./client/dist

# Copy the Python backend code
COPY server-python/ ./server-python/

# Expose the port the FastAPI app runs on
EXPOSE 5000

# Command to run the FastAPI application
CMD ["uvicorn", "server-python.main:app", "--host", "0.0.0.0", "--port", "5000"]
