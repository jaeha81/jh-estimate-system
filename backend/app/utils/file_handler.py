"""파일 업로드/다운로드 유틸"""

import os
import re
import tempfile
import uuid
from pathlib import Path
from fastapi import UploadFile

from app.models.db import get_db

ALLOWED_EXTENSIONS = {".xlsx", ".xls"}
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB
BUCKET_NAME = os.getenv("SUPABASE_BUCKET", "estimate-files")


def sanitize_filename(filename: str) -> str:
    """경로 traversal 방지 + 안전한 파일명 반환"""
    filename = Path(filename).name  # 경로 제거
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)  # 특수문자 제거
    return filename


def validate_extension(filename: str) -> bool:
    """허용 확장자 검증"""
    ext = Path(filename).suffix.lower()
    return ext in ALLOWED_EXTENSIONS


async def read_upload_file(file: UploadFile) -> tuple[bytes, str]:
    """UploadFile → (bytes, safe_filename)"""
    content = await file.read()
    safe_name = sanitize_filename(file.filename or "unknown.xlsx")
    if not validate_extension(safe_name):
        raise ValueError(f"허용되지 않는 확장자: {Path(safe_name).suffix}")
    if len(content) > MAX_UPLOAD_SIZE:
        raise ValueError(f"파일 크기 초과: {len(content)} > {MAX_UPLOAD_SIZE}")
    return content, safe_name


def upload_to_storage(file_bytes: bytes, storage_path: str) -> str:
    """Supabase Storage에 파일 업로드"""
    db = get_db()
    db.storage.from_(BUCKET_NAME).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"},
    )
    return storage_path


def download_from_storage(storage_path: str) -> bytes:
    """Supabase Storage에서 파일 다운로드"""
    db = get_db()
    return db.storage.from_(BUCKET_NAME).download(storage_path)


def get_signed_url(storage_path: str, expires_in: int = 3600) -> str:
    """Supabase Storage signed URL 생성"""
    db = get_db()
    result = db.storage.from_(BUCKET_NAME).create_signed_url(storage_path, expires_in)
    return result.get("signedURL", "")


def save_bytes_to_temp(file_bytes: bytes, filename: str) -> str:
    """바이트 데이터를 임시 파일에 저장"""
    temp_dir = tempfile.mkdtemp(prefix="jh_estimate_")
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)
    return file_path


def delete_temp_file(file_path: str) -> None:
    """임시 파일 및 디렉토리 삭제"""
    if os.path.exists(file_path):
        os.remove(file_path)
        parent = os.path.dirname(file_path)
        if parent and os.path.isdir(parent) and not os.listdir(parent):
            os.rmdir(parent)


def make_storage_path(filename: str, user_id: str | None = None) -> str:
    """Storage 경로 생성"""
    uid = user_id or "anonymous"
    unique = uuid.uuid4().hex[:8]
    return f"{uid}/{unique}_{filename}"
