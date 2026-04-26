"""pdf_analyzer.py 단위 테스트 — anthropic 클라이언트 mock"""
import sys, os, json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from unittest.mock import patch, MagicMock


def _make_mock_client(response_json: list):
    """anthropic.Anthropic mock 반환"""
    client = MagicMock()
    msg = MagicMock()
    msg.content = [MagicMock(text=json.dumps(response_json))]
    client.messages.create.return_value = msg
    return client


def test_normal_response():
    """정상 응답 파싱"""
    expected = [
        {"item_name": "석고보드 9.5T", "quantity": 100.0, "unit": "m²", "estimated_cost": 8500.0},
        {"item_name": "페인트 도장", "quantity": 80.0, "unit": "m²", "estimated_cost": 5000.0},
    ]
    with patch("app.agents.pdf_analyzer.anthropic.Anthropic", return_value=_make_mock_client(expected)):
        from app.agents.pdf_analyzer import PdfAnalyzer
        analyzer = PdfAnalyzer()
        result = analyzer.analyze(b"fake_pdf_bytes", "test.pdf")
    assert len(result) == 2, f"expected 2 items, got {len(result)}"
    assert result[0]["item_name"] == "석고보드 9.5T"
    assert result[0]["quantity"] == 100.0
    assert result[1]["unit"] == "m²"
    print("  PASS  test_normal_response")


def test_null_fields():
    """수량·단가 null 처리"""
    expected = [{"item_name": "잡공사", "quantity": None, "unit": None, "estimated_cost": None}]
    with patch("app.agents.pdf_analyzer.anthropic.Anthropic", return_value=_make_mock_client(expected)):
        from app.agents.pdf_analyzer import PdfAnalyzer
        result = PdfAnalyzer().analyze(b"fake", "doc.pdf")
    assert result[0]["quantity"] is None
    assert result[0]["unit"] is None
    print("  PASS  test_null_fields")


def test_api_error_returns_empty():
    """API 오류 시 빈 리스트 반환 (파이프라인 비중단)"""
    client = MagicMock()
    client.messages.create.side_effect = Exception("API timeout")
    with patch("app.agents.pdf_analyzer.anthropic.Anthropic", return_value=client):
        from app.agents.pdf_analyzer import PdfAnalyzer
        result = PdfAnalyzer().analyze(b"fake", "error.pdf")
    assert result == [], f"expected [], got {result}"
    print("  PASS  test_api_error_returns_empty")


def test_codeblock_stripped():
    """```json 코드블록 자동 제거"""
    raw = '```json\n[{"item_name": "타일공사", "quantity": 50, "unit": "m²", "estimated_cost": 12000}]\n```'
    client = MagicMock()
    msg = MagicMock()
    msg.content = [MagicMock(text=raw)]
    client.messages.create.return_value = msg
    with patch("app.agents.pdf_analyzer.anthropic.Anthropic", return_value=client):
        from app.agents.pdf_analyzer import PdfAnalyzer
        result = PdfAnalyzer().analyze(b"fake", "test.pdf")
    assert len(result) == 1
    assert result[0]["item_name"] == "타일공사"
    print("  PASS  test_codeblock_stripped")


def test_invalid_json_returns_empty():
    """JSON 파싱 실패 시 빈 리스트"""
    client = MagicMock()
    msg = MagicMock()
    msg.content = [MagicMock(text="이것은 JSON이 아닙니다")]
    client.messages.create.return_value = msg
    with patch("app.agents.pdf_analyzer.anthropic.Anthropic", return_value=client):
        from app.agents.pdf_analyzer import PdfAnalyzer
        result = PdfAnalyzer().analyze(b"fake", "bad.pdf")
    assert result == []
    print("  PASS  test_invalid_json_returns_empty")


def test_missing_item_name_filtered():
    """item_name 없는 항목 필터링"""
    expected = [
        {"item_name": "정상항목", "quantity": 1, "unit": "식", "estimated_cost": 100000},
        {"quantity": 5, "unit": "m²", "estimated_cost": 5000},  # item_name 없음
    ]
    with patch("app.agents.pdf_analyzer.anthropic.Anthropic", return_value=_make_mock_client(expected)):
        from app.agents.pdf_analyzer import PdfAnalyzer
        result = PdfAnalyzer().analyze(b"fake", "test.pdf")
    assert len(result) == 1, f"item_name 없는 항목이 필터링되지 않음: {result}"
    print("  PASS  test_missing_item_name_filtered")


if __name__ == "__main__":
    # 모듈 재임포트 문제 방지를 위해 순서대로 실행
    tests = [test_normal_response, test_null_fields, test_api_error_returns_empty,
             test_codeblock_stripped, test_invalid_json_returns_empty, test_missing_item_name_filtered]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n결과: {passed}/{len(tests)} 통과")
