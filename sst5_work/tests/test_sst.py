import uuid
import os
import sys
import unittest
import zipfile
import io
import re
from unittest.mock import patch

# Setup path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import app
from app.config import settings, Settings
from app.main import app as fastapi_app
from app.db.connection import db, Database
from app.db.migrations import run_migrations
from app.services.storage_service import StorageService
from app.services.enquiry_service import EnquiryService
from starlette.testclient import TestClient

class TestShreeShyamToys(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        run_migrations()
        # Seed catalogue records are hidden by default; expose them only inside the test database.
        db.execute("UPDATE products SET availability = 'in_stock' WHERE id BETWEEN 1 AND 12")
        cls.client = TestClient(fastapi_app)

    def test_01_public_pages(self):
        """Test public endpoints: Home, Catalogue, Detail, Robots, Sitemap."""
        # Homepage
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        self.assertIn("Shree Shyam Toys", res_home.text)
        self.assertIn("Wholesale", res_home.text)

        # Catalogue
        res_cat = self.client.get("/catalogue")
        self.assertEqual(res_cat.status_code, 200)
        self.assertIn("Heritage Cuddle Teddy Bear", res_cat.text)

        # Category Filter
        res_filter = self.client.get("/catalogue?category=classic-teddy-bears")
        self.assertEqual(res_filter.status_code, 200)
        self.assertIn("Classic Teddy Bears", res_filter.text)

        # Search
        res_search = self.client.get("/catalogue?q=Panda")
        self.assertEqual(res_search.status_code, 200)
        self.assertIn("Gentle Giant Panda Plush", res_search.text)

        # Product Detail
        res_detail = self.client.get("/product/heritage-cuddle-teddy-bear")
        self.assertEqual(res_detail.status_code, 200)
        self.assertIn("Heritage Cuddle Teddy Bear", res_detail.text)
        self.assertIn("SST-TB-101", res_detail.text)
        self.assertIn("Enquire for Wholesale Details", res_detail.text)

        # Robots.txt
        res_robots = self.client.get("/robots.txt")
        self.assertEqual(res_robots.status_code, 200)
        self.assertIn("Disallow: /admin/", res_robots.text)

        # Sitemap.xml
        res_sitemap = self.client.get("/sitemap.xml")
        self.assertEqual(res_sitemap.status_code, 200)
        self.assertIn("heritage-cuddle-teddy-bear", res_sitemap.text)

    def test_02_pricing_policy_and_fake_claims(self):
        """Verify that NO public retail/wholesale currency prices or unverified claims are exposed."""
        res_home = self.client.get("/")
        self.assertNotIn("₹", res_home.text)
        self.assertNotIn("Rs.", res_home.text)
        self.assertNotIn("India's No.1", res_home.text)
        self.assertNotIn("largest supplier", res_home.text)
        self.assertNotIn("pan-India delivery", res_home.text)
        self.assertNotIn("hypoallergenic", res_home.text.lower())
        self.assertNotIn("919876543210", res_home.text)
        self.assertNotIn("production facility caters", res_home.text.lower())
        self.assertNotIn("virgin siliconized", res_home.text.lower())
        self.assertNotIn("engineered for retail", res_home.text.lower())
        self.assertNotIn("carefully assembled stitching", res_home.text.lower())
        self.assertNotIn("fresh production lines", res_home.text.lower())
        self.assertNotIn("commercial volume allocation", res_home.text.lower())

        res_cat = self.client.get("/catalogue")
        self.assertNotIn("custom production enquiries", res_cat.text.lower())
        self.assertNotIn("₹", res_cat.text)
        self.assertNotIn("Rs.", res_cat.text)
        self.assertNotIn("919876543210", res_cat.text)

        res_detail = self.client.get("/product/heritage-cuddle-teddy-bear")
        self.assertNotIn("₹", res_detail.text)
        self.assertNotIn("Rs.", res_detail.text)
        self.assertNotIn("919876543210", res_detail.text)
        self.assertNotIn("virgin siliconized", res_detail.text.lower())
        self.assertNotIn("export corrugated", res_detail.text.lower())
        self.assertNotIn("anti-allergic", res_detail.text.lower())

    def test_03_customer_auth_and_profile(self):
        """Test customer login, session handling, and mobile update."""
        login_res = self.client.post("/auth/test-login?email=buyer_delhi@example.com&name=Vikram+Singh&role=customer", follow_redirects=False)
        self.assertEqual(login_res.status_code, 303)
        cookie = login_res.headers.get("set-cookie")
        self.assertIsNotNone(cookie)

        # View Profile
        res_prof = self.client.get("/customer/profile", headers={"Cookie": cookie})
        self.assertEqual(res_prof.status_code, 200)
        self.assertIn("Vikram Singh", res_prof.text)

        # Update Mobile
        res_upd = self.client.post("/customer/profile", data={"name": "Vikram Singh", "mobile": "+91 98111 22334"}, headers={"Cookie": cookie}, follow_redirects=False)
        self.assertEqual(res_upd.status_code, 303)

        # Verify update
        res_prof2 = self.client.get("/customer/profile", headers={"Cookie": cookie})
        self.assertIn("98111 22334", res_prof2.text)

        # Verify Google OAuth / login redirect safety
        res_evil = self.client.post("/auth/test-login?email=buyer_delhi@example.com&role=customer&redirect=https://evil.com", follow_redirects=False)
        self.assertEqual(res_evil.status_code, 303)
        self.assertEqual(res_evil.headers.get("Location"), "/")

        res_proto_rel = self.client.post("/auth/test-login?email=buyer_delhi@example.com&role=customer&redirect=//attacker.com", follow_redirects=False)
        self.assertEqual(res_proto_rel.status_code, 303)
        self.assertEqual(res_proto_rel.headers.get("Location"), "/")

        res_safe = self.client.post("/auth/test-login?email=buyer_delhi@example.com&role=customer&redirect=/catalogue", follow_redirects=False)
        self.assertEqual(res_safe.status_code, 303)
        self.assertEqual(res_safe.headers.get("Location"), "/catalogue")

    def test_04_moq_validation_and_enquiry_creation(self):
        """Test strict item-level MOQ validation and DB-first WhatsApp enquiry saving."""
        fresh_client = TestClient(fastapi_app)
        login_res = fresh_client.post("/auth/test-login?email=wholesale_buyer@toyhub.in&name=Rajesh+Kumar&role=customer", follow_redirects=False)
        cookie = login_res.headers.get("set-cookie")

        # 1. Invalid Quantity (MOQ is 30, customer enters 15) -> MUST FAIL
        bad_payload = {
            "customer_mobile": "+91 99999 88888",
            "items": [{"product_id": 1, "quantity": 15}]
        }
        res_fail = fresh_client.post("/api/enquiry/submit", json=bad_payload, headers={"Cookie": cookie})
        self.assertEqual(res_fail.status_code, 400)
        self.assertIn("Minimum order quantity", res_fail.json()["detail"])

        # 2. Missing Mobile -> MUST FAIL
        bad_mobile_payload = {
            "customer_mobile": "",
            "items": [{"product_id": 1, "quantity": 30}]
        }
        res_no_mobile = fresh_client.post("/api/enquiry/submit", json=bad_mobile_payload, headers={"Cookie": cookie})
        self.assertEqual(res_no_mobile.status_code, 400)
        self.assertIn("valid mobile number", res_no_mobile.json()["detail"].lower())

        # 3. Valid Multi-Product Wholesale Enquiry
        good_payload = {
            "customer_name": "Rajesh Kumar (ToyHub)",
            "customer_email": "wholesale_buyer@toyhub.in",
            "customer_mobile": "+91 99999 88888",
            "notes": "Bulk supply quotation for 3 retail branches in Delhi NCR.",
            "items": [
                {"product_id": 1, "quantity": 60, "selected_size": "60 CM", "selected_colour": "Classic Brown"},
                {"product_id": 4, "quantity": 25, "selected_size": "35 CM", "selected_colour": "Black & White Natural"}
            ]
        }
        res_ok = fresh_client.post("/api/enquiry/submit", json=good_payload, headers={"Cookie": cookie})
        self.assertEqual(res_ok.status_code, 200)
        data = res_ok.json()
        self.assertTrue(data["success"])
        ref = data["enquiry_reference"]
        self.assertTrue(ref.startswith("SST-ENQ-"))
        self.assertIn("ToyHub", data["whatsapp_message"])

        # 4. Verify DB Persistence & Snapshot Isolation
        db_enq = db.fetch_one("SELECT * FROM enquiries WHERE enquiry_reference = %s", (ref,))
        self.assertIsNotNone(db_enq)
        self.assertEqual(db_enq["customer_mobile"], "+91 99999 88888")

        db_items = db.fetch_all("SELECT * FROM enquiry_items WHERE enquiry_id = %s", (db_enq["id"],))
        self.assertEqual(len(db_items), 2)
        self.assertEqual(db_items[0]["sku"], "SST-TB-101")
        self.assertEqual(db_items[0]["quantity"], 60)

        # 5. Verify Customer Enquiries Dashboard
        res_dash = fresh_client.get("/customer/enquiries", headers={"Cookie": cookie})
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn(ref, res_dash.text)
        self.assertIn("60 pcs", res_dash.text)

    def test_05_admin_authorization(self):
        """Verify that unauthorized accounts cannot access admin routes, while allowlisted accounts can."""
        fresh_client = TestClient(fastapi_app)
        
        # 1. Unauthenticated request to /admin (no session) -> Redirects to /auth/login
        res_unauth = fresh_client.get("/admin", follow_redirects=False)
        self.assertEqual(res_unauth.status_code, 303)
        self.assertIn("/auth/login", res_unauth.headers["Location"])

        # 2. Logged-in regular customer accessing /admin -> 403 Forbidden
        fresh_client.post("/auth/test-login?email=normal_buyer@toyhub.in&name=Normal+Buyer&role=customer", follow_redirects=False)
        res_cust_admin = fresh_client.get("/admin", follow_redirects=False)
        self.assertEqual(res_cust_admin.status_code, 403)

        # 3. Unauthorized email attempting admin login -> 403 Forbidden
        res_fake_admin = fresh_client.post("/auth/test-login?email=attacker@random.com&role=admin", follow_redirects=False)
        self.assertEqual(res_fake_admin.status_code, 403)

        # 4. Authorized Admin from allowlist -> 303 Redirect to /admin with valid admin cookie
        res_admin_login = fresh_client.post("/auth/test-login?email=admin@shreeshyamtoys.com&name=Main+Admin&role=admin", follow_redirects=False)
        self.assertEqual(res_admin_login.status_code, 303)
        admin_cookie = res_admin_login.headers.get("set-cookie")
        self.assertIsNotNone(admin_cookie)

        # Access /admin dashboard -> 200 OK
        res_dash = fresh_client.get("/admin", headers={"Cookie": admin_cookie})
        self.assertEqual(res_dash.status_code, 200)
        self.assertIn("Operational Overview", res_dash.text)

    def test_06_admin_crud_operations(self):
        """Test Admin Product creation, duplication, soft-archive, and category CRUD."""
        fresh_client = TestClient(fastapi_app)
        admin_login = fresh_client.post("/auth/test-login?email=admin@shreeshyamtoys.com&name=Main+Admin&role=admin", follow_redirects=False)
        admin_cookie = admin_login.headers.get("set-cookie")

        # 1. Create Product
        prod_data = {
            "name": "Pastel Pony Plush",
            "sku": f"SST-PN-{uuid.uuid4().hex[:6].upper()}",
            "category_id": 5,
            "moq": 35,
            "description": "Charming pastel pony soft toy with embroidered saddle.",
            "material": "Velboa & Virgin Polyfill",
            "size_info": "30cm, 45cm",
            "available_colours": "Pastel Pink, Mint Green",
            "availability": "in_stock",
            "is_featured": True,
            "is_new_arrival": True,
            "seo_title": "Pastel Pony Plush Wholesale",
            "seo_description": "Bulk enquiry for pastel pony plush toys."
        }
        res_create = fresh_client.post("/admin/products/new", data=prod_data, headers={"Cookie": admin_cookie}, follow_redirects=False)
        self.assertEqual(res_create.status_code, 303)
        created_id = int(res_create.headers["Location"].split("/products/")[1].split("/edit")[0])

        # Verify created
        p = db.fetch_one("SELECT * FROM products WHERE id = %s", (created_id,))
        self.assertTrue(p["sku"].startswith("SST-PN-"))
        self.assertEqual(p["moq"], 35)

        # 2. Duplicate Product
        res_dup = fresh_client.post(f"/admin/products/{created_id}/duplicate", headers={"Cookie": admin_cookie}, follow_redirects=False)
        self.assertEqual(res_dup.status_code, 303)
        dup_id = int(res_dup.headers["Location"].split("/products/")[1].split("/edit")[0])
        dup_p = db.fetch_one("SELECT * FROM products WHERE id = %s", (dup_id,))
        self.assertTrue(dup_p["sku"].endswith("-COPY"))
        self.assertEqual(dup_p["availability"], "hidden")

        # 3. Soft Archive Product
        res_arch = fresh_client.post(f"/admin/products/{created_id}/archive", headers={"Cookie": admin_cookie}, follow_redirects=False)
        self.assertEqual(res_arch.status_code, 303)
        arch_p = db.fetch_one("SELECT is_archived FROM products WHERE id = %s", (created_id,))
        self.assertTrue(arch_p["is_archived"])

        # Verify it disappears from public catalogue
        pub_check = fresh_client.get("/catalogue?q=Pastel+Pony")
        self.assertNotIn(p["sku"], pub_check.text)

        # 4. Restore Product
        res_rest = fresh_client.post(f"/admin/products/{created_id}/restore", headers={"Cookie": admin_cookie}, follow_redirects=False)
        self.assertEqual(res_rest.status_code, 303)
        rest_p = db.fetch_one("SELECT is_archived FROM products WHERE id = %s", (created_id,))
        self.assertFalse(rest_p["is_archived"])

    def test_07_exports_and_everything_zip(self):
        """Test XLSX, CSV, and full backup ZIP generation."""
        fresh_client = TestClient(fastapi_app)
        admin_login = fresh_client.post("/auth/test-login?email=admin@shreeshyamtoys.com&name=Main+Admin&role=admin", follow_redirects=False)
        admin_cookie = admin_login.headers.get("set-cookie")

        # Products XLSX
        res_xlsx = fresh_client.get("/admin/exports/products?format=xlsx", headers={"Cookie": admin_cookie})
        self.assertEqual(res_xlsx.status_code, 200)
        self.assertIn("application/vnd.openxmlformats", res_xlsx.headers["Content-Type"])

        # Enquiries CSV
        res_csv = fresh_client.get("/admin/exports/enquiries?format=csv", headers={"Cookie": admin_cookie})
        self.assertEqual(res_csv.status_code, 200)
        self.assertIn("text/csv", res_csv.headers["Content-Type"])
        self.assertIn("Enquiry Ref", res_csv.text)

        # Everything ZIP
        res_zip = fresh_client.get("/admin/exports/all/zip", headers={"Cookie": admin_cookie})
        self.assertEqual(res_zip.status_code, 200)
        self.assertIn("application/zip", res_zip.headers["Content-Type"])

        # Inspect ZIP structure
        with zipfile.ZipFile(io.BytesIO(res_zip.content)) as zf:
            names = zf.namelist()
            self.assertIn("products.xlsx", names)
            self.assertIn("enquiries.xlsx", names)
            self.assertIn("enquiry_items.xlsx", names)
            self.assertIn("customers.xlsx", names)
            self.assertIn("categories.xlsx", names)
            self.assertIn("website_settings.xlsx", names)
            self.assertIn("faq.xlsx", names)
            self.assertIn("social_links.xlsx", names)
            self.assertIn("media_manifest.xlsx", names)

    def test_08_security_headers_and_seo_schema(self):
        """Verify security headers and structured data are present without price fields."""
        res = self.client.get("/")
        self.assertEqual(res.headers.get("X-Content-Type-Options"), "nosniff")
        self.assertEqual(res.headers.get("X-Frame-Options"), "SAMEORIGIN")
        self.assertEqual(res.headers.get("X-XSS-Protection"), "1; mode=block")

        # Breadcrumbs schema check on catalogue
        res_cat = self.client.get("/catalogue")
        self.assertIn("BreadcrumbList", res_cat.text)

        # Product schema check on product detail
        res_prod = self.client.get("/product/heritage-cuddle-teddy-bear")
        self.assertIn("BreadcrumbList", res_prod.text)
        self.assertIn('"@type": "Product"', res_prod.text)
        # CRITICAL: Verify NO price in JSON-LD
        self.assertNotIn('"price":', res_prod.text)
        self.assertNotIn('"priceCurrency":', res_prod.text)
        self.assertNotIn('"priceValidUntil":', res_prod.text)

    def test_09_production_cannot_use_sqlite(self):
        """Verify production environment strictly prohibits SQLite and requires Supabase PostgreSQL."""
        with patch.object(type(settings), 'is_production', True):
            with self.assertRaises(RuntimeError) as ctx:
                Database(db_url="")
            self.assertIn("Production environment detected, but DATABASE_URL is missing", str(ctx.exception))

    def test_10_production_cannot_use_local_storage_fallback(self):
        """Verify production environment strictly fails upload rather than falling back to local disk."""
        with patch.object(type(settings), 'is_production', True):
            success, err = StorageService.save_file(b"test-bytes", "test.jpg", "image/jpeg")
            self.assertFalse(success)
            self.assertIn("Production Upload Failed", err)

    def test_11_missing_production_secret_key_fails_safely(self):
        """Verify missing or empty SECRET_KEY and ADMIN_EMAILS in production mode raise RuntimeError on initialization."""
        orig_env = os.environ.get("ENVIRONMENT")
        orig_key = os.environ.get("SECRET_KEY")
        orig_admin = os.environ.get("ADMIN_EMAILS")
        orig_app_url = os.environ.get("APP_URL")
        orig_google_redirect = os.environ.get("GOOGLE_REDIRECT_URI")
        try:
            # 1. Missing SECRET_KEY in production
            os.environ["ENVIRONMENT"] = "production"
            os.environ["SECRET_KEY"] = ""
            os.environ["ADMIN_EMAILS"] = "admin@shreeshyamtoys.com"
            os.environ["APP_URL"] = "https://shreeshyamtoys.onrender.com"
            os.environ["GOOGLE_REDIRECT_URI"] = "https://shreeshyamtoys.onrender.com/auth/google/callback"
            with self.assertRaises(RuntimeError) as ctx:
                Settings()
            self.assertIn("SECRET_KEY environment variable is missing or empty in production mode", str(ctx.exception))

            # 2. Missing ADMIN_EMAILS in production
            os.environ["SECRET_KEY"] = "prod-secret-random-12345"
            os.environ["ADMIN_EMAILS"] = ""
            os.environ["APP_URL"] = "https://shreeshyamtoys.onrender.com"
            os.environ["GOOGLE_REDIRECT_URI"] = "https://shreeshyamtoys.onrender.com/auth/google/callback"
            with self.assertRaises(RuntimeError) as ctx2:
                Settings()
            self.assertIn("ADMIN_EMAILS environment variable is missing or empty in production mode", str(ctx2.exception))

            # 3. Missing APP_URL in production
            os.environ["ADMIN_EMAILS"] = "admin@shreeshyamtoys.com"
            os.environ["APP_URL"] = ""
            with self.assertRaises(RuntimeError) as ctx3:
                Settings()
            self.assertIn("APP_URL environment variable is missing or empty in production mode", str(ctx3.exception))

            # 4. Localhost APP_URL is rejected in production
            os.environ["APP_URL"] = "http://localhost:8000"
            with self.assertRaises(RuntimeError) as ctx4:
                Settings()
            self.assertIn("APP_URL must not point to localhost", str(ctx4.exception))

            # 5. Google redirect URI is mandatory and cannot point to localhost
            os.environ["APP_URL"] = "https://shreeshyamtoys.onrender.com"
            os.environ["GOOGLE_REDIRECT_URI"] = ""
            with self.assertRaises(RuntimeError) as ctx5:
                Settings()
            self.assertIn("GOOGLE_REDIRECT_URI environment variable is missing or empty", str(ctx5.exception))

            os.environ["GOOGLE_REDIRECT_URI"] = "http://localhost:8000/auth/google/callback"
            with self.assertRaises(RuntimeError) as ctx6:
                Settings()
            self.assertIn("GOOGLE_REDIRECT_URI must be a valid public", str(ctx6.exception))
        finally:
            if orig_env is not None:
                os.environ["ENVIRONMENT"] = orig_env
            else:
                os.environ.pop("ENVIRONMENT", None)
            if orig_key is not None:
                os.environ["SECRET_KEY"] = orig_key
            else:
                os.environ.pop("SECRET_KEY", None)
            if orig_admin is not None:
                os.environ["ADMIN_EMAILS"] = orig_admin
            else:
                os.environ.pop("ADMIN_EMAILS", None)
            if orig_app_url is not None:
                os.environ["APP_URL"] = orig_app_url
            else:
                os.environ.pop("APP_URL", None)
            if orig_google_redirect is not None:
                os.environ["GOOGLE_REDIRECT_URI"] = orig_google_redirect
            else:
                os.environ.pop("GOOGLE_REDIRECT_URI", None)

    def test_12_missing_whatsapp_number_does_not_generate_fake_url(self):
        """Verify that when no WhatsApp number is configured, no fake URL is generated."""
        from app.services.auth_service import AuthService
        # Ensure database setting has no whatsapp number
        db.execute("UPDATE website_settings SET value = '' WHERE key = 'whatsapp_number'")
        
        cust = AuthService.sync_customer("test_wa_gid_12", "test_wa_buyer@buyer.com", "Test WA Buyer", None)
        
        with patch.object(settings, 'WHATSAPP_NUMBER', ''):
            processed_items = [{
                "product_id": 1,
                "product_name": "Heritage Cuddle Teddy Bear",
                "sku": "SST-TB-101",
                "category_name": "Classic Teddy Bears",
                "selected_size": "30 CM",
                "selected_colour": "Classic Brown",
                "quantity": 30,
                "moq_at_enquiry": 30
            }]
            with patch.object(EnquiryService, 'validate_and_calculate_items', return_value=(True, processed_items, None)):
                success, enq_record, err = EnquiryService.create_enquiry(
                    customer_id=cust["id"],
                    customer_name="Test WA Buyer",
                    customer_email="test_wa_buyer@buyer.com",
                    customer_mobile="+91 99999 77777",
                    raw_items=[{"product_id": 1, "quantity": 30}],
                    notes="Test enquiry"
                )
                self.assertTrue(success)
                self.assertIsNone(enq_record["whatsapp_url"])
                self.assertNotIn("919876543210", str(enq_record))

    def test_13_test_login_is_unavailable_in_production(self):
        """Verify /auth/test-login returns 404 in production environment."""
        with patch.object(type(settings), 'is_production', True):
            res_post = self.client.post("/auth/test-login?email=buyer@test.com&role=customer")
            self.assertEqual(res_post.status_code, 404)
            res_get = self.client.get("/auth/test-login?email=buyer@test.com&role=customer")
            self.assertEqual(res_get.status_code, 404)

    def test_14_render_configuration_contains_port(self):
        """Verify render.yaml and Procfile contain proper $PORT start command and no fake WhatsApp."""
        render_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "render.yaml"))
        with open(render_path, "r") as f:
            render_content = f.read()
        self.assertIn('startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"', render_content)
        self.assertNotIn('919876543210', render_content)

        procfile_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Procfile"))
        with open(procfile_path, "r") as f:
            procfile_content = f.read()
        self.assertIn('uvicorn main:app --host 0.0.0.0 --port $PORT', procfile_content)

if __name__ == "__main__":
    unittest.main()
