from fastapi import APIRouter, Request, Depends, Form
from fastapi.responses import RedirectResponse
from app.routes.dependencies import require_customer
from app.services.cms_service import CMSService
from app.services.enquiry_service import EnquiryService
from app.db.connection import db

router = APIRouter(prefix="/customer", tags=["Customer"])

@router.get("/profile")
def customer_profile(request: Request, user: dict = Depends(require_customer), success: str = None):
    from app.main import templates
    settings = CMSService.get_settings()
    customer = CMSService.get_customer_by_id(user["user_id"])
    return templates.TemplateResponse(request=request, name="customer/profile.html", context={
        "request": request,
        "user": user,
        "customer": customer,
        "settings": settings,
        "success": success
    })

@router.post("/profile")
def update_profile(request: Request, mobile: str = Form(...), name: str = Form(...), user: dict = Depends(require_customer)):
    clean_mobile = mobile.strip()
    clean_name = name.strip()
    db.execute("""
        UPDATE customers 
        SET mobile = %s, name = %s, last_activity_at = CURRENT_TIMESTAMP
        WHERE id = %s
    """, (clean_mobile, clean_name, user["user_id"]))
    return RedirectResponse("/customer/profile?success=Profile+updated+successfully", status_code=303)

@router.get("/enquiries")
def customer_enquiries(request: Request, user: dict = Depends(require_customer)):
    from app.main import templates
    settings = CMSService.get_settings()
    enquiries = EnquiryService.get_customer_enquiries(user["user_id"])
    return templates.TemplateResponse(request=request, name="customer/enquiries.html", context={
        "request": request,
        "user": user,
        "enquiries": enquiries,
        "settings": settings
    })
