-- =================================================================
-- brand_profiles 초기 데이터 (seed)
-- 사용법: brand_sample_log.md 작성 완료 후 실제 값으로 수정하여 실행
-- =================================================================

-- ── 작성 가이드 ───────────────────────────────────────────────
-- sheet_mapping: {"세부내역": "실제 시트탭 이름"}
-- column_mapping: {"item_name": "열문자"} — B, C, D ... 형태
-- fixed_row_count: true면 행 추가 시도 안 함 (MVP 기본값)
--
-- brand_sample_log.md 분석 후 아래 INSERT 문을 실제 값으로 채울 것
-- =================================================================

-- ── 브랜드 #1 (예시 — 실제 분석 후 수정) ────────────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '브랜드1',   -- ← 실제 브랜드/클라이언트명으로 교체
  '{
    "세부내역": "세부내역서",
    "갑지": "갑지"
  }'::jsonb,
  '{
    "item_name": "B",
    "spec":      "C",
    "unit":      "D",
    "qty":       "E",
    "unit_price":"I",
    "amount":    "J",
    "data_start_row": 7
  }'::jsonb,
  true,
  '브랜드1 분석 메모: 행 수 고정 40행, J열 수식 자동계산'
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 브랜드 #2 (예시 — 실제 분석 후 수정) ────────────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '브랜드2',
  '{
    "세부내역": "내역서"
  }'::jsonb,
  '{
    "item_name": "C",
    "spec":      "D",
    "unit":      "E",
    "qty":       "F",
    "unit_price":"G",
    "amount":    "H",
    "data_start_row": 5
  }'::jsonb,
  true,
  ''
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 브랜드 #3 ────────────────────────────────────────────────
-- brand_sample_log.md 작성 후 동일 패턴으로 추가

-- ── 확인 쿼리 ─────────────────────────────────────────────────
SELECT
  brand_name,
  fixed_row_count,
  sheet_mapping->>'세부내역' AS 세부내역시트명,
  column_mapping->>'item_name' AS 품명열,
  column_mapping->>'amount' AS 금액열,
  created_at
FROM brand_profiles
ORDER BY created_at;
