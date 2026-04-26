"""SQLite 로컬 DB — Supabase 클라이언트 호환 인터페이스

DB_TYPE=sqlite 환경변수 설정 시 활성화.
Supabase 플루언트 API (table().select().eq().execute()) 를 SQLite로 에뮬레이션.
"""

import json
import os
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DB_PATH = os.getenv("SQLITE_PATH", str(Path(__file__).parent.parent.parent / "local.db"))
LOCAL_STORAGE_DIR = os.getenv(
    "LOCAL_STORAGE_DIR",
    str(Path(__file__).parent.parent.parent / "local_storage"),
)

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS brand_profiles (
    id TEXT PRIMARY KEY,
    brand_name TEXT NOT NULL,
    sheet_mapping TEXT,
    column_mapping TEXT,
    fixed_row_count INTEGER DEFAULT 0,
    notes TEXT,
    created_at TEXT
);

CREATE TABLE IF NOT EXISTS estimate_sessions (
    id TEXT PRIMARY KEY,
    original_file_path TEXT,
    status TEXT DEFAULT 'PENDING',
    brand_profile_id TEXT,
    result_file_path TEXT,
    error_message TEXT,
    created_at TEXT,
    FOREIGN KEY (brand_profile_id) REFERENCES brand_profiles(id)
);

CREATE TABLE IF NOT EXISTS estimate_line_items (
    id TEXT PRIMARY KEY,
    session_id TEXT NOT NULL,
    item_name_raw TEXT,
    item_name_std TEXT,
    spec TEXT,
    unit TEXT,
    qty REAL,
    unit_price REAL,
    amount REAL,
    process_major TEXT,
    process_minor TEXT,
    confidence REAL,
    review_flag INTEGER DEFAULT 0,
    confirmed_at TEXT,
    confirmed_by TEXT,
    source_row INTEGER,
    FOREIGN KEY (session_id) REFERENCES estimate_sessions(id)
);

