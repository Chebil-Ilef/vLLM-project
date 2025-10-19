import os
import time
import logging
from typing import List, Dict, Optional

from openai import OpenAI
from openai._exceptions import APIError, APITimeoutError, RateLimitError

logger = logging.getLogger(__name__)

# -------- Client Factory --------
def _get_client() -> OpenAI:
    base = os.getenv("VLLM_URL", "http://vLLM:8000/v1")
    key = os.getenv("VLLM_API_KEY", "devkey")
    return OpenAI(base_url=base, api_key=key)

def _normalize_messages(messages: List[Dict] | str) -> List[Dict]:

    if isinstance(messages, str):
        return [{"role": "user", "content": messages}]
    norm: List[Dict] = []
    for m in messages or []:
        if isinstance(m, dict):
            norm.append({"role": m.get("role", "user"), "content": m.get("content", "")})
        else:
            norm.append({"role": "user", "content": str(m)})
    return norm

# -------- High-level helpers --------
def call_vllm_chat(
    messages: List[Dict] | str,
    model_name: Optional[str] = None,
    max_tokens: int = 512,
    temperature: float = 0.0,
    retries: int = 3,
    backoff_factor: float = 0.5,
    **kwargs,
) -> str:

    client = _get_client()
    model = model_name or os.getenv("VLLM_MODEL") 

    payload = {
        "model": model,
        "messages": _normalize_messages(messages),
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    payload.update(kwargs)

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            logger.info("Calling chat.completions (attempt %d/%d, model=%s)", attempt, retries, model)
            resp = client.chat.completions.create(**payload)
            return resp.choices[0].message.content or ""
        except (APIError, APITimeoutError, RateLimitError, Exception) as e:
            last_exc = e
            logger.warning("Chat attempt %d/%d failed: %s", attempt, retries, e)
            if attempt == retries:
                logger.error("Chat failed after %d attempts", retries)
                raise
            sleep = backoff_factor * (2 ** (attempt - 1))
            logger.info("Retrying in %.1fs...", sleep)
            time.sleep(sleep)

    raise last_exc or RuntimeError("Unknown error in call_vllm_chat")

def openai_chat_completion(
    model: Optional[str] = None,
    messages: Optional[List[Dict]] = None,
    max_tokens: int = 512,
    temperature: float = 0.0,
    retries: int = 3,
    backoff_factor: float = 0.5,
    **kwargs,
):


    client = _get_client()
    model = model or os.getenv("VLLM_MODEL")
    messages = _normalize_messages(messages or [])

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    payload.update(kwargs)

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            logger.info("Calling chat.completions (full response) attempt %d/%d", attempt, retries)
            return client.chat.completions.create(**payload)
        except (APIError, APITimeoutError, RateLimitError, Exception) as e:
            last_exc = e
            logger.warning("Attempt %d/%d failed: %s", attempt, retries, e)
            if attempt == retries:
                raise
            time.sleep(backoff_factor * (2 ** (attempt - 1)))

def openai_completion(
    model: Optional[str] = None,
    prompt: str = "",
    max_tokens: int = 512,
    temperature: float = 0.0,
    retries: int = 3,
    backoff_factor: float = 0.5,
    **kwargs,
):

    client = _get_client()
    model = model or os.getenv("VLLM_MODEL")

    payload = {
        "model": model,
        "prompt": prompt,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    payload.update(kwargs)

    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            logger.info("Calling completions (attempt %d/%d, model=%s)", attempt, retries, model)
            return client.completions.create(**payload)
        except (APIError, APITimeoutError, RateLimitError, Exception) as e:
            last_exc = e
            logger.warning("Completions attempt %d/%d failed: %s", attempt, retries, e)
            if attempt == retries:
                raise
            time.sleep(backoff_factor * (2 ** (attempt - 1)))