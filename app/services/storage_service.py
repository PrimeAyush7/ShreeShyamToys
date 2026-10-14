import os
import uuid
import logging
from typing import Optional, Dict, Any, Tuple
from app.config import settings
from app.db.connection import db

logger = logging.getLogger("sst.storage")

ALLOWED_MIME_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/svg+xml": ".svg",
    "image/x-icon": ".ico"
}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

class StorageService:
    @staticmethod
    def save_file(file_bytes: bytes, filename: str, content_type: str, entity_type: str = "product", entity_id: str = "") -> Tuple[bool, str]:
        """
        Validates and saves an uploaded file.
        v2.0 Upgrade:
        - Supports permanent PostgreSQL BYTEA / SQLite BLOB storage in `stored_media` (served at `/media/{id}`)
          so uploads survive Render restarts even without external Supabase Storage buckets.
        - If Supabase Storage is explicitly configured with valid credentials, attempts Supabase first and
          seamlessly falls back to permanent Database BYTEA storage.
        - Never uses ephemeral local disk in production.
        """
        if not file_bytes:
            return False, "Uploaded file is empty."
        if len(file_bytes) > MAX_FILE_SIZE:
            return False, "File exceeds maximum permitted size of 5MB."

        content_type_clean = (content_type or "").lower().split(";")[0].strip()
        if content_type_clean not in ALLOWED_MIME_TYPES:
            ext = os.path.splitext(filename or "")[1].lower()
            matching = [mime for mime, e in ALLOWED_MIME_TYPES.items() if e == ext]
            if not matching:
                return False, f"Unsupported file format '{content_type}'. Allowed types: JPG, PNG, WEBP, SVG, ICO."
            content_type_clean = matching[0]

        ext = ALLOWED_MIME_TYPES[content_type_clean]
        media_id = f"{uuid.uuid4().hex[:16]}{ext}"

        # 1. Optional Supabase Storage if credentials are provided
        if settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            try:
                import requests
                url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{entity_type}/{media_id}"
                headers = {
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": content_type_clean
                }
                res = requests.post(url, data=file_bytes, headers=headers, timeout=15)
                if res.status_code in (200, 201):
                    public_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{entity_type}/{media_id}"
                    StorageService._record_manifest(public_url, media_id, content_type_clean, len(file_bytes), entity_type, entity_id)
                    logger.info(f"Uploaded media to Supabase Storage: {public_url}")
                    return True, public_url
            except Exception as e:
                logger.warning(f"Supabase Storage upload skipped/failed, using permanent DB BYTEA storage: {e}")

        # 2. Permanent Database Binary Storage (`stored_media` table -> `/media/{media_id}`)
        try:
            if db.is_postgres:
                import psycopg2
                binary_param = psycopg2.Binary(file_bytes)
            else:
                binary_param = sqlite3.Binary(file_bytes) if 'sqlite3' in globals() else memoryview(file_bytes)

            db.execute("""
                INSERT INTO stored_media (id, file_name, mime_type, file_size, file_data, entity_type, entity_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (media_id, filename or media_id, content_type_clean, len(file_bytes), binary_param, entity_type, str(entity_id)))

            media_url = f"/media/{media_id}"
            StorageService._record_manifest(media_url, media_id, content_type_clean, len(file_bytes), entity_type, entity_id)
            logger.info(f"Saved permanent media to database: {media_url} ({len(file_bytes)} bytes)")
            return True, media_url
        except Exception as e:
            logger.error(f"Permanent database media save failed: {e}")
            return False, f"Database media storage error: {str(e)}"

    @staticmethod
    def get_media(media_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves binary media payload from `stored_media` by ID."""
        try:
            row = db.fetch_one("SELECT id, file_name, mime_type, file_size, file_data FROM stored_media WHERE id = %s", (media_id,))
            if not row or row.get("file_data") is None:
                return None
            raw_data = row["file_data"]
            if isinstance(raw_data, memoryview):
                raw_data = raw_data.tobytes()
            elif not isinstance(raw_data, (bytes, bytearray)):
                raw_data = bytes(raw_data)
            return {
                "id": row["id"],
                "file_name": row["file_name"],
                "mime_type": row["mime_type"] or "image/jpeg",
                "file_size": row["file_size"],
                "file_bytes": raw_data
            }
        except Exception as e:
            logger.error(f"Error fetching media {media_id}: {e}")
            return None

    @staticmethod
    def _record_manifest(url: str, filename: str, mime: str, size: int, entity_type: str, entity_id: str):
        try:
            db.execute("""
                INSERT INTO media_manifest (file_url, file_name, mime_type, file_size, entity_type, entity_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (url, filename, mime, size, entity_type, str(entity_id)))
        except Exception as e:
            logger.warning(f"Could not record media manifest: {e}")

    @staticmethod
    def list_manifest():
        return db.fetch_all("SELECT * FROM media_manifest ORDER BY created_at DESC")
