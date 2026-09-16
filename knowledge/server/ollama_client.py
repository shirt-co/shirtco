#!/usr/bin/env python3
"""Optional Ollama client for Mac Studio embeddings and answers."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

DEFAULT_HOST = os.environ.get("OLLAMA_HOST", "http://127.0.0.1:11434").rstrip("/")
EMBED_MODEL = os.environ.get("SHIRTCO_EMBED_MODEL", "nomic-embed-text")
CHAT_MODEL = os.environ.get("SHIRTCO_CHAT_MODEL", "llama3.1:8b")


class OllamaError(RuntimeError):
    pass


def _request(path: str, payload: dict[str, Any], timeout: int = 120) -> dict[str, Any]:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{DEFAULT_HOST}{path}",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise OllamaError(f"Ollama is not reachable at {DEFAULT_HOST}: {exc}") from exc


def available() -> bool:
    try:
        with urllib.request.urlopen(f"{DEFAULT_HOST}/api/tags", timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError, ValueError):
        return False


def embed(text: str, model: str = EMBED_MODEL) -> list[float]:
    result = _request("/api/embeddings", {"model": model, "prompt": text})
    vector = result.get("embedding")
    if not isinstance(vector, list):
        raise OllamaError("Ollama embeddings response was missing an embedding vector.")
    return [float(value) for value in vector]


def chat(prompt: str, model: str = CHAT_MODEL) -> str:
    result = _request(
        "/api/chat",
        {
            "model": model,
            "stream": False,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are the Shirt Co company brain. Answer only from the provided "
                        "Shirt Co documents. If the documents do not contain the answer, say so. "
                        "Never invent prices, due dates, customer details, or Printavo status changes. "
                        "Cite the document title you used."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
        },
        timeout=180,
    )
    message = result.get("message") or {}
    content = message.get("content")
    if not content:
        raise OllamaError("Ollama chat response was empty.")
    return str(content).strip()
