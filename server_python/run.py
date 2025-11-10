import argparse
import subprocess
import sys
import os
import logging
import atexit
import select # For non-blocking I/O
import time
from dotenv import load_dotenv # Import load_dotenv

# --- Logging ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Global list to store subprocess.Popen objects
running_processes = []

def cleanup_processes():
    """Terminates all background processes started by this script."""
    logger.info("Initiating cleanup of background processes...")
    for proc in running_processes:
        if proc.poll() is None: # Check if process is still running
            logger.info(f"Terminating process with PID: {proc.pid}")
            proc.terminate()
            try:
                proc.wait(timeout=5) # Wait for process to terminate
            except subprocess.TimeoutExpired:
                logger.warning(f"Process {proc.pid} did not terminate gracefully, killing it.")
                proc.kill()
    logger.info("All background processes cleaned up.")

# Register the cleanup function to run on script exit
atexit.register(cleanup_processes)

def main():
    # Load environment variables from .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(script_dir, '.env')) # Explicitly load .env

    parser = argparse.ArgumentParser(description="Vareon FastAPI Backend Runner")
    parser.add_argument("--dev", action="store_true", help="Run the development server with uvicorn.")
    parser.add_argument("--prod", action="store_true", help="Run the production server with gunicorn.")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host for the server.")
    parser.add_argument("--port", type=int, default=5000, help="Port for the backend server. Default is 5000.")
    parser.add_argument("--workers", type=int, default=4, help="Number of worker processes for gunicorn.")
    parser.add_argument("--with-frontend", action="store_true", help="Also build the Node.js frontend and serve it from FastAPI.")
    args = parser.parse_args()

    # Get the absolute path of the directory containing this script (server-python)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # Get the parent directory (Vareon)
    project_root = os.path.dirname(script_dir)
    frontend_dir = os.path.join(project_root, 'client') # Assuming frontend is in Vareon/client
    frontend_build_dir = os.path.join(project_root, 'dist', 'public') # Corrected path for build output

    # Add the project root to sys.path so 'server-python' can be imported as a top-level package
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    if args.dev:
        # --- Build Frontend (if --with-frontend is specified) ---
        if args.with_frontend:
            logger.info("Building Node.js frontend...")
            if not os.path.isdir(frontend_dir):
                logger.error(f"Frontend source directory not found: {frontend_dir}. Skipping frontend build.")
            else:
                try:
                    logger.info("Running 'npm install' for frontend...")
                    npm_install_result = subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True, capture_output=True, text=True)
                    logger.info(f"npm install completed. Stdout lines: {len(npm_install_result.stdout.splitlines())}, Stderr lines: {len(npm_install_result.stderr.splitlines())}")
                    if npm_install_result.stderr:
                        logger.warning(f"npm install had warnings/errors. Full stderr:\n{npm_install_result.stderr}")

                    logger.info("Running 'npm run build' for frontend...")
                    npm_build_result = subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, check=True, capture_output=True, text=True)
                    logger.info(f"npm run build completed. Stdout lines: {len(npm_build_result.stdout.splitlines())}, Stderr lines: {len(npm_build_result.stderr.splitlines())}")
                    if npm_build_result.stderr:
                        logger.warning(f"npm run build had warnings/errors. Full stderr:\n{npm_build_result.stderr}")
                    logger.info("Frontend build successful.")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Frontend build failed: {e.cmd}\nStdout:\n{e.stdout}\nStderr:\n{e.stderr}")
                    sys.exit(1)
                except FileNotFoundError:
                    logger.error("npm command not found. Please ensure Node.js and npm are installed.")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Failed to build frontend: {e}")
                    sys.exit(1)

        # --- Start Python Backend ---
        logger.info(f"Starting Python backend development server on http://{args.host}:{args.port}")

        new_env = os.environ.copy()
        new_env["PYTHONPATH"] = project_root + os.pathsep + new_env.get("PYTHONPATH", "")
        new_env["DATASET_STORAGE_DIR"] = os.path.join(script_dir, 'data', 'neosyntis_datasets')

        try:
                        backend_process = subprocess.Popen(
                            [
                                sys.executable, "-m", "uvicorn",
                                "server_python.main:app",
                                "--host", args.host,
                                "--port", str(args.port)
                            ],
                            cwd=script_dir,
                            env=new_env, # Pass current environment variables
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                        )
                        running_processes.append(backend_process)
                        logger.info(f"Python backend started with PID: {backend_process.pid}")

        except Exception as e:
            logger.error(f"Failed to start Python backend: {e}")
            sys.exit(1)

        logger.info("\n=========================================")
        logger.info("          Vareon is running!            ")
        logger.info("=========================================")
        logger.info(f"- Backend (Python): http://{args.host}:{args.port}")
        if args.with_frontend and os.path.isdir(frontend_build_dir):
            logger.info(f"- Frontend (served by FastAPI):  http://{args.host}:{args.port}")
        else:
            logger.info("- Frontend: Not built or not served.")
        logger.info("\nPress Ctrl+C to stop all servers.")

        # --- Stream logs from subprocesses ---
        pipes = {}
        if backend_process:
            pipes[backend_process.stdout.fileno()] = (backend_process.stdout, "[Backend]")
            pipes[backend_process.stderr.fileno()] = (backend_process.stderr, "[Backend ERROR]")

        try:
            while running_processes:
                # Check if any process has exited
                for proc in list(running_processes): # Iterate over a copy
                    if proc.poll() is not None: # Process has exited
                        stderr_output = proc.stderr.read().decode('utf-8')
                        if stderr_output:
                            logger.error(f"Backend process (PID: {proc.pid}) exited with status {proc.poll()}. Stderr:\n{stderr_output}")
                        else:
                            logger.error(f"Backend process (PID: {proc.pid}) exited with status {proc.poll()}. No stderr output.")
                        running_processes.remove(proc) # Remove the exited process
                        if not running_processes:
                            break

                if not running_processes:
                    break

                # Use select to wait for data on any pipe
                readable_fds = list(pipes.keys())
                rlist, _, _ = select.select(readable_fds, [], [], 0.1) # 0.1 second timeout

                for fd in rlist:
                    stream, prefix = pipes[fd]
                    line = stream.readline() # Read a line
                    if line:
                        decoded_line = line.decode('utf-8').strip()
                        # Special handling for Uvicorn's INFO messages from stderr
                        # Uvicorn often logs INFO to stderr, which we don't want to label as ERROR
                        if prefix == "[Backend ERROR]" and "INFO:" in decoded_line:
                            logger.info(f"[Backend] {decoded_line}") # Log as INFO
                        else:
                            logger.info(f"{prefix} {decoded_line}")
                    
        except KeyboardInterrupt:
            logger.info("Ctrl+C detected. Initiating graceful shutdown.")
            # atexit.register will handle cleanup_processes
            sys.exit(0)
        except Exception as e:
            logger.error(f"An error occurred during log streaming: {e}")
            sys.exit(1)

    elif args.prod:
        logger.info(f"Starting production server with gunicorn on http://{args.host}:{args.port}")
        try:
            subprocess.run(
                [
                    'gunicorn',
                    '--workers',
                    str(args.workers),
                    '--bind',
                    f'{args.host}:{args.port}',
                    'server_python.main:app',
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to start gunicorn: {e}")
            sys.exit(1)
        except FileNotFoundError:
            logger.error("Gunicorn not found. Please make sure it's installed (pip install gunicorn).")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()
