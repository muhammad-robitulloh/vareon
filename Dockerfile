# Stage 1: Build the React frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app

COPY client/package.json client/package-lock.json ./client/

WORKDIR /app/client
RUN npm install

COPY client/ ./
RUN npm run build

# Stage 2: Serve the Python backend and static frontend files
FROM python:3.10-slim-buster

WORKDIR /app

# Install Python dependencies
COPY server-python/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the built frontend from the previous stage
COPY --from=frontend-builder /app/client/dist ./client/dist

# Copy the Python backend code
COPY server-python/ ./server-python/

# Expose the port the FastAPI app runs on
EXPOSE 5000

# Command to run the FastAPI application
# Assuming your main FastAPI app is in server-python/main.py
# and it serves static files from ./client/dist
CMD ["uvicorn", "server-python.main:app", "--host", "0.0.0.0", "--port", "5000"]