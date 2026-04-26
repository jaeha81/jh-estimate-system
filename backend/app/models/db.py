"""DB 클라이언트 싱글톤 — Supabase 또는 SQLite 로컬"""

import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))


@lru_cache(maxsize=1)
def get_db():
    """DB_TYPE=sqlite 이면 LocalDBClient, 기본은 Supabase Client 반환"""
    db_type = os.getenv("DB_TYPE", "supabase").lower()

    if db_type == "sqlite":
        from app.models.local_db import LocalDBClient
        return LocalDBClient()

    from supabase import create_client
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY 환경변수 필요")
    return create_client(url, key)
