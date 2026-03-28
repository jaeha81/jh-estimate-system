"use client";

import { useState, useEffect, useCallback } from "react";
import { useParams, useRouter } from "next/navigation";
import { ConfirmCard } from "@/components/ConfirmCard";
import { ProgressBar } from "@/components/ProgressBar";
import { getItems, confirmItem, exportSession, type LineItem } from "@/lib/api";

export default function ConfirmPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const router = useRouter();
  const [items, setItems] = useState<LineItem[]>([]);
  const [currentIdx, setCurrentIdx] = useState(0);
  const [totalReview, setTotalReview] = useState(0);
  const [confirmed, setConfirmed] = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!sessionId) return;
    getItems(sessionId, true).then((res) => {
      setItems(res.items);
      setTotalReview(res.items.length);
      setLoading(false);
    });
  }, [sessionId]);

  const handleConfirm = useCallback(
    async (data: {
      process_major: string;
      process_minor?: string;
      item_name_std?: string;
    }) => {
      const item = items[currentIdx];
      await confirmItem(item.id, data);
      setConfirmed((c) => c + 1);

      if (currentIdx + 1 >= items.length) {
        // 모두 완료 → export
        try {
          await exportSession(sessionId);
        } catch {
          // export 실패해도 결과 페이지로 이동
        }
        router.push(`/results/${sessionId}`);
      } else {
        setCurrentIdx((i) => i + 1);
      }
    },
    [items, currentIdx, sessionId, router]
  );

  const handleSkip = useCallback(() => {
    if (currentIdx + 1 >= items.length) {
      router.push(`/results/${sessionId}`);
    } else {
      setCurrentIdx((i) => i + 1);
    }
  }, [currentIdx, items.length, sessionId, router]);

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
        <p className="text-gray-600 mt-4">항목 불러오는 중...</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="max-w-3xl mx-auto px-6 py-12 text-center">
        <p className="text-gray-600">확인이 필요한 항목이 없습니다.</p>
        <button
          onClick={() => router.push(`/results/${sessionId}`)}
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg"
        >
          결과 확인
        </button>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">공정 분류 확인</h2>
        <p className="text-gray-600 mt-1">
          AI가 분류한 결과를 검토하고 확정해주세요.
        </p>
      </div>

      <ProgressBar value={confirmed} total={totalReview} />

      <div className="text-sm text-gray-500">
        {currentIdx + 1} / {items.length} 항목
      </div>

      <ConfirmCard
        key={items[currentIdx].id}
        item={items[currentIdx]}
        onConfirm={handleConfirm}
        onSkip={handleSkip}
      />
    </div>
  );
}
