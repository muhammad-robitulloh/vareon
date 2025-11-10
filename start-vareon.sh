#!/bin/bash

# Script to build and run the Vareon application (both frontend and backend)
# Exit immediately if a command exits with a non-zero status.
set -e

# Navigate to the script's directory to ensure paths are correct
cd "$(dirname "$0")"

# Function to kill all background processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    # Kill all processes in the same process group as this script
    # This is a robust way to ensure all child processes are terminated.
    kill 0
    echo "Servers stopped."
}

# Set trap to call cleanup function on script exit (e.g., Ctrl+C)
trap cleanup SIGINT SIGTERM EXIT

# 1. Install dependencies and build the frontend and node server
echo "--- Installing dependencies and building project... ---"
npm install
npm run build
echo "--- Build successful ---"

# 2. Start the Python backend server in the background
echo ""
echo "--- Starting Python backend server (production)... ---"
python server_python/run.py --prod &
PYTHON_BACKEND_PID=$!
echo "Python backend started with PID: $PYTHON_BACKEND_PID"

# 3. Start the Node.js frontend server in the background
echo ""
echo "--- Starting Node.js frontend server (production)... ---"
npm start &
NODE_FRONTEND_PID=$!
echo "Node.js frontend server started with PID: $NODE_FRONTEND_PID"

echo ""
echo "========================================"
echo "          Vareon is running!            "
echo "========================================"
echo ""
echo "Access the application at http://localhost:3000 (or the port configured in your Node.js server)."
echo "The Python API is running on port 8001."
echo ""
echo "Press Ctrl+C to stop all servers."
echo ""

# Wait for all background processes to finish.
# The script will pause here until cleanup is triggered.
wait
