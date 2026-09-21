from fastapi import APIRouter, Request, Depends, Form, HTTPException, Query, UploadFile, File
from fastapi.responses import RedirectResponse, Response, StreamingResponse
from typing import Optional, List
from app.routes.dependencies import require_admin
from app.services.cms_service import CMSService
from app.services.product_service import ProductService
from app.services.enquiry_service import EnquiryService
from app.services.export_service import ExportService
from app.services.storage_service import StorageService
from app.services.audit_service import AuditService
from app.db.connection import db

router = APIRouter(prefix="/admin", tags=["Admin"])

# ----------------- Dashboard -----------------
@router.get("")
@router.get("/")
def admin_dashboard(request: Request, admin: dict = Depends(require_admin)):
    from app.main import templates
    metrics = CMSService.get_dashboard_metrics()
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin": admin,
        "metrics": metrics,
        "settings": settings
    })

# ----------------- Products -----------------
@router.get("/products")
def admin_products(
    request: Request,
    q: Optional[str] = None,
    category_id: Optional[int] = None,
    status: Optional[str] = None,
    archived: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    from app.main import templates
    categories = ProductService.get_categories(active_only=False)
    show_archived = (archived == "1")
    products = ProductService.get_admin_products(search=q, category_id=category_id, status=status, show_archived=show_archived)
    settings = CMSService.get_settings()

    return templates.TemplateResponse("admin/products.html", {
        "request": request,
        "admin": admin,
        "products": products,
        "categories": categories,
        "search_query": q or "",
        "selected_category": category_id,
        "selected_status": status,
        "show_archived": show_archived,
        "settings": settings
    })

@router.get("/products/new")
def admin_new_product(request: Request, admin: dict = Depends(require_admin)):
    from app.main import templates
    categories = ProductService.get_categories(active_only=False)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "admin": admin,
        "product": None,
        "categories": categories,
        "settings": settings,
        "is_edit": False
    })

@router.post("/products/new")
def admin_create_product(
    request: Request,
    name: str = Form(...),
    sku: str = Form(...),
    category_id: int = Form(...),
    moq: int = Form(1),
    description: str = Form(""),
    material: str = Form(""),
    size_info: str = Form(""),
    available_colours: str = Form(""),
    weight: str = Form(""),
    dimensions: str = Form(""),
    tags: str = Form(""),
    availability: str = Form("in_stock"),
    is_featured: bool = Form(False),
    is_new_arrival: bool = Form(False),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    initial_image_url: str = Form(""),
    admin: dict = Depends(require_admin)
):
    data = {
        "name": name,
        "sku": sku,
        "category_id": category_id,
        "moq": moq,
        "description": description,
        "material": material,
        "size_info": size_info,
        "available_colours": available_colours,
        "weight": weight,
        "dimensions": dimensions,
        "tags": tags,
        "availability": availability,
        "is_featured": is_featured,
        "is_new_arrival": is_new_arrival,
        "seo_title": seo_title,
        "seo_description": seo_description,
        "initial_image_url": initial_image_url
    }
    product_id = ProductService.create_product(data)
    AuditService.log(admin["email"], "create_product", "product", str(product_id), f"Created product '{name}' (SKU: {sku})")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Product+created+successfully", status_code=303)

