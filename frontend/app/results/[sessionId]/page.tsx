"use client";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { getSession, exportSession, type SessionStatus } from "@/lib/api";

export default function ResultsPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [session, setSession] = useState<SessionStatus | null>(null);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) return;

    const fetchAndPoll = async () => {
      const data = await getSession(sessionId);
      setSession(data);

      // PROCESSING 상태면 2초 간격 폴링 (최대 90초)
      if (data.status === "PROCESSING" || data.status === "PENDING") {
        let attempts = 0;
        const timer = setInterval(async () => {
          attempts++;
          try {
            const updated = await getSession(sessionId);
            setSession(updated);
            if (updated.status !== "PROCESSING" && updated.status !== "PENDING") {
              clearInterval(timer);
            }
          } catch {
            clearInterval(timer);
          }
          if (attempts >= 45) clearInterval(timer);
        }, 2000);
        return () => clearInterval(timer);
      }
    };

    fetchAndPoll();
  }, [sessionId]);

  const handleDownload = async () => {
    setExporting(true);
    setError("");
    try {
      const res = await exportSession(sessionId);
      setDownloadUrl(res.download_url);
      window.open(res.download_url, "_blank");
    } catch (err) {
      setError(err instanceof Error ? err.message : "내보내기 실패");
    } finally {
      setExporting(false);
    }
  };

  if (!session) {
    return (
      <div className="max-w-2xl mx-auto px-6 py-12 text-center">
        <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto px-6 py-12 space-y-8">
      <div className="text-center space-y-2">
        <div className="text-5xl">
          {session.status === "DONE" ? "✅" : "⏳"}
        </div>
        <h2 className="text-2xl font-bold text-gray-900">
          {session.status === "DONE" ? "처리 완료" : "처리 중"}
        </h2>
      </div>

      {/* 요약 */}
      <div className="bg-white rounded-xl border p-6 space-y-3">
        <div className="grid grid-cols-2 gap-4 text-sm">
          {session.brand_name && (
            <div>
              <p className="text-gray-500">브랜드</p>
              <p className="font-medium">{session.brand_name}</p>
            </div>
          )}
          <div>
            <p className="text-gray-500">총 항목 수</p>
            <p className="font-medium">{session.total_items}개</p>
          </div>
          <div>
            <p className="text-gray-500">미확인 항목</p>
            <p className="font-medium">{session.review_items}개</p>
          </div>
          <div>
            <p className="text-gray-500">상태</p>
            <p className="font-medium">{session.status}</p>
          </div>
        </div>
      </div>

      {/* 컨펌 대기 안내 */}
      {session.status === "CONFIRM_WAIT" && (
        <div className="space-y-3">
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-sm text-yellow-800">
            {session.review_items}개 항목의 공정 분류를 확인해야 합니다.
          </div>
          <Link
            href={`/confirm/${sessionId}`}
            className="block w-full py-3 bg-yellow-500 hover:bg-yellow-600 text-white rounded-xl font-medium text-center"
          >
            공정 분류 확인하기 →
          </Link>
        </div>
      )}

      {/* 다운로드 */}
      {session.status === "DONE" && (
        <div className="space-y-3">
          <button
            onClick={handleDownload}
            disabled={exporting}
            className="w-full py-3 bg-blue-600 text-white rounded-xl font-medium hover:bg-blue-700 disabled:opacity-50"
          >
            {exporting ? "내보내기 중..." : "결과 파일 다운로드"}
          </button>
          {downloadUrl && (
            <a
              href={downloadUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="block text-center text-sm text-blue-600 underline"
            >
              다운로드 링크 열기
            </a>
          )}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}

      {/* 새 파일 */}
      <div className="text-center pt-4">
        <Link
          href="/upload"
          className="text-blue-600 hover:text-blue-800 text-sm font-medium"
        >
          새 파일 처리하기 &rarr;
        </Link>
      </div>
    </div>
  );
}
