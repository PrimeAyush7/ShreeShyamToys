import logging
from typing import Optional
from app.db.connection import db

logger = logging.getLogger("sst.audit")

class AuditService:
    @staticmethod
    def log(admin_email: str, action: str, target_type: str, target_id: Optional[str] = None, details: Optional[str] = None):
        """Records an administrative audit log entry."""
        try:
            db.execute("""
                INSERT INTO audit_logs (admin_email, action, target_type, target_id, details)
                VALUES (%s, %s, %s, %s, %s)
            """, (admin_email, action, target_type, str(target_id) if target_id else "", details or ""))
        except Exception as e:
            logger.error(f"Failed to record audit log: {e}")

    @staticmethod
    def list_logs(limit: int = 100, offset: int = 0):
        return db.fetch_all("""
            SELECT * FROM audit_logs 
            ORDER BY created_at DESC 
            LIMIT %s OFFSET %s
        """, (limit, offset))
