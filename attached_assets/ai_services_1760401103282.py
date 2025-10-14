import logging
import re
from .. import config
from . import llm_utils
from . import file_utils

logger = logging.getLogger(__name__)

def deteksi_niat_pengguna(pesan_pengguna: str) -> str:
    """
    Detects user intent: shell, program, or conversation.
    """
    messages = [
        {"role": "system", "content": '''You are an intent detector. Classify the user's message as "shell", "program", or "conversation". Return only one word.'''},
        {"role": "user", "content": f"Detect intent for: '{pesan_pengguna}'"}
    ]
    success, niat = llm_utils.call_llm(messages, config.INTENT_DETECTION_MODEL, max_tokens=10, temperature=0.0)
    niat_cleaned = niat.strip().lower()
    if success and niat_cleaned in ["shell", "program", "conversation"]:
        return niat_cleaned
    return "conversation"

def generate_reasoning(user_message: str, detected_intent: str, chat_history: list = None) -> str:
    """
    Generates a detailed reasoning for the AI's chosen action.
    """
    system_prompt = f"You are an AI assistant. Based on the user's message and the detected intent '{detected_intent}', explain your thought process and what you plan to do next. Be concise and clear."
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]
    if chat_history:
        messages.extend(chat_history[-5:]) # Provide some recent context

    success, reasoning_text = llm_utils.call_llm(messages, config.REASONING_MODEL, max_tokens=config.REASONING_MAX_TOKENS, temperature=config.REASONING_TEMPERATURE)
    if success:
        return reasoning_text
    else:
        return f"[Reasoning generation failed: {reasoning_text}]"

def minta_kode(prompt: str, error_context: str = None, chat_history: list = None, target_language: str = None) -> tuple[bool, str, str | None]:
    """
    Requests LLM to generate or fix code.
    """
    system_info_message = f"You are an AI coding assistant on OS: {config.SYSTEM_INFO['os']}. Provide complete, runnable code in a single Markdown block."
    
    messages = [{"role": "system", "content": system_info_message}]
    if chat_history:
        messages.extend(chat_history[-5:])

    if error_context:
        messages.append({"role": "user", "content": f"Fix the following error:\n\n{error_context}"})
    else:
        messages.append({"role": "user", "content": prompt})
    
    model = config.ERROR_FIX_MODEL if error_context else config.CODE_GEN_MODEL
    success, response_content = llm_utils.call_llm(messages, model, max_tokens=2048, temperature=0.5)

    if success:
        cleaned_code, detected_language = llm_utils.ekstrak_kode_dari_llm(response_content, target_language)
        return True, cleaned_code, detected_language
    else:
        return False, response_content, None

def generate_filename(prompt: str, detected_language: str = "txt") -> str:
    """
    Generates a sanitized, relevant filename.
    """
    extension_map = {
        "python": ".py", "bash": ".sh", "javascript": ".js", "html": ".html", "css": ".css",
        "java": ".java", "c": ".c", "cpp": ".cpp", "txt": ".txt"
    }
    messages = [
        {"role": "system", "content": f"Generate a short, descriptive, lowercase filename (no spaces, use underscores, no extension) for a '{detected_language}' file based on this prompt. Example: 'web_scraper'."},
        {"role": "user", "content": prompt}
    ]
    success, filename = llm_utils.call_llm(messages, config.FILENAME_GEN_MODEL, max_tokens=25, temperature=0.5)
    
    if not success:
        return f"generated_code{extension_map.get(detected_language, '.txt')}"

    # Sanitize the filename
    filename = re.sub(r'[^\w-]+', '_', filename.strip().lower())
    return f"{filename}{extension_map.get(detected_language, '.txt')}"

def konversi_ke_perintah_shell(bahasa_natural: str, chat_history: list = None) -> tuple[bool, str]:
    """
    Converts natural language to an executable shell command.
    """
    system_message = f"You are a translator for OS: {config.SYSTEM_INFO['os']}. Convert the instruction to a single-line shell command. If impossible, respond with 'CANNOT_CONVERT'."
    messages = [{"role": "system", "content": system_message}]
    if chat_history:
        messages.extend(chat_history[-5:])
    messages.append({"role": "user", "content": f"Instruction: {bahasa_natural}"})

    return llm_utils.call_llm(messages, config.COMMAND_CONVERSION_MODEL, max_tokens=150, temperature=0.2)

def minta_jawaban_konversasi(prompt: str, chat_history: list) -> tuple[bool, str]:
    """
    Requests a conversational answer, maintaining context.
    """
    messages = [{"role": "system", "content": f"You are a helpful AI assistant on OS: {config.SYSTEM_INFO['os']}."}]
    messages.extend(chat_history[-10:])
    messages.append({"role": "user", "content": prompt})

    success, response = llm_utils.call_llm(messages, config.CONVERSATION_MODEL, max_tokens=1500, temperature=0.75)
    return success, response
