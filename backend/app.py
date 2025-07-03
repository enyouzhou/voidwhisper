from __future__ import annotations

"""Flask application entry-point."""

from pathlib import Path

from flask import Flask, send_from_directory
from flask_cors import CORS

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.config import settings
from backend.routers.quote import bp as quote_bp

# Determine static folder where generated images live
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
_OUTPUT_DIR = _PROJECT_ROOT / "output"
_OUTPUT_DIR.mkdir(exist_ok=True)

# Serve frontend build (static) at root path
_FRONTEND_DIR = _PROJECT_ROOT / "frontend"

app = Flask(__name__, static_folder=str(_FRONTEND_DIR), static_url_path="")
CORS(app)  # allow all origins in dev

# Register API routes
app.register_blueprint(quote_bp)

# Root → index.html
@app.route("/")
def _index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/static/<path:filename>")
def serve_generated_image(filename: str):
    """Serve files from the output directory so frontend can load images via <img>."""
    return send_from_directory(_OUTPUT_DIR, filename)


if __name__ == "__main__":
    app.run(host=settings.host, port=settings.port, debug=settings.debug) 