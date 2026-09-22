import os
from typing import Optional, Dict, Any
import secrets
from fastapi import APIRouter, Request, Response, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse, JSONResponse
from app.config import settings
from app.services.auth_service import AuthService
from app.db.connection import db

router = APIRouter(prefix="/auth", tags=["Auth"])

def sanitize_redirect(target: Optional[str]) -> str:
    """
    Validates that the post-login redirect destination is a safe relative internal path.
    Allow only safe internal relative paths such as '/' or '/catalogue'.
    Reject/ignore absolute external URLs such as 'https://example.com', '//example.com', etc.
    """
    if not target or not isinstance(target, str):
        return "/"
    target = target.strip()
    # Reject protocol schemes (http:, https:, javascript:, data:, etc.)
    if ":" in target:
        return "/"
    # Must start with a single leading slash, and NOT start with '//' (protocol-relative) or '/\'
    if not target.startswith("/") or target.startswith("//") or target.startswith("/\\"):
        return "/"
    return target

@router.get("/google")
def google_login(request: Request, redirect: str = "/"):
    """Initiates Google OAuth 2.0 flow with safe relative redirect state."""
    safe_redirect = sanitize_redirect(redirect)
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        # If Google credentials are not configured, redirect to login page with clear notice or test flow
        return RedirectResponse(f"/auth/login?redirect={safe_redirect}&unconfigured=1")

    state = f"{secrets.token_urlsafe(16)}:{safe_redirect}"
    auth_url = AuthService.get_google_oauth_url(state)
    response = RedirectResponse(auth_url)
    response.set_cookie("sst_oauth_state", state, httponly=True, max_age=600, samesite="lax", secure=(settings.ENVIRONMENT == "production"))
    return response

@router.get("/google/callback")
def google_callback(request: Request, code: Optional[str] = None, state: Optional[str] = None, error: Optional[str] = None):
    """Handles Google OAuth callback and safely validates redirect target."""
    if error or not code:
        return RedirectResponse("/auth/login?error=Google+login+was+cancelled+or+failed")

    # State validation
    cookie_state = request.cookies.get("sst_oauth_state")
    if not cookie_state or cookie_state != state:
        return RedirectResponse("/auth/login?error=Invalid+OAuth+state+signature")

    raw_target = state.split(":", 1)[1] if ":" in (state or "") else "/"
    redirect_target = sanitize_redirect(raw_target)

    # Exchange code for access token
    tokens = AuthService.exchange_code_for_token(code)
    if not tokens or "access_token" not in tokens:
        return RedirectResponse("/auth/login?error=Could+not+exchange+Google+token")

    # Fetch user info
    userinfo = AuthService.fetch_google_user_info(tokens["access_token"])
    if not userinfo or not userinfo.get("email"):
        return RedirectResponse("/auth/login?error=Could+not+retrieve+Google+user+information")

    google_id = userinfo.get("id") or userinfo.get("sub")
    email = userinfo.get("email").strip().lower()
    name = userinfo.get("name") or email.split("@")[0]
    avatar = userinfo.get("picture")

    # Check if admin
    is_admin = AuthService.is_admin_email(email)
    if is_admin:
        admin_rec = AuthService.sync_admin(google_id, email, name)

    # Sync customer record
    customer_rec = AuthService.sync_customer(google_id, email, name, avatar)

    # Create signed session
    session_data = {
        "user_id": customer_rec["id"],
        "google_id": google_id,
        "email": email,
        "name": name,
        "avatar_url": avatar,
        "mobile": customer_rec.get("mobile"),
        "is_admin": is_admin
    }
    cookie_val = AuthService.sign_session(session_data)

    target = "/admin" if (is_admin and "admin" in redirect_target) else redirect_target
    resp = RedirectResponse(target, status_code=303)
    resp.set_cookie("sst_session", cookie_val, httponly=True, max_age=86400 * 30, samesite="lax", secure=(settings.ENVIRONMENT == "production"))
    resp.delete_cookie("sst_oauth_state")
    return resp

@router.get("/login")
def login_page(request: Request, redirect: str = "/", error: Optional[str] = None, unconfigured: Optional[str] = None):
    from app.main import templates
    from app.services.cms_service import CMSService
    safe_redirect = sanitize_redirect(redirect)
    settings_data = CMSService.get_settings()
    return templates.TemplateResponse(request=request, name="auth_login.html", context={
        "request": request,
        "redirect": safe_redirect,
        "error": error,
        "unconfigured": bool(unconfigured),
        "settings": settings_data
    })

@router.get("/logout")
def logout():
    resp = RedirectResponse("/", status_code=303)
    resp.delete_cookie("sst_session")
    return resp

@router.api_route("/test-login", methods=["GET", "POST"])
def test_login(request: Request, email: str = Query(...), name: str = Query("Test User"), role: str = Query("customer"), redirect: str = Query("/")):
    """
    Development/Testing helper ONLY. Simulates Google OAuth callback session creation.
    Strictly disabled in production mode. Cannot bypass Google OAuth in production.
    """
    if settings.is_production:
        raise HTTPException(status_code=404, detail="Test login endpoint is disabled in production environments. Real Google OAuth is required.")
    clean_email = email.strip().lower()
    is_admin = AuthService.is_admin_email(clean_email)
    
    if role == "admin" and not is_admin:
        # Strictly reject unauthorized admin login attempts
        raise HTTPException(status_code=403, detail="Email is not in the authorized admin allowlist.")

    google_id = f"test_gid_{clean_email.replace('@', '_').replace('.', '_')}"
    customer_rec = AuthService.sync_customer(google_id, clean_email, name, None)
    
    if is_admin:
        AuthService.sync_admin(google_id, clean_email, name)

    session_data = {
        "user_id": customer_rec["id"],
        "google_id": google_id,
        "email": clean_email,
        "name": name,
        "avatar_url": None,
        "mobile": customer_rec.get("mobile"),
        "is_admin": is_admin
    }
    cookie_val = AuthService.sign_session(session_data)
    
    safe_redirect = sanitize_redirect(redirect)
    target = "/admin" if (is_admin and "admin" in safe_redirect) else safe_redirect
    resp = RedirectResponse(target, status_code=303)
    resp.set_cookie("sst_session", cookie_val, httponly=True, max_age=86400 * 30, samesite="lax", secure=(settings.ENVIRONMENT == "production"))
    return resp
