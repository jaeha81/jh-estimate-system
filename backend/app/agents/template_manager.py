"""브랜드 프로필 관리 + 엑셀 템플릿 감지"""

from app.models.db import get_db
from app.services.excel_service import get_sheet_names


class TemplateManager:
    """brand_profiles 테이블과 엑셀 파일을 연결"""

    def get_brand_profile(self, brand_name: str) -> dict | None:
        """brand_name으로 프로필 조회"""
        db = get_db()
        result = (
            db.table("brand_profiles")
            .select("*")
            .eq("brand_name", brand_name)
            .execute()
        )
        if result.data:
            return result.data[0]
        return None

    def get_all_profiles(self) -> list[dict]:
        """전체 프로필 조회"""
        db = get_db()
        result = db.table("brand_profiles").select("*").execute()
        return result.data or []

    def detect_brand(self, file_path: str) -> str | None:
        """시트 이름 패턴으로 브랜드 자동 감지"""
        sheet_names = get_sheet_names(file_path)
        sheet_set = {s.lower().strip() for s in sheet_names}

        profiles = self.get_all_profiles()
        best_match = None
        best_score = 0

        for profile in profiles:
            mapping = profile.get("sheet_mapping", {})
            score = 0
            for key, expected_sheet in mapping.items():
                if expected_sheet.lower().strip() in sheet_set:
                    score += 1
            if score > best_score:
                best_score = score
                best_match = profile["brand_name"]

        return best_match if best_score > 0 else None

    def get_detail_sheet_info(
        self, file_path: str, profile: dict
    ) -> tuple[str, dict, int]:
        """프로필 기반 세부내역 시트 정보 반환

        Returns:
            (sheet_name, column_mapping, data_start_row)
        """
        sheet_mapping = profile.get("sheet_mapping", {})
        column_mapping = profile.get("column_mapping", {})
        data_start_row = int(column_mapping.pop("data_start_row", 5))

        # 세부내역 시트 이름 결정
        detail_sheet_name = sheet_mapping.get("세부내역", "세부내역서")

        # 실제 시트 이름 매칭
        actual_sheets = get_sheet_names(file_path)
        matched = None
        for s in actual_sheets:
            if detail_sheet_name.lower() in s.lower():
                matched = s
                break

        if not matched:
            # 폴백: 첫 번째 시트 제외 나머지 중 첫 번째
            matched = actual_sheets[1] if len(actual_sheets) > 1 else actual_sheets[0]

        return matched, column_mapping, data_start_row
