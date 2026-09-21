import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from app.db.connection import db

logger = logging.getLogger("sst.products")

def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return re.sub(r'^-+|-+$', '', text)

class ProductService:
    # ------------------ Public Catalogue ------------------
    @staticmethod
    def get_public_products(
        category_slug: Optional[str] = None,
        search_query: Optional[str] = None,
        availability: Optional[str] = None,
        is_featured: Optional[bool] = None,
        is_new_arrival: Optional[bool] = None,
        sort_by: str = "featured",
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Retrieves non-archived, non-hidden products for public catalogue."""
        conditions = ["p.is_archived = FALSE", "p.availability != 'hidden'"]
        params = []

        if category_slug:
            conditions.append("c.slug = %s")
            params.append(category_slug)

        if search_query:
            term = f"%{search_query.strip()}%"
            conditions.append("(p.name LIKE %s OR p.sku LIKE %s OR p.tags LIKE %s OR c.name LIKE %s)")
            params.extend([term, term, term, term])

        if availability:
            conditions.append("p.availability = %s")
            params.append(availability)

        if is_featured is not None:
            conditions.append("p.is_featured = %s")
            params.append(True if is_featured else False)

        if is_new_arrival is not None:
            conditions.append("p.is_new_arrival = %s")
            params.append(True if is_new_arrival else False)

        where_clause = " AND ".join(conditions)

        # Sorting
        order_clause = "p.is_featured DESC, p.created_at DESC"
        if sort_by == "newest":
            order_clause = "p.created_at DESC"
        elif sort_by == "name_asc":
            order_clause = "p.name ASC"
        elif sort_by == "name_desc":
            order_clause = "p.name DESC"
        elif sort_by == "moq_low":
            order_clause = "p.moq ASC"
        elif sort_by == "moq_high":
            order_clause = "p.moq DESC"

        query = f"""
            SELECT p.*, c.name as category_name, c.slug as category_slug,
                   (SELECT image_url FROM product_images WHERE product_id = p.id ORDER BY is_primary DESC, display_order ASC LIMIT 1) as primary_image_url
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE {where_clause}
            ORDER BY {order_clause}
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return db.fetch_all(query, params)

    @staticmethod
    def get_public_product_by_slug(slug: str) -> Optional[Dict[str, Any]]:
        """Fetches product detail, variants, and gallery for public display."""
        product = db.fetch_one("""
            SELECT p.*, c.name as category_name, c.slug as category_slug
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            WHERE p.slug = %s AND p.is_archived = FALSE AND p.availability != 'hidden'
        """, (slug,))
        if not product:
            return None

        # Fetch variants
        variants = db.fetch_all("""
            SELECT * FROM product_variants 
            WHERE product_id = %s AND is_active = TRUE
            ORDER BY id ASC
        """, (product["id"],))
        product["variants"] = variants

        # Fetch images
        images = db.fetch_all("""
            SELECT * FROM product_images 
            WHERE product_id = %s
            ORDER BY is_primary DESC, display_order ASC, id ASC
        """, (product["id"],))
        product["images"] = images
        product["primary_image_url"] = images[0]["image_url"] if images else "/static/images/placeholder.svg"
        return product

    @staticmethod
    def get_featured_products(limit: int = 8) -> List[Dict[str, Any]]:
        return ProductService.get_public_products(is_featured=True, limit=limit)

    @staticmethod
    def get_new_arrivals(limit: int = 8) -> List[Dict[str, Any]]:
        return ProductService.get_public_products(is_new_arrival=True, limit=limit)

    # ------------------ Admin Product Management ------------------
    @staticmethod
    def get_admin_products(search: Optional[str] = None, category_id: Optional[int] = None, status: Optional[str] = None, show_archived: bool = False) -> List[Dict[str, Any]]:
        conditions = []
        params = []
        if not show_archived:
            conditions.append("p.is_archived = FALSE")
        else:
            conditions.append("p.is_archived = TRUE")

        if search:
            term = f"%{search.strip()}%"
            conditions.append("(p.name LIKE %s OR p.sku LIKE %s OR c.name LIKE %s)")
            params.extend([term, term, term])

        if category_id:
            conditions.append("p.category_id = %s")
            params.append(category_id)

        if status:
            conditions.append("p.availability = %s")
            params.append(status)

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"""
            SELECT p.*, c.name as category_name,
                   (SELECT count(*) FROM product_variants WHERE product_id = p.id) as variant_count,
                   (SELECT count(*) FROM product_images WHERE product_id = p.id) as image_count,
                   (SELECT image_url FROM product_images WHERE product_id = p.id ORDER BY is_primary DESC, display_order ASC LIMIT 1) as primary_image_url
            FROM products p
            LEFT JOIN categories c ON p.category_id = c.id
            {where_clause}
            ORDER BY p.updated_at DESC
        """
        return db.fetch_all(query, params)

    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
        product = db.fetch_one("SELECT * FROM products WHERE id = %s", (product_id,))
        if not product:
            return None
        product["variants"] = db.fetch_all("SELECT * FROM product_variants WHERE product_id = %s ORDER BY id ASC", (product_id,))
        product["images"] = db.fetch_all("SELECT * FROM product_images WHERE product_id = %s ORDER BY is_primary DESC, display_order ASC", (product_id,))
        return product

    @staticmethod
    def create_product(data: Dict[str, Any]) -> int:
        slug = data.get("slug") or slugify(data["name"])
        # Ensure slug uniqueness
        existing_slug = db.fetch_one("SELECT id FROM products WHERE slug = %s", (slug,))
        if existing_slug:
            slug = f"{slug}-{data.get('sku', '').lower()}"

        product_id = db.execute("""
            INSERT INTO products (
                name, slug, sku, category_id, description, material, size_info,
                available_colours, moq, weight, dimensions, tags, availability,
                is_featured, is_new_arrival, is_archived, seo_title, seo_description
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s,
                %s, %s, FALSE, %s, %s
            )
        """, (
            data["name"], slug, data["sku"], data["category_id"], data.get("description", ""),
            data.get("material", ""), data.get("size_info", ""), data.get("available_colours", ""),
            data.get("moq", 1), data.get("weight", ""), data.get("dimensions", ""),
            data.get("tags", ""), data.get("availability", "in_stock"),
            bool(data.get("is_featured", False)), bool(data.get("is_new_arrival", False)),
            data.get("seo_title", ""), data.get("seo_description", "")
        ))

        # Add initial image if provided
        if data.get("initial_image_url"):
            db.execute("""
                INSERT INTO product_images (product_id, image_url, alt_text, display_order, is_primary)
                VALUES (%s, %s, %s, 1, TRUE)
            """, (product_id, data["initial_image_url"], data["name"]))

        return product_id

    @staticmethod
    def update_product(product_id: int, data: Dict[str, Any]) -> bool:
        slug = data.get("slug") or slugify(data["name"])
        # Check slug uniqueness excluding this product
        existing = db.fetch_one("SELECT id FROM products WHERE slug = %s AND id != %s", (slug, product_id))
        if existing:
            slug = f"{slug}-{data.get('sku', '').lower()}"

        db.execute("""
            UPDATE products SET
                name = %s, slug = %s, sku = %s, category_id = %s, description = %s,
                material = %s, size_info = %s, available_colours = %s, moq = %s,
                weight = %s, dimensions = %s, tags = %s, availability = %s,
                is_featured = %s, is_new_arrival = %s, seo_title = %s, seo_description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            data["name"], slug, data["sku"], data["category_id"], data.get("description", ""),
            data.get("material", ""), data.get("size_info", ""), data.get("available_colours", ""),
            data.get("moq", 1), data.get("weight", ""), data.get("dimensions", ""),
            data.get("tags", ""), data.get("availability", "in_stock"),
            bool(data.get("is_featured", False)), bool(data.get("is_new_arrival", False)),
            data.get("seo_title", ""), data.get("seo_description", ""),
            product_id
        ))
        return True

    @staticmethod
    def duplicate_product(product_id: int) -> Optional[int]:
        """Duplicates a product with its variants and images under a new SKU."""
        p = ProductService.get_product_by_id(product_id)
        if not p:
            return None
        new_sku = f"{p['sku']}-COPY"
        new_name = f"{p['name']} (Copy)"
        new_slug = f"{p['slug']}-copy"

        new_id = db.execute("""
            INSERT INTO products (
                name, slug, sku, category_id, description, material, size_info,
                available_colours, moq, weight, dimensions, tags, availability,
                is_featured, is_new_arrival, is_archived, seo_title, seo_description
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, 'hidden',
                FALSE, FALSE, FALSE, %s, %s
            )
        """, (
            new_name, new_slug, new_sku, p["category_id"], p["description"],
            p["material"], p["size_info"], p["available_colours"], p["moq"],
            p["weight"], p["dimensions"], p["tags"], p["seo_title"], p["seo_description"]
        ))

        # Copy variants
        for v in p["variants"]:
            db.execute("""
                INSERT INTO product_variants (product_id, size, colour, sku_suffix, variant_moq, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (new_id, v["size"], v["colour"], v["sku_suffix"], v["variant_moq"], v["is_active"]))

        # Copy images
        for img in p["images"]:
            db.execute("""
                INSERT INTO product_images (product_id, image_url, alt_text, display_order, is_primary)
                VALUES (%s, %s, %s, %s, %s)
            """, (new_id, img["image_url"], img["alt_text"], img["display_order"], img["is_primary"]))

        return new_id

    @staticmethod
    def archive_product(product_id: int):
        db.execute("UPDATE products SET is_archived = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (product_id,))

    @staticmethod
    def restore_product(product_id: int):
        db.execute("UPDATE products SET is_archived = FALSE, updated_at = CURRENT_TIMESTAMP WHERE id = %s", (product_id,))

    # ------------------ Variants & Images ------------------
    @staticmethod
    def add_variant(product_id: int, size: str, colour: str, sku_suffix: str = "", variant_moq: Optional[int] = None) -> int:
        return db.execute("""
            INSERT INTO product_variants (product_id, size, colour, sku_suffix, variant_moq, is_active)
            VALUES (%s, %s, %s, %s, %s, TRUE)
        """, (product_id, size.strip(), colour.strip(), sku_suffix.strip(), variant_moq))

    @staticmethod
    def delete_variant(variant_id: int):
        db.execute("DELETE FROM product_variants WHERE id = %s", (variant_id,))

    @staticmethod
    def add_image(product_id: int, image_url: str, alt_text: str = "", is_primary: bool = False) -> int:
        if is_primary:
            db.execute("UPDATE product_images SET is_primary = FALSE WHERE product_id = %s", (product_id,))
        count = db.fetch_one("SELECT count(*) as cnt FROM product_images WHERE product_id = %s", (product_id,))
        order = (count["cnt"] if count else 0) + 1
        return db.execute("""
            INSERT INTO product_images (product_id, image_url, alt_text, display_order, is_primary)
            VALUES (%s, %s, %s, %s, %s)
        """, (product_id, image_url, alt_text, order, is_primary))

    @staticmethod
    def delete_image(image_id: int):
        db.execute("DELETE FROM product_images WHERE id = %s", (image_id,))

    @staticmethod
    def set_primary_image(product_id: int, image_id: int):
        db.execute("UPDATE product_images SET is_primary = FALSE WHERE product_id = %s", (product_id,))
        db.execute("UPDATE product_images SET is_primary = TRUE WHERE id = %s AND product_id = %s", (image_id, product_id))

    # ------------------ Categories ------------------
    @staticmethod
    def get_categories(active_only: bool = True) -> List[Dict[str, Any]]:
        clause = "WHERE is_active = TRUE" if active_only else ""
        return db.fetch_all(f"""
            SELECT c.*, (SELECT count(*) FROM products WHERE category_id = c.id AND is_archived = FALSE) as product_count
            FROM categories c
            {clause}
            ORDER BY display_order ASC, name ASC
        """)

    @staticmethod
    def get_category_by_id(cat_id: int) -> Optional[Dict[str, Any]]:
        return db.fetch_one("SELECT * FROM categories WHERE id = %s", (cat_id,))

    @staticmethod
    def get_category_by_slug(slug: str) -> Optional[Dict[str, Any]]:
        return db.fetch_one("SELECT * FROM categories WHERE slug = %s", (slug,))

    @staticmethod
    def create_category(data: Dict[str, Any]) -> int:
        slug = data.get("slug") or slugify(data["name"])
        return db.execute("""
            INSERT INTO categories (name, slug, description, image_url, display_order, is_active, seo_title, seo_description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["name"], slug, data.get("description", ""), data.get("image_url", ""),
            data.get("display_order", 0), bool(data.get("is_active", True)),
            data.get("seo_title", ""), data.get("seo_description", "")
        ))

    @staticmethod
    def update_category(cat_id: int, data: Dict[str, Any]) -> bool:
        slug = data.get("slug") or slugify(data["name"])
        db.execute("""
            UPDATE categories SET
                name = %s, slug = %s, description = %s, image_url = %s,
                display_order = %s, is_active = %s, seo_title = %s, seo_description = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (
            data["name"], slug, data.get("description", ""), data.get("image_url", ""),
            data.get("display_order", 0), bool(data.get("is_active", True)),
            data.get("seo_title", ""), data.get("seo_description", ""),
            cat_id
        ))
        return True

    @staticmethod
    def delete_category(cat_id: int) -> Tuple[bool, str]:
        # Check if products exist in this category
        has_products = db.fetch_one("SELECT id FROM products WHERE category_id = %s", (cat_id,))
        if has_products:
            return False, "Cannot delete category containing existing products. Archive or reassign products first."
        db.execute("DELETE FROM categories WHERE id = %s", (cat_id,))
        return True, "Category deleted successfully."
