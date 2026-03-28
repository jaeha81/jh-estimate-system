"""세션 라우터 — 파일 업로드 + 상태 조회"""

from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import Optional

from app.models.db import get_db
from app.schemas.estimate import SessionCreateResponse, SessionStatusResponse
from app.utils.file_handler import read_upload_file
from app.agents.orchestrator import Orchestrator

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionCreateResponse)
async def create_session(
    file: UploadFile = File(...),
    brand_name: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = BackgroundTasks(),
):
    """파일 업로드 → 세션 생성 → 백그라운드 파이프라인 실행"""
    file_bytes, safe_name = await read_upload_file(file)

    db = get_db()
    result = db.table("estimate_sessions").insert({
        "original_file_path": f"pending/{safe_name}",
        "status": "PENDING",
    }).execute()

    session_id = result.data[0]["id"]

    orchestrator = Orchestrator()
    background_tasks.add_task(
        orchestrator.run_pipeline, session_id, file_bytes, safe_name, brand_name
    )

    return SessionCreateResponse(session_id=session_id)


@router.get("/{session_id}", response_model=SessionStatusResponse)
async def get_session(session_id: str):
    """세션 상태 조회"""
    db = get_db()

    result = (
        db.table("estimate_sessions")
        .select("*, brand_profiles(brand_name)")
        .eq("id", session_id)
        .execute()
    )

    if not result.data:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다")

    session = result.data[0]

    # 항목 수 집계
    items_result = (
        db.table("estimate_line_items")
        .select("id, review_flag, confirmed_at")
        .eq("session_id", session_id)
        .execute()
    )
    items = items_result.data or []
    total_items = len(items)
    review_items = sum(
        1 for i in items if i.get("review_flag") and not i.get("confirmed_at")
    )

    brand = session.get("brand_profiles")
    brand_name = brand["brand_name"] if brand else None

    return SessionStatusResponse(
        session_id=session_id,
        status=session["status"],
        brand_name=brand_name,
        total_items=total_items,
        review_items=review_items,
        error_message=session.get("error_message"),
        created_at=session.get("created_at"),
    )
