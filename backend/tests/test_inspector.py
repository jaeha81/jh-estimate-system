"""inspector.py 단위 테스트 — API 호출 없음"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.agents.inspector import Inspector


def make_item(id_, name, major, confidence):
    return {
        "id": id_,
        "item_name_raw": name,
        "item_name_std": name,
        "process_major": major,
        "confidence": confidence,
        "review_flag": confidence < 0.7,
    }


def test_pass_all_high():
    """모든 항목 신뢰도 높음 → passed=True, issues 없음"""
    items = [make_item(f"id-{i}", f"품목{i}", "목공사", 0.9) for i in range(5)]
    result = Inspector().run(items)
    assert result["passed"] is True, f"expected passed=True, got {result}"
    assert result["issues"] == [], result["issues"]
    assert result["confidence_summary"]["high"] == 5


def test_fail_low_confidence():
    """신뢰도 0.3 항목 → passed=False, issues에 등록"""
    items = [
        make_item("id-1", "철거공사", "철거공사", 0.9),
        make_item("id-2", "불명항목", "미분류", 0.2),
    ]
    result = Inspector().run(items)
    assert result["passed"] is False, result
    issue_ids = [i["item_id"] for i in result["issues"]]
    assert "id-2" in issue_ids, issue_ids


def test_fail_missing_process():
    """process_major 없는 항목 → issues 등록"""
    items = [make_item("id-1", "?", "", 0.9)]
    result = Inspector().run(items)
    assert result["passed"] is False
    assert any("누락" in i["reason"] for i in result["issues"])


def test_duplicate_detection():
    """동일 품명 4회 이상 → 중복 이슈 등록"""
    items = [make_item(f"id-{i}", "석고보드", "목공사", 0.9) for i in range(4)]
    result = Inspector().run(items)
    assert result["passed"] is False
    assert any("중복" in i["reason"] for i in result["issues"])


def test_empty_items():
    """빈 리스트 → passed=True"""
    result = Inspector().run([])
    assert result["passed"] is True
    assert result["issues"] == []


if __name__ == "__main__":
    tests = [test_pass_all_high, test_fail_low_confidence, test_fail_missing_process,
             test_duplicate_detection, test_empty_items]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  FAIL  {t.__name__}: {e}")
    print(f"\n결과: {passed}/{len(tests)} 통과")
