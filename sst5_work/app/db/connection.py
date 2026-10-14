import os
import re
import sqlite3
import logging
import threading
from typing import List, Dict, Any, Optional, Tuple, Union
from app.config import settings

logger = logging.getLogger("sst.db")

class Database:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url if db_url is not None else settings.DATABASE_URL
        is_prod = settings.is_production
        self.is_postgres = bool(self.db_url and (self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://")))
        self._pg_pool = None
        self._sqlite_path = os.getenv("SQLITE_DB_PATH", "/tmp/shree_shyam_toys.db")
        self._lock = threading.Lock()
        self._sqlite_seeded = False

        if is_prod and not self.is_postgres:
            raise RuntimeError(
                "CRITICAL CONFIGURATION ERROR: Production environment detected, but DATABASE_URL "
                "is missing or not a valid Supabase PostgreSQL connection string. Running on SQLite "
                "in production is strictly prohibited to prevent data loss on Render restarts/redeploys. "
                "Please set DATABASE_URL in your Render environment variables."
            )

        if self.is_postgres:
            self._init_pg_pool(allow_fallback=True)

        if not self.is_postgres:
            logger.info(f"Using SQLite database at {self._sqlite_path}")

    def _init_pg_pool(self, allow_fallback: bool = True) -> bool:
        try:
            import psycopg2
            from psycopg2.pool import SimpleConnectionPool
            pg_url = self.db_url
            if pg_url.startswith("postgres://"):
                pg_url = pg_url.replace("postgres://", "postgresql://", 1)
            self._pg_pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=pg_url, connect_timeout=3)
            # Test connection immediately with a fast query
            conn = self._pg_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1;")
            finally:
                self._pg_pool.putconn(conn)
            self.is_postgres = True
            logger.info("Connected to PostgreSQL / Supabase connection pool.")
            return True
        except Exception as e:
            logger.warning(f"PostgreSQL connection attempt failed ({e}).")
            if allow_fallback:
                logger.warning("Using fast SQLite fallback while Supabase is paused/unreachable.")
                self.is_postgres = False
                self._pg_pool = None
                return False
            raise RuntimeError(f"Failed to establish production database connection: {e}")

    def _switch_to_sqlite_fallback(self, err: Exception):
        logger.warning(f"PostgreSQL query error ({err}); switching to resilient SQLite fallback.")
        with self._lock:
            self.is_postgres = False
            self._pg_pool = None
            if not self._sqlite_seeded:
                self._sqlite_seeded = True
                try:
                    from app.db.migrations import run_migrations
                    run_migrations()
                except Exception as mig_err:
                    logger.warning(f"Fallback migration notice: {mig_err}")

    def try_reconnect_postgres_background(self) -> bool:
        """Called ONLY from background thread (never from HTTP request / healthcheck threads)."""
        if not self.is_postgres and self.db_url and (self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://")):
            with self._lock:
                if not self.is_postgres:
                    ok = self._init_pg_pool(allow_fallback=True)
                    if ok:
                        try:
                            from app.db.migrations import run_migrations
                            run_migrations()
                        except Exception:
                            pass
                    return ok
        return self.is_postgres

    def _get_sqlite_conn(self):
        conn = sqlite3.connect(self._sqlite_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _adapt_query_for_engine(self, query: str) -> str:
        if not self.is_postgres:
            query = re.sub(r'(?<!%)%s', '?', query)
        else:
            query = re.sub(r'\?', '%s', query)
        return query

    def _get_valid_pg_conn(self):
        conn = self._pg_pool.getconn()
        try:
            if conn.closed != 0:
                self._pg_pool.putconn(conn, close=True)
                conn = self._pg_pool.getconn()
        except Exception:
            pass
        return conn

    def fetch_all(self, query: str, params: Union[Tuple, List] = ()) -> List[Dict[str, Any]]:
        if self.is_postgres:
            pg_query = self._adapt_query_for_engine(query)
            from psycopg2.extras import RealDictCursor
            conn = None
            try:
                conn = self._get_valid_pg_conn()
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(pg_query, params)
                    res = cur.fetchall()
                    return [dict(r) for r in res]
            except Exception as e:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn, close=True)
                    except Exception:
                        pass
                    conn = None
                self._switch_to_sqlite_fallback(e)
            finally:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn)
                    except Exception:
                        pass

        sq_query = self._adapt_query_for_engine(query)
        conn = self._get_sqlite_conn()
        try:
            cur = conn.cursor()
            cur.execute(sq_query, params)
            res = cur.fetchall()
            return [dict(r) for r in res]
        finally:
            conn.close()

    def fetch_one(self, query: str, params: Union[Tuple, List] = ()) -> Optional[Dict[str, Any]]:
        if self.is_postgres:
            pg_query = self._adapt_query_for_engine(query)
            from psycopg2.extras import RealDictCursor
            conn = None
            try:
                conn = self._get_valid_pg_conn()
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(pg_query, params)
                    res = cur.fetchone()
                    return dict(res) if res else None
            except Exception as e:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn, close=True)
                    except Exception:
                        pass
                    conn = None
                self._switch_to_sqlite_fallback(e)
            finally:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn)
                    except Exception:
                        pass

        sq_query = self._adapt_query_for_engine(query)
        conn = self._get_sqlite_conn()
        try:
            cur = conn.cursor()
            cur.execute(sq_query, params)
            res = cur.fetchone()
            return dict(res) if res else None
        finally:
            conn.close()

    def execute(self, query: str, params: Union[Tuple, List] = ()) -> int:
        """Executes INSERT/UPDATE/DELETE and returns inserted id, lastrowid, or affected rows."""
        if self.is_postgres:
            pg_query = self._adapt_query_for_engine(query)
            conn = None
            try:
                conn = self._get_valid_pg_conn()
                with conn.cursor() as cur:
                    is_insert = pg_query.strip().upper().startswith("INSERT") and "RETURNING" not in pg_query.upper()
                    has_serial_id = any(tbl in pg_query.lower() for tbl in (
                        "into categories", "into products", "into product_variants",
                        "into product_images", "into enquiries", "into enquiry_items",
                        "into social_links", "into faqs", "into media_manifest", "into audit_logs"
                    ))
                    if is_insert and has_serial_id:
                        cur.execute(pg_query.rstrip(";") + " RETURNING id", params)
                        row = cur.fetchone()
                        conn.commit()
                        return row[0] if row else cur.rowcount
                    else:
                        cur.execute(pg_query, params)
                        conn.commit()
                        return cur.rowcount
            except Exception as e:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn, close=True)
                    except Exception:
                        pass
                    conn = None
                self._switch_to_sqlite_fallback(e)
            finally:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn)
                    except Exception:
                        pass

        sq_query = self._adapt_query_for_engine(query)
        conn = self._get_sqlite_conn()
        try:
            cur = conn.cursor()
            cur.execute(sq_query, params)
            conn.commit()
            return cur.lastrowid or cur.rowcount
        finally:
            conn.close()

    def execute_script(self, script: str):
        """Executes multi-statement SQL script."""
        if self.is_postgres:
            conn = None
            try:
                conn = self._get_valid_pg_conn()
                with conn.cursor() as cur:
                    cur.execute(script)
                    conn.commit()
                return
            except Exception as e:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn, close=True)
                    except Exception:
                        pass
                    conn = None
                self._switch_to_sqlite_fallback(e)
            finally:
                if conn and self._pg_pool:
                    try:
                        self._pg_pool.putconn(conn)
                    except Exception:
                        pass

        def adapt_sql_for_sqlite(sql: str) -> str:
            sql = re.sub(r'CREATE\s+EXTENSION[^;]+;', '', sql, flags=re.IGNORECASE)
            sql = re.sub(r'\bSERIAL\s+PRIMARY\s+KEY\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', sql, flags=re.IGNORECASE)
            sql = re.sub(r'TIMESTAMP\s+WITH\s+TIME\s+ZONE', 'TIMESTAMP', sql, flags=re.IGNORECASE)
            sql = re.sub(r'\bBYTEA\b', 'BLOB', sql, flags=re.IGNORECASE)
            return sql

        adapted = adapt_sql_for_sqlite(script)
        conn = self._get_sqlite_conn()
        try:
            conn.executescript(adapted)
        finally:
            conn.close()

    def ping_keepalive_background(self) -> Dict[str, Any]:
        """Runs in background daemon thread to keep Supabase active without ever blocking HTTP healthchecks."""
        self.try_reconnect_postgres_background()
        try:
            self.execute(
                "UPDATE website_settings SET updated_at = CURRENT_TIMESTAMP WHERE key = %s",
                ("business_name",)
            )
            return {"ok": True, "engine": "postgresql" if self.is_postgres else "sqlite_fallback"}
        except Exception as e:
            return {"ok": False, "engine": "postgresql" if self.is_postgres else "sqlite_fallback", "error": str(e)}

# Global database instance
db = Database()
