from fastapi import APIRouter, Request, Response, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse, Response as FastAPIResponse
from typing import Optional, List
from app.services.product_service import ProductService
from app.services.cms_service import CMSService
from app.services.enquiry_service import EnquiryService
from app.routes.dependencies import get_current_user

router = APIRouter(tags=["Public"])

@router.get("/")
def home(request: Request):
    from app.main import templates
    user = get_current_user(request)
    settings = CMSService.get_settings()
    sections = CMSService.get_homepage_sections(enabled_only=True)
    categories = ProductService.get_categories(active_only=True)
    featured_products = ProductService.get_featured_products(limit=8)
    new_arrivals = ProductService.get_new_arrivals(limit=8)
    faqs = CMSService.get_faqs(active_only=True)
    social_links = CMSService.get_social_links(enabled_only=True)

    return templates.TemplateResponse(request=request, name="index.html", context={
        "request": request,
        "user": user,
        "settings": settings,
        "sections": sections,
        "categories": categories,
        "featured_products": featured_products,
        "new_arrivals": new_arrivals,
        "faqs": faqs,
        "social_links": social_links
    })

@router.get("/catalogue")
def catalogue(
    request: Request,
    category: Optional[str] = None,
    q: Optional[str] = None,
    availability: Optional[str] = None,
    sort: str = "featured",
    featured: Optional[str] = None,
    new_arrival: Optional[str] = None,
    page: int = 1
):
    from app.main import templates
    user = get_current_user(request)
    settings = CMSService.get_settings()
    categories = ProductService.get_categories(active_only=True)
    social_links = CMSService.get_social_links(enabled_only=True)

    limit = 24
    offset = (page - 1) * limit
    is_feat = True if featured == "1" else None
    is_new = True if new_arrival == "1" else None

    products = ProductService.get_public_products(
        category_slug=category,
        search_query=q,
        availability=availability,
        is_featured=is_feat,
        is_new_arrival=is_new,
        sort_by=sort,
        limit=limit,
        offset=offset
    )

    # Active category object if category slug specified
    current_category = None
    if category:
        current_category = ProductService.get_category_by_slug(category)

    return templates.TemplateResponse(request=request, name="catalogue.html", context={
        "request": request,
        "user": user,
        "settings": settings,
        "products": products,
        "categories": categories,
        "current_category": current_category,
        "selected_category": category,
        "search_query": q or "",
        "selected_availability": availability,
        "selected_sort": sort,
        "selected_featured": featured,
        "selected_new_arrival": new_arrival,
        "page": page,
        "social_links": social_links
    })

@router.get("/category/{slug}")
def category_view(request: Request, slug: str):
    category = ProductService.get_category_by_slug(slug)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return catalogue(request, category=slug)

@router.get("/product/{slug}")
def product_detail(request: Request, slug: str):
    from app.main import templates
    user = get_current_user(request)
    settings = CMSService.get_settings()
    social_links = CMSService.get_social_links(enabled_only=True)

    product = ProductService.get_public_product_by_slug(slug)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found or currently unavailable")

    # Fetch related products from same category
    related_products = ProductService.get_public_products(
        category_slug=product.get("category_slug"),
        limit=4
    )
    # Filter out current product
    related_products = [p for p in related_products if p["id"] != product["id"]][:4]

    return templates.TemplateResponse(request=request, name="product_detail.html", context={
        "request": request,
        "user": user,
        "settings": settings,
        "product": product,
        "related_products": related_products,
        "social_links": social_links
    })

@router.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    from app.config import settings
    base_url = settings.APP_URL.rstrip('/')
    return f"""User-agent: *
Allow: /
Disallow: /admin/
Disallow: /customer/
Disallow: /api/
Sitemap: {base_url}/sitemap.xml
"""

@router.get("/sitemap.xml")
def sitemap_xml():
    from app.config import settings as settings_obj
    settings = CMSService.get_settings()
    base_url = settings_obj.APP_URL.rstrip("/")
    categories = ProductService.get_categories(active_only=True)
    products = ProductService.get_public_products(limit=500)

    urls = [
        f"<url><loc>{base_url}/</loc><priority>1.0</priority><changefreq>daily</changefreq></url>",
        f"<url><loc>{base_url}/catalogue</loc><priority>0.9</priority><changefreq>daily</changefreq></url>"
    ]
    for c in categories:
        urls.append(f"<url><loc>{base_url}/category/{c['slug']}</loc><priority>0.8</priority><changefreq>weekly</changefreq></url>")
    for p in products:
        urls.append(f"<url><loc>{base_url}/product/{p['slug']}</loc><priority>0.7</priority><changefreq>weekly</changefreq></url>")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(urls)}
</urlset>"""
    return FastAPIResponse(content=sitemap_content, media_type="application/xml")
