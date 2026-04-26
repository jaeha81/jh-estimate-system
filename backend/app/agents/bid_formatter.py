"""입찰 양식 정리 — 원본 복사 → 결과 되쓰기 → Storage 업로드"""

import os
from pathlib import Path

from app.models.db import get_db
from app.services.excel_service import (
    write_results_to_excel,
    write_classification_sheet,
    make_output_path,
    create_pdf_result_excel,
)
from app.utils.file_handler import (
    download_from_storage,
    upload_to_storage,
    get_signed_url,
    save_bytes_to_temp,
    delete_temp_file,
    make_storage_path,
)


class BidFormatter:
    """분류 완료된 데이터를 엑셀 양식에 되쓰기"""

    def format(self, session_id: str) -> str:
        """전체 포맷팅 파이프라인 → Storage 경로 반환"""
        db = get_db()

        # 세션 조회
        session = (
            db.table("estimate_sessions")
            .select("*, brand_profiles(*)")
            .eq("id", session_id)
            .single()
            .execute()
        )
        session_data = session.data

        # 원본 파일 경로 + 확장자 확인
        original_path = session_data["original_file_path"]
        filename = os.path.basename(original_path)
        is_pdf = Path(filename).suffix.lower() == ".pdf"

        # 분류 완료 항목 조회
        items_result = (
            db.table("estimate_line_items")
            .select("*")
            .eq("session_id", session_id)
            .execute()
        )
        items = items_result.data or []

        if is_pdf:
            # PDF 경로: 원본 Excel 없음 → 새 Excel 결과 파일 생성
            output_path = create_pdf_result_excel(items, filename)
            temp_source = None
        else:
            # Excel 경로: 원본 다운로드 → 되쓰기
            file_bytes = download_from_storage(original_path)
            temp_source = save_bytes_to_temp(file_bytes, filename)

            profile = session_data.get("brand_profiles") or {}
            column_mapping = dict(profile.get("column_mapping", {}))
            data_start_row = int(column_mapping.pop("data_start_row", 5))
            sheet_mapping = profile.get("sheet_mapping", {})
            sheet_name = sheet_mapping.get("세부내역", "세부내역서")

            output_path = make_output_path(temp_source)
            write_results_to_excel(
                source_path=temp_source,
                output_path=output_path,
                sheet_name=sheet_name,
                column_mapping=column_mapping,
                items=items,
                data_start_row=data_start_row,
            )

        # 공정 분류 결과 시트 추가
        write_classification_sheet(output_path=output_path, items=items)

        # Storage 업로드
        with open(output_path, "rb") as f:
            result_bytes = f.read()
        result_storage_path = make_storage_path(f"result_{Path(filename).stem}.xlsx")
        upload_to_storage(result_bytes, result_storage_path)

        # 세션 업데이트
        db.table("estimate_sessions").update({
            "result_file_path": result_storage_path,
            "status": "DONE",
        }).eq("id", session_id).execute()

        # 임시 파일 정리
        if temp_source:
            delete_temp_file(temp_source)
        delete_temp_file(output_path)

        return result_storage_path

    def get_download_url(self, storage_path: str, expires_in: int = 3600) -> str:
        """signed URL 반환"""
        return get_signed_url(storage_path, expires_in)
