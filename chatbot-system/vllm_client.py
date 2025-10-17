import os
import requests
from typing import List, Dict


def _build_url(path: str) -> str:
    base = os.getenv("VLLM_URL", "http://vllm:8000")
    return base.rstrip("/") + path


def call_vllm_chat(messages: List[Dict], model_name: str = None, max_tokens: int = 512, temperature: float = 0.0) -> str:

    model_name = model_name or os.getenv("VLLM_MODEL")
    url = _build_url("/v1/chat/completions")

    api_key = os.getenv("VLLM_API_KEY")
    headers = {
        "Content-Type": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    resp = requests.post(url, json=payload, headers=headers, timeout=120)
    resp.raise_for_status()
    data = resp.json()

    try:
        return data["choices"][0]["message"]["content"]
    except Exception:
        # Fallback to raw text if different API shape
        if "choices" in data and len(data["choices"]) > 0 and "text" in data["choices"][0]:
            return data["choices"][0]["text"]
        raise


if __name__ == "__main__":

    try:
        print(call_vllm_chat([{"role": "user", "content": "Say hello in one sentence."}], max_tokens=20))
    except Exception as e:
        print("vLLM HTTP client test failed:", e)
