from __future__ import annotations

"""Centralised configuration loader.
Reads environment variables (optionally from a .env file) once at import time and
exposes them via the `settings` singleton.
"""

from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv

# Load .env from project root if present.
load_dotenv()


class _MissingKey(RuntimeError):
    """Raised when a required env var is missing."""


@dataclass(frozen=True, slots=True)
class Settings:
    # GPT-4o-mini / OpenAI-compatible
    openai_api_key: str
    openai_base_url: str

    # Flux image API
    flux_api_key: str

    # Supabase (all optional for first-run demo)
    supabase_url: Optional[str] = None
    supabase_key: Optional[str] = None

    # Flask settings
    host: str = "0.0.0.0"
    port: int = 5001
    debug: bool = True


def _require(key: str) -> str:
    value = os.getenv(key)
    if not value:
        raise _MissingKey(f"Environment variable '{key}' is required but missing.")
    return value


def _build_settings() -> Settings:
    return Settings(
        openai_api_key=_require("OPENAI_API_KEY"),
        openai_base_url=_require("OPENAI_BASE_URL"),
        flux_api_key=_require("FLUX_API_KEY"),
        supabase_url=os.getenv("SUPABASE_URL"),
        supabase_key=os.getenv("SUPABASE_KEY"),
    )


settings: Settings = _build_settings()

__all__ = ["settings", "Settings"] 