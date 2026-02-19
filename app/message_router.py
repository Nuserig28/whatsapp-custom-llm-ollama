from __future__ import annotations

from typing import List, Dict

from app.config import get_settings
from app.ollama_service import OllamaService, OllamaConfig


settings = get_settings()

ollama_service = OllamaService(
    OllamaConfig(
        base_url=settings.ollama_base_url,
        model=settings.ollama_model,
    )
)


def normalize_history(raw_history) -> List[Dict[str, str]]:
    normalized: List[Dict[str, str]] = []

    for item in raw_history or []:
        if isinstance(item, dict):
            role = item.get("role")
            content = item.get("content")
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                normalized.append({"role": role, "content": content.strip()})
            continue

        if isinstance(item, tuple) and len(item) >= 2:
            role = item[0]
            content = item[1]
            if role in ("user", "assistant") and isinstance(content, str) and content.strip():
                normalized.append({"role": role, "content": content.strip()})

    return normalized


def generate_reply(history, user_input: str) -> str:
    history = normalize_history(history)

    messages: List[Dict[str, str]] = []

    # Simple system prompt (English only)
    messages.append({
        "role": "system",
        "content": (
            "You are chatting on WhatsApp like a friendly human.\n"
            "- Write natural English.\n"
            "- Keep it short (1–2 sentences).\n"
            "- No AI disclaimers.\n"
            "- No formal tone.\n"
        )
    })

    messages.extend(history[-8:])
    messages.append({"role": "user", "content": user_input})

    reply = ollama_service.generate(messages).strip()
    return reply
