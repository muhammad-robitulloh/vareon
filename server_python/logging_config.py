
import logging
import os
import sys
from rich.logging import RichHandler

# A list of all known backend components that can have their log levels configured.
# The names should correspond to the logger names (e.g., 'server_python.arcana').
KNOWN_COMPONENTS = [
    "arcana",
    "cognisys",
    "myntrix",
    "neosyntis",
    "orchestrator",
    "context_memory",
    "git_service",
    "terminal",
    "main_app",       # For server_python/main.py
    "run_script",     # For server_python/run.py
    "auth",           # For server_python/auth.py
    "database",       # For server_python/database.py
]

def setup_logging():
    """
    Configures the logging for the entire application using RichHandler.

    This function sets up a sophisticated logging system that is both
    highly readable and configurable via environment variables.

    - It uses RichHandler for beautifully formatted, colorized console output.
    - The root logging level can be set with the `LOG_LEVEL` env var (e.g., "INFO", "DEBUG").
    - The log level for each specific backend component can be overridden using
      `LOG_LEVEL_<COMPONENT_NAME>` (e.g., `LOG_LEVEL_ARCANA="DEBUG"`).
    - It also configures the log level for key third-party libraries like uvicorn and gunicorn.
    """
    # 1. Determine the root logging level
    root_log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if root_log_level not in log_levels:
        root_log_level = "INFO"

    # 2. Create a RichHandler for beautiful console output.
    #    - show_time=False because the default formatter will add it.
    #    - rich_tracebacks=True for better exception reporting.
    handler = RichHandler(
        rich_tracebacks=True,
        show_time=False,
        show_level=False,
        show_path=False
    )

    # 3. Define the logging format.
    #    - %(name)s will show the logger name (e.g., 'run_script', 'server_python.arcana.api')
    #      which helps in identifying the source of the log.
    formatter = logging.Formatter(
        "%(asctime)s [%(name)-20s] [%(levelname)-8s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    handler.setFormatter(formatter)

    # 4. Configure the root logger.
    #    - We get the root logger and remove any existing handlers to avoid duplicate logs.
    #    - We then add our configured RichHandler.
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()
    root_logger.setLevel(root_log_level)
    root_logger.addHandler(handler)

    # 5. Set log levels for specific components based on environment variables.
    #    This allows for granular control over log verbosity.
    for component in KNOWN_COMPONENTS:
        env_var_name = f"LOG_LEVEL_{component.upper()}"
        log_level = os.environ.get(env_var_name)
        if log_level and log_level.upper() in log_levels:
            logger_name = f"server_python.{component}" if component not in ["run_script", "main_app"] else component
            logging.getLogger(logger_name).setLevel(log_level.upper())
            logging.getLogger("main_app").info(f"Log level for '{logger_name}' set to {log_level.upper()} from environment variable.")

    # 6. Adjust log levels for noisy third-party libraries.
    #    This keeps the log output clean and focused on our application's logic.
    logging.getLogger("uvicorn.access").setLevel(os.environ.get("LOG_LEVEL_UVICORN_ACCESS", "WARNING").upper())
    logging.getLogger("uvicorn.error").setLevel(os.environ.get("LOG_LEVEL_UVICORN_ERROR", "INFO").upper())
    logging.getLogger("gunicorn.error").setLevel(os.environ.get("LOG_LEVEL_GUNICORN", "INFO").upper())

    logging.getLogger("main_app").info(f"Logging setup complete. Root level: {root_log_level}")

if __name__ == '__main__':
    # Example of how to use it.
    # You can run this file directly to test the logging configuration.
    # Try running with:
    # LOG_LEVEL=DEBUG LOG_LEVEL_ARCANA=INFO python -m server_python.logging_config

    os.environ['LOG_LEVEL_ARCANA'] = 'DEBUG' # Simulate setting an env var
    setup_logging()

    # Get loggers with specific names
    main_logger = logging.getLogger("main_app")
    arcana_logger = logging.getLogger("server_python.arcana")
    cognisys_logger = logging.getLogger("server_python.cognisys")

    main_logger.info("This is an info message from the main application.")
    main_logger.debug("This is a debug message from the main application.")
    arcana_logger.debug("This is a debug message from Arcana. It should be visible.")
    arcana_logger.warning("This is a warning from Arcana.")
    cognisys_logger.info("This is an info from Cognisys.")
    cognisys_logger.debug("This is a debug message from Cognisys. It should NOT be visible by default.")

    try:
        1 / 0
    except ZeroDivisionError:
        main_logger.exception("A handled exception occurred!")