CREATE TABLE IF NOT EXISTS keyword_dict (
    id TEXT PRIMARY KEY,
    keyword TEXT UNIQUE NOT NULL,
    process_major TEXT,
    process_minor TEXT,
    source TEXT,
    confirm_count INTEGER DEFAULT 0,
    created_at TEXT
);
"""


def _get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_schema():
    with _get_conn() as conn:
        conn.executescript(SCHEMA_SQL)


def _row_to_dict(row: sqlite3.Row) -> dict:
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, str):
            try:
                d[k] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                pass
    # review_flag: SQLite INTEGER → Python bool
    if "review_flag" in d and isinstance(d["review_flag"], int):
        d["review_flag"] = bool(d["review_flag"])
    return d


class _Response:
    def __init__(self, data: list):
        self.data = data


class _QueryBuilder:
    """Supabase 호환 쿼리 빌더"""

    def __init__(self, table: str):
        self._table = table
        self._select_cols = "*"
        self._wheres: list[tuple[str, str, Any]] = []  # (col, op, val)
        self._order_col: str | None = None
        self._insert_data: dict | list | None = None
        self._update_data: dict | None = None
        self._single = False

    # ── 선택 ────────────────────────────────────────────────────
    def select(self, cols: str = "*"):
        self._select_cols = cols
        return self

    def order(self, col: str):
        self._order_col = col
        return self

    def single(self):
        self._single = True
        return self

    # ── 조건 ────────────────────────────────────────────────────
    def eq(self, col: str, val: Any):
        self._wheres.append((col, "=", val))
        return self

    def is_(self, col: str, val: str):
        # Supabase .is_("col", "null") → IS NULL
        if val == "null":
            self._wheres.append((col, "IS NULL", None))
        else:
            self._wheres.append((col, "IS NOT NULL", None))
        return self

    # ── 쓰기 ────────────────────────────────────────────────────
    def insert(self, data: dict | list):
        self._insert_data = data
        return self

    def update(self, data: dict):
        self._update_data = data
        return self

    # ── 실행 ────────────────────────────────────────────────────
    def execute(self) -> _Response:
        if self._insert_data is not None:
            return self._do_insert()
        if self._update_data is not None:
            return self._do_update()
        return self._do_select()

    # ── 내부 구현 ────────────────────────────────────────────────
    def _build_where(self) -> tuple[str, list]:
        parts, params = [], []
        for col, op, val in self._wheres:
            if op == "IS NULL":
                parts.append(f'"{col}" IS NULL')
            elif op == "IS NOT NULL":
                parts.append(f'"{col}" IS NOT NULL')
            else:
                # bool → int for SQLite
                if isinstance(val, bool):
                    val = int(val)
                parts.append(f'"{col}" {op} ?')
                params.append(val)
        clause = ("WHERE " + " AND ".join(parts)) if parts else ""
        return clause, params

    def _do_select(self) -> _Response:
        # Supabase join 구문 파싱: "*, brand_profiles(brand_name)" or "*, brand_profiles(*)"
        join_table, join_cols = self._parse_join_select()
        where, params = self._build_where()
        order = f'ORDER BY "{self._order_col}"' if self._order_col else ""

        with _get_conn() as conn:
            rows = conn.execute(
                f'SELECT * FROM "{self._table}" {where} {order}', params
            ).fetchall()

        data = [_row_to_dict(r) for r in rows]

        # 조인 처리: brand_profiles(brand_name) 등
        if join_table and data:
            for row in data:
                fk = row.get(f"{join_table[:-1]}_id") or row.get(f"{join_table}_id")
                if fk:
                    with _get_conn() as conn:
                        jr = conn.execute(
                            f'SELECT * FROM "{join_table}" WHERE id = ?', [fk]
                        ).fetchone()
                    row[join_table] = _row_to_dict(jr) if jr else None
                else:
                    row[join_table] = None

        if self._single:
            return _Response(data[0] if data else None)  # type: ignore[arg-type]
        return _Response(data)

    def _parse_join_select(self) -> tuple[str | None, list[str]]:
        """"*, brand_profiles(brand_name)" → ("brand_profiles", ["brand_name"])"""
        cols = self._select_cols
        if "(" not in cols:
            return None, []
        import re
        m = re.search(r'(\w+)\(([^)]+)\)', cols)
        if not m:
            return None, []
        table = m.group(1)
        join_cols = [c.strip() for c in m.group(2).split(",")]
        return table, join_cols

    def _do_insert(self) -> _Response:
        rows = self._insert_data if isinstance(self._insert_data, list) else [self._insert_data]
        now = datetime.now(timezone.utc).isoformat()
        inserted = []
        with _get_conn() as conn:
            for row in rows:
                row = dict(row)
                if "id" not in row:
                    row["id"] = str(uuid.uuid4())
                if "created_at" not in row and "created_at" in self._get_cols():
                    row["created_at"] = now
                # JSON 직렬화
                for k, v in row.items():
                    if isinstance(v, (dict, list)):
                        row[k] = json.dumps(v, ensure_ascii=False)
                    if isinstance(v, bool):
                        row[k] = int(v)
                cols = ", ".join(f'"{c}"' for c in row)
                placeholders = ", ".join("?" for _ in row)
                conn.execute(
                    f'INSERT OR REPLACE INTO "{self._table}" ({cols}) VALUES ({placeholders})',
                    list(row.values()),
                )
                inserted.append(row)
        return _Response([_row_to_dict_from_plain(r) for r in inserted])

    def _do_update(self) -> _Response:
        data = dict(self._update_data)  # type: ignore[arg-type]
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                data[k] = json.dumps(v, ensure_ascii=False)
            if isinstance(v, bool):
                data[k] = int(v)
        where, params = self._build_where()
        sets = ", ".join(f'"{c}" = ?' for c in data)
        with _get_conn() as conn:
            conn.execute(
                f'UPDATE "{self._table}" SET {sets} {where}',
                list(data.values()) + params,
            )
        return _Response([])

    def _get_cols(self) -> list[str]:
        with _get_conn() as conn:
            rows = conn.execute(f'PRAGMA table_info("{self._table}")').fetchall()
        return [r["name"] for r in rows]


def _row_to_dict_from_plain(row: dict) -> dict:
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, str):
            try:
                d[k] = json.loads(v)
            except (json.JSONDecodeError, ValueError):
                pass
    if "review_flag" in d and isinstance(d["review_flag"], int):
        d["review_flag"] = bool(d["review_flag"])
    return d


class _LocalStorage:
    def __init__(self, bucket: str):
        self._bucket = bucket
        self._base = Path(LOCAL_STORAGE_DIR) / bucket
        self._base.mkdir(parents=True, exist_ok=True)

    def upload(self, path: str, file: bytes, file_options: dict | None = None):
        dest = self._base / path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(file)

    def download(self, path: str) -> bytes:
        return (self._base / path).read_bytes()

    def create_signed_url(self, path: str, expires_in: int = 3600) -> dict:
        # 로컬에서는 file:// URL 반환
        full = (self._base / path).resolve()
        return {"signedURL": full.as_uri()}


class LocalStorageClient:
    def from_(self, bucket: str) -> _LocalStorage:
        return _LocalStorage(bucket)


class LocalDBClient:
    """Supabase Client 호환 로컬 SQLite 클라이언트"""

    def __init__(self):
        _init_schema()
        self.storage = LocalStorageClient()

    def table(self, name: str) -> _QueryBuilder:
        return _QueryBuilder(name)