@router.get("/products/{product_id}/edit")
def admin_edit_product(request: Request, product_id: int, success: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    product = ProductService.get_product_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    categories = ProductService.get_categories(active_only=False)
    settings = CMSService.get_settings()

    return templates.TemplateResponse("admin/product_form.html", {
        "request": request,
        "admin": admin,
        "product": product,
        "categories": categories,
        "settings": settings,
        "is_edit": True,
        "success": success
    })

@router.post("/products/{product_id}/edit")
def admin_update_product(
    request: Request,
    product_id: int,
    name: str = Form(...),
    sku: str = Form(...),
    category_id: int = Form(...),
    moq: int = Form(1),
    description: str = Form(""),
    material: str = Form(""),
    size_info: str = Form(""),
    available_colours: str = Form(""),
    weight: str = Form(""),
    dimensions: str = Form(""),
    tags: str = Form(""),
    availability: str = Form("in_stock"),
    is_featured: bool = Form(False),
    is_new_arrival: bool = Form(False),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    admin: dict = Depends(require_admin)
):
    data = {
        "name": name,
        "sku": sku,
        "category_id": category_id,
        "moq": moq,
        "description": description,
        "material": material,
        "size_info": size_info,
        "available_colours": available_colours,
        "weight": weight,
        "dimensions": dimensions,
        "tags": tags,
        "availability": availability,
        "is_featured": is_featured,
        "is_new_arrival": is_new_arrival,
        "seo_title": seo_title,
        "seo_description": seo_description
    }
    ProductService.update_product(product_id, data)
    AuditService.log(admin["email"], "update_product", "product", str(product_id), f"Updated product '{name}' (SKU: {sku})")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Product+updated+successfully", status_code=303)

@router.post("/products/{product_id}/duplicate")
def admin_duplicate_product(product_id: int, admin: dict = Depends(require_admin)):
    new_id = ProductService.duplicate_product(product_id)
    if new_id:
        AuditService.log(admin["email"], "duplicate_product", "product", str(new_id), f"Duplicated from product ID {product_id}")
        return RedirectResponse(f"/admin/products/{new_id}/edit?success=Product+duplicated+successfully", status_code=303)
    return RedirectResponse("/admin/products?error=Failed+to+duplicate", status_code=303)

@router.post("/products/{product_id}/archive")
def admin_archive_product(product_id: int, admin: dict = Depends(require_admin)):
    ProductService.archive_product(product_id)
    AuditService.log(admin["email"], "archive_product", "product", str(product_id), "Archived product")
    return RedirectResponse("/admin/products?success=Product+archived+successfully", status_code=303)

@router.post("/products/{product_id}/restore")
def admin_restore_product(product_id: int, admin: dict = Depends(require_admin)):
    ProductService.restore_product(product_id)
    AuditService.log(admin["email"], "restore_product", "product", str(product_id), "Restored product from archive")
    return RedirectResponse("/admin/products?archived=1&success=Product+restored+successfully", status_code=303)

# Product Variants
@router.post("/products/{product_id}/variants/add")
def admin_add_variant(
    product_id: int,
    size: str = Form(...),
    colour: str = Form(...),
    sku_suffix: str = Form(""),
    variant_moq: Optional[int] = Form(None),
    admin: dict = Depends(require_admin)
):
    ProductService.add_variant(product_id, size, colour, sku_suffix, variant_moq)
    AuditService.log(admin["email"], "add_variant", "product", str(product_id), f"Added variant {size} / {colour}")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Variant+added", status_code=303)

@router.post("/products/{product_id}/variants/{variant_id}/delete")
def admin_delete_variant(product_id: int, variant_id: int, admin: dict = Depends(require_admin)):
    ProductService.delete_variant(variant_id)
    AuditService.log(admin["email"], "delete_variant", "product", str(product_id), f"Deleted variant ID {variant_id}")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Variant+deleted", status_code=303)

# Product Images
@router.post("/products/{product_id}/images/upload")
async def admin_upload_product_image(
    product_id: int,
    image_file: UploadFile = File(...),
    alt_text: str = Form(""),
    is_primary: bool = Form(False),
    admin: dict = Depends(require_admin)
):
    file_bytes = await image_file.read()
    success, result = StorageService.save_file(
        file_bytes=file_bytes,
        filename=image_file.filename,
        content_type=image_file.content_type or "image/jpeg",
        entity_type="product",
        entity_id=str(product_id)
    )
    if not success:
        return RedirectResponse(f"/admin/products/{product_id}/edit?error={result}", status_code=303)
    
    ProductService.add_image(product_id, result, alt_text, is_primary)
    AuditService.log(admin["email"], "add_image", "product", str(product_id), f"Uploaded image {result}")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Image+uploaded", status_code=303)

@router.post("/products/{product_id}/images/{image_id}/delete")
def admin_delete_product_image(product_id: int, image_id: int, admin: dict = Depends(require_admin)):
    ProductService.delete_image(image_id)
    AuditService.log(admin["email"], "delete_image", "product", str(product_id), f"Deleted image ID {image_id}")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Image+deleted", status_code=303)

@router.post("/products/{product_id}/images/{image_id}/primary")
def admin_set_primary_image(product_id: int, image_id: int, admin: dict = Depends(require_admin)):
    ProductService.set_primary_image(product_id, image_id)
    AuditService.log(admin["email"], "set_primary_image", "product", str(product_id), f"Set image ID {image_id} as primary")
    return RedirectResponse(f"/admin/products/{product_id}/edit?success=Primary+image+updated", status_code=303)

# ----------------- Categories -----------------
@router.get("/categories")
def admin_categories(request: Request, admin: dict = Depends(require_admin), success: Optional[str] = None, error: Optional[str] = None):
    from app.main import templates
    categories = ProductService.get_categories(active_only=False)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/categories.html", {
        "request": request,
        "admin": admin,
        "categories": categories,
        "settings": settings,
        "success": success,
        "error": error
    })

