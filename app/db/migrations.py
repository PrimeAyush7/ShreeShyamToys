import os
import logging
from app.db.connection import db

logger = logging.getLogger("sst.migrations")

def _column_exists(table: str, column: str) -> bool:
    try:
        if db.is_postgres:
            row = db.fetch_one(
                "SELECT column_name FROM information_schema.columns WHERE table_name = %s AND column_name = %s",
                (table, column)
            )
            return bool(row)
        else:
            rows = db.fetch_all(f"PRAGMA table_info({table})")
            return any(r.get("name") == column for r in rows)
    except Exception:
        return False

def _ensure_column(table: str, column: str, col_def: str):
    if not _column_exists(table, column):
        try:
            db.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
            logger.info(f"Added column {table}.{column}")
        except Exception as e:
            logger.warning(f"Could not add column {table}.{column}: {e}")

def run_migrations():
    """Runs initial database schema, seed migrations, and v2.0 B2B schema upgrades."""
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "migrations"))
    
    schema_file = os.path.join(migrations_dir, "001_initial_schema.sql")
    seed_file = os.path.join(migrations_dir, "002_seed_data.sql")
    v2_file = os.path.join(migrations_dir, "003_v2_upgrades.sql")
    
    # Check if products table already exists
    try:
        if db.is_postgres:
            table_check = db.fetch_one("SELECT to_regclass('public.products') as exists;")
            table_exists = bool(table_check and table_check.get("exists"))
        else:
            table_check = db.fetch_one("SELECT name FROM sqlite_master WHERE type='table' AND name='products';")
            table_exists = bool(table_check and table_check.get("name"))
    except Exception as e:
        logger.warning(f"Error checking table existence: {e}")
        table_exists = False

    if not table_exists:
        logger.info("Initializing database schema...")
        if os.path.exists(schema_file):
            with open(schema_file, "r", encoding="utf-8") as f:
                db.execute_script(f.read())
            logger.info("Schema applied successfully.")
            
        if os.path.exists(seed_file):
            logger.info("Applying initial seed data...")
            with open(seed_file, "r", encoding="utf-8") as f:
                db.execute_script(f.read())
            logger.info("Seed data loaded successfully.")
    else:
        logger.info("Core database schema exists, checking v2.0 upgrades...")

    # Always apply 003_v2_upgrades.sql (idempotent CREATE TABLE IF NOT EXISTS stored_media)
    if os.path.exists(v2_file):
        try:
            with open(v2_file, "r", encoding="utf-8") as f:
                db.execute_script(f.read())
        except Exception as e:
            logger.warning(f"v2 migration script notice: {e}")

    # Ensure v2 columns exist on products and enquiries
    _ensure_column("products", "carton_qty", "INTEGER DEFAULT 0")
    _ensure_column("products", "video_url", "TEXT DEFAULT ''")
    _ensure_column("products", "size_scale_label", "VARCHAR(128) DEFAULT ''")
    _ensure_column("products", "occasion_tag", "VARCHAR(128) DEFAULT ''")
    _ensure_column("enquiries", "customer_city", "VARCHAR(128) DEFAULT ''")

    # Populate intelligent v2 B2B defaults on existing seed products if empty
    v2_product_defaults = [
        (1, 90, "Medium 30cm–90cm • Standard Gift & Retail Shelf Size", "gift_shop"),
        (2, 30, "Giant 5FT (150cm) • Full Human-Height Showroom Display", "jumbo_display"),
        (3, 120, "Medium 40cm–60cm • High-Margin Valentine & Festival Size", "valentine_festival"),
        (4, 60, "Sitting 35cm–75cm • Weighted Desk & Hamper Size", "gift_shop"),
        (5, 100, "Safari 40cm–65cm • Toy Store Display Size", "gift_shop"),
        (6, 80, "Pillow 60cm–120cm • Long Hug Cushion Scale", "gift_shop"),
        (7, 250, "Compact 20cm • Counter Impulse & Claw Machine Size", "claw_arcade"),
        (8, 120, "Cylindrical 25cm–60cm • Trendy Lifestyle Store Size", "valentine_festival"),
        (9, 120, "Toddler 30cm–50cm • Baby Hamper & Nursery Safe Scale", "baby_hamper"),
        (10, 80, "Sitting 45cm • Collector Shelf Scale", "gift_shop"),
        (11, 50, "Mid-Jumbo 3FT (90cm) • Waist-High Gift Bear Scale", "jumbo_display"),
        (12, 100, "Compact 38cm • Retail Counter & Arcade Scale", "claw_arcade"),
    ]
    for pid, carton_qty, scale_lbl, occ_tag in v2_product_defaults:
        try:
            db.execute("""
                UPDATE products
                SET carton_qty = CASE WHEN carton_qty IS NULL OR carton_qty = 0 THEN %s ELSE carton_qty END,
                    size_scale_label = CASE WHEN size_scale_label IS NULL OR size_scale_label = '' THEN %s ELSE size_scale_label END,
                    occasion_tag = CASE WHEN occasion_tag IS NULL OR occasion_tag = '' THEN %s ELSE occasion_tag END
                WHERE id = %s
            """, (carton_qty, scale_lbl, occ_tag, pid))
        except Exception as e:
            logger.warning(f"Could not seed v2 product defaults for id={pid}: {e}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
