import os
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
import platform
import logging

logger = logging.getLogger(__name__)

# Determine project root
try:
    PROJECT_ROOT = Path(find_dotenv()).parent.resolve()
except Exception:
    PROJECT_ROOT = Path(__file__).parent.parent.parent.resolve()

# Define data directories and files
GENERATED_FILES_PATH = PROJECT_ROOT / "generated_files"
FILES_STORAGE_PATH = PROJECT_ROOT / "files_storage"
CHAT_HISTORY_FILE = GENERATED_FILES_PATH / "chat_history.json"
SHELL_HISTORY_FILE = GENERATED_FILES_PATH / "shell_history.json"
TOKEN_USAGE_FILE = GENERATED_FILES_PATH / "token_usage.json"
ENV_PATH = PROJECT_ROOT / ".env"

# Ensure data directories and essential files exist
GENERATED_FILES_PATH.mkdir(exist_ok=True)
FILES_STORAGE_PATH.mkdir(exist_ok=True)
for f in [CHAT_HISTORY_FILE, SHELL_HISTORY_FILE, TOKEN_USAGE_FILE, ENV_PATH]:
    if not f.exists():
        f.touch()
        if f.suffix == '.json':
            f.write_text("[]")

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH, encoding='utf-8', override=True)

# LLM Configuration from environment variables
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://openrouter.ai/api/v1/chat/completions")
CODE_GEN_MODEL = os.getenv("CODE_GEN_MODEL", "moonshotai/kimi-dev-72b:free")
ERROR_FIX_MODEL = os.getenv("ERROR_FIX_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1:free")
CONVERSATION_MODEL = os.getenv("CONVERSATION_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
COMMAND_CONVERSION_MODEL = os.getenv("COMMAND_CONVERSION_MODEL", "nvidia/llama-3.3-nemotron-super-49b-v1:free")
FILENAME_GEN_MODEL = os.getenv("FILENAME_GEN_MODEL", "mistralai/mistral-small-3.2-24b-instruct")
INTENT_DETECTION_MODEL = os.getenv("INTENT_DETECTION_MODEL", "mistralai/mistral-small-3.2-24b-instruct")

# Reasoning Model Settings
REASONING_ENABLED = os.getenv("REASONING_ENABLED", "false").lower() == "true"
REASONING_MODEL = os.getenv("REASONING_MODEL", CONVERSATION_MODEL) # Default to conversation model
REASONING_MAX_TOKENS = int(os.getenv("REASONING_MAX_TOKENS", "200"))
REASONING_TEMPERATURE = float(os.getenv("REASONING_TEMPERATURE", "0.7"))
REASONING_APPLY_TO_MODELS = [m.strip() for m in os.getenv("REASONING_APPLY_TO_MODELS", "").split(',') if m.strip()]

# Telegram Bot Settings
TELEGRAM_ENABLED = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "") # Optional: If set, only this chat ID can interact

# System information (initialized once)
def _get_system_info():
    try:
        system = platform.system()
        if system == "Linux":
            if os.environ.get("TERMUX_VERSION"):
                os_name = "Termux"
            else:
                try:
                    with open("/etc/os-release") as f:
                        lines = f.readlines()
                        info = dict(line.strip().split('=', 1) for line in lines if '=' in line)
                        os_name = info.get('PRETTY_NAME', 'Linux').strip('"')
                except FileNotFoundError:
                    os_name = f"Linux ({platform.release()})"
        else:
            os_name = f"{system} ({platform.release()})"

        shell = os.environ.get("SHELL", "Unknown")
        
        info = {"os": os_name, "shell": shell}
        logger.info(f"System Info Detected: {info}")
        return info

    except Exception as e:
        logger.error(f"Failed to get system info: {e}")
        return {"os": "Unknown", "shell": "Unknown"}

SYSTEM_INFO = _get_system_info()