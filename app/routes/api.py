from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from app.routes.dependencies import get_current_user, require_admin
from app.services.enquiry_service import EnquiryService
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService
from app.models.schemas import EnquiryCreate

router = APIRouter(prefix="/api", tags=["API"])

@router.post("/enquiry/validate")
async def validate_enquiry(data: Dict[str, Any]):
    items = data.get("items", [])
    is_valid, processed_items, err = EnquiryService.validate_and_calculate_items(items)
    if not is_valid:
        return JSONResponse(status_code=400, content={"valid": False, "error": err})
    return {"valid": True, "items": processed_items}

@router.post("/enquiry/submit")
async def submit_enquiry(request: Request, payload: EnquiryCreate):
    """
    Submits a wholesale B2B enquiry.
    v2.0 Upgrade: Supports BOTH logged-in Google accounts AND 1-click Guest B2B checkout!
    """
    user = get_current_user(request)
    customer_id = user["user_id"] if user else None

    customer_name = (payload.customer_name or (user.get("name") if user else "") or "Wholesale Buyer").strip()
    customer_email = (payload.customer_email or (user.get("email") if user else "") or "guest@shreeshyamtoys.com").strip()
    customer_mobile = (payload.customer_mobile or (user.get("mobile") if user else "") or "").strip()
    customer_city = (payload.customer_city or "").strip()

    if not customer_mobile or len(customer_mobile) < 8:
        raise HTTPException(status_code=400, detail="A valid mobile number is required to submit a wholesale enquiry.")

    raw_items = [itm.dict() if hasattr(itm, "dict") else itm.model_dump() for itm in payload.items]
    success, record, err = EnquiryService.create_enquiry(
        customer_id=customer_id,
        customer_name=customer_name,
        customer_email=customer_email,
        customer_mobile=customer_mobile,
        raw_items=raw_items,
        notes=payload.notes or "",
        customer_city=customer_city
    )

    if not success:
        raise HTTPException(status_code=400, detail=err)

    return {
        "success": True,
        "enquiry_reference": record["enquiry_reference"],
        "whatsapp_url": record["whatsapp_url"],
        "whatsapp_message": record["whatsapp_message"],
        "message": f"Enquiry {record['enquiry_reference']} safely archived in database."
    }

@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    entity_type: str = Form("product"),
    entity_id: str = Form(""),
    admin: dict = Depends(require_admin)
):
    """Admin-only file upload endpoint with MIME, size checks, and permanent PostgreSQL BYTEA storage."""
    file_bytes = await file.read()
    success, result = StorageService.save_file(
        file_bytes=file_bytes,
        filename=file.filename,
        content_type=file.content_type or "application/octet-stream",
        entity_type=entity_type,
        entity_id=entity_id
    )
    if not success:
        raise HTTPException(status_code=400, detail=result)
        
    AuditService.log(
        admin_email=admin["email"],
        action="upload_media",
        target_type=entity_type,
        target_id=entity_id,
        details=f"Uploaded file {file.filename} -> {result}"
    )
    return {"success": True, "url": result}
