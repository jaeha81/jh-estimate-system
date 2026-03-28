"""Pydantic 스키마"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── 세션 ───────────────────────────────────────────
class SessionCreateResponse(BaseModel):
    session_id: str
    status: str = "PENDING"
    message: str = "파이프라인 시작됨"


class SessionStatusResponse(BaseModel):
    session_id: str
    status: str
    brand_name: Optional[str] = None
    total_items: int = 0
    review_items: int = 0
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None


# ── 라인 아이템 ────────────────────────────────────
class LineItemResponse(BaseModel):
    id: str
    item_name_raw: str
    item_name_std: Optional[str] = None
    process_major: Optional[str] = None
    process_minor: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    qty: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None
    confidence: Optional[float] = None
    review_flag: bool = False
    confirmed_at: Optional[datetime] = None
    source_row: int = 0


class LineItemConfirmRequest(BaseModel):
    process_major: str
    process_minor: Optional[str] = None
    item_name_std: Optional[str] = None


class LineItemConfirmResponse(BaseModel):
    id: str
    confirmed: bool = True
    message: str = "확정 완료"


class ItemsListResponse(BaseModel):
    session_id: str
    items: list[LineItemResponse]
    total: int
    review_count: int


# ── 내보내기 ───────────────────────────────────────
class ExportResponse(BaseModel):
    session_id: str
    download_url: str
    message: str = "내보내기 완료"


# ── 브랜드 프로필 ──────────────────────────────────
class BrandProfileResponse(BaseModel):
    id: str
    brand_name: str
    sheet_mapping: dict
    column_mapping: dict
    fixed_row_count: bool = True
    notes: Optional[str] = None


class BrandProfileCreateRequest(BaseModel):
    brand_name: str
    sheet_mapping: dict = Field(default_factory=dict)
    column_mapping: dict = Field(default_factory=dict)
    fixed_row_count: bool = True
    notes: Optional[str] = None


class BrandProfilesListResponse(BaseModel):
    brands: list[BrandProfileResponse]
    total: int


# ── 공통 ───────────────────────────────────────────
class ErrorResponse(BaseModel):
    error: str
    detail: Optional[str] = None
