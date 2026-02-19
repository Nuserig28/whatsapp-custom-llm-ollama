import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    # Meta
    meta_verify_token: str
    meta_app_secret: str
    meta_access_token: str
    meta_phone_number_id: str
    meta_graph_api_version: str

    # Ollama
    ollama_base_url: str
    ollama_model: str

    # Storage
    sqlite_path: str

    # Rate limiting (per WhatsApp sender)
    rate_limit_wa_per_minute: int


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _get_int_env(name: str, default: int) -> int:
    raw = os.getenv(name, "").strip()
    if not raw:
        return default
    try:
        val = int(raw)
        return val if val > 0 else default
    except ValueError:
        return default


def get_settings() -> Settings:
    return Settings(
        meta_verify_token=_require_env("META_WA_VERIFY_TOKEN"),
        meta_app_secret=_require_env("META_APP_SECRET"),
        meta_access_token=_require_env("META_WA_ACCESS_TOKEN"),
        meta_phone_number_id=_require_env("META_WA_PHONE_NUMBER_ID"),
        meta_graph_api_version=os.getenv("META_GRAPH_API_VERSION", "v25.0").strip() or "v25.0",
        ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434").strip() or "http://127.0.0.1:11434",
        ollama_model=os.getenv("OLLAMA_MODEL", "llama3.1:8b-instruct-q8_0").strip() or "llama3.1:8b-instruct-q8_0",
        sqlite_path=os.getenv("SQLITE_PATH", "./app_data.sqlite").strip() or "./app_data.sqlite",
        rate_limit_wa_per_minute=_get_int_env("RATE_LIMIT_WA_PER_MINUTE", 10),
    )
