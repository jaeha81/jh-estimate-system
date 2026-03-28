"""라인 아이템 라우터 — 항목 목록 + 공정 확정"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query

from app.models.db import get_db
from app.schemas.estimate import (
    ItemsListResponse,
    LineItemResponse,
    LineItemConfirmRequest,
    LineItemConfirmResponse,
)

router = APIRouter(tags=["items"])


@router.get("/sessions/{session_id}/items", response_model=ItemsListResponse)
async def get_items(session_id: str, review_only: bool = Query(False)):
    """세션의 항목 목록 조회"""
    db = get_db()

    query = db.table("estimate_line_items").select("*").eq("session_id", session_id)
    if review_only:
        query = query.eq("review_flag", True).is_("confirmed_at", "null")

    result = query.order("source_row").execute()
    items = result.data or []

    review_count = sum(
        1 for i in items if i.get("review_flag") and not i.get("confirmed_at")
    )

    return ItemsListResponse(
        session_id=session_id,
        items=[LineItemResponse(**i) for i in items],
        total=len(items),
        review_count=review_count,
    )


@router.patch("/items/{item_id}/confirm", response_model=LineItemConfirmResponse)
async def confirm_item(item_id: str, body: LineItemConfirmRequest):
    """공정 확정 + keyword_dict USER_CONFIRM 누적"""
    db = get_db()

    # 항목 조회
    result = db.table("estimate_line_items").select("*").eq("id", item_id).execute()
    if not result.data:
        raise HTTPException(status_code=404, detail="항목을 찾을 수 없습니다")

    item = result.data[0]

    # 항목 업데이트
    update_data = {
        "process_major": body.process_major,
        "process_minor": body.process_minor,
        "confirmed_by": "user",
        "confirmed_at": datetime.now(timezone.utc).isoformat(),
        "confidence": 1.0,
    }
    if body.item_name_std:
        update_data["item_name_std"] = body.item_name_std

    db.table("estimate_line_items").update(update_data).eq("id", item_id).execute()

    # keyword_dict에 USER_CONFIRM 누적
    keyword = item["item_name_raw"].strip()
    existing = (
        db.table("keyword_dict")
        .select("id, confirm_count")
        .eq("keyword", keyword)
        .execute()
    )

    if existing.data:
        # 기존 키워드 confirm_count 증가
        kw = existing.data[0]
        db.table("keyword_dict").update({
            "process_major": body.process_major,
            "process_minor": body.process_minor,
            "confirm_count": kw["confirm_count"] + 1,
        }).eq("id", kw["id"]).execute()
    else:
        # 새 키워드 추가
        db.table("keyword_dict").insert({
            "keyword": keyword,
            "process_major": body.process_major,
            "process_minor": body.process_minor,
            "source": "USER_CONFIRM",
            "confirm_count": 1,
        }).execute()

    return LineItemConfirmResponse(id=item_id)
