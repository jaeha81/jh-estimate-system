import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "JH 견적시스템",
  description: "인테리어 견적 AI 에이전트 자동화 시스템",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="ko"
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col bg-gray-50">
        <header className="bg-white border-b px-6 py-4">
          <div className="max-w-4xl mx-auto flex items-center gap-3">
            <h1 className="text-xl font-bold text-gray-900">JH 견적시스템</h1>
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
              MVP
            </span>
          </div>
        </header>
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
