from __future__ import annotations

"""Flux image generation service wrapper.

Send a prompt to tu-zi Flux API and download the generated image locally.
Returns the local file path so that other services (e.g. Supabase) can upload
or simply serve it.
"""

import json
import os
import time
import uuid
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional

import requests
from PIL import Image

from backend.config import settings

FLUX_ENDPOINT = "https://api.tu-zi.com/v1/images/generations"
OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


class FluxError(RuntimeError):
    """Wrap exceptions coming from Flux API"""


def _default_prompt(quote: str) -> str:
    return (
        f"Create a clean, high-quality typographic poster with bold, readable white text on a dark background. "
        f"The quote text should be: \"{quote}\". "
        f"Use modern, sans-serif font with excellent readability. Dark gradient background. Minimalist design."
    )


def generate_image(quote: str, *, aspect_ratio: str = "3:4") -> str:
    """Generate an image for *quote* and save to ./output/*.

    Returns absolute file path. Raises FluxError on failure.
    """
    headers = {
        "Authorization": f"Bearer {settings.flux_api_key}",
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {
        "model": "flux-kontext-pro",
        "prompt": _default_prompt(quote),
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
        "safety_tolerance": 2,
        "prompt_upsampling": False,
    }

    try:
        resp = requests.post(FLUX_ENDPOINT, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
    except Exception as exc:
        raise FluxError(f"Flux request failed: {exc}") from exc

    try:
        data = resp.json()
    except json.JSONDecodeError as exc:
        raise FluxError(f"Invalid JSON from Flux: {exc}\nRaw: {resp.text[:200]}") from exc

    # Flux response schema assumption: {"data": [{"url": "https://…"}]} or {"url": "…"}
    url: Optional[str] = None
    if isinstance(data, dict):
        if "url" in data:
            url = data["url"]
        elif "data" in data and isinstance(data["data"], list) and data["data"]:
            first = data["data"][0]
            url = first.get("url")
            b64_data = first.get("b64_json")

    if not url:
        raise FluxError(f"Cannot find image url in response: {data}")

    # download
    img_resp = requests.get(url, timeout=120)
    img_resp.raise_for_status()

    file_path = OUTPUT_DIR / f"{int(time.time())}-{uuid.uuid4().hex}.png"
    with open(file_path, "wb") as f:
        f.write(img_resp.content)

    return str(file_path.resolve())


def generate_background(topic: str, aspect_ratio: str = "3:4") -> str:
    """Generate a background image (no text) related to *topic* and return local path."""
    # Build prompt with no text request
    prompt = (
        f"Abstract dark gradient or subtle texture background with objects as descorations inspired by {topic}. "
        "No words, no text, high-resolution, cinematic lighting."
    )
    headers = {
        "Authorization": f"Bearer {settings.flux_api_key}",
        "Content-Type": "application/json; charset=utf-8",
    }
    payload = {
        "model": "flux-kontext-pro",
        "prompt": prompt,
        "aspect_ratio": aspect_ratio,
        "output_format": "png",
        "safety_tolerance": 2,
        "prompt_upsampling": False,
    }
    try:
        resp = requests.post(FLUX_ENDPOINT, headers=headers, json=payload, timeout=120)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        raise FluxError(f"Flux background request failed: {exc}") from exc

    url: Optional[str] = None
    b64_data: Optional[str] = None
    if isinstance(data, dict):
        if "url" in data:
            url = data["url"]
        elif "data" in data and isinstance(data["data"], list) and data["data"]:
            first = data["data"][0]
            url = first.get("url")
            b64_data = first.get("b64_json")

    file_path = OUTPUT_DIR / f"bg-{int(time.time())}-{uuid.uuid4().hex}.png"

    if url:
        img_resp = requests.get(url, timeout=120)
        img_resp.raise_for_status()
        with open(file_path, "wb") as f:
            f.write(img_resp.content)
    elif b64_data:
        try:
            img_bytes = base64.b64decode(b64_data)
            img = Image.open(BytesIO(img_bytes))
            img.save(file_path, format="PNG")
        except Exception as exc:
            raise FluxError(f"Failed to decode b64 image: {exc}") from exc
    else:
        raise FluxError(f"Cannot find image url or b64_json in background response: {data}")

    return str(file_path.resolve())

__all__ = ["generate_background", "FluxError"] 