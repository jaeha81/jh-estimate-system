"""내보내기 라우터"""

from fastapi import APIRouter, HTTPException

from app.schemas.estimate import ExportResponse
from app.agents.orchestrator import Orchestrator

router = APIRouter(prefix="/sessions", tags=["exports"])


@router.post("/{session_id}/export", response_model=ExportResponse)
async def export_session(session_id: str):
    """미확인 항목 없으면 엑셀 내보내기 → signed URL 반환"""
    orchestrator = Orchestrator()
    url = orchestrator.trigger_export(session_id)

    if not url:
        raise HTTPException(
            status_code=400,
            detail="미확인 항목이 남아있습니다. 모든 항목을 확정해주세요.",
        )

    return ExportResponse(session_id=session_id, download_url=url)
