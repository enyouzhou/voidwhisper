"""Random quote retriever for RAG context.

For MVP, loads a list of pre-existing cynical quotes from a text file (one quote per line)
under `assets/quotes.txt`. If the file is missing, falls back to a small built-in list.
"""
from __future__ import annotations

import random
from pathlib import Path
from typing import List

# Try load external corpus
_DEFAULT_QUOTES = [
    "Life is short; so is your attention span.",
    "Success is just failure with better PR.",
    "Dream big, nap often.",
    "The early bird gets exhausted first.",
    "Hope is the first step on the road to disappointment.",
]

_CORPUS: List[str]

_corpus_path = Path("assets/quotes.txt")
if _corpus_path.exists():
    _CORPUS = [line.strip() for line in _corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()]
else:
    _CORPUS = _DEFAULT_QUOTES


def random_quotes(k: int = 8) -> List[str]:
    """Return *k* distinct random quotes from the corpus."""
    if k >= len(_CORPUS):
        return random.sample(_CORPUS, len(_CORPUS))
    return random.sample(_CORPUS, k)

__all__ = ["random_quotes"] 