from __future__ import annotations

"""Wrapper around OpenAI GPT-4o-mini for generating short cynical quotes."""

from typing import Any

from openai import OpenAI

from backend.config import settings
from backend.services.rag_retriever import random_quotes

# Initialise once – OpenAI python SDK v1.x
_client = OpenAI(api_key=settings.openai_api_key, base_url=settings.openai_base_url)

MODEL_NAME = "gpt-4o-all"  # alias on tu-zi.com that routes to gpt-4o-mini.

_SYSTEM_PROMPT = (
    "You are a cynical comedian who writes dark, humorous anti-inspirational English quotes. "
    "Return ONE short quote (max 18 words). Do NOT add any extra text."
)


def generate_quote(_: str | None = None) -> str:  # topic ignored for random mode
    """Generate a brand-new cynical quote.

    Uses random reference quotes to steer style (lightweight RAG). Raises RuntimeError on failure.
    """

    references = random_quotes(8)
    ref_block = "\n".join(f"- {q}" for q in references)
    user_prompt = (
        "Here are some reference quotes:\n"
        f"{ref_block}\n\n"
        "Create ONE brand-new anti-inspirational quote in similar style (max 18 words)."
    )

    try:
        completion: Any = _client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.9,
            max_tokens=60,
        )
    except Exception as exc:
        raise RuntimeError(f"GPT request failed: {exc}") from exc

    return completion.choices[0].message.content.strip()


__all__ = ["generate_quote"] 