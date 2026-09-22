from fastapi import APIRouter, Request, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
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
    user = get_current_user(request)
    if not user:
        raise HTTPException(status_code=401, detail="Please log in with Google to submit a wholesale enquiry.")

    customer_name = payload.customer_name if payload.customer_name is not None else user.get("name")
    customer_email = payload.customer_email if payload.customer_email is not None else user.get("email")
    # If customer explicitly passed mobile, use it; otherwise fallback to profile mobile
    customer_mobile = payload.customer_mobile if payload.customer_mobile is not None else user.get("mobile")

    if not customer_mobile or len(customer_mobile.strip()) < 8:
        raise HTTPException(status_code=400, detail="A valid mobile number is required to submit a wholesale enquiry.")

    raw_items = [itm.dict() for itm in payload.items]
    success, record, err = EnquiryService.create_enquiry(
        customer_id=user["user_id"],
        customer_name=customer_name,
        customer_email=customer_email,
        customer_mobile=customer_mobile,
        raw_items=raw_items,
        notes=payload.notes or ""
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
    """Admin-only file upload endpoint with MIME and size checks."""
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
