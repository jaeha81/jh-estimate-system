const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function fetchWithTimeout(
  url: string,
  options: RequestInit = {},
  timeoutMs = 10000
): Promise<Response> {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeoutMs);
  try {
    return await fetch(url, { ...options, signal: controller.signal });
  } catch (err: unknown) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("요청 시간 초과 — 백엔드 서버에 연결할 수 없습니다");
    }
    throw err;
  } finally {
    clearTimeout(id);
  }
}

export interface LineItem {
  id: string;
  item_name_raw: string;
  item_name_std: string | null;
  process_major: string | null;
  process_minor: string | null;
  spec: string | null;
  unit: string | null;
  qty: number | null;
  unit_price: number | null;
  amount: number | null;
  confidence: number | null;
  review_flag: boolean;
  confirmed_at: string | null;
  source_row: number;
}

export interface SessionStatus {
  session_id: string;
  status: string;
  brand_name: string | null;
  total_items: number;
  review_items: number;
  error_message: string | null;
  created_at: string | null;
}

export interface BrandProfile {
  id: string;
  brand_name: string;
  sheet_mapping: Record<string, string>;
  column_mapping: Record<string, string>;
  fixed_row_count: boolean;
  notes: string | null;
}

export async function createSession(
  file: File,
  brandName?: string,
  aiMode?: "api" | "mock"
): Promise<{ session_id: string }> {
  const formData = new FormData();
  formData.append("file", file);
  if (brandName) formData.append("brand_name", brandName);
  if (aiMode) formData.append("ai_mode", aiMode);

  const res = await fetchWithTimeout(
    `${API_URL}/api/v1/sessions`,
    { method: "POST", body: formData },
    30000
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getSession(sessionId: string): Promise<SessionStatus> {
  const res = await fetchWithTimeout(`${API_URL}/api/v1/sessions/${sessionId}`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getItems(
  sessionId: string,
  reviewOnly = false
): Promise<{ items: LineItem[]; total: number; review_count: number }> {
  const url = `${API_URL}/api/v1/sessions/${sessionId}/items?review_only=${reviewOnly}`;
  const res = await fetchWithTimeout(url);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function confirmItem(
  itemId: string,
  data: {
    process_major: string;
    process_minor?: string;
    item_name_std?: string;
  }
): Promise<void> {
  const res = await fetchWithTimeout(
    `${API_URL}/api/v1/items/${itemId}/confirm`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data),
    }
  );
  if (!res.ok) throw new Error(await res.text());
}

export async function exportSession(
  sessionId: string
): Promise<{ download_url: string }> {
  const res = await fetchWithTimeout(
    `${API_URL}/api/v1/sessions/${sessionId}/export`,
    { method: "POST" },
    30000
  );
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}

export async function getBrands(): Promise<{
  brands: BrandProfile[];
  total: number;
}> {
  const res = await fetchWithTimeout(`${API_URL}/api/v1/brand-profiles`);
  if (!res.ok) throw new Error(await res.text());
  return res.json();
}
