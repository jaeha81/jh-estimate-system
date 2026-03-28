-- =================================================================
-- brand_profiles 초기 데이터 (seed)
-- brand_sample_log.md 분석 기반 실제 값
-- =================================================================

-- ── 브랜드 #1: 한샘 리하우스 (리모델링 표준) ─────────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '한샘리하우스',
  '{
    "세부내역": "세부내역서",
    "갑지": "표지"
  }'::jsonb,
  '{
    "item_name": "B",
    "spec": "C",
    "unit": "D",
    "qty": "E",
    "material_cost": "F",
    "labor_cost": "G",
    "expense_cost": "H",
    "unit_price": "I",
    "amount": "J",
    "data_start_row": 7
  }'::jsonb,
  true,
  '행 수 고정 80~120행. I열=F+G+H 합산, J열=E×I 수식. 대공종 헤더 A:B 병합, 배경색 회색'
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 브랜드 #2: 래미안 인테리어 (아파트 인테리어) ─────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '래미안인테리어',
  '{
    "세부내역": "내역서",
    "갑지": "갑지"
  }'::jsonb,
  '{
    "item_name": "C",
    "spec": "D",
    "unit": "E",
    "qty": "F",
    "unit_price": "G",
    "amount": "H",
    "data_start_row": 5
  }'::jsonb,
  true,
  '재료비/노무비 통합 단가. B열 대공종 세로 병합. 60~90행'
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 브랜드 #3: 영림가구 (주방/가구 전문) ─────────────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '영림가구',
  '{
    "세부내역": "견적서",
    "갑지": "견적서"
  }'::jsonb,
  '{
    "item_name": "B",
    "spec": "C",
    "qty": "D",
    "unit": "E",
    "unit_price": "F",
    "amount": "G",
    "data_start_row": 10
  }'::jsonb,
  false,
  '갑지+세부내역 단일 시트 통합. 행 가변(옵션 추가 시). 상단 A1:H3 로고 병합. 하단 소계→VAT→총액'
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 브랜드 #4: 일반 중소 인테리어 업체 ───────────────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '일반인테리어A',
  '{
    "세부내역": "세부내역",
    "갑지": "갑지"
  }'::jsonb,
  '{
    "item_name": "B",
    "spec": "C",
    "unit": "D",
    "qty": "E",
    "unit_price": "F",
    "amount": "G",
    "data_start_row": 4
  }'::jsonb,
  true,
  '재료비/노무비 분리 없음. A열 대공종 세로 병합. 부대비용 별도 시트. 40~70행'
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 브랜드 #5: 관급 양식 (공공기관 입찰) ─────────────────────
INSERT INTO brand_profiles (brand_name, sheet_mapping, column_mapping, fixed_row_count, notes)
VALUES (
  '관급양식',
  '{
    "세부내역": "세부내역서",
    "갑지": "총괄표"
  }'::jsonb,
  '{
    "item_name": "B",
    "spec": "C",
    "unit": "D",
    "qty": "E",
    "material_cost": "F",
    "material_amount": "G",
    "labor_cost": "H",
    "labor_amount": "I",
    "expense_cost": "J",
    "expense_amount": "K",
    "amount": "L",
    "data_start_row": 8
  }'::jsonb,
  true,
  '열 12개(A~L)로 가장 복잡. 재료비/노무비/경비 각각 단가+금액 분리. 공종번호 계층구조(1→1-1→1-1-1). 100~200행'
)
ON CONFLICT (brand_name) DO UPDATE SET
  sheet_mapping   = EXCLUDED.sheet_mapping,
  column_mapping  = EXCLUDED.column_mapping,
  fixed_row_count = EXCLUDED.fixed_row_count,
  notes           = EXCLUDED.notes,
  updated_at      = NOW();

-- ── 확인 쿼리 ─────────────────────────────────────────────────
SELECT
  brand_name,
  fixed_row_count,
  sheet_mapping->>'세부내역' AS 세부내역시트명,
  column_mapping->>'item_name' AS 품명열,
  column_mapping->>'amount' AS 금액열,
  column_mapping->>'data_start_row' AS 시작행,
  created_at
FROM brand_profiles
ORDER BY created_at;