@router.get("/categories/new")
def admin_new_category(request: Request, admin: dict = Depends(require_admin)):
    from app.main import templates
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/category_form.html", {
        "request": request,
        "admin": admin,
        "category": None,
        "settings": settings,
        "is_edit": False
    })

@router.post("/categories/new")
def admin_create_category(
    name: str = Form(...),
    description: str = Form(""),
    image_url: str = Form(""),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    admin: dict = Depends(require_admin)
):
    cat_id = ProductService.create_category({
        "name": name,
        "description": description,
        "image_url": image_url,
        "display_order": display_order,
        "is_active": is_active,
        "seo_title": seo_title,
        "seo_description": seo_description
    })
    AuditService.log(admin["email"], "create_category", "category", str(cat_id), f"Created category '{name}'")
    return RedirectResponse("/admin/categories?success=Category+created+successfully", status_code=303)

@router.get("/categories/{cat_id}/edit")
def admin_edit_category(request: Request, cat_id: int, admin: dict = Depends(require_admin)):
    from app.main import templates
    category = ProductService.get_category_by_id(cat_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/category_form.html", {
        "request": request,
        "admin": admin,
        "category": category,
        "settings": settings,
        "is_edit": True
    })

@router.post("/categories/{cat_id}/edit")
def admin_update_category(
    cat_id: int,
    name: str = Form(...),
    description: str = Form(""),
    image_url: str = Form(""),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    seo_title: str = Form(""),
    seo_description: str = Form(""),
    admin: dict = Depends(require_admin)
):
    ProductService.update_category(cat_id, {
        "name": name,
        "description": description,
        "image_url": image_url,
        "display_order": display_order,
        "is_active": is_active,
        "seo_title": seo_title,
        "seo_description": seo_description
    })
    AuditService.log(admin["email"], "update_category", "category", str(cat_id), f"Updated category '{name}'")
    return RedirectResponse("/admin/categories?success=Category+updated+successfully", status_code=303)

@router.post("/categories/{cat_id}/delete")
def admin_delete_category(cat_id: int, admin: dict = Depends(require_admin)):
    success, msg = ProductService.delete_category(cat_id)
    if not success:
        return RedirectResponse(f"/admin/categories?error={msg}", status_code=303)
    AuditService.log(admin["email"], "delete_category", "category", str(cat_id), "Deleted category")
    return RedirectResponse("/admin/categories?success=Category+deleted", status_code=303)

# ----------------- Customers -----------------
@router.get("/customers")
def admin_customers(request: Request, q: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    customers = CMSService.get_customers(search=q)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/customers.html", {
        "request": request,
        "admin": admin,
        "customers": customers,
        "search_query": q or "",
        "settings": settings
    })

@router.get("/customers/{customer_id}")
def admin_customer_detail(request: Request, customer_id: str, admin: dict = Depends(require_admin)):
    from app.main import templates
    customer = CMSService.get_customer_by_id(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/customer_detail.html", {
        "request": request,
        "admin": admin,
        "customer": customer,
        "settings": settings
    })

