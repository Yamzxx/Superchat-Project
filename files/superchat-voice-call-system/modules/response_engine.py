"""
response_engine.py
Generates conversational AI responses via the Ollama HTTP API.
"""

import json
import urllib.request
import urllib.error

from config import OLLAMA_BASE_URL, OLLAMA_MODEL, SYSTEM_PROMPT


class ResponseEngineError(Exception):
    pass


def generate_response(history: list[dict]) -> str:
    """
    Send conversation history to Ollama and return the assistant's reply.

    Args:
        history: List of {role, content} dicts (user + assistant turns).

    Returns:
        AI response text.

    Raises:
        ResponseEngineError: On network failure or unexpected API response.
    """
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history

    payload = json.dumps({
        "model":    OLLAMA_MODEL,
        "messages": messages,
        "stream":   False,
        "options":  {
            "temperature":   0.7,
            "num_predict":   256,
        },
    }).encode("utf-8")

    url = f"{OLLAMA_BASE_URL}/api/chat"
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise ResponseEngineError(
            f"Cannot reach Ollama at {OLLAMA_BASE_URL}. "
            f"Is Ollama running? Details: {exc}"
        )
    except json.JSONDecodeError as exc:
        raise ResponseEngineError(f"Invalid JSON from Ollama: {exc}")

    try:
        text = data["message"]["content"].strip()
    except (KeyError, TypeError) as exc:
        raise ResponseEngineError(f"Unexpected Ollama response shape: {data}")

    if not text:
        raise ResponseEngineError("Ollama returned an empty response.")

    return text
