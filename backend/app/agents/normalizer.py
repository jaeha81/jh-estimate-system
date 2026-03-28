"""세부내역 시트 파싱 → DB 저장"""

from app.models.db import get_db
from app.services.excel_service import parse_detail_sheet


class Normalizer:
    """엑셀 세부내역 → 정규화된 행 데이터"""

    def normalize(
        self,
        file_path: str,
        sheet_name: str,
        column_mapping: dict,
        data_start_row: int,
        session_id: str,
    ) -> list[dict]:
        """세부내역 시트를 파싱하여 정규화된 항목 리스트 반환"""
        rows = parse_detail_sheet(file_path, sheet_name, column_mapping, data_start_row)

        items = []
        for row in rows:
            item = {
                "session_id": session_id,
                "item_name_raw": row["item_name_raw"],
                "source_sheet": row["source_sheet"],
                "source_row": row["source_row"],
                "spec": row.get("spec"),
                "unit": row.get("unit"),
                "review_flag": False,
            }

            # 숫자 필드 안전 변환
            for field in ("qty", "unit_price", "amount", "material_cost", "labor_cost", "expense_cost"):
                val = row.get(field)
                if val is not None:
                    try:
                        item[field] = float(val)
                    except (ValueError, TypeError):
                        item[field] = None

            items.append(item)

        return items

    def save_to_db(self, items: list[dict]) -> int:
        """정규화된 항목을 estimate_line_items에 배치 삽입"""
        if not items:
            return 0

        db = get_db()
        BATCH_SIZE = 50
        inserted = 0

        for i in range(0, len(items), BATCH_SIZE):
            batch = items[i : i + BATCH_SIZE]
            # None 값 필드 정리
            clean_batch = []
            for item in batch:
                clean = {k: v for k, v in item.items() if v is not None}
                # 필수 필드 보장
                clean["session_id"] = item["session_id"]
                clean["item_name_raw"] = item["item_name_raw"]
                clean["source_sheet"] = item["source_sheet"]
                clean["source_row"] = item["source_row"]
                clean["review_flag"] = item.get("review_flag", False)
                clean_batch.append(clean)

            db.table("estimate_line_items").insert(clean_batch).execute()
            inserted += len(clean_batch)

        return inserted
