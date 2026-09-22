import logging
from typing import Dict, Any, List, Optional, Tuple
from app.db.connection import db
from app.config import settings

logger = logging.getLogger("sst.cms")

class CMSService:
    # ------------------ Website Settings ------------------
    @staticmethod
    def get_settings() -> Dict[str, str]:
        """Returns all website settings as a simple key-value dictionary."""
        rows = db.fetch_all("SELECT key, value FROM website_settings")
        data = {r["key"]: r["value"] for r in rows}
        # APP_URL is deployment configuration, not editable CMS content.
        data["app_url"] = settings.APP_URL
        return data

    @staticmethod
    def update_settings(updates: Dict[str, str]):
        for k, v in updates.items():
            db.execute("""
                INSERT INTO website_settings (key, value, updated_at)
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value, updated_at = CURRENT_TIMESTAMP
            """, (k, v))

    # ------------------ Homepage Sections ------------------
    @staticmethod
    def get_homepage_sections(enabled_only: bool = True) -> Dict[str, Dict[str, Any]]:
        clause = "WHERE is_enabled = TRUE" if enabled_only else ""
        rows = db.fetch_all(f"SELECT * FROM homepage_sections {clause} ORDER BY display_order ASC")
        return {r["section_key"]: dict(r) for r in rows}

    @staticmethod
    def update_homepage_section(section_key: str, data: Dict[str, Any]):
        db.execute("""
            UPDATE homepage_sections SET
                title = %s, subtitle = %s, content = %s,
                cta_label = %s, cta_url = %s, image_url = %s,
                is_enabled = %s, display_order = %s, updated_at = CURRENT_TIMESTAMP
            WHERE section_key = %s
        """, (
            data.get("title", ""), data.get("subtitle", ""), data.get("content", ""),
            data.get("cta_label", ""), data.get("cta_url", ""), data.get("image_url", ""),
            bool(data.get("is_enabled", True)), int(data.get("display_order", 0)),
            section_key
        ))

    # ------------------ Social Links ------------------
    @staticmethod
    def get_social_links(enabled_only: bool = True) -> List[Dict[str, Any]]:
        clause = "WHERE is_enabled = TRUE" if enabled_only else ""
        return db.fetch_all(f"SELECT * FROM social_links {clause} ORDER BY display_order ASC, name ASC")

    @staticmethod
    def create_social_link(platform: str, name: str, url: str, icon: str = "", display_order: int = 0, is_enabled: bool = True) -> int:
        return db.execute("""
            INSERT INTO social_links (platform, name, url, icon, is_enabled, display_order)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (platform, name, url, icon, is_enabled, display_order))

    @staticmethod
    def update_social_link(link_id: int, platform: str, name: str, url: str, icon: str = "", display_order: int = 0, is_enabled: bool = True):
        db.execute("""
            UPDATE social_links SET
                platform = %s, name = %s, url = %s, icon = %s,
                display_order = %s, is_enabled = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (platform, name, url, icon, display_order, is_enabled, link_id))

    @staticmethod
    def delete_social_link(link_id: int):
        db.execute("DELETE FROM social_links WHERE id = %s", (link_id,))

    # ------------------ FAQs ------------------
    @staticmethod
    def get_faqs(active_only: bool = True) -> List[Dict[str, Any]]:
        clause = "WHERE is_active = TRUE" if active_only else ""
        return db.fetch_all(f"SELECT * FROM faqs {clause} ORDER BY display_order ASC, id ASC")

    @staticmethod
    def create_faq(question: str, answer: str, display_order: int = 0, is_active: bool = True) -> int:
        return db.execute("""
            INSERT INTO faqs (question, answer, display_order, is_active)
            VALUES (%s, %s, %s, %s)
        """, (question, answer, display_order, is_active))

    @staticmethod
    def update_faq(faq_id: int, question: str, answer: str, display_order: int = 0, is_active: bool = True):
        db.execute("""
            UPDATE faqs SET
                question = %s, answer = %s, display_order = %s,
                is_active = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (question, answer, display_order, is_active, faq_id))

    @staticmethod
    def delete_faq(faq_id: int):
        db.execute("DELETE FROM faqs WHERE id = %s", (faq_id,))

    # ------------------ Admin Customer Management ------------------
    @staticmethod
    def get_customers(search: Optional[str] = None, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        conditions = []
        params = []
        if search:
            term = f"%{search.strip()}%"
            conditions.append("(name LIKE %s OR email LIKE %s OR mobile LIKE %s)")
            params.extend([term, term, term])

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"""
            SELECT c.*, 
                   (SELECT count(*) FROM enquiries WHERE customer_id = c.id) as enquiry_count
            FROM customers c
            {where_clause}
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return db.fetch_all(query, params)

    @staticmethod
    def get_customer_by_id(customer_id: str) -> Optional[Dict[str, Any]]:
        customer = db.fetch_one("SELECT * FROM customers WHERE id = %s", (customer_id,))
        if customer:
            customer["enquiries"] = db.fetch_all("""
                SELECT * FROM enquiries WHERE customer_id = %s ORDER BY created_at DESC
            """, (customer_id,))
        return customer

    @staticmethod
    def set_customer_status(customer_id: str, status: str):
        if status in ('active', 'disabled'):
            db.execute("UPDATE customers SET status = %s WHERE id = %s", (status, customer_id))

    # ------------------ Admin Dashboard Metrics ------------------
    @staticmethod
    def get_dashboard_metrics() -> Dict[str, Any]:
        tot_products = db.fetch_one("SELECT count(*) as cnt FROM products WHERE is_archived = FALSE")["cnt"]
        active_products = db.fetch_one("SELECT count(*) as cnt FROM products WHERE is_archived = FALSE AND availability = 'in_stock'")["cnt"]
        out_of_stock = db.fetch_one("SELECT count(*) as cnt FROM products WHERE is_archived = FALSE AND availability = 'out_of_stock'")["cnt"]
        categories_cnt = db.fetch_one("SELECT count(*) as cnt FROM categories WHERE is_active = TRUE")["cnt"]
        customers_cnt = db.fetch_one("SELECT count(*) as cnt FROM customers")["cnt"]
        
        tot_enquiries = db.fetch_one("SELECT count(*) as cnt FROM enquiries")["cnt"]
        new_enquiries = db.fetch_one("SELECT count(*) as cnt FROM enquiries WHERE status = 'new'")["cnt"]
        pending_enquiries = db.fetch_one("SELECT count(*) as cnt FROM enquiries WHERE status IN ('new', 'contacted', 'quotation_sent')")["cnt"]
        
        recent_enquiries = db.fetch_all("SELECT * FROM enquiries ORDER BY created_at DESC LIMIT 5")
        recent_customers = db.fetch_all("SELECT * FROM customers ORDER BY created_at DESC LIMIT 5")
        
        return {
            "total_products": tot_products,
            "active_products": active_products,
            "out_of_stock_products": out_of_stock,
            "categories_count": categories_cnt,
            "customers_count": customers_cnt,
            "total_enquiries": tot_enquiries,
            "new_enquiries": new_enquiries,
            "pending_enquiries": pending_enquiries,
            "recent_enquiries": recent_enquiries,
            "recent_customers": recent_customers,
            "db_status": "Connected (" + ("PostgreSQL" if db.is_postgres else "SQLite") + ")"
        }
