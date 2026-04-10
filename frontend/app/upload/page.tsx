"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UploadZone } from "@/components/UploadZone";
import { createSession, getSession, getBrands, type BrandProfile } from "@/lib/api";

export default function UploadPage() {
  const router = useRouter();
  const [brands, setBrands] = useState<BrandProfile[]>([]);
  const [selectedBrand, setSelectedBrand] = useState("");
  const [aiMode, setAiMode] = useState<"api" | "mock">("mock");
  const [isUploading, setIsUploading] = useState(false);
  const [statusMessage, setStatusMessage] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getBrands()
      .then((res) => setBrands(res.brands))
      .catch(() => {});
  }, []);

  const handleFileSelect = useCallback(
    async (file: File) => {
      setIsUploading(true);
      setError("");
      setStatusMessage("파일 업로드 중...");

      try {
        const { session_id } = await createSession(
          file,
          selectedBrand || undefined,
          aiMode
        );
        setStatusMessage("AI 분류 처리 중...");

        // 2초 간격 폴링 (최대 60초)
        let attempts = 0;
        const maxAttempts = 30;

        const poll = setInterval(async () => {
          attempts++;
          try {
            const session = await getSession(session_id);
            setStatusMessage(
              `처리 중... (${session.total_items}개 항목 감지)`
            );

            if (session.status === "CONFIRM_WAIT") {
              clearInterval(poll);
              router.push(`/confirm/${session_id}`);
            } else if (session.status === "DONE") {
              clearInterval(poll);
              router.push(`/results/${session_id}`);
            } else if (session.status === "ERROR") {
              clearInterval(poll);
              setError(session.error_message || "처리 중 오류 발생");
              setIsUploading(false);
            }

            if (attempts >= maxAttempts) {
              clearInterval(poll);
              setError("처리 시간 초과. 잠시 후 다시 시도해주세요.");
              setIsUploading(false);
            }
          } catch {
            clearInterval(poll);
            setError("상태 조회 실패");
            setIsUploading(false);
          }
        }, 2000);
      } catch (err) {
        setError(err instanceof Error ? err.message : "업로드 실패");
        setIsUploading(false);
      }
    },
    [selectedBrand, aiMode, router]
  );

  return (
    <div className="max-w-2xl mx-auto px-6 py-12 space-y-8">
      <div>
        <h2 className="text-2xl font-bold text-gray-900">견적 파일 업로드</h2>
        <p className="text-gray-600 mt-1">
          엑셀 견적서를 업로드하면 AI가 공정을 자동 분류합니다.
        </p>
      </div>

      {/* 브랜드 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          브랜드 선택 (선택사항)
        </label>
        <select
          value={selectedBrand}
          onChange={(e) => setSelectedBrand(e.target.value)}
          disabled={isUploading}
          className="w-full border rounded-lg px-4 py-2.5 text-sm"
        >
          <option value="">자동 감지</option>
          {brands.map((b) => (
            <option key={b.id} value={b.brand_name}>
              {b.brand_name}
            </option>
          ))}
        </select>
      </div>

      {/* AI 모드 선택 */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          AI 분류 모드
        </label>
        <div className="flex gap-3">
          <button
            type="button"
            onClick={() => setAiMode("mock")}
            disabled={isUploading}
            className={`flex-1 px-4 py-3 rounded-lg border-2 text-sm font-medium transition-colors ${
              aiMode === "mock"
                ? "border-blue-600 bg-blue-50 text-blue-700"
                : "border-gray-200 text-gray-600 hover:border-gray-300"
            }`}
          >
            <div className="font-semibold">테스트 모드</div>
            <div className="text-xs mt-0.5 font-normal opacity-75">
              키워드 사전만 사용 · API 크레딧 미사용
            </div>
          </button>
          <button
            type="button"
            onClick={() => setAiMode("api")}
            disabled={isUploading}
            className={`flex-1 px-4 py-3 rounded-lg border-2 text-sm font-medium transition-colors ${
              aiMode === "api"
                ? "border-green-600 bg-green-50 text-green-700"
                : "border-gray-200 text-gray-600 hover:border-gray-300"
            }`}
          >
            <div className="font-semibold">Claude AI 모드</div>
            <div className="text-xs mt-0.5 font-normal opacity-75">
              미매칭 항목 Claude API 분류 · 프로덕션용
            </div>
          </button>
        </div>
      </div>

      {/* 업로드 존 */}
      <UploadZone onFileSelect={handleFileSelect} disabled={isUploading} />

      {/* 상태 메시지 */}
      {isUploading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-blue-600 border-t-transparent mb-3" />
          <p className="text-gray-700">{statusMessage}</p>
        </div>
      )}

      {/* 에러 */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-700 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
}
