"""PDF 분석 에이전트 — PDF → Claude API → 공정 항목 리스트 추출"""

import base64
import logging
import os

import anthropic

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = """당신은 한국 인테리어/건설 견적 PDF 분석 전문가입니다.

## 역할
PDF 문서에서 공정 항목을 추출해 구조화된 JSON으로 반환합니다.

## 출력 형식
JSON 배열만 반환합니다 (설명 텍스트 없음):
[
  {
    "item_name": "항목명",
    "quantity": 수량(숫자 또는 null),
    "unit": "단위(ea/m²/m/식 등 또는 null)",
    "estimated_cost": 예상단가(숫자 또는 null)
  }
]

## 처리 규칙
- 합계/소계/부가세 행은 제외
- 수량·단가가 명시되지 않으면 null 처리
- 항목명은 원문 그대로 유지 (정규화 불필요)
- 표가 없는 일반 문서면 빈 배열 반환
"""


class PdfAnalyzer:
    """PDF 파일에서 공정 항목을 추출하는 에이전트"""

    def __init__(self):
        self._client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY", ""))
        self._model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

    def analyze(self, file_bytes: bytes, filename: str = "document.pdf") -> list[dict]:
        """PDF 바이트 → 공정 항목 리스트 반환.

        오류 발생 시 빈 리스트 반환 (파이프라인 비중단).
        """
        try:
            return self._call_api(file_bytes, filename)
        except Exception as e:
            logger.error(f"[pdf_analyzer] 분석 실패 ({filename}): {e}")
            return []

    def _call_api(self, file_bytes: bytes, filename: str) -> list[dict]:
        import json

        pdf_b64 = base64.standard_b64encode(file_bytes).decode("utf-8")

        message = self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=_SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "document",
                            "source": {
                                "type": "base64",
                                "media_type": "application/pdf",
                                "data": pdf_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": f"위 PDF({filename})에서 공정 항목을 추출해 JSON 배열로 반환하세요.",
                        },
                    ],
                }
            ],
        )

        raw = message.content[0].text.strip()

        # 코드블록 제거
        if raw.startswith("```"):
            lines = raw.splitlines()
            raw = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

        items = json.loads(raw)

        if not isinstance(items, list):
            return []

        # 필수 필드 보정
        result = []
        for item in items:
            if not isinstance(item, dict) or not item.get("item_name"):
                continue
            result.append(
                {
                    "item_name": str(item["item_name"]),
                    "quantity": _to_float(item.get("quantity")),
                    "unit": item.get("unit") or None,
                    "estimated_cost": _to_float(item.get("estimated_cost")),
                }
            )
        return result


def _to_float(value) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
