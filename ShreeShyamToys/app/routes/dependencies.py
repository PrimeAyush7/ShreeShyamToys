from fastapi import Request, HTTPException, Depends
from fastapi.responses import RedirectResponse
from typing import Optional, Dict, Any
from app.services.auth_service import AuthService
from app.db.connection import db

def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    cookie_val = request.cookies.get("sst_session")
    if not cookie_val:
        return None
    session_data = AuthService.verify_session(cookie_val)
    if not session_data:
        return None
        
    # Refresh fresh customer record from DB
    customer = db.fetch_one("SELECT * FROM customers WHERE id = %s", (session_data["user_id"],))
    if not customer or customer["status"] == "disabled":
        return None

    session_data["mobile"] = customer.get("mobile")
    session_data["name"] = customer["name"]
    # Re-verify admin allowlist dynamically
    session_data["is_admin"] = AuthService.is_admin_email(customer["email"])
    return session_data

def require_customer(request: Request) -> Dict[str, Any]:
    user = get_current_user(request)
    if not user:
        # If API request return 401, else redirect
        if request.url.path.startswith("/api/"):
            raise HTTPException(status_code=401, detail="Authentication required via Google Login.")
        raise HTTPException(status_code=303, headers={"Location": f"/auth/login?redirect={request.url.path}"})
    return user

def require_admin(request: Request) -> Dict[str, Any]:
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=303, headers={"Location": f"/auth/login?redirect={request.url.path}"})
    if not user.get("is_admin"):
        raise HTTPException(status_code=403, detail="Access denied. Only authorized administrator Google accounts are permitted.")
    return user
