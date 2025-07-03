from __future__ import annotations

"""Overlay a quote onto a background image.

This function ensures the background is the desired size (1080×1350), darkens
it slightly for contrast, wraps the text, and draws it centered.

Returns the path of the generated image.
"""

import textwrap
import time
import uuid
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageEnhance

__all__ = ["overlay_quote"]

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)
TARGET_SIZE = (1080, 1350)

# Try to load a bundled font; fall back to default if missing
_FONT_PATHS = [
    "assets/fonts/Inter-Bold.ttf",  # custom path (user can add font here)
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",  # macOS example
]

def _get_font(size: int = 72) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:  # type: ignore
    for path in _FONT_PATHS:
        fp = Path(path)
        if fp.exists():
            try:
                return ImageFont.truetype(str(fp), size=size)
            except Exception:
                continue
    # fallback
    return ImageFont.load_default()

def overlay_quote(bg_path: str, quote: str) -> str:
    bg = Image.open(bg_path).convert("RGB")

    # Resize/crop to target aspect ratio
    bg = bg.resize(TARGET_SIZE, Image.LANCZOS)

    # Darken background slightly for better text contrast
    enhancer = ImageEnhance.Brightness(bg)
    bg = enhancer.enhance(0.6)

    # Prepare drawing context
    draw = ImageDraw.Draw(bg)

    # Dynamically choose font size based on quote length
    max_chars = max(len(line) for line in quote.split("\n"))
    if max_chars < 30:
        font_size = 72
    elif max_chars < 60:
        font_size = 60
    else:
        font_size = 48

    font = _get_font(font_size)

    # Wrap text to fit width (~20 chars per line)
    wrapped = textwrap.fill(quote, width=20)

    # Measure text block size
    bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=10, align="center")
    w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]

    # Center position
    x = (TARGET_SIZE[0] - w) / 2
    y = (TARGET_SIZE[1] - h) / 2

    # Draw text (white)
    draw.multiline_text(
        (x, y), wrapped, font=font, fill=(255, 255, 255), align="center", spacing=10
    )

    # Save output
    out_path = OUTPUT_DIR / f"{int(time.time())}-{uuid.uuid4().hex}.png"
    bg.save(out_path, format="PNG", quality=95)

    return str(out_path) 