"""라인 아이템 라우터 — 항목 목록 + 공정 확정"""

from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Query

import logging

from app.models.db import get_db
from app.schemas.estimate import (
    ItemsListResponse,
    LineItemResponse,
    LineItemConfirmRequest,
    LineItemConfirmResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter(tags=["items"])


@router.get("/sessions/{session_id}/items", response_model=ItemsListResponse)
async def get_items(session_id: str, review_only: bool = Query(False)):
    """세션의 항목 목록 조회"""
    try:
        db = get_db()
        query = db.table("estimate_line_items").select("*").eq("session_id", session_id)
        if review_only:
            query = query.eq("review_flag", True).is_("confirmed_at", "null")
        result = query.order("source_row").execute()
        items = result.data or []
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 실패: {e}")

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
    try:
        db = get_db()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 실패: {e}")

    # 항목 조회
    try:
        result = db.table("estimate_line_items").select("*").eq("id", item_id).execute()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"데이터베이스 연결 실패: {e}")
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

    # 세션 모든 review 항목 완료 시 자동 export + DONE 전환
    try:
        remaining = (
            db.table("estimate_line_items")
            .select("id")
            .eq("session_id", item["session_id"])
            .eq("review_flag", True)
            .is_("confirmed_at", "null")
            .execute()
        )
        if not (remaining.data or []):
            from app.agents.orchestrator import Orchestrator

            try:
                Orchestrator().trigger_export(item["session_id"])
            except Exception as exc:
                # export 실패해도 confirm 응답은 성공으로 반환
                logger.error(
                    f"자동 export 실패 (session={item['session_id']}): {exc}"
                )
    except Exception as exc:
        logger.error(f"컨펌 완료 상태 확인 실패 (item={item_id}): {exc}")

    return LineItemConfirmResponse(id=item_id)
