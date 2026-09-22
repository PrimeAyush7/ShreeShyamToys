import os
import urllib.parse
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings
from app.db.migrations import run_migrations
from app.routes import auth, public, customer, admin, api

# Initialize App
app = FastAPI(
    title="Shree Shyam Toys — Wholesale B2B Plush & Soft Toy Catalogue",
    description="Production-ready B2B catalogue and WhatsApp enquiry engine.",
    docs_url="/api/docs" if settings.DEBUG else None,
    redoc_url=None
)

# Startup event
@app.on_event("startup")
def startup_event():
    run_migrations()

# Security Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        if not settings.DEBUG:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATES_DIR = os.path.join(BASE_DIR, "templates")
UPLOADS_DIR = settings.UPLOAD_DIR

os.makedirs(STATIC_DIR, exist_ok=True)
os.makedirs(UPLOADS_DIR, exist_ok=True)

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
app.mount("/uploads", StaticFiles(directory=UPLOADS_DIR), name="uploads")

# Starlette-compatible Jinja2Templates class supporting both modern (request=request, name=..., context=...)
# and legacy positional calling conventions across all Starlette versions.
class CompatibleJinja2Templates(Jinja2Templates):
    def TemplateResponse(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        name = kwargs.pop("name", None)
        context = kwargs.pop("context", None)

        if args:
            if isinstance(args[0], str):
                name = args[0]
                if len(args) > 1 and isinstance(args[1], dict):
                    context = args[1]
            else:
                request = args[0]
                if len(args) > 1 and isinstance(args[1], str):
                    name = args[1]
                if len(args) > 2 and isinstance(args[2], dict):
                    context = args[2]

        if context is None:
            context = {}
        if request is not None and "request" not in context:
            context["request"] = request

        req = context.get("request", request)

        try:
            return super().TemplateResponse(request=req, name=name, context=context, **kwargs)
        except TypeError:
            return super().TemplateResponse(name=name, context=context, **kwargs)

# Templates instance
templates = CompatibleJinja2Templates(directory=TEMPLATES_DIR)

# Jinja2 custom filters
def urlencode_filter(s):
    return urllib.parse.quote(str(s or ''))

def format_date(val, fmt="%b %d, %Y"):
    if not val:
        return ""
    if isinstance(val, str):
        return val[:10]
    return val.strftime(fmt)

templates.env.filters["urlencode"] = urlencode_filter
templates.env.filters["format_date"] = format_date

# Error Handlers
@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    from app.services.cms_service import CMSService
    settings_data = CMSService.get_settings()
    return templates.TemplateResponse(
        request=request,
        name="errors/404.html",
        context={
            "request": request,
            "settings": settings_data,
            "user": None,
            "detail": exc.detail if hasattr(exc, "detail") else "Page not found"
        },
        status_code=404
    )

@app.exception_handler(403)
async def forbidden_exception_handler(request: Request, exc: HTTPException):
    from app.services.cms_service import CMSService
    settings_data = CMSService.get_settings()
    return templates.TemplateResponse(
        request=request,
        name="errors/403.html",
        context={
            "request": request,
            "settings": settings_data,
            "user": None,
            "detail": exc.detail if hasattr(exc, "detail") else "Access Forbidden"
        },
        status_code=403
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: Exception):
    from app.services.cms_service import CMSService
    settings_data = CMSService.get_settings()
    return templates.TemplateResponse(
        request=request,
        name="errors/500.html",
        context={
            "request": request,
            "settings": settings_data,
            "user": None,
            "detail": "An unexpected error occurred. Our engineers have been alerted."
        },
        status_code=500
    )

# Include Routers
app.include_router(public.router)
app.include_router(auth.router)
app.include_router(customer.router)
app.include_router(admin.router)
app.include_router(api.router)
