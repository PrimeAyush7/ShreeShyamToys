import datetime
import urllib.parse
import logging
from typing import List, Dict, Any, Tuple, Optional
from app.db.connection import db
from app.config import settings

logger = logging.getLogger("sst.enquiries")

class EnquiryService:
    @staticmethod
    def validate_and_calculate_items(items: List[Dict[str, Any]]) -> Tuple[bool, List[Dict[str, Any]], Optional[str]]:
        """
        Validates that:
        1. At least one item is in the enquiry.
        2. Each item references an existing, non-archived product.
        3. Each item meets or exceeds the product's or variant's MOQ.
        Returns: (is_valid, processed_items_with_snapshots, error_message)
        """
        if not items:
            return False, [], "Your enquiry list is currently empty. Please add products to enquire."

        processed_items = []
        for idx, item in enumerate(items, 1):
            product_id = item.get("product_id")
            qty = int(item.get("quantity", 0))

            product = db.fetch_one("""
                SELECT p.*, c.name as category_name 
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = %s AND p.is_archived = FALSE
            """, (product_id,))

            if not product:
                return False, [], f"Product ID {product_id} is unavailable or archived."

            # Determine MOQ (variant MOQ if set, otherwise product MOQ)
            effective_moq = product["moq"]
            variant_id = item.get("variant_id")
            selected_size = item.get("selected_size") or ""
            selected_colour = item.get("selected_colour") or ""

            if variant_id:
                variant = db.fetch_one("SELECT * FROM product_variants WHERE id = %s AND product_id = %s", (variant_id, product_id))
                if variant:
                    if variant.get("variant_moq"):
                        effective_moq = variant["variant_moq"]
                    if not selected_size:
                        selected_size = variant["size"]
                    if not selected_colour:
                        selected_colour = variant["colour"]

            # Strict MOQ validation
            if qty < effective_moq:
                return False, [], f"Minimum order quantity for '{product['name']}' is {effective_moq} pieces (you entered {qty})."

            processed_items.append({
                "product_id": product["id"],
                "product_name": product["name"],
                "sku": product["sku"],
                "category_name": product.get("category_name") or "General Plush",
                "selected_size": selected_size,
                "selected_colour": selected_colour,
                "quantity": qty,
                "moq_at_enquiry": effective_moq
            })

        return True, processed_items, None

    @staticmethod
    def generate_whatsapp_message(
        customer_name: str,
        customer_mobile: str,
        customer_email: str,
        items: List[Dict[str, Any]],
        notes: str = ""
    ) -> str:
        """Generates cleanly structured, professional wholesale enquiry message."""
        lines = [
            "Hello Shree Shyam Toys,",
            "I would like to enquire about the following wholesale products:\n"
        ]

        for i, itm in enumerate(items, 1):
            lines.append(f"• {itm['product_name']}")
            lines.append(f"  SKU: {itm['sku']}")
            if itm.get('selected_size'):
                lines.append(f"  Size: {itm['selected_size']}")
            if itm.get('selected_colour'):
                lines.append(f"  Colour: {itm['selected_colour']}")
            lines.append(f"  Quantity: {itm['quantity']} pcs (MOQ: {itm['moq_at_enquiry']})\n")

        lines.append("Customer Details:")
        lines.append(f"Name: {customer_name}")
        lines.append(f"Mobile: {customer_mobile}")
        lines.append(f"Email: {customer_email}")
        
        if notes and notes.strip():
            lines.append(f"Notes: {notes.strip()}")

        lines.append("\nPlease share availability and wholesale quotation.")
        lines.append("Thank you.")
        return "\n".join(lines)

    @staticmethod
    def create_enquiry(
        customer_id: str,
        customer_name: str,
        customer_email: str,
        customer_mobile: str,
        raw_items: List[Dict[str, Any]],
        notes: str = ""
    ) -> Tuple[bool, Dict[str, Any], Optional[str]]:
        """
        Creates enquiry record in database FIRST.
        Then formats WhatsApp message and URL.
        Returns: (success, result_dict, error_msg)
        """
        # Validate customer details
        if not customer_mobile or len(customer_mobile.strip()) < 8:
            return False, {}, "A valid mobile contact number is mandatory for wholesale enquiries."
        if not customer_name or not customer_name.strip():
            return False, {}, "Customer name is required."
        if not customer_email or not customer_email.strip():
            return False, {}, "Customer email is required."

        # Validate items and MOQ
        is_valid, processed_items, err_msg = EnquiryService.validate_and_calculate_items(raw_items)
        if not is_valid:
            return False, {}, err_msg

        # Update customer record's mobile if not set or changed
        db.execute("""
            UPDATE customers 
            SET mobile = %s, last_activity_at = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (customer_mobile.strip(), customer_id))

        # Generate unique reference e.g. SST-ENQ-2026-XXXX
        year = datetime.datetime.now().year
        count_res = db.fetch_one("SELECT count(*) as cnt FROM enquiries")
        next_num = (count_res["cnt"] if count_res else 0) + 1
        ref = f"SST-ENQ-{year}-{next_num:04d}"

        # Generate WhatsApp message
        whatsapp_msg = EnquiryService.generate_whatsapp_message(
            customer_name=customer_name,
            customer_mobile=customer_mobile,
            customer_email=customer_email,
            items=processed_items,
            notes=notes
        )

        # 1. SAVE TO DATABASE FIRST
        enquiry_id = db.execute("""
            INSERT INTO enquiries (
                enquiry_reference, customer_id, customer_name, customer_email,
                customer_mobile, status, notes, whatsapp_message
            ) VALUES (%s, %s, %s, %s, %s, 'new', %s, %s)
        """, (ref, customer_id, customer_name, customer_email, customer_mobile, notes, whatsapp_msg))

        # Save snapshot items
        for itm in processed_items:
            db.execute("""
                INSERT INTO enquiry_items (
                    enquiry_id, product_id, product_name, sku, category_name,
                    selected_size, selected_colour, quantity, moq_at_enquiry
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                enquiry_id, itm["product_id"], itm["product_name"], itm["sku"],
                itm["category_name"], itm["selected_size"], itm["selected_colour"],
                itm["quantity"], itm["moq_at_enquiry"]
            ))

        # Retrieve configured WhatsApp number from settings or environment (NO fake fallback)
        setting = db.fetch_one("SELECT value FROM website_settings WHERE key = 'whatsapp_number'")
        raw_number = ((setting["value"] if (setting and setting.get("value")) else "") or settings.WHATSAPP_NUMBER or "").strip()
        clean_number = "".join(filter(str.isdigit, raw_number))
        # WhatsApp wa.me requires an international number without +, spaces, or 0-prefix.
        # This site is India-focused, so a 10-digit Indian mobile is normalized to +91.
        if len(clean_number) == 10:
            clean_number = "91" + clean_number
        elif clean_number.startswith("0") and len(clean_number) == 11:
            clean_number = "91" + clean_number[1:]

        if clean_number and len(clean_number) >= 11:
            encoded_text = urllib.parse.quote(whatsapp_msg)
            whatsapp_url = f"https://wa.me/{clean_number}?text={encoded_text}"
        else:
            whatsapp_url = None

        enquiry_record = db.fetch_one("SELECT * FROM enquiries WHERE id = %s", (enquiry_id,))
        enquiry_record["items"] = processed_items
        enquiry_record["whatsapp_url"] = whatsapp_url

        return True, enquiry_record, None

    @staticmethod
    def get_customer_enquiries(customer_id: str) -> List[Dict[str, Any]]:
        """Fetches enquiries for a specific logged-in customer."""
        enquiries = db.fetch_all("""
            SELECT * FROM enquiries 
            WHERE customer_id = %s 
            ORDER BY created_at DESC
        """, (customer_id,))
        for enq in enquiries:
            enq["enquiry_items"] = enq["items"] = db.fetch_all("""
                SELECT * FROM enquiry_items WHERE enquiry_id = %s ORDER BY id ASC
            """, (enq["id"],))
        return enquiries

    @staticmethod
    def get_admin_enquiries(
        status: Optional[str] = None,
        search: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        conditions = []
        params = []

        if status:
            conditions.append("e.status = %s")
            params.append(status)

        if search:
            term = f"%{search.strip()}%"
            conditions.append("(e.enquiry_reference LIKE %s OR e.customer_name LIKE %s OR e.customer_email LIKE %s OR e.customer_mobile LIKE %s)")
            params.extend([term, term, term, term])

        where_clause = "WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"""
            SELECT e.*, 
                   (SELECT count(*) FROM enquiry_items WHERE enquiry_id = e.id) as item_count,
                   (SELECT sum(quantity) FROM enquiry_items WHERE enquiry_id = e.id) as total_quantity
            FROM enquiries e
            {where_clause}
            ORDER BY e.created_at DESC
            LIMIT %s OFFSET %s
        """
        params.extend([limit, offset])
        return db.fetch_all(query, params)

    @staticmethod
    def get_enquiry_detail(enquiry_id: int) -> Optional[Dict[str, Any]]:
        enquiry = db.fetch_one("SELECT * FROM enquiries WHERE id = %s", (enquiry_id,))
        if not enquiry:
            return None
        enquiry["enquiry_items"] = enquiry["items"] = db.fetch_all("SELECT * FROM enquiry_items WHERE enquiry_id = %s ORDER BY id ASC", (enquiry_id,))
        return enquiry

    @staticmethod
    def update_enquiry_status(enquiry_id: int, new_status: str, notes: Optional[str] = None) -> bool:
        valid_statuses = ['new', 'contacted', 'quotation_sent', 'confirmed', 'completed', 'cancelled']
        if new_status not in valid_statuses:
            return False
        
        if notes is not None:
            db.execute("""
                UPDATE enquiries 
                SET status = %s, notes = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_status, notes, enquiry_id))
        else:
            db.execute("""
                UPDATE enquiries 
                SET status = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (new_status, enquiry_id))
        return True
