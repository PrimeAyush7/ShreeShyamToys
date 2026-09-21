import hmac
import hashlib
import json
import base64
import time
import urllib.parse
import uuid
import logging
import requests
from typing import Optional, Dict, Any, Tuple
from app.config import settings
from app.db.connection import db

logger = logging.getLogger("sst.auth")

class AuthService:
    @staticmethod
    def sign_session(payload: Dict[str, Any]) -> str:
        """Signs a session payload with SECRET_KEY."""
        data_str = json.dumps(payload, separators=(',', ':'))
        b64_data = base64.urlsafe_b64encode(data_str.encode()).decode()
        signature = hmac.new(settings.SECRET_KEY.encode(), b64_data.encode(), hashlib.sha256).hexdigest()
        return f"{b64_data}.{signature}"

    @staticmethod
    def verify_session(cookie_value: Optional[str]) -> Optional[Dict[str, Any]]:
        """Verifies session cookie and returns payload if valid."""
        if not cookie_value or "." not in cookie_value:
            return None
        try:
            b64_data, signature = cookie_value.split(".", 1)
            expected_sig = hmac.new(settings.SECRET_KEY.encode(), b64_data.encode(), hashlib.sha256).hexdigest()
            if not hmac.compare_digest(signature, expected_sig):
                return None
            json_bytes = base64.urlsafe_b64decode(b64_data.encode())
            payload = json.loads(json_bytes.decode())
            # Optional expiration check
            if "exp" in payload and payload["exp"] < time.time():
                return None
            return payload
        except Exception:
            return None

    @staticmethod
    def get_google_oauth_url(state: str) -> str:
        """Constructs the Google OAuth 2.0 authorization URL."""
        params = {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "online",
            "state": state,
            "prompt": "select_account"
        }
        return f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"

    @staticmethod
    def exchange_code_for_token(code: str) -> Optional[Dict[str, Any]]:
        """Exchanges Google authorization code for tokens."""
        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": settings.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code"
        }
        try:
            res = requests.post(token_url, data=payload, timeout=10)
            if res.status_code == 200:
                return res.json()
            logger.error(f"Google token exchange failed: {res.status_code} {res.text}")
            return None
        except Exception as e:
            logger.error(f"Exception during Google token exchange: {e}")
            return None

    @staticmethod
    def fetch_google_user_info(access_token: str) -> Optional[Dict[str, Any]]:
        """Fetches Google user profile from Google UserInfo endpoint."""
        userinfo_url = "https://www.googleapis.com/oauth2/v2/userinfo"
        headers = {"Authorization": f"Bearer {access_token}"}
        try:
            res = requests.get(userinfo_url, headers=headers, timeout=10)
            if res.status_code == 200:
                return res.json()
            logger.error(f"Google userinfo request failed: {res.status_code} {res.text}")
            return None
        except Exception as e:
            logger.error(f"Exception during Google userinfo fetch: {e}")
            return None

    @staticmethod
    def sync_customer(google_id: str, email: str, name: str, avatar_url: Optional[str] = None) -> Dict[str, Any]:
        """Creates or updates a customer record upon Google authentication."""
        existing = db.fetch_one("SELECT * FROM customers WHERE google_id = %s OR email = %s", (google_id, email))
        now = "datetime('now')" if not db.is_postgres else "NOW()"
        
        if existing:
            customer_id = existing["id"]
            db.execute("""
                UPDATE customers 
                SET name = %s, avatar_url = %s, last_login_at = CURRENT_TIMESTAMP, last_activity_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (name, avatar_url or existing.get("avatar_url"), customer_id))
            return db.fetch_one("SELECT * FROM customers WHERE id = %s", (customer_id,))
        else:
            customer_id = f"cust_{uuid.uuid4().hex[:12]}"
            db.execute("""
                INSERT INTO customers (id, google_id, name, email, avatar_url, status)
                VALUES (%s, %s, %s, %s, %s, 'active')
            """, (customer_id, google_id, name, email, avatar_url))
            return db.fetch_one("SELECT * FROM customers WHERE id = %s", (customer_id,))

    @staticmethod
    def is_admin_email(email: str) -> bool:
        """Verifies if an email is in the authorized admin allowlist or admins table."""
        email_clean = email.strip().lower()
        if email_clean in settings.admin_email_list:
            return True
        admin = db.fetch_one("SELECT id FROM admins WHERE LOWER(email) = %s AND is_active = TRUE", (email_clean,))
        return bool(admin)

    @staticmethod
    def sync_admin(google_id: str, email: str, name: str) -> Optional[Dict[str, Any]]:
        """Verifies and registers/updates an authorized admin."""
        email_clean = email.strip().lower()
        if not AuthService.is_admin_email(email_clean):
            return None
            
        existing = db.fetch_one("SELECT * FROM admins WHERE LOWER(email) = %s", (email_clean,))
        if existing:
            db.execute("""
                UPDATE admins 
                SET google_id = %s, name = %s, last_login_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (google_id, name, existing["id"]))
            return db.fetch_one("SELECT * FROM admins WHERE id = %s", (existing["id"],))
        else:
            admin_id = f"adm_{uuid.uuid4().hex[:12]}"
            role = "superadmin" if email_clean == settings.admin_email_list[0] else "admin"
            db.execute("""
                INSERT INTO admins (id, google_id, email, name, role, is_active, last_login_at)
                VALUES (%s, %s, %s, %s, %s, TRUE, CURRENT_TIMESTAMP)
            """, (admin_id, google_id, email_clean, name, role))
            return db.fetch_one("SELECT * FROM admins WHERE id = %s", (admin_id,))
