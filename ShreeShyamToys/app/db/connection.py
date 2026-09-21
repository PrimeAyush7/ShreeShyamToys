import os
import re
import sqlite3
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
from app.config import settings

logger = logging.getLogger("sst.db")

class Database:
    def __init__(self, db_url: Optional[str] = None):
        self.db_url = db_url or settings.DATABASE_URL
        is_prod = settings.is_production
        self.is_postgres = bool(self.db_url and (self.db_url.startswith("postgres://") or self.db_url.startswith("postgresql://")))
        self._pg_pool = None
        self._sqlite_path = None

        if is_prod:
            if not self.is_postgres:
                raise RuntimeError(
                    "CRITICAL CONFIGURATION ERROR: Production environment detected, but DATABASE_URL "
                    "is missing or not a valid Supabase PostgreSQL connection string. Running on SQLite "
                    "in production is strictly prohibited to prevent data loss on Render restarts/redeploys. "
                    "Please set DATABASE_URL in your Render environment variables."
                )
            try:
                import psycopg2
                from psycopg2.pool import SimpleConnectionPool
                pg_url = self.db_url
                if pg_url.startswith("postgres://"):
                    pg_url = pg_url.replace("postgres://", "postgresql://", 1)
                self._pg_pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=pg_url)
                logger.info("Connected to Supabase PostgreSQL connection pool.")
            except Exception as e:
                logger.critical(f"Failed to connect to Supabase PostgreSQL in production: {e}")
                raise RuntimeError(f"Failed to establish production database connection: {e}")
        else:
            # Local development or testing environment
            if self.is_postgres:
                try:
                    import psycopg2
                    from psycopg2.pool import SimpleConnectionPool
                    pg_url = self.db_url
                    if pg_url.startswith("postgres://"):
                        pg_url = pg_url.replace("postgres://", "postgresql://", 1)
                    self._pg_pool = SimpleConnectionPool(minconn=1, maxconn=10, dsn=pg_url)
                    logger.info("Connected to PostgreSQL / Supabase connection pool.")
                except Exception as e:
                    logger.warning(f"PostgreSQL connection failed ({e}), falling back to SQLite for local development.")
                    self.is_postgres = False

            if not self.is_postgres:
                self._sqlite_path = os.getenv("SQLITE_DB_PATH", "/tmp/shree_shyam_toys.db")
                logger.info(f"Using SQLite database for development at {self._sqlite_path}")

    def _get_sqlite_conn(self):
        conn = sqlite3.connect(self._sqlite_path, timeout=30.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA busy_timeout = 10000")
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    def _adapt_query_for_engine(self, query: str) -> str:
        if not self.is_postgres:
            # Convert %s placeholders to ? for SQLite
            query = re.sub(r'(?<!%)%s', '?', query)
        else:
            # Convert ? placeholders to %s for PostgreSQL
            query = re.sub(r'\?', '%s', query)
        return query

    def fetch_all(self, query: str, params: Union[Tuple, List] = ()) -> List[Dict[str, Any]]:
        query = self._adapt_query_for_engine(query)
        if self.is_postgres:
            from psycopg2.extras import RealDictCursor
            conn = self._pg_pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    res = cur.fetchall()
                    return [dict(r) for r in res]
            finally:
                self._pg_pool.putconn(conn)
        else:
            conn = self._get_sqlite_conn()
            try:
                cur = conn.cursor()
                cur.execute(query, params)
                res = cur.fetchall()
                return [dict(r) for r in res]
            finally:
                conn.close()

    def fetch_one(self, query: str, params: Union[Tuple, List] = ()) -> Optional[Dict[str, Any]]:
        query = self._adapt_query_for_engine(query)
        if self.is_postgres:
            from psycopg2.extras import RealDictCursor
            conn = self._pg_pool.getconn()
            try:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    res = cur.fetchone()
                    return dict(res) if res else None
            finally:
                self._pg_pool.putconn(conn)
        else:
            conn = self._get_sqlite_conn()
            try:
                cur = conn.cursor()
                cur.execute(query, params)
                res = cur.fetchone()
                return dict(res) if res else None
            finally:
                conn.close()

    def execute(self, query: str, params: Union[Tuple, List] = ()) -> int:
        """Executes INSERT/UPDATE/DELETE and returns lastrowid or affected rows."""
        query = self._adapt_query_for_engine(query)
        if self.is_postgres:
            conn = self._pg_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute(query, params)
                    conn.commit()
                    return cur.rowcount
            finally:
                self._pg_pool.putconn(conn)
        else:
            conn = self._get_sqlite_conn()
            try:
                cur = conn.cursor()
                cur.execute(query, params)
                conn.commit()
                return cur.lastrowid or cur.rowcount
            finally:
                conn.close()

    def execute_script(self, script: str):
        """Executes multi-statement SQL script."""
        if self.is_postgres:
            conn = self._pg_pool.getconn()
            try:
                with conn.cursor() as cur:
                    cur.execute(script)
                    conn.commit()
            finally:
                self._pg_pool.putconn(conn)
        else:
            def adapt_sql_for_sqlite(sql: str) -> str:
                sql = re.sub(r'CREATE\s+EXTENSION[^;]+;', '', sql, flags=re.IGNORECASE)
                sql = re.sub(r'\bSERIAL\s+PRIMARY\s+KEY\b', 'INTEGER PRIMARY KEY AUTOINCREMENT', sql, flags=re.IGNORECASE)
                sql = re.sub(r'TIMESTAMP\s+WITH\s+TIME\s+ZONE', 'TIMESTAMP', sql, flags=re.IGNORECASE)
                return sql
            
            adapted = adapt_sql_for_sqlite(script)
            conn = self._get_sqlite_conn()
            try:
                conn.executescript(adapted)
            finally:
                conn.close()

# Global database instance
db = Database()
