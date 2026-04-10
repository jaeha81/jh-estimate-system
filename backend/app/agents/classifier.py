"""공정 분류 에이전트 — keyword_dict 우선 + Claude API 보조"""

import csv
import json
import os
from functools import lru_cache
from pathlib import Path

import anthropic

from app.models.db import get_db

# 로컬 CSV 폴백 경로 (Supabase 연결 불가 시 사용)
_LOCAL_CSV = Path(__file__).parent.parent.parent.parent / "docs" / "phase0" / "keyword_dict_v1.csv"

CONFIDENCE_THRESHOLD = float(os.getenv("CONFIDENCE_THRESHOLD", "0.7"))

SYSTEM_PROMPT = """당신은 한국 인테리어/건설 공정 분류 전문가입니다.

## ① 역할
품명(item_name_raw)을 받아 대공종(process_major)과 세부공정(process_minor)으로 분류합니다.

## ② 입력
JSON 배열: [{"id": "uuid", "item_name_raw": "품명", "spec": "규격"}]

## ③ 출력
JSON 배열: [{"id": "uuid", "process_major": "대공종", "process_minor": "세부공정", "item_name_std": "표준품명", "confidence": 0.0~1.0}]

## ④ 처리 규칙
- 대공종 목록: 철거공사, 목공사, 도장/도배공사, 타일공사, 석공사, 바닥공사, 위생/설비공사, 전기공사, 설비공사, 유리공사, 창호공사, 주방공사, 가구공사, 잡공사, 운반/양중비, 폐기물처리, 가설공사, 안전관리비, 보험료, 일반관리비, 이윤, 부가가치세
- confidence: 확실=0.9~1.0, 높음=0.7~0.89, 보통=0.4~0.69, 낮음=0.0~0.39
- item_name_std: 원본을 표준화한 이름 (예: "석고보드 9.5T 붙임" → "석고보드 9.5T")

## ⑤ 금지 사항
- 목록에 없는 대공종 사용 금지
- 확신 없으면 confidence 낮게 설정 (임의 추정 금지)

## ⑥ 참고 데이터
아래 키워드 사전을 우선 참조하세요:
{keyword_dict_json}

## ⑦ 예외 처리
- 분류 불가 시: process_major="미분류", confidence=0.1
- 합계/소계 행: 무시 (빈 배열 반환)
"""


@lru_cache(maxsize=1)
def _load_keyword_dict() -> dict[str, dict]:
    """keyword_dict 테이블 전체를 메모리 캐시. DB 연결 실패 시 로컬 CSV 폴백."""
    try:
        db = get_db()
        result = db.table("keyword_dict").select("keyword, process_major, process_minor").execute()
        if result.data:
            mapping = {}
            for row in result.data:
                mapping[row["keyword"].strip()] = {
                    "process_major": row["process_major"],
                    "process_minor": row.get("process_minor"),
                }
            return mapping
    except Exception:
        pass

    # 로컬 CSV 폴백
    if _LOCAL_CSV.exists():
        mapping = {}
        with open(_LOCAL_CSV, encoding="utf-8") as f:
            for row in csv.DictReader(f):
                keyword = row.get("keyword", "").strip()
                if keyword:
                    mapping[keyword] = {
                        "process_major": row.get("process_major", "미분류"),
                        "process_minor": row.get("process_minor") or None,
                    }
        return mapping

    return {}


def _match_keyword(item_name: str, kw_dict: dict) -> dict | None:
    """키워드 사전 정확 매칭"""
    name = item_name.strip()
    # 정확 매칭
    if name in kw_dict:
        return kw_dict[name]
    # 부분 매칭 (키워드가 품명에 포함)
    for keyword, mapping in kw_dict.items():
        if keyword in name:
            return mapping
    return None


