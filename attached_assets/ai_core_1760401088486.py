import json
import logging
import asyncio

from . import config
from .utils import llm_utils, ai_services, file_utils, shell_utils

# --- Logging Configuration ---
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    level=logging.INFO,
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# --- Main Class for Web Backend Core Logic ---

class AICore:
    """
    Encapsulates all core logic required for the web dashboard backend.
    Orchestrates calls to various utility modules.
    """
    def __init__(self):
        """Initializes in-memory stores for session data."""
        self.user_contexts: dict = {}
        self.chat_histories: dict = {}
        logger.info(f"AICore initialized. Project root: {config.PROJECT_ROOT}")

    def get_user_context(self, chat_id: int) -> dict:
        """Retrieves user context, initializing if absent."""
        if chat_id not in self.user_contexts:
            self.user_contexts[chat_id] = {}
        return self.user_contexts[chat_id]

    def get_chat_history(self, chat_id: int) -> list:
        """Retrieves chat history, initializing if absent."""
        if chat_id not in self.chat_histories:
            self.chat_histories[chat_id] = []
        return self.chat_histories[chat_id]

    async def process_chat_stream(self, chat_id: int, message: str, attached_file_path: str = None, is_telegram_chat: bool = False):
        """
        Main generator to handle a chat request and stream back responses.
        """
        logger.info(f"[Core] Chat stream started for chat_id {chat_id} (Telegram: {is_telegram_chat}): '{message}'")
        yield self._format_stream_chunk("status", "Thinking...")

        current_chat_history = self.get_chat_history(chat_id)
        file_content = None

        if attached_file_path:
            read_result = file_utils.read_file(attached_file_path)
            if read_result.get("error"):
                yield self._format_stream_chunk("error", f"Failed to read attached file: {read_result["error"]}")
                yield self._format_stream_chunk("done", "")
                return
            file_content = read_result["content"]
            logger.info(f"Attached file content read from {attached_file_path}")
            # Add file content to the message for AI processing
            message_with_file = f"{message}\n\nAttached File ({attached_file_path}):\n```\n{file_content}\n```"
        else:
            message_with_file = message

        niat = ai_services.deteksi_niat_pengguna(message_with_file)
        yield self._format_stream_chunk("reasoning_chunk", f"Intent: {niat}")

        # Conditionally generate and stream reasoning
        if config.REASONING_ENABLED and niat in config.REASONING_APPLY_TO_MODELS:
            reasoning = ai_services.generate_reasoning(message_with_file, niat, chat_history=current_chat_history)
            yield self._format_stream_chunk("reasoning_chunk", reasoning)

        if niat == "shell":
            success, command = ai_services.konversi_ke_perintah_shell(message_with_file, chat_history=current_chat_history)
            if not success or command == "CANNOT_CONVERT":
                yield self._format_stream_chunk("error", "Could not convert to a shell command.")
            else:
                yield self._format_stream_chunk("command", command)

        elif niat == "program":
            success, code, lang = ai_services.minta_kode(message_with_file, chat_history=current_chat_history)
            if success:
                filename = ai_services.generate_filename(message_with_file, lang)
                file_utils.write_file(f"generated_files/{filename}", code)
                yield self._format_stream_chunk("generated_code", {"filename": filename, "language": lang, "code": code})
            else:
                yield self._format_stream_chunk("error", "Failed to generate code.")

        else: # Conversation
            success, response = ai_services.minta_jawaban_konversasi(message_with_file, chat_history=current_chat_history)
            if success:
                current_chat_history.append({"role": "user", "content": message})
                current_chat_history.append({"role": "assistant", "content": response})
                self.chat_histories[chat_id] = current_chat_history
                yield self._format_stream_chunk("message_chunk", response)
            else:
                yield self._format_stream_chunk("error", "Failed to get a response.")

        yield self._format_stream_chunk("done", "")

    def _format_stream_chunk(self, type: str, content: any):
        """Helper to format a JSON chunk for streaming responses."""
        return json.dumps({"type": type, "content": content}) + '\n'

# --- Create a single instance for the application to use ---
ai_core_instance = AICore()
