"""메인 오케스트레이터 — 전체 파이프라인 실행"""

import logging

from app.models.db import get_db
from app.agents.template_manager import TemplateManager
from app.agents.normalizer import Normalizer
from app.agents.classifier import classify_items, update_db_with_results
from app.agents.bid_formatter import BidFormatter
from app.services.excel_service import save_upload_to_temp
from app.utils.file_handler import upload_to_storage, make_storage_path, delete_temp_file

logger = logging.getLogger(__name__)


class Orchestrator:
    """파이프라인: 업로드 → 감지 → 파싱 → 정규화 → 분류 → 컨펌/완료"""

    def __init__(self):
        self.template_mgr = TemplateManager()
        self.normalizer = Normalizer()
        self.bid_formatter = BidFormatter()

    def run_pipeline(
        self,
        session_id: str,
        file_bytes: bytes,
        file_name: str,
        brand_name: str | None = None,
        ai_mode: str = "api",
    ) -> str:
        """전체 파이프라인 실행. 최종 status 반환."""
        db = get_db()

        try:
            # 1. Storage 업로드
            storage_path = make_storage_path(file_name)
            upload_to_storage(file_bytes, storage_path)

            db.table("estimate_sessions").update({
                "original_file_path": storage_path,
                "status": "PROCESSING",
            }).eq("id", session_id).execute()

            # 2. 임시 파일 저장 (엑셀 파싱용)
            temp_path = save_upload_to_temp(file_bytes, file_name)

            # 3. 브랜드 감지 or 지정
            if not brand_name:
                brand_name = self.template_mgr.detect_brand(temp_path)

            profile = None
            if brand_name:
                profile = self.template_mgr.get_brand_profile(brand_name)

            if not profile:
                # 프로필 없으면 기본값 사용
                profile = {
                    "brand_name": brand_name or "unknown",
                    "sheet_mapping": {"세부내역": "세부내역서"},
                    "column_mapping": {
                        "item_name": "B", "spec": "C", "unit": "D",
                        "qty": "E", "unit_price": "F", "amount": "G",
                        "data_start_row": 5,
                    },
                    "fixed_row_count": True,
                }

            # 브랜드 프로필 연결
            if brand_name:
                db_profile = self.template_mgr.get_brand_profile(brand_name)
                if db_profile:
                    db.table("estimate_sessions").update({
                        "brand_profile_id": db_profile["id"],
                    }).eq("id", session_id).execute()

            # 4. 시트 정보 추출
            sheet_name, col_mapping, start_row = self.template_mgr.get_detail_sheet_info(
                temp_path, dict(profile)
            )

            # 5. 정규화
            items = self.normalizer.normalize(
                temp_path, sheet_name, col_mapping, start_row, session_id
            )

            # 6. DB 저장
            self.normalizer.save_to_db(items)

            # 7. DB에서 ID 포함 항목 재조회
            result = (
                db.table("estimate_line_items")
                .select("*")
                .eq("session_id", session_id)
                .execute()
            )
            db_items = result.data or []

            # 8. 분류
            classified = classify_items(db_items, ai_mode=ai_mode)

            # 9. 분류 결과 DB 업데이트
            update_db_with_results(classified)

            # 10. review_flag 집계
            review_count = sum(1 for item in classified if item.get("review_flag"))

            # 11. 상태 결정
            if review_count > 0:
                final_status = "CONFIRM_WAIT"
            else:
                final_status = "DONE"
                # 컨펌 불필요 시 바로 포맷팅
                self.bid_formatter.format(session_id)

            db.table("estimate_sessions").update({
                "status": final_status,
            }).eq("id", session_id).execute()

            # 임시 파일 정리
            delete_temp_file(temp_path)

            return final_status

        except Exception as e:
            logger.error(f"파이프라인 오류 (session={session_id}): {e}")
            db.table("estimate_sessions").update({
                "status": "ERROR",
                "error_message": str(e)[:500],
            }).eq("id", session_id).execute()
            return "ERROR"

    def trigger_export(self, session_id: str) -> str | None:
        """미확인 항목 없으면 export 실행 → download URL 반환"""
        db = get_db()
        result = (
            db.table("estimate_line_items")
            .select("id")
            .eq("session_id", session_id)
            .eq("review_flag", True)
            .is_("confirmed_at", "null")
            .execute()
        )
        unconfirmed = result.data or []

        if unconfirmed:
            return None  # 아직 미확인 항목 있음

        storage_path = self.bid_formatter.format(session_id)
        return self.bid_formatter.get_download_url(storage_path)
