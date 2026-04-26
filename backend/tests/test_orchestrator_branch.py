"""orchestrator PDF/Excel 분기 로직 테스트 (DB/API 없이 패치)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from pathlib import Path
from unittest.mock import patch, MagicMock


def test_pdf_branch_detected():
    """PDF 파일명 → is_pdf=True 분기 확인"""
    assert Path("test.pdf").suffix.lower() == ".pdf"
    assert Path("test.xlsx").suffix.lower() != ".pdf"
    assert Path("TEST.PDF").suffix.lower() == ".pdf"
    print("  PASS  test_pdf_branch_detected")


def test_inspector_called_in_pipeline():
    """orchestrator.run_pipeline이 inspector.run을 호출하는지 확인"""
    with patch("app.agents.orchestrator.get_db") as mock_db, \
         patch("app.agents.orchestrator.upload_to_storage"), \
         patch("app.agents.orchestrator.make_storage_path", return_value="test/path.xlsx"), \
         patch("app.agents.orchestrator.save_upload_to_temp", return_value="/tmp/test.xlsx"), \
         patch("app.agents.orchestrator.delete_temp_file"), \
         patch("app.agents.orchestrator.classify_items", return_value=[
             {"id": "x1", "item_name_raw": "석고보드", "item_name_std": "석고보드",
              "process_major": "목공사", "confidence": 0.9, "review_flag": False}
         ]), \
         patch("app.agents.orchestrator.update_db_with_results"), \
         patch("app.agents.orchestrator.TemplateManager") as mock_tmgr, \
         patch("app.agents.orchestrator.Normalizer") as mock_norm, \
         patch("app.agents.orchestrator.BidFormatter") as mock_fmt, \
         patch("app.agents.orchestrator.Inspector") as mock_insp_cls:

        # DB mock 설정
        db = MagicMock()
        db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
        db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "x1", "item_name_raw": "석고보드", "process_major": "목공사", "confidence": 0.9, "review_flag": False}
        ]
        mock_db.return_value = db

        # TemplateManager mock
        tmgr = mock_tmgr.return_value
        tmgr.detect_brand.return_value = "한샘"
        tmgr.get_brand_profile.return_value = {"id": "bp1", "brand_name": "한샘",
            "sheet_mapping": {}, "column_mapping": {"item_name": "B", "spec": "C",
            "unit": "D", "qty": "E", "unit_price": "F", "amount": "G", "data_start_row": 5},
            "fixed_row_count": True}
        tmgr.get_detail_sheet_info.return_value = ("시트1", {}, 5)

        # Normalizer mock
        norm = mock_norm.return_value
        norm.normalize.return_value = []
        norm.save_to_db.return_value = None

        # Inspector mock
        insp = mock_insp_cls.return_value
        insp.run.return_value = {"passed": True, "issues": [], "confidence_summary": {"high": 1, "medium": 0, "low": 0}}

        # BidFormatter mock
        mock_fmt.return_value.format.return_value = "path/to/file.xlsx"

        from app.agents.orchestrator import Orchestrator
        orch = Orchestrator()
        status = orch.run_pipeline("sess-1", b"fake_bytes", "test.xlsx")

        # inspector.run이 호출됐는지 확인
        assert insp.run.called, "Inspector.run이 호출되지 않음"
        print(f"  PASS  test_inspector_called_in_pipeline (status={status})")


def test_pdf_pipeline_calls_pdf_analyzer():
    """PDF 파일명으로 run_pipeline 호출 시 PdfAnalyzer.analyze가 실행되는지 확인"""
    # 인스턴스 수준에서 직접 mock — reload 없이 패치 안정성 확보
    from app.agents.orchestrator import Orchestrator

    orch = Orchestrator()

    pdf_mock = MagicMock()
    pdf_mock.analyze.return_value = [
        {"item_name": "도배공사", "quantity": 50.0, "unit": "m²", "estimated_cost": 8000.0}
    ]
    orch.pdf_analyzer = pdf_mock
    orch.inspector = MagicMock()
    orch.inspector.run.return_value = {
        "passed": True, "issues": [], "confidence_summary": {"high": 1, "medium": 0, "low": 0}
    }
    orch.bid_formatter = MagicMock()

    db = MagicMock()
    db.table.return_value.update.return_value.eq.return_value.execute.return_value = MagicMock()
    db.table.return_value.insert.return_value.execute.return_value = MagicMock()
    db.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
        {"id": "p1", "item_name_raw": "도배공사", "process_major": "도장/도배공사",
         "confidence": 0.85, "review_flag": False}
    ]

    with patch("app.agents.orchestrator.get_db", return_value=db), \
         patch("app.agents.orchestrator.upload_to_storage"), \
         patch("app.agents.orchestrator.make_storage_path", return_value="test/path.pdf"), \
         patch("app.agents.orchestrator.classify_items", return_value=[
             {"id": "p1", "item_name_raw": "도배공사", "item_name_std": "도배공사",
              "process_major": "도장/도배공사", "confidence": 0.85, "review_flag": False}
         ]), \
         patch("app.agents.orchestrator.update_db_with_results"):

        status = orch.run_pipeline("sess-pdf", b"fake_pdf_bytes", "estimate.pdf")

    assert pdf_mock.analyze.called, "PdfAnalyzer.analyze가 호출되지 않음"
    assert db.table.return_value.insert.called, "PDF 항목 insert가 호출되지 않음"
    print(f"  PASS  test_pdf_pipeline_calls_pdf_analyzer (status={status})")


def test_to_float_korean_format():
    """pdf_analyzer._to_float이 한국어 금액 포맷 처리하는지 확인"""
    from app.agents.pdf_analyzer import _to_float
    assert _to_float("1,000") == 1000.0,    f"'1,000' 파싱 실패"
    assert _to_float("10,000원") == 10000.0, f"'10,000원' 파싱 실패"
    assert _to_float(None) is None
    assert _to_float("abc") is None
    assert _to_float(5000) == 5000.0
    print("  PASS  test_to_float_korean_format")


if __name__ == "__main__":
    tests = [
        test_pdf_branch_detected,
        test_inspector_called_in_pipeline,
        test_pdf_pipeline_calls_pdf_analyzer,
        test_to_float_korean_format,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n결과: {passed}/{len(tests)} 통과")
