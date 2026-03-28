"use client";

import { useState } from "react";
import type { LineItem } from "@/lib/api";

const PROCESS_MAJORS = [
  "철거공사", "목공사", "도장/도배공사", "타일공사", "석공사",
  "바닥공사", "위생/설비공사", "전기공사", "설비공사", "유리공사",
  "창호공사", "주방공사", "가구공사", "잡공사", "운반/양중비",
  "폐기물처리", "가설공사", "안전관리비", "보험료", "일반관리비",
  "이윤", "부가가치세",
];

interface ConfirmCardProps {
  item: LineItem;
  onConfirm: (data: {
    process_major: string;
    process_minor?: string;
    item_name_std?: string;
  }) => void;
  onSkip: () => void;
}

export function ConfirmCard({ item, onConfirm, onSkip }: ConfirmCardProps) {
  const [major, setMajor] = useState(item.process_major || "");
  const [minor, setMinor] = useState(item.process_minor || "");
  const [stdName, setStdName] = useState(item.item_name_std || item.item_name_raw);

  const confidenceColor =
    (item.confidence ?? 0) >= 0.7
      ? "text-green-600 bg-green-50"
      : (item.confidence ?? 0) >= 0.4
        ? "text-orange-600 bg-orange-50"
        : "text-red-600 bg-red-50";

  return (
    <div className="border rounded-xl p-6 bg-white shadow-sm space-y-4">
      {/* 헤더 */}
      <div className="flex justify-between items-start">
        <div>
          <p className="text-sm text-gray-500">원본 품명 (행 {item.source_row})</p>
          <p className="text-lg font-semibold">{item.item_name_raw}</p>
          {item.spec && (
            <p className="text-sm text-gray-500">규격: {item.spec}</p>
          )}
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${confidenceColor}`}>
          신뢰도 {((item.confidence ?? 0) * 100).toFixed(0)}%
        </span>
      </div>

      {/* 입력 폼 */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            대공종
          </label>
          <select
            value={major}
            onChange={(e) => setMajor(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          >
            <option value="">선택하세요</option>
            {PROCESS_MAJORS.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            세부공정
          </label>
          <input
            type="text"
            value={minor}
            onChange={(e) => setMinor(e.target.value)}
            placeholder="세부공정 입력"
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            표준 품명
          </label>
          <input
            type="text"
            value={stdName}
            onChange={(e) => setStdName(e.target.value)}
            className="w-full border rounded-lg px-3 py-2 text-sm"
          />
        </div>
      </div>

      {/* 버튼 */}
      <div className="flex gap-3 justify-end">
        <button
          onClick={onSkip}
          className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800 border rounded-lg"
        >
          건너뛰기
        </button>
        <button
          onClick={() =>
            onConfirm({
              process_major: major,
              process_minor: minor || undefined,
              item_name_std: stdName || undefined,
            })
          }
          disabled={!major}
          className="px-6 py-2 text-sm text-white bg-blue-600 hover:bg-blue-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
        >
          확정
        </button>
      </div>
    </div>
  );
}
