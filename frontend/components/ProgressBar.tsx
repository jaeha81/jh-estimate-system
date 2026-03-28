"use client";

interface ProgressBarProps {
  value: number;
  total: number;
}

export function ProgressBar({ value, total }: ProgressBarProps) {
  const pct = total > 0 ? Math.round((value / total) * 100) : 0;

  return (
    <div className="w-full">
      <div className="flex justify-between text-sm text-gray-600 mb-1">
        <span>
          {value} / {total} 완료
        </span>
        <span>{pct}%</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className="bg-blue-600 h-3 rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}
