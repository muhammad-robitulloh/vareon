import argparse
import subprocess
import sys
import os
import logging
import atexit
import select
import time
from dotenv import load_dotenv

# --- Basic Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Global list to keep track of running subprocesses ---
running_processes = []

def cleanup_processes():
    """Ensure all child processes are terminated on exit."""
    logger.info("Shutting down subprocesses...")
    for proc in running_processes:
        if proc.poll() is None:  # If the process is still running
            try:
                proc.terminate()
                proc.wait(timeout=5)
                logger.info(f"Terminated process with PID: {proc.pid}")
            except subprocess.TimeoutExpired:
                proc.kill()
                logger.warning(f"Forcefully killed process with PID: {proc.pid}")
            except Exception as e:
                logger.error(f"Error during cleanup of process {proc.pid}: {e}")
    # Special cleanup for gunicorn parent process if it exists
    try:
        # This is a bit of a hack, but gunicorn can be stubborn
        import psutil # Import here to avoid dependency if not needed
        if any("gunicorn" in p.name() for p in psutil.process_iter()):
             os.system("pkill gunicorn")
             logger.info("Attempted to clean up any stray gunicorn processes.")
    except NameError: # psutil might not be installed
        pass
    except Exception as e:
        logger.error(f"Error during gunicorn cleanup: {e}")


# Register the cleanup function to be called on script exit
atexit.register(cleanup_processes)


def main():
    # Load environment variables from .env file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    dotenv_path = os.path.join(script_dir, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        logger.info(f"Loaded environment variables from {dotenv_path}")
    else:
        logger.warning(f".env file not found at {dotenv_path}. Proceeding with system environment variables.")

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
                    "--port", str(args.port),
                    "--reload" # Added for development convenience
                ],
                cwd=script_dir,
                env=new_env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True, # Decode stdout/stderr as text
                bufsize=1, # Line-buffered
                universal_newlines=True # Ensure text mode works across platforms
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
        # Make stdout and stderr non-blocking
        os.set_blocking(backend_process.stdout.fileno(), False)
        os.set_blocking(backend_process.stderr.fileno(), False)

        try:
            while backend_process.poll() is None:
                # Check stdout
                stdout_line = backend_process.stdout.readline()
                if stdout_line:
                    logger.info(f"[Backend] {stdout_line.strip()}")

                # Check stderr
                stderr_line = backend_process.stderr.readline()
                if stderr_line:
                    # Uvicorn often logs INFO to stderr, so we check for that
                    if "INFO:" in stderr_line:
                        logger.info(f"[Backend] {stderr_line.strip()}")
                    else:
                        logger.error(f"[Backend ERROR] {stderr_line.strip()}")

                time.sleep(0.1) # Prevent busy-waiting

        except KeyboardInterrupt:
            logger.info("Ctrl+C detected. Initiating graceful shutdown.")
            sys.exit(0)
        except Exception as e:
            logger.error(f"An error occurred during log streaming: {e}")
            sys.exit(1)
        finally:
            # This block will run when the loop terminates, either by process exit or error
            if backend_process.poll() is not None:
                logger.warning(f"Backend process exited with code {backend_process.poll()}.")
                # Drain any remaining output
                for line in backend_process.stdout:
                    logger.info(f"[Backend] {line.strip()}")
                for line in backend_process.stderr:
                    logger.error(f"[Backend ERROR] {line.strip()}")


    elif args.prod:
        logger.info(f"Starting production server with gunicorn on http://{args.host}:{args.port}")
        # In production, we want gunicorn to be the main process to allow for easy management.
        # We use os.execvpe to replace the current Python script with the gunicorn process.
        # This means the Python script will no longer be running, and gunicorn takes over.
        # atexit cleanup will NOT run in this case, which is fine because gunicorn manages its workers.
        
        # Set up environment
        new_env = os.environ.copy()
        new_env["PYTHONPATH"] = project_root + os.pathsep + new_env.get("PYTHONPATH", "")
        new_env["DATASET_STORAGE_DIR"] = os.path.join(script_dir, 'data', 'neosyntis_datasets')

        gunicorn_executable = "gunicorn" # Assumes gunicorn is in the system's PATH

        # Command and arguments for gunicorn
        gunicorn_args = [
            gunicorn_executable,
            '--workers', str(args.workers),
            '--bind', f'{args.host}:{args.port}',
            '--worker-class', 'uvicorn.workers.UvicornWorker', # Use uvicorn workers for async performance
            'server_python.main:app',
        ]
        
        try:
            logger.info(f"Executing command: {' '.join(gunicorn_args)}")
            # Replace the current process with gunicorn
            os.execvpe(gunicorn_executable, gunicorn_args, new_env)
        except FileNotFoundError:
            logger.error("Gunicorn not found. Please make sure it's installed (pip install gunicorn uvicorn).")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to start gunicorn: {e}")
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()