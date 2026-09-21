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
        In production: Strictly uses Supabase Storage. If Supabase is unconfigured or fails,
        returns an explicit admin error and NEVER falls back to local ephemeral filesystem.
        In local development: Allows local filesystem storage if configured.
        """
        if len(file_bytes) > MAX_FILE_SIZE:
            return False, "File exceeds maximum permitted size of 5MB."
            
        content_type_clean = content_type.lower().split(";")[0].strip()
        if content_type_clean not in ALLOWED_MIME_TYPES:
            # Check extension as fallback
            ext = os.path.splitext(filename)[1].lower()
            matching = [mime for mime, e in ALLOWED_MIME_TYPES.items() if e == ext]
            if not matching:
                return False, f"Unsupported file format '{content_type}'. Allowed types: JPG, PNG, WEBP, SVG, ICO."
            content_type_clean = matching[0]

        ext = ALLOWED_MIME_TYPES[content_type_clean]
        safe_filename = f"{uuid.uuid4().hex[:12]}{ext}"

        # ---------------- PRODUCTION STORAGE (SUPABASE ONLY) ----------------
        if settings.is_production:
            if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
                err_msg = (
                    "Production Upload Failed: Supabase Storage credentials (SUPABASE_URL and "
                    "SUPABASE_SERVICE_ROLE_KEY) are missing in environment variables. Local filesystem "
                    "fallback is strictly disabled in production to protect media integrity."
                )
                logger.error(err_msg)
                return False, err_msg

            try:
                import requests
                url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{entity_type}/{safe_filename}"
                headers = {
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": content_type_clean
                }
                res = requests.post(url, data=file_bytes, headers=headers, timeout=20)
                if res.status_code in (200, 201):
                    public_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{entity_type}/{safe_filename}"
                    StorageService._record_manifest(public_url, safe_filename, content_type_clean, len(file_bytes), entity_type, entity_id)
                    logger.info(f"Successfully uploaded media to Supabase Storage: {public_url}")
                    return True, public_url
                else:
                    err_msg = f"Supabase Storage rejected upload (HTTP {res.status_code}): {res.text}"
                    logger.error(err_msg)
                    return False, f"Cloud storage upload error: {err_msg}"
            except Exception as e:
                err_msg = f"Supabase Storage connection exception: {str(e)}"
                logger.error(err_msg)
                return False, f"Cloud storage service unreachable: {err_msg}"

        # ---------------- LOCAL DEVELOPMENT STORAGE ----------------
        # In non-production, check if Supabase is optionally configured
        if settings.STORAGE_BACKEND == "supabase" and settings.SUPABASE_URL and settings.SUPABASE_SERVICE_ROLE_KEY:
            try:
                import requests
                url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/{settings.SUPABASE_STORAGE_BUCKET}/{entity_type}/{safe_filename}"
                headers = {
                    "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                    "Content-Type": content_type_clean
                }
                res = requests.post(url, data=file_bytes, headers=headers, timeout=15)
                if res.status_code in (200, 201):
                    public_url = f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{settings.SUPABASE_STORAGE_BUCKET}/{entity_type}/{safe_filename}"
                    StorageService._record_manifest(public_url, safe_filename, content_type_clean, len(file_bytes), entity_type, entity_id)
                    return True, public_url
            except Exception as e:
                logger.warning(f"Development Supabase upload failed, using local disk: {e}")

        # Local development filesystem storage
        upload_path = os.path.join(settings.UPLOAD_DIR, entity_type)
        os.makedirs(upload_path, exist_ok=True)
        dest_path = os.path.join(upload_path, safe_filename)
        with open(dest_path, "wb") as f:
            f.write(file_bytes)

        url = f"/uploads/{entity_type}/{safe_filename}"
        StorageService._record_manifest(url, safe_filename, content_type_clean, len(file_bytes), entity_type, entity_id)
        return True, url

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
