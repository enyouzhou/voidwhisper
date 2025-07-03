from __future__ import annotations

"""/api/quote endpoint blueprint.

Query params:
    topic (str, optional) – subject to write about. default "life".

Response JSON:
    {
        "quote": "text",
        "img_url": "http://..." | "/abs/path/to/png"
    }
"""

import pathlib
import random
from flask import Blueprint, jsonify, request

from backend.services.gpt_client import generate_quote
from backend.services.flux_client import FluxError, generate_background
from backend.services.supabase_client import supabase_client
from backend.services.text_overlay import overlay_quote

bp = Blueprint("quote", __name__, url_prefix="/api")

# Predefined random topics for entertaining quotes
_TOPICS = [
    "life",
    "coffee",
    "work",
    "procrastination",
    "love",
    "success",
    "failure",
    "money",
    "coffee",
    "sleep",
    "cats",
    "technology",
    "meeting",
    "monday",
]


def _to_public_path(local_path: str) -> str:
    """Return /static/<filename> so frontend <img src> can load via Flask static route."""
    return f"/static/{pathlib.Path(local_path).name}"


@bp.route("/quote", methods=["GET"])
def get_quote():
    # Use provided topic; if missing/empty, pick a random one for fun
    topic_param = request.args.get("topic", "").strip()
    topic = topic_param if topic_param else random.choice(_TOPICS)

    try:
        quote = generate_quote(topic)
    except Exception as exc:
        return jsonify({"error": str(exc)}), 500

    try:
        bg_path = generate_background(topic)
    except FluxError as exc:
        return jsonify({"error": str(exc), "quote": quote}), 502

    # Overlay text locally
    final_path = overlay_quote(bg_path, quote)

    # Try upload to Supabase; fallback to local file uri
    supa_url = supabase_client.upload_and_insert(quote, final_path)
    img_url = supa_url if supa_url else _to_public_path(final_path)

    return jsonify({"quote": quote, "img_url": img_url}) 