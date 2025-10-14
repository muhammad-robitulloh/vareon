import requests
import json
import re
import logging
import time
from .. import config

logger = logging.getLogger(__name__)

def call_llm(messages: list, model: str, max_tokens: int = 512, temperature: float = 0.7, extra_headers: dict = None) -> tuple[bool, str]:
    """
    Generic function to send requests to an LLM model.
    """
    if not config.OPENROUTER_API_KEY or not config.LLM_BASE_URL:
        logger.error("[LLM ERROR] API Key or LLM Base URL not set.")
        return False, "API Key or LLM Base URL not set. Please check configuration."

    payload = {"model": model, "messages": messages, "max_tokens": max_tokens, "temperature": temperature}
    headers = {"Authorization": f"Bearer {config.OPENROUTER_API_KEY}", "Content-Type": "application/json"}
    if extra_headers: headers.update(extra_headers)

    try:
        res = requests.post(config.LLM_BASE_URL, json=payload, headers=headers, timeout=300)
        res.raise_for_status()
        data = res.json()
        if "choices" in data and data["choices"]:
            usage = data.get("usage", {})
            log_token_usage(model, usage.get("prompt_tokens", 0), usage.get("completion_tokens", 0), usage.get("total_tokens", 0))
            return True, data["choices"][0]["message"]["content"]
        else:
            logger.error(f"[LLM] Response format error: {data}")
            return False, f"LLM response not in expected format. Debug: {data}"
    except requests.exceptions.RequestException as e:
        logger.error(f"[LLM] API request failed: {e}")
        return False, f"Failed to connect to LLM API: {e}"
    except Exception as e:
        logger.error(f"[LLM] Unexpected error: {e}")
        return False, f"An unexpected error occurred: {e}"

def ekstrak_kode_dari_llm(text_response: str, target_language: str = None) -> tuple[str, str]:
    """
    Extracts Markdown code blocks from LLM responses.
    """
    code_block_pattern = r"```(?P<lang>\w+)?\n(?P<content>.*?)```"
    matches = re.findall(code_block_pattern, text_response, re.DOTALL)
    
    if matches:
        # Prefer the target language if specified
        if target_language:
            for lang, content in matches:
                if lang and lang.lower() == target_language.lower():
                    return content.strip(), lang.lower()
        # Otherwise, take the first valid language block
        for lang, content in matches:
            if lang:
                return content.strip(), lang.lower()
        # Fallback to the first block if no language is specified
        return matches[0][1].strip(), "unknown"

    return text_response.strip(), "unknown"

def log_token_usage(model: str, prompt: int, completion: int, total: int):
    try:
        from .file_utils import get_token_usage_data, save_token_usage_data
        usage_data = get_token_usage_data()
        usage_data.append({"timestamp": time.time(), "model": model, "prompt_tokens": prompt, "completion_tokens": completion, "total_tokens": total})
        save_token_usage_data(usage_data)
    except Exception as e:
        logger.error(f"[Core] Failed to log token usage: {e}")