def classify_items(items: list[dict], ai_mode: str = "api") -> list[dict]:
    """1단계: keyword_dict 매칭 → 2단계: 미매칭 처리 (ai_mode에 따라 분기)

    ai_mode:
        "api"  — 미매칭 항목을 Claude API로 분류 (프로덕션)
        "mock" — 미매칭 항목을 review_flag=True로 표시, API 미사용 (개발/테스트)
    """
    kw_dict = _load_keyword_dict()

    matched = []
    unmatched = []

    for item in items:
        name = item.get("item_name_raw", "")
        result = _match_keyword(name, kw_dict)
        if result:
            item["process_major"] = result["process_major"]
            item["process_minor"] = result.get("process_minor")
            item["item_name_std"] = name
            item["confidence"] = 1.0
            item["review_flag"] = False
            matched.append(item)
        else:
            unmatched.append(item)

    if unmatched:
        if ai_mode == "mock":
            # Mock 모드: API 미사용, 미매칭 항목은 사용자 확인 대기
            for item in unmatched:
                item["process_major"] = "미분류"
                item["process_minor"] = None
                item["item_name_std"] = item["item_name_raw"]
                item["confidence"] = 0.0
                item["review_flag"] = True
            matched.extend(unmatched)
        else:
            # API 모드: Claude로 분류
            classified = _classify_with_claude(unmatched, kw_dict)
            for item in classified:
                conf = item.get("confidence", 0)
                item["review_flag"] = conf < CONFIDENCE_THRESHOLD
                matched.append(item)

    return matched


def _classify_with_claude(items: list[dict], kw_dict: dict) -> list[dict]:
    """Claude API 배치 분류"""
    api_key = os.getenv("CLAUDE_API_KEY")
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

    if not api_key:
        # API 키 없으면 모두 미분류 처리
        for item in items:
            item["process_major"] = "미분류"
            item["process_minor"] = None
            item["item_name_std"] = item["item_name_raw"]
            item["confidence"] = 0.1
            item["review_flag"] = True
        return items

    client = anthropic.Anthropic(api_key=api_key)

    # 키워드 사전 전체를 프롬프트에 주입 (기존 30개 제한 제거)
    system = SYSTEM_PROMPT.replace("{keyword_dict_json}", json.dumps(kw_dict, ensure_ascii=False))

    # 입력 준비
    input_data = [
        {"id": item.get("id", ""), "item_name_raw": item["item_name_raw"], "spec": item.get("spec", "")}
        for item in items
    ]

    # 배치 (최대 30개씩)
    BATCH = 30
    all_results = []

    for i in range(0, len(input_data), BATCH):
        batch = input_data[i : i + BATCH]
        response = client.messages.create(
            model=model,
            max_tokens=4096,
            system=system,
            messages=[
                {
                    "role": "user",
                    "content": f"다음 품명들을 분류해주세요:\n{json.dumps(batch, ensure_ascii=False)}",
                }
            ],
        )

        text = response.content[0].text
        # JSON 추출
        try:
            # ```json ... ``` 블록 추출
            if "```" in text:
                json_str = text.split("```")[1]
                if json_str.startswith("json"):
                    json_str = json_str[4:]
                results = json.loads(json_str.strip())
            else:
                results = json.loads(text.strip())
            all_results.extend(results)
        except (json.JSONDecodeError, IndexError):
            # 파싱 실패 시 미분류 처리
            for b in batch:
                all_results.append({
                    "id": b["id"],
                    "process_major": "미분류",
                    "process_minor": None,
                    "item_name_std": b["item_name_raw"],
                    "confidence": 0.1,
                })

    # 결과를 원본 items에 병합
    result_map = {r["id"]: r for r in all_results}
    for item in items:
        item_id = item.get("id", "")
        if item_id in result_map:
            r = result_map[item_id]
            item["process_major"] = r.get("process_major", "미분류")
            item["process_minor"] = r.get("process_minor")
            item["item_name_std"] = r.get("item_name_std", item["item_name_raw"])
            item["confidence"] = r.get("confidence", 0.5)
        else:
            item["process_major"] = "미분류"
            item["process_minor"] = None
            item["item_name_std"] = item["item_name_raw"]
            item["confidence"] = 0.1

    return items


def update_db_with_results(items: list[dict]) -> int:
    """분류 결과를 estimate_line_items에 업데이트"""
    db = get_db()
    updated = 0
    for item in items:
        item_id = item.get("id")
        if not item_id:
            continue
        db.table("estimate_line_items").update({
            "process_major": item.get("process_major"),
            "process_minor": item.get("process_minor"),
            "item_name_std": item.get("item_name_std"),
            "confidence": item.get("confidence"),
            "review_flag": item.get("review_flag", False),
        }).eq("id", item_id).execute()
        updated += 1
    return updated
