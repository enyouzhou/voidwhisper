from __future__ import annotations

"""Supabase helper: upload image to storage and insert row into `quotes` table.
Requires SUPABASE_URL and SUPABASE_KEY in environment (.env).
If these env vars are missing, the functions become no-ops so that the rest of
backend works without a database during early development.
"""

import mimetypes
import os
import pathlib
import time
import uuid
from typing import Optional

try:
    from supabase import Client, create_client
except ModuleNotFoundError:  # Supabase lib optional
    Client = None  # type: ignore

auth_missing_msg = (
    "Supabase client not initialised: SUPABASE_URL or SUPABASE_KEY missing."
)


class _SupabaseStub:  # graceful fallback when not configured
    def upload_and_insert(self, quote: str, image_path: str) -> Optional[str]:
        print(auth_missing_msg)
        return None


if Client is not None:
    from backend.config import settings

    if settings.supabase_url and settings.supabase_key:

        _sb: Client = create_client(settings.supabase_url, settings.supabase_key)

        BUCKET = "images"
        TABLE = "quotes"

        def _ensure_bucket_exists():
            buckets = [b["name"] for b in _sb.storage.list_buckets()]
            if BUCKET not in buckets:
                _sb.storage.create_bucket(BUCKET, public=True)

        _ensure_bucket_exists()

        def _public_image_url(key: str) -> str:
            return f"{settings.supabase_url}/storage/v1/object/public/{BUCKET}/{key}"

        class SupabaseClient:
            def upload_and_insert(self, quote: str, image_path: str) -> Optional[str]:
                key = f"{int(time.time())}-{uuid.uuid4().hex}{pathlib.Path(image_path).suffix}"
                mime, _ = mimetypes.guess_type(image_path)
                with open(image_path, "rb") as f:
                    _sb.storage.from_(BUCKET).upload(key, f, {"content-type": mime or "image/png"})
                url = _public_image_url(key)
                _sb.table(TABLE).insert({"quote": quote, "img_url": url}).execute()
                return url

    else:
        SupabaseClient = _SupabaseStub  # type: ignore

else:
    SupabaseClient = _SupabaseStub  # type: ignore

# Singleton instance used by other services
supabase_client = SupabaseClient()

__all__ = ["supabase_client"] 