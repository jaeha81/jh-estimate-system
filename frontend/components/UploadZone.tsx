"use client";

import { useCallback, useState } from "react";

interface UploadZoneProps {
  onFileSelect: (file: File) => void;
  disabled?: boolean;
}

export function UploadZone({ onFileSelect, disabled }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setIsDragging(false);
      if (disabled) return;

      const file = e.dataTransfer.files[0];
      if (file && isValidFile(file)) {
        setFileName(file.name);
        onFileSelect(file);
      }
    },
    [onFileSelect, disabled]
  );

  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file && isValidFile(file)) {
        setFileName(file.name);
        onFileSelect(file);
      }
    },
    [onFileSelect]
  );

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setIsDragging(true);
      }}
      onDragLeave={() => setIsDragging(false)}
      onDrop={handleDrop}
      className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors cursor-pointer ${
        isDragging
          ? "border-blue-500 bg-blue-50"
          : "border-gray-300 hover:border-gray-400"
      } ${disabled ? "opacity-50 cursor-not-allowed" : ""}`}
    >
      <label className="cursor-pointer block">
        <input
          type="file"
          accept=".xlsx,.xls"
          onChange={handleChange}
          className="hidden"
          disabled={disabled}
        />
        <div className="space-y-3">
          <div className="text-4xl">📂</div>
          {fileName ? (
            <p className="text-lg font-medium text-green-700">{fileName}</p>
          ) : (
            <>
              <p className="text-lg font-medium text-gray-700">
                견적 파일을 드래그하거나 클릭하세요
              </p>
              <p className="text-sm text-gray-500">
                .xlsx, .xls (최대 50MB)
              </p>
            </>
          )}
        </div>
      </label>
    </div>
  );
}

function isValidFile(file: File): boolean {
  const ext = file.name.toLowerCase().split(".").pop();
  return ext === "xlsx" || ext === "xls";
}