@router.post("/customers/{customer_id}/status")
def admin_toggle_customer_status(customer_id: str, status: str = Form(...), admin: dict = Depends(require_admin)):
    CMSService.set_customer_status(customer_id, status)
    AuditService.log(admin["email"], "update_customer_status", "customer", customer_id, f"Changed status to {status}")
    return RedirectResponse(f"/admin/customers/{customer_id}?success=Customer+status+updated", status_code=303)

# ----------------- Enquiries -----------------
@router.get("/enquiries")
def admin_enquiries(
    request: Request,
    status: Optional[str] = None,
    q: Optional[str] = None,
    admin: dict = Depends(require_admin)
):
    from app.main import templates
    enquiries = EnquiryService.get_admin_enquiries(status=status, search=q)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/enquiries.html", {
        "request": request,
        "admin": admin,
        "enquiries": enquiries,
        "selected_status": status,
        "search_query": q or "",
        "settings": settings
    })

@router.get("/enquiries/{enquiry_id}")
def admin_enquiry_detail(request: Request, enquiry_id: int, success: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    enquiry = EnquiryService.get_enquiry_detail(enquiry_id)
    if not enquiry:
        raise HTTPException(status_code=404, detail="Enquiry not found")
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/enquiry_detail.html", {
        "request": request,
        "admin": admin,
        "enquiry": enquiry,
        "settings": settings,
        "success": success
    })

@router.post("/enquiries/{enquiry_id}/status")
def admin_update_enquiry_status(
    enquiry_id: int,
    status: str = Form(...),
    notes: str = Form(""),
    admin: dict = Depends(require_admin)
):
    EnquiryService.update_enquiry_status(enquiry_id, status, notes)
    AuditService.log(admin["email"], "update_enquiry_status", "enquiry", str(enquiry_id), f"Status updated to '{status}'")
    return RedirectResponse(f"/admin/enquiries/{enquiry_id}?success=Status+updated+successfully", status_code=303)

# ----------------- Website Settings & CMS -----------------
@router.get("/settings")
def admin_settings_page(request: Request, success: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "admin": admin,
        "settings": settings,
        "success": success
    })

@router.post("/settings")
def admin_update_settings(request: Request, admin: dict = Depends(require_admin)):
    import asyncio
    # Extract all form items
    # In FastAPI, we can inspect request.form()
    return RedirectResponse("/admin/settings", status_code=303)

@router.post("/settings/save")
async def admin_save_settings(request: Request, admin: dict = Depends(require_admin)):
    form_data = await request.form()
    updates = {k: v for k, v in form_data.items() if not k.startswith("_")}
    CMSService.update_settings(updates)
    AuditService.log(admin["email"], "update_settings", "settings", "global", f"Updated {len(updates)} settings keys")
    return RedirectResponse("/admin/settings?success=Settings+saved+successfully", status_code=303)

@router.get("/homepage")
def admin_homepage_sections(request: Request, success: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    sections = CMSService.get_homepage_sections(enabled_only=False)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/homepage_cms.html", {
        "request": request,
        "admin": admin,
        "sections": sections,
        "settings": settings,
        "success": success
    })

@router.post("/homepage/{section_key}")
def admin_update_homepage_section(
    section_key: str,
    title: str = Form(""),
    subtitle: str = Form(""),
    content: str = Form(""),
    cta_label: str = Form(""),
    cta_url: str = Form(""),
    image_url: str = Form(""),
    is_enabled: bool = Form(True),
    display_order: int = Form(0),
    admin: dict = Depends(require_admin)
):
    CMSService.update_homepage_section(section_key, {
        "title": title,
        "subtitle": subtitle,
        "content": content,
        "cta_label": cta_label,
        "cta_url": cta_url,
        "image_url": image_url,
        "is_enabled": is_enabled,
        "display_order": display_order
    })
    AuditService.log(admin["email"], "update_homepage_section", "homepage", section_key, f"Updated section '{section_key}'")
    return RedirectResponse("/admin/homepage?success=Section+updated+successfully", status_code=303)

