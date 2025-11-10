import os
from flask import Flask, send_from_directory
import logging

# --- Logging Setup ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Determine the path to the frontend build directory
# Assuming this script is in Vareon/server-python
# and frontend build is in Vareon/dist/public (relative to Vareon root)
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir) # This is /data/data/com.termux/files/home/VE/Vareon
frontend_build_dir = os.path.join(project_root, 'dist', 'public') # Corrected path

if not os.path.isdir(frontend_build_dir):
    logger.warning(f"Frontend build directory not found: {frontend_build_dir}. "
                   "Please ensure 'npm run build' has been executed in the frontend directory.")

@app.route('/')
def serve_index():
    return send_from_directory(frontend_build_dir, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    if os.path.exists(os.path.join(frontend_build_dir, path)):
        return send_from_directory(frontend_build_dir, path)
    # For client-side routing, serve index.html for any other path
    return send_from_directory(frontend_build_dir, 'index.html')

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000) # Default to 8000 for frontend
    args, unknown = parser.parse_known_args()

    logger.info(f"Starting Flask static file server on http://{args.host}:{args.port}")
    app.run(host=args.host, port=args.port, debug=True)