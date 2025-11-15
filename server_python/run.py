import argparse
import subprocess
import sys
import os
import logging
import atexit
import time
from dotenv import load_dotenv

# --- Path Setup ---
# This is crucial to ensure that the 'server_python' module can be found.
# We add the project's root directory to the Python path.
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Now that the path is set up, we can import our modules.
from server_python.logging_config import setup_logging

# --- Global list to keep track of running subprocesses ---
running_processes = []

# Get a logger with a specific name for this script
logger = logging.getLogger("run_script")

def cleanup_processes():
    """Ensure all child processes are terminated on exit."""
    logger.info("Shutting down subprocesses...")
    for proc in running_processes:
        if proc.poll() is None:  # If the process is still running
            try:
                # Send SIGTERM first for graceful shutdown
                proc.terminate()
                proc.wait(timeout=5)
                logger.info(f"Terminated process with PID: {proc.pid}")
            except subprocess.TimeoutExpired:
                # Force kill if terminate doesn't work
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
    except (ImportError, NameError): # psutil might not be installed
        pass
    except Exception as e:
        logger.error(f"Error during gunicorn cleanup: {e}")


# Register the cleanup function to be called on script exit
atexit.register(cleanup_processes)


def main():
    # --- Load environment variables and setup logging FIRST ---
    dotenv_path = os.path.join(script_dir, '.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
        # Note: Logging is set up after this, so this message will use the new format.
    
    # Setup the centralized logging configuration
    setup_logging()

    if os.path.exists(dotenv_path):
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
    parser.add_argument("--tunnel", action="store_true", help="Run a cloudflared tunnel to expose the local server.")
    args = parser.parse_args()

    frontend_dir = os.path.join(project_root, 'client') # Assuming frontend is in Vareon/client
    frontend_build_dir = os.path.join(project_root, 'dist', 'public') # Corrected path for build output

    if args.dev:
        # --- Build Frontend (if --with-frontend is specified) ---
        if args.with_frontend:
            logger.info("Building Node.js frontend...")
            if not os.path.isdir(frontend_dir):
                logger.error(f"Frontend source directory not found: {frontend_dir}. Skipping frontend build.")
            else:
                try:
                    # We use subprocess.run here because these are short-lived build commands.
                    logger.info("Running 'npm install' for frontend...")
                    npm_install_result = subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True, capture_output=True, text=True)
                    logger.info(f"npm install completed. Stdout lines: {len(npm_install_result.stdout.splitlines())}")
                    if npm_install_result.stderr:
                        logger.warning(f"npm install had warnings/errors.")

                    logger.info("Running 'npm run build' for frontend...")
                    npm_build_result = subprocess.run(['npm', 'run', 'build'], cwd=frontend_dir, check=True, capture_output=True, text=True)
                    logger.info(f"npm run build completed. Stdout lines: {len(npm_build_result.stdout.splitlines())}")
                    if npm_build_result.stderr:
                        logger.warning(f"npm run build had warnings/errors.")
                    logger.info("Frontend build successful.")

                except subprocess.CalledProcessError as e:
                    logger.error(f"Frontend build failed: {e.cmd}\nStderr:\n{e.stderr}")
                    sys.exit(1)
                except FileNotFoundError:
                    logger.error("npm command not found. Please ensure Node.js and npm are installed.")
                    sys.exit(1)
                except Exception as e:
                    logger.error(f"Failed to build frontend: {e}", exc_info=True)
                    sys.exit(1)

        # --- Start Python Backend ---
        logger.info(f"Starting Python backend development server on http://{args.host}:{args.port}")

        new_env = os.environ.copy()
        new_env["PYTHONPATH"] = project_root + os.pathsep + new_env.get("PYTHONPATH", "")
        new_env["DATASET_STORAGE_DIR"] = os.path.join(script_dir, 'data', 'neosyntis_datasets')
        # Ensure the backend uses the same logging config by passing LOG_LEVEL vars
        for key, value in os.environ.items():
            if key.startswith("LOG_LEVEL"):
                new_env[key] = value

        try:
            # The backend (uvicorn) process will inherit the standard output and error streams.
            # This allows RichHandler to manage the output directly, preventing duplicated or
            # poorly formatted log messages.
            backend_process = subprocess.Popen(
                [
                    sys.executable, "-m", "uvicorn",
                    "server_python.main:app",
                    "--host", args.host,
                    "--port", str(args.port),
                    "--reload"
                ],
                cwd=script_dir,
                env=new_env,
                # Let the subprocess print directly to the console
                stdout=sys.stdout,
                stderr=sys.stderr,
            )
            running_processes.append(backend_process)
            logger.info(f"Python backend process started with PID: {backend_process.pid}")

        except Exception as e:
            logger.error(f"Failed to start Python backend: {e}", exc_info=True)
            sys.exit(1)

        # --- Start Cloudflared Tunnel (if --tunnel is specified) ---
        if args.tunnel:
            logger.info("Starting cloudflared tunnel...")
            try:
                # The cloudflared command will output its logs to its stdout/stderr,
                # which are inherited by the parent process, so they will appear in the console.
                tunnel_process = subprocess.Popen(
                    ["cloudflared", "tunnel", "--url", f"http://{args.host}:{args.port}", "run", "arcana"],
                    stdout=sys.stdout,
                    stderr=sys.stderr,
                )
                running_processes.append(tunnel_process)
                logger.info(f"Cloudflared tunnel process started with PID: {tunnel_process.pid}. It may take a moment to connect.")
            except FileNotFoundError:
                logger.error("'cloudflared' command not found. Please ensure it is installed and in your PATH.")
                # We don't exit here, the main server can still run locally.
            except Exception as e:
                logger.error(f"Failed to start cloudflared tunnel: {e}", exc_info=True)

        logger.info("\n=========================================")
        logger.info("          Vareon is running!            ")
        logger.info("=========================================")
        logger.info(f"- Backend (Python): http://{args.host}:{args.port}")
        if args.with_frontend and os.path.isdir(frontend_build_dir):
            logger.info(f"- Frontend (served by FastAPI):  http://{args.host}:{args.port}")
        else:
            logger.info("- Frontend: Not built or not served.")
        logger.info("\nPress Ctrl+C to stop all servers.")

        # --- Wait for backend process to exit ---
        try:
            # Now we just wait for the process to complete. The atexit handler
            # will take care of termination on script exit (e.g., Ctrl+C).
            backend_process.wait()
        except KeyboardInterrupt:
            logger.info("Ctrl+C detected. Initiating graceful shutdown via atexit handler.")
            # The atexit handler will be called automatically.
            sys.exit(0)
        except Exception as e:
            logger.error(f"An unexpected error occurred while waiting for backend: {e}", exc_info=True)
            sys.exit(1)
        finally:
            if backend_process.poll() is not None:
                logger.warning(f"Backend process exited with code {backend_process.poll()}.")

    elif args.prod:
        logger.info(f"Starting production server with gunicorn on http://{args.host}:{args.port}")
        # In production, we use os.execvpe to replace the current script with gunicorn.
        # This is standard practice and means the atexit handler will not run, as
        # gunicorn takes over process management.
        
        new_env = os.environ.copy()
        new_env["PYTHONPATH"] = project_root + os.pathsep + new_env.get("PYTHONPATH", "")
        new_env["DATASET_STORAGE_DIR"] = os.path.join(script_dir, 'data', 'neosyntis_datasets')

        gunicorn_executable = "gunicorn"

        gunicorn_args = [
            gunicorn_executable,
            '--workers', str(args.workers),
            '--bind', f'{args.host}:{args.port}',
            '--worker-class', 'uvicorn.workers.UvicornWorker',
            # Tell gunicorn to use our logging config by setting the log config class
            '--log-config-dict', '{"version": 1, "disable_existing_loggers": false}',
            'server_python.main:app',
        ]
        
        try:
            logger.info(f"Executing command: {' '.join(gunicorn_args)}")
            os.execvpe(gunicorn_executable, gunicorn_args, new_env)
        except FileNotFoundError:
            logger.error("Gunicorn not found. Please make sure it's installed (pip install gunicorn uvicorn).")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to start gunicorn: {e}", exc_info=True)
            sys.exit(1)

    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()