# Plan: JH-견적시스템 Phase 1 MVP — 구현 진행 상황

## 최종 업데이트: 2026-03-28

---

## Phase 0 — ✅ 완료
- [x] Supabase 프로젝트 생성 + schema.sql 실행 (4개 테이블)
- [x] backend/.env 실제 키 입력 (Supabase + Claude API)
- [x] keyword_dict 임포트 (94개 레코드)
- [x] brand_sample_log.md 5개 브랜드 분석
- [x] brand_profiles_seed.sql 실행 (5개 브랜드)
- [x] GitHub push 완료

---

## Phase 1 MVP — 구현 중

### Wave 1: 백엔드 기반 — ✅ 완료
- [x] backend/requirements.txt
- [x] backend/app/__init__.py (+ models, schemas, services, utils, agents, routers)
- [x] backend/app/models/db.py — Supabase 클라이언트 싱글톤
- [x] backend/app/schemas/estimate.py — Pydantic 스키마 전체
- [x] backend/app/services/excel_service.py — openpyxl 파싱/쓰기 유틸
- [x] backend/app/utils/file_handler.py — 파일 업로드/다운로드 유틸
- [x] 구문 검사 전체 통과

### Wave 2: 에이전트 5개 — ✅ 완료
- [x] backend/app/agents/template_manager.py — 브랜드 감지 + 프로필 조회
- [x] backend/app/agents/normalizer.py — 세부내역 파싱 → DB 저장
- [x] backend/app/agents/classifier.py — keyword_dict + Claude API 분류
- [x] backend/app/agents/bid_formatter.py — 원본 복사 → 결과 되쓰기
- [x] backend/app/agents/orchestrator.py — 전체 파이프라인 오케스트레이션
- [x] 구문 검사 전체 통과

### Wave 3: API 라우터 + 프론트엔드 — ✅ 코드 작성 완료
- [x] backend/app/routers/sessions.py — POST /sessions, GET /sessions/{id}
- [x] backend/app/routers/items.py — GET /items, PATCH /items/{id}/confirm
- [x] backend/app/routers/exports.py — POST /sessions/{id}/export
- [x] backend/app/routers/brands.py — GET/POST /brand-profiles
- [x] backend/app/main.py — FastAPI 앱 + CORS + 4개 라우터
- [x] frontend/ Next.js 프로젝트 생성 (zustand 설치)
- [x] frontend/lib/api.ts — API 클라이언트
- [x] frontend/components/ — UploadZone, ProgressBar, ConfirmCard
- [x] frontend/app/ — layout, page, upload, confirm/[sessionId], results/[sessionId]
- [x] frontend/.env.local
- [x] 백엔드 구문 검사 전체 통과

### Wave 4: 검증 — ✅ 완료 (2026-04-07)
- [x] 프론트엔드 빌드 검증 — 성공 (Next.js 16.2.1 + Tailwind v3)
  - Tailwind v4→v3 다운그레이드 (postcss.config.js CJS 형식)
  - globals.css → @tailwind base/components/utilities 방식으로 수정
  - tailwindcss, autoprefixer, postcss를 devDependencies→dependencies로 이동
- [x] 백엔드 임포트/라우트 테스트 — 성공 (Python 3.13 기준)
  - requirements.txt 버전 고정(==) → 최소 버전(>=)으로 완화
  - Python 3.14 미지원 패키지 문제: py -3.13 사용 권장
- [x] API 라우트 8개 확인 — /sessions, /items, /exports, /brand-profiles, /
- [ ] Railway + Vercel 프로젝트 연결 (배포) — 실제 키 입력 후 진행

---

## 로컬 실행 방법

```bash
# 1. 백엔드 (Python 3.13 권장 — 3.14는 일부 패키지 미지원)
cd backend
cp .env.example .env
# .env에 실제 키 입력 (Supabase URL/키, Claude API 키)
py -3.13 -m pip install -r requirements.txt
py -3.13 -m uvicorn app.main:app --reload --port 8000

# 2. 프론트엔드
cd frontend
npm install          # tailwindcss, postcss, autoprefixer 포함됨
npm run dev          # http://localhost:3000

# 3. 빌드 검증 (배포 전)
cd frontend && npm run build
```

## 핵심 환경변수 (.env에 필요한 값)
- SUPABASE_URL=https://zpqbytnddorsnxiqblko.supabase.co
- SUPABASE_ANON_KEY=(Supabase Dashboard > Settings > API)
- SUPABASE_SERVICE_ROLE_KEY=(Supabase Dashboard > Settings > API)
- CLAUDE_API_KEY=(Anthropic Console)
- CLAUDE_MODEL=claude-sonnet-4-6
