import os
import time
import logging
from typing import List, Dict

import requests

logger = logging.getLogger(__name__)


def _build_url(path: str) -> str:
    base = os.getenv("VLLM_URL", "http://vllm:8000")
    # ensure path starts with a slash
    if not path.startswith("/"):
        path = "/" + path
    return base.rstrip("/") + path


def call_vllm_chat(
    messages: List[Dict],
    model_name: str = None,
    max_tokens: int = 512,
    temperature: float = 0.0,
    retries: int = 3,
    backoff_factor: float = 0.5,
) -> str:
    """
    Call the vLLM HTTP API with basic retry/backoff and logging.

    Raises the last requests exception if all attempts fail.
    """

    model_name = model_name or os.getenv("VLLM_MODEL")
    url = _build_url("/v1/chat/completions")

    api_key = os.getenv("VLLM_API_KEY")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    last_exc = None
    for attempt in range(1, retries + 1):
        try:
            logger.info("Calling vLLM at %s (attempt %d/%d)", url, attempt, retries)
            resp = requests.post(url, json=payload, headers=headers, timeout=120)
            resp.raise_for_status()
            data = resp.json()

            # Primary response shape (OpenAI-like)
            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                # Fallback to older/text shapes
                if "choices" in data and len(data["choices"]) > 0 and "text" in data["choices"][0]:
                    return data["choices"][0]["text"]
                # If shape is unexpected, return full JSON as string for debugging
                logger.debug("Unexpected vLLM response shape: %s", data)
                raise RuntimeError("Unexpected vLLM response shape: %s" % (data,))

        except requests.RequestException as e:
            last_exc = e
            logger.warning("vLLM request attempt %d/%d failed: %s", attempt, retries, e)
            if attempt == retries:
                logger.error("vLLM request failed after %d attempts", retries)
                # raise the original exception so caller can inspect it
                raise
            sleep_time = backoff_factor * (2 ** (attempt - 1))
            logger.info("Retrying in %.1f seconds...", sleep_time)
            time.sleep(sleep_time)


def openai_chat_completion(model: str = None, messages: List[Dict] = None, max_tokens: int = 512, temperature: float = 0.0, **kwargs) -> Dict:
    """
    OpenAI-compatible wrapper that calls the vLLM HTTP endpoint and returns the full response dict.

    Returns a dict with at least `choices` similar to OpenAI. This keeps compatibility with code expecting
    the OpenAI ChatCompletion response shape.
    """
    messages = messages or []
    # Use the main call function which returns the assistant text; but keep full response by making a raw request
    url = _build_url("/v1/chat/completions")
    api_key = os.getenv("VLLM_API_KEY")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model or os.getenv("VLLM_MODEL"),
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    # Include any extra kwargs into payload (openai has many optional fields)
    payload.update(kwargs)

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        print(
            call_vllm_chat(
                [{"role": "user", "content": "Say hello in one sentence."}], max_tokens=20
            )
        )
    except Exception as e:
        logger.exception("vLLM HTTP client test failed: %s", e)
