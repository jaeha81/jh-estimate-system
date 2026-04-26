"""검수 에이전트 — classifier 분류 결과 품질 검수"""

import logging

logger = logging.getLogger(__name__)

# 검수 기준값
_LOW_CONFIDENCE = float(0.4)   # 이하면 낮은 신뢰도 이슈 등록
_DUP_THRESHOLD  = 3            # 동일 표준품명이 이 횟수 초과 시 중복 의심


class Inspector:
    """분류 결과를 검수해 이슈 리포트 반환"""

    def run(self, classified_items: list[dict]) -> dict:
        """검수 실행.

        Args:
            classified_items: classify_items() 반환값 (id, process_major,
                              item_name_std, confidence, review_flag 포함)

        Returns:
            {
                "passed": bool,
                "issues": [{"item_id": str, "reason": str}],
                "confidence_summary": {"high": int, "medium": int, "low": int},
            }
        """
        issues: list[dict] = []
        conf_summary = {"high": 0, "medium": 0, "low": 0}

        # 중복 탐지용 카운터
        name_counter: dict[str, list[str]] = {}

        for item in classified_items:
            item_id = str(item.get("id", ""))
            confidence = item.get("confidence", 1.0)
            process_major = item.get("process_major", "")
            std_name = item.get("item_name_std") or item.get("item_name_raw", "")

            # 신뢰도 분류
            if confidence >= 0.7:
                conf_summary["high"] += 1
            elif confidence >= _LOW_CONFIDENCE:
                conf_summary["medium"] += 1
            else:
                conf_summary["low"] += 1
                if item_id:
                    issues.append({
                        "item_id": item_id,
                        "reason": f"분류 신뢰도 낮음 ({confidence:.2f}) — 수동 확인 필요",
                    })

            # 공정 누락 검사
            if not process_major or process_major == "미분류":
                if item_id:
                    issues.append({
                        "item_id": item_id,
                        "reason": "공정 분류 누락 (process_major 없음)",
                    })

            # 중복 탐지 수집
            if std_name:
                name_counter.setdefault(std_name, [])
                if item_id:
                    name_counter[std_name].append(item_id)

        # 중복 의심 이슈 등록
        for name, ids in name_counter.items():
            if len(ids) > _DUP_THRESHOLD:
                for dup_id in ids:
                    issues.append({
                        "item_id": dup_id,
                        "reason": f"중복 의심: '{name}' 항목이 {len(ids)}회 등장",
                    })

        # item_id당 이슈 중복 제거 (같은 item_id에 여러 이슈 → 첫 번째만 유지)
        seen: set[str] = set()
        deduped: list[dict] = []
        for issue in issues:
            key = issue["item_id"]
            if key not in seen:
                seen.add(key)
                deduped.append(issue)

        passed = len(deduped) == 0

        logger.info(
            f"[inspector] 검수 완료 — 전체 {len(classified_items)}건 "
            f"| 이슈 {len(deduped)}건 | passed={passed}"
        )

        return {
            "passed": passed,
            "issues": deduped,
            "confidence_summary": conf_summary,
        }
