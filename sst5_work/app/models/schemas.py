from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, EmailStr

# Customer Schemas
class CustomerBase(BaseModel):
    name: str
    email: str
    mobile: Optional[str] = None
    avatar_url: Optional[str] = None

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None

# Product & Variant Schemas
class ProductVariantSchema(BaseModel):
    id: Optional[int] = None
    size: str
    colour: str
    sku_suffix: Optional[str] = ""
    variant_moq: Optional[int] = None
    is_active: bool = True

class ProductCreateUpdate(BaseModel):
    name: str
    slug: Optional[str] = None
    sku: str
    category_id: int
    description: Optional[str] = ""
    material: Optional[str] = ""
    size_info: Optional[str] = ""
    available_colours: Optional[str] = ""
    moq: int = Field(default=1, ge=1)
    weight: Optional[str] = ""
    dimensions: Optional[str] = ""
    tags: Optional[str] = ""
    availability: str = Field(default="in_stock")  # in_stock, out_of_stock, coming_soon, hidden
    is_featured: bool = False
    is_new_arrival: bool = False
    seo_title: Optional[str] = ""
    seo_description: Optional[str] = ""
    variants: Optional[List[ProductVariantSchema]] = []

# Category Schemas
class CategoryCreateUpdate(BaseModel):
    name: str
    slug: Optional[str] = None
    description: Optional[str] = ""
    image_url: Optional[str] = ""
    display_order: int = 0
    is_active: bool = True
    seo_title: Optional[str] = ""
    seo_description: Optional[str] = ""

# Enquiry Schemas
class EnquiryItemInput(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    selected_size: Optional[str] = ""
    selected_colour: Optional[str] = ""
    quantity: int = Field(..., ge=1)

class EnquiryCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_mobile: str
    notes: Optional[str] = ""
    items: List[EnquiryItemInput]

class EnquiryStatusUpdate(BaseModel):
    status: str  # new, contacted, quotation_sent, confirmed, completed, cancelled
    notes: Optional[str] = None

# Website Settings & CMS
class SettingUpdate(BaseModel):
    settings: Dict[str, str]

class FAQCreateUpdate(BaseModel):
    question: str
    answer: str
    display_order: int = 0
    is_active: bool = True

class SocialLinkCreateUpdate(BaseModel):
    platform: str
    name: str
    url: str
    icon: Optional[str] = ""
    is_enabled: bool = True
    display_order: int = 0
