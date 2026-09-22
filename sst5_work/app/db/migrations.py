import os
import logging
from app.db.connection import db

logger = logging.getLogger("sst.migrations")

def run_migrations():
    """Runs initial database schema and seed migrations if tables do not exist."""
    migrations_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "migrations"))
    
    schema_file = os.path.join(migrations_dir, "001_initial_schema.sql")
    seed_file = os.path.join(migrations_dir, "002_seed_data.sql")
    cleanup_file = os.path.join(migrations_dir, "003_content_safety_cleanup.sql")
    
    # Check if products table already exists
    table_check = None
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
        logger.info("Database schema already exists, skipping initial creation.")

    # Idempotent post-seed cleanup also runs against databases created by earlier project versions.
    if os.path.exists(cleanup_file):
        logger.info("Applying content safety cleanup migration...")
        with open(cleanup_file, "r", encoding="utf-8") as f:
            db.execute_script(f.read())
        logger.info("Content safety cleanup applied successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_migrations()
