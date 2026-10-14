import datetime
from typing import List, Dict, Any, Optional

def _pdf_escape(text: str) -> str:
    """Escapes text for standard PDF Type1 Helvetica strings."""
    if not text:
        return ""
    clean = (
        str(text)
        .replace("•", "-")
        .replace("—", "-")
        .replace("–", "-")
        .replace("’", "'")
        .replace("“", '"')
        .replace("”", '"')
    )
    # Keep printable ASCII
    clean = "".join(ch if 32 <= ord(ch) <= 126 else " " for ch in clean)
    return clean.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

class PDFCatalogueService:
    @staticmethod
    def generate_catalogue_pdf(
        products: List[Dict[str, Any]],
        categories: List[Dict[str, Any]],
        settings: Dict[str, Any],
        selected_category: Optional[str] = None
    ) -> bytes:
        """
        Generates a multi-page branded B2B Wholesale Catalogue PDF (A4 portrait: 595 x 842 pt)
        using 100% pure Python (zero external C/system library dependencies for Render reliability).
        """
        business_name = settings.get("business_name") or "Shree Shyam Toys"
        address = settings.get("address") or "Delhi, India"
        whatsapp = settings.get("whatsapp_number") or settings.get("phone") or "Connect via Website Enquiry"
        email = settings.get("email") or "contact@shreeshyamtoys.com"
        app_url = settings.get("app_url") or "https://shree-shyam-toys.onrender.com"
        today_str = datetime.date.today().strftime("%d %b %Y")

        # Group products or list sequentially, 10 products per page
        items_per_page = 10
        chunks = [products[i:i + items_per_page] for i in range(0, max(len(products), 1), items_per_page)]
        total_pages = len(chunks)

        page_streams: List[bytes] = []

        for page_idx, page_items in enumerate(chunks, 1):
            ops = []

            # Top Caramel Header Banner (rect: x=30, y=755, w=535, h=62)
            ops.append("0.545 0.271 0.075 rg")
            ops.append("30 755 535 62 re f")

            # Header Title & Subtitle in White
            ops.append("BT /F2 16 Tf 1 1 1 rg 44 794 Td ({}) Tj ET".format(
                _pdf_escape(f"{business_name.upper()} - B2B WHOLESALE CATALOGUE")
            ))
            sub_hdr = f"Date: {today_str}  |  Location: {address}  |  WhatsApp Desk: {whatsapp}  |  Email: {email}"
            ops.append("BT /F1 8.5 Tf 0.98 0.92 0.84 rg 44 777 Td ({}) Tj ET".format(_pdf_escape(sub_hdr[:105])))
            ops.append("BT /F1 8 Tf 0.98 0.92 0.84 rg 44 764 Td ({}) Tj ET".format(
                _pdf_escape(f"Live Interactive Catalogue & Bulk Quotation Portal: {app_url}   (Page {page_idx} of {total_pages})")
            ))

            # Table Column Header Bar (y=726, h=22)
            ops.append("0.96 0.93 0.90 rg")
            ops.append("30 726 535 22 re f")
            ops.append("0.16 0.11 0.08 rg")
            ops.append("BT /F2 8.5 Tf 38 734 Td (SKU CODE) Tj ET")
            ops.append("BT /F2 8.5 Tf 105 734 Td (PRODUCT NAME & CATEGORY) Tj ET")
            ops.append("BT /F2 8.5 Tf 285 734 Td (SIZES & COLOURS) Tj ET")
            ops.append("BT /F2 8.5 Tf 430 734 Td (MOQ LOT) Tj ET")
            ops.append("BT /F2 8.5 Tf 490 734 Td (CARTON PACK) Tj ET")

            y = 664
            for row_idx, p in enumerate(page_items):
                # Alternating card background
                if row_idx % 2 == 0:
                    ops.append("0.992 0.984 0.976 rg")
                else:
                    ops.append("1 1 1 rg")
                ops.append(f"30 {y} 535 56 re f")

                # Border line
                ops.append("0.90 0.86 0.82 RG 0.6 w")
                ops.append(f"30 {y} 535 56 re S")

                sku = _pdf_escape(p.get("sku") or "")
                name = _pdf_escape((p.get("name") or "")[:34])
                cat = _pdf_escape((p.get("category_name") or "Plush Collection")[:32])
                scale_lbl = _pdf_escape((p.get("size_scale_label") or "")[:42])
                sizes = _pdf_escape((p.get("size_info") or "Standard")[:28])
                colours = _pdf_escape((p.get("available_colours") or "Assorted")[:28])
                moq = int(p.get("moq") or 20)
                carton = int(p.get("effective_carton_qty") or (moq * 3))
                status_str = "IN STOCK" if p.get("availability") == "in_stock" else "COMING SOON"

                # SKU & Status
                ops.append("0.545 0.271 0.075 rg")
                ops.append(f"BT /F2 8.5 Tf 38 {y + 36} Td ({sku}) Tj ET")
                ops.append("0.42 0.36 0.32 rg")
                ops.append(f"BT /F1 7.5 Tf 38 {y + 22} Td ({_pdf_escape(status_str)}) Tj ET")

                # Name, Category & Scale
                ops.append("0.15 0.10 0.07 rg")
                ops.append(f"BT /F2 9.5 Tf 105 {y + 36} Td ({name}) Tj ET")
                ops.append("0.45 0.36 0.31 rg")
                ops.append(f"BT /F1 8 Tf 105 {y + 23} Td (Category: {cat}) Tj ET")
                ops.append(f"BT /F1 7.5 Tf 105 {y + 11} Td ({scale_lbl}) Tj ET")

                # Sizes & Colours
                ops.append("0.20 0.15 0.12 rg")
                ops.append(f"BT /F1 8 Tf 285 {y + 34} Td (Sizes: {sizes}) Tj ET")
                ops.append(f"BT /F1 8 Tf 285 {y + 20} Td (Colours: {colours}) Tj ET")

                # MOQ & Carton Tier
                ops.append("0.36 0.13 0.71 rg")
                ops.append(f"BT /F2 9 Tf 430 {y + 32} Td ({moq} pcs) Tj ET")
                ops.append("0.45 0.36 0.31 rg")
                ops.append(f"BT /F1 7.5 Tf 430 {y + 19} Td (Min Order) Tj ET")

                ops.append("0.02 0.58 0.40 rg")
                ops.append(f"BT /F2 9 Tf 490 {y + 32} Td ({carton} pcs) Tj ET")
                ops.append("0.45 0.36 0.31 rg")
                ops.append(f"BT /F1 7.5 Tf 490 {y + 19} Td (Full Carton) Tj ET")

                y -= 62

            # Footer Note Box
            ops.append("0.96 0.93 0.90 rg")
            ops.append("30 28 535 34 re f")
            ops.append("0.30 0.20 0.15 rg")
            ops.append(
                "BT /F2 8 Tf 40 47 Td ({}) Tj ET".format(
                    _pdf_escape("HOW TO ORDER BULK: 1. Visit Online Catalogue  2. Add Items / Full Cartons to Enquiry Bag  3. Submit Direct to WhatsApp (No Login Needed)")
                )
            )
            ops.append(
                "BT /F1 7.5 Tf 40 35 Td ({}) Tj ET".format(
                    _pdf_escape("Note: Wholesale quotations are customized based on order volume (MOQ Lot vs Full Carton vs Distributor Bulk Tier) and delivery city.")
                )
            )

            page_streams.append("\n".join(ops).encode("latin-1", errors="replace"))

        # Assemble standard PDF 1.4 document
        objects: List[bytes] = []

        # Object 1: Catalog
        objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
        # Object 2: Pages (placeholder, updated below)
        objects.append(b"")
        # Object 3: Font F1 (Helvetica)
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        # Object 4: Font F2 (Helvetica-Bold)
        objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        page_obj_Method_ids = []
        for stream_bytes in page_streams:
            content_obj_id = len(objects) + 1
            stream_obj = (
                f"<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
                + stream_bytes
                + b"\nendstream"
            )
            objects.append(stream_obj)

            page_obj_id = len(objects) + 1
            page_obj_Method_ids.append(page_obj_id)
            page_dict = (
                f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
                f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
                f"/Contents {content_obj_id} 0 R >>"
            ).encode("ascii")
            objects.append(page_dict)

        kids_str = " ".join(f"{pid} 0 R" for pid in page_obj_Method_ids)
        objects[1] = f"<< /Type /Pages /Kids [{kids_str}] /Count {len(page_obj_Method_ids)} >>".encode("ascii")

        # Serialize PDF with xref table
        out = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for idx, obj_body in enumerate(objects, 1):
            offsets.append(len(out))
            out.extend(f"{idx} 0 obj\n".encode("ascii"))
            out.extend(obj_body)
            out.extend(b"\nendobj\n")

        xref_pos = len(out)
        out.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
        out.extend(b"0000000000 65535 f \n")
        for off in offsets[1:]:
            out.extend(f"{off:010d} 00000 n \n".encode("ascii"))

        out.extend(
            f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF\n".encode("ascii")
        )
        return bytes(out)
