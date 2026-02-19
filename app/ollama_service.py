from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests

from app.config import get_settings


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str
    model: str


class OllamaService:
    def __init__(self, config: Optional[OllamaConfig] = None, session: Optional[requests.Session] = None):
        settings = get_settings()
        self.config = config or OllamaConfig(
            base_url=settings.ollama_base_url.rstrip("/"),
            model=settings.ollama_model,
        )
        self.session = session or requests.Session()

    def generate(self, messages: List[Dict[str, str]]) -> str:
        url = f"{self.config.base_url}/api/chat"

        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.3,
                "top_p": 0.85,
                "repeat_penalty": 1.15,
                "num_predict": 90,
                "num_ctx": 8192,
                "num_batch": 512,
            },
        }

        start = time.time()
        resp = self.session.post(url, json=payload, timeout=120)
        resp.raise_for_status()

        data = resp.json()
        content = data.get("message", {}).get("content", "").strip()

        elapsed = round(time.time() - start, 2)
        print(f"[OLLAMA] model={self.config.model} | {elapsed}s | chars={len(content)}")

        return content
