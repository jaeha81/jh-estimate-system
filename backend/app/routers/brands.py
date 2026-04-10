"""브랜드 프로필 라우터"""

from fastapi import APIRouter, HTTPException

from app.models.db import get_db
from app.schemas.estimate import (
    BrandProfileResponse,
    BrandProfileCreateRequest,
    BrandProfilesListResponse,
)

router = APIRouter(prefix="/brand-profiles", tags=["brands"])


@router.get("", response_model=BrandProfilesListResponse)
async def list_brands():
    """브랜드 프로필 목록"""
    try:
        db = get_db()
        result = db.table("brand_profiles").select("*").order("created_at").execute()
        brands = result.data or []
    except Exception:
        return BrandProfilesListResponse(brands=[], total=0)
    return BrandProfilesListResponse(
        brands=[BrandProfileResponse(**b) for b in brands],
        total=len(brands),
    )


@router.post("", response_model=BrandProfileResponse)
async def create_brand(body: BrandProfileCreateRequest):
    """브랜드 프로필 등록"""
    try:
        db = get_db()
        result = db.table("brand_profiles").insert({
            "brand_name": body.brand_name,
            "sheet_mapping": body.sheet_mapping,
            "column_mapping": body.column_mapping,
            "fixed_row_count": body.fixed_row_count,
            "notes": body.notes,
        }).execute()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 실패: {e}")
    return BrandProfileResponse(**result.data[0])