# ----------------- Social Links -----------------
@router.get("/social")
def admin_social_links(request: Request, success: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    links = CMSService.get_social_links(enabled_only=False)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/social_links.html", {
        "request": request,
        "admin": admin,
        "links": links,
        "settings": settings,
        "success": success
    })

@router.post("/social/new")
def admin_create_social_link(
    platform: str = Form(...),
    name: str = Form(...),
    url: str = Form(...),
    icon: str = Form(""),
    display_order: int = Form(0),
    is_enabled: bool = Form(True),
    admin: dict = Depends(require_admin)
):
    link_id = CMSService.create_social_link(platform, name, url, icon, display_order, is_enabled)
    AuditService.log(admin["email"], "create_social_link", "social", str(link_id), f"Created social link {platform}")
    return RedirectResponse("/admin/social?success=Social+link+created", status_code=303)

@router.post("/social/{link_id}/delete")
def admin_delete_social_link(link_id: int, admin: dict = Depends(require_admin)):
    CMSService.delete_social_link(link_id)
    AuditService.log(admin["email"], "delete_social_link", "social", str(link_id), "Deleted social link")
    return RedirectResponse("/admin/social?success=Social+link+deleted", status_code=303)

# ----------------- FAQs -----------------
@router.get("/faqs")
def admin_faqs(request: Request, success: Optional[str] = None, admin: dict = Depends(require_admin)):
    from app.main import templates
    faqs = CMSService.get_faqs(active_only=False)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/faqs.html", {
        "request": request,
        "admin": admin,
        "faqs": faqs,
        "settings": settings,
        "success": success
    })

@router.post("/faqs/new")
def admin_create_faq(
    question: str = Form(...),
    answer: str = Form(...),
    display_order: int = Form(0),
    is_active: bool = Form(True),
    admin: dict = Depends(require_admin)
):
    faq_id = CMSService.create_faq(question, answer, display_order, is_active)
    AuditService.log(admin["email"], "create_faq", "faq", str(faq_id), "Created FAQ")
    return RedirectResponse("/admin/faqs?success=FAQ+created", status_code=303)

@router.post("/faqs/{faq_id}/delete")
def admin_delete_faq(faq_id: int, admin: dict = Depends(require_admin)):
    CMSService.delete_faq(faq_id)
    AuditService.log(admin["email"], "delete_faq", "faq", str(faq_id), "Deleted FAQ")
    return RedirectResponse("/admin/faqs?success=FAQ+deleted", status_code=303)

# ----------------- Exports & Backups -----------------
@router.get("/exports")
def admin_exports_page(request: Request, admin: dict = Depends(require_admin)):
    from app.main import templates
    settings = CMSService.get_settings()
    manifest = StorageService.list_manifest()
    return templates.TemplateResponse("admin/exports.html", {
        "request": request,
        "admin": admin,
        "settings": settings,
        "manifest_count": len(manifest)
    })

@router.get("/exports/{table_name}")
def admin_download_export(table_name: str, format: str = "xlsx", admin: dict = Depends(require_admin)):
    content, filename, media_type = ExportService.export_table(table_name, format_type=format)
    AuditService.log(admin["email"], "export_data", "export", table_name, f"Exported {table_name} as {format}")
    return Response(
        content=content,
        media_type=media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

@router.get("/exports/all/zip")
def admin_download_everything(admin: dict = Depends(require_admin)):
    zip_bytes, filename = ExportService.export_everything_zip()
    AuditService.log(admin["email"], "export_everything", "backup", "all", "Generated full system backup ZIP")
    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

# ----------------- Audit Logs -----------------
@router.get("/audit-logs")
def admin_audit_logs(request: Request, admin: dict = Depends(require_admin)):
    from app.main import templates
    logs = AuditService.list_logs(limit=100)
    settings = CMSService.get_settings()
    return templates.TemplateResponse("admin/audit_logs.html", {
        "request": request,
        "admin": admin,
        "logs": logs,
        "settings": settings
    })
