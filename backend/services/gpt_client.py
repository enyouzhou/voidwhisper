from __future__ import annotations

"""Wrapper around OpenAI GPT-4o-mini for generating short cynical quotes."""

from typing import Any

from openai import OpenAI

from backend.config import settings

# Initialise once – OpenAI python SDK v1.x
_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

MODEL_NAME = "gpt-4o-all"  # alias on tu-zi.com that routes to gpt-4o-mini.

_SYSTEM_PROMPT = (
    "You are a cynical comedian who writes dark, humorous anti-inspirational English quotes. "
    "Return ONE short quote (max 18 words). Do NOT add any extra text."
)


def generate_quote(topic: str) -> str:
    """Generate a poisonous chicken-soup quote about *topic*.

    Raises RuntimeError on API failure.
    """
    try:
        completion: Any = _client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"Write a quote about: {topic}"},
            ],
            temperature=0.9,
            max_tokens=60,
        )
    except Exception as exc:  # pragma: no cover – log + re-raise
        raise RuntimeError(f"GPT request failed: {exc}") from exc

    return completion.choices[0].message.content.strip()


__all__ = ["generate_quote"] 