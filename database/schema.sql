-- =================================================================
-- JH-견적시스템 Supabase 스키마
-- 실행 방법: Supabase Dashboard > SQL Editor > 이 파일 전체 붙여넣기 > Run
-- =================================================================

-- ── 확장 ──────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ── ENUM 타입 ──────────────────────────────────────────────────
CREATE TYPE session_status AS ENUM (
  'PENDING',
  'PROCESSING',
  'CONFIRM_WAIT',
  'DONE',
  'ERROR'
);

CREATE TYPE keyword_source AS ENUM (
  'MANUAL',
  'USER_CONFIRM'
);

-- ── 1. 브랜드 프로필 ──────────────────────────────────────────
-- 브랜드/클라이언트별 엑셀 매핑 규칙 저장
CREATE TABLE brand_profiles (
  id               UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_name       TEXT NOT NULL UNIQUE,

  -- 시트 이름 매핑: {"세부내역": "세부내역서", "갑지": "Sheet1"}
  sheet_mapping    JSONB NOT NULL DEFAULT '{}',

  -- 열 위치 매핑: {"item_name": "B", "qty": "E", "unit_price": "F", "amount": "G"}
  column_mapping   JSONB NOT NULL DEFAULT '{}',

  -- true: 행 수 고정 템플릿 (MVP 기본값), false: 행 추가 가능
  fixed_row_count  BOOLEAN NOT NULL DEFAULT true,

  notes            TEXT,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE brand_profiles IS '브랜드/클라이언트별 엑셀 양식 매핑 프로필';
COMMENT ON COLUMN brand_profiles.sheet_mapping IS '{"세부내역": "실제시트명"} 형태의 시트 이름 매핑';
COMMENT ON COLUMN brand_profiles.column_mapping IS '{"item_name": "B", "qty": "E"} 형태의 열 위치 매핑';
COMMENT ON COLUMN brand_profiles.fixed_row_count IS 'true: 행 수 고정 (MVP), false: 행 추가 허용';

-- ── 2. 견적 세션 ──────────────────────────────────────────────
-- 하나의 견적 파일 처리 작업 단위
CREATE TABLE estimate_sessions (
  id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  brand_profile_id    UUID REFERENCES brand_profiles(id) ON DELETE SET NULL,

  -- Supabase Storage 경로: "estimate-files/{user_id}/{filename}"
  original_file_path  TEXT NOT NULL,
  result_file_path    TEXT,

  status              session_status NOT NULL DEFAULT 'PENDING',
  error_message       TEXT,

  -- Supabase Auth 연동 시 활성화
  user_id             UUID,

  created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE estimate_sessions IS '견적 파일 처리 세션. 하나의 파일 업로드 = 하나의 세션';
COMMENT ON COLUMN estimate_sessions.status IS 'PENDING:대기 / PROCESSING:처리중 / CONFIRM_WAIT:컨펌대기 / DONE:완료 / ERROR:오류';

-- ── 3. 세부 내역 항목 ────────────────────────────────────────
-- 세부내역 시트에서 추출·정규화된 각 행
CREATE TABLE estimate_line_items (
  id                UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  session_id        UUID NOT NULL REFERENCES estimate_sessions(id) ON DELETE CASCADE,

  -- 원본 품명 (절대 변경 금지)
  item_name_raw     TEXT NOT NULL,
  -- LLM이 정규화한 표준 품명
  item_name_std     TEXT,

  -- 공정 분류
  process_major     TEXT,   -- 대공종 (예: 철거공사, 목공사, 도장공사)
  process_minor     TEXT,   -- 세부 공정

  -- 규격/단위
  spec              TEXT,
  unit              TEXT,   -- m², m, EA, 식, etc.

  -- 수량/단가/금액
  qty               NUMERIC(15, 4),
  material_cost     NUMERIC(15, 2),   -- 재료비
  labor_cost        NUMERIC(15, 2),   -- 노무비
  expense_cost      NUMERIC(15, 2),   -- 경비
  unit_price        NUMERIC(15, 2),   -- 단가
  amount            NUMERIC(15, 2),   -- 금액 (qty × unit_price)

  -- 원본 추적
  source_sheet      TEXT NOT NULL,    -- 원본 시트명
  source_row        INTEGER NOT NULL, -- 원본 행 번호 (1-based)

  -- AI 분류 메타
  confidence        FLOAT CHECK (confidence IS NULL OR (confidence >= 0 AND confidence <= 1)),
  review_flag       BOOLEAN NOT NULL DEFAULT false,  -- true: 사용자 확인 필요

  -- 사용자 컨펌 결과
  confirmed_by      TEXT,
  confirmed_at      TIMESTAMPTZ,

  created_at        TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at        TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE estimate_line_items IS '세부내역 시트 각 행의 정규화 결과';
COMMENT ON COLUMN estimate_line_items.item_name_raw IS '원본 품명 — 절대 수정 금지';
COMMENT ON COLUMN estimate_line_items.confidence IS 'LLM 공정 분류 신뢰도 0.0~1.0. 0.7 미만이면 review_flag=true';
COMMENT ON COLUMN estimate_line_items.review_flag IS 'true: 사용자 확인 필요. confirmed_at이 채워지면 완료';

-- ── 4. 키워드 사전 ──────────────────────────────────────────
-- 현장 용어 ↔ 공정 매핑 누적 저장소
CREATE TABLE keyword_dict (
  id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  keyword         TEXT NOT NULL UNIQUE,
  process_major   TEXT NOT NULL,
  process_minor   TEXT,
  source          keyword_source NOT NULL DEFAULT 'MANUAL',

  -- 사용자가 이 매핑을 확정한 횟수 (높을수록 신뢰)
  confirm_count   INTEGER NOT NULL DEFAULT 0,

  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE keyword_dict IS '현장 용어 → 공정 분류 매핑 사전. 사용자 컨펌 시 자동 누적';
COMMENT ON COLUMN keyword_dict.source IS 'MANUAL: 수동 입력, USER_CONFIRM: 사용자 확정으로 추가';
COMMENT ON COLUMN keyword_dict.confirm_count IS '높을수록 신뢰도 높음. 분류 시 우선 참조';

-- ── 인덱스 ────────────────────────────────────────────────────
CREATE INDEX idx_line_items_session_id ON estimate_line_items(session_id);
CREATE INDEX idx_line_items_review_flag ON estimate_line_items(review_flag) WHERE review_flag = true;
CREATE INDEX idx_line_items_session_review ON estimate_line_items(session_id, review_flag);
CREATE INDEX idx_keyword_dict_keyword ON keyword_dict(keyword);
CREATE INDEX idx_keyword_dict_process ON keyword_dict(process_major, process_minor);
CREATE INDEX idx_sessions_status ON estimate_sessions(status);
CREATE INDEX idx_sessions_user_id ON estimate_sessions(user_id) WHERE user_id IS NOT NULL;

-- ── updated_at 자동 갱신 트리거 ──────────────────────────────
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_brand_profiles_updated_at
  BEFORE UPDATE ON brand_profiles
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_estimate_sessions_updated_at
  BEFORE UPDATE ON estimate_sessions
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_estimate_line_items_updated_at
  BEFORE UPDATE ON estimate_line_items
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trg_keyword_dict_updated_at
  BEFORE UPDATE ON keyword_dict
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ── Row Level Security (RLS) ──────────────────────────────────
-- Supabase Auth 연동 전까지는 service_role key로만 접근
ALTER TABLE estimate_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE estimate_line_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE brand_profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE keyword_dict ENABLE ROW LEVEL SECURITY;

-- service_role은 RLS 우회 (백엔드 서버용)
-- 향후 Supabase Auth 연동 시 아래 정책 활성화:
/*
CREATE POLICY "사용자 본인 세션만 접근"
  ON estimate_sessions FOR ALL
  USING (auth.uid() = user_id);

CREATE POLICY "사용자 본인 항목만 접근"
  ON estimate_line_items FOR ALL
  USING (
    session_id IN (
      SELECT id FROM estimate_sessions WHERE user_id = auth.uid()
    )
  );
*/

-- ── 완료 메시지 ───────────────────────────────────────────────
DO $$
BEGIN
  RAISE NOTICE '✅ JH-견적시스템 스키마 생성 완료';
  RAISE NOTICE '   테이블: brand_profiles, estimate_sessions, estimate_line_items, keyword_dict';
  RAISE NOTICE '   다음 단계: scripts/import_keywords.py 로 keyword_dict_v1.csv 임포트';
END $$;
