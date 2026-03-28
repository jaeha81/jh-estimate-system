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

### Wave 4: 검증 — ⬜ 미완료
- [ ] 프론트엔드 빌드 검증 (Next.js 15 다운그레이드 완료, 빌드 테스트 필요)
- [ ] 백엔드 uvicorn 실행 테스트
- [ ] http://localhost:8000/docs 에서 10개 엔드포인트 확인
- [ ] 프론트엔드 dev 서버 실행 + UI 확인
- [ ] Railway + Vercel 프로젝트 연결 (배포)

---

## 다른 PC에서 이어서 작업할 때

```bash
# 1. 레포 클론
git clone https://github.com/jaeha81/jh-estimate-system.git
cd jh-estimate-system

# 2. 백엔드 설정
cd backend
cp .env.example .env
# .env에 실제 키 입력 (Supabase URL/키, Claude API 키)
pip install -r requirements.txt

# 3. 프론트엔드 설정
cd ../frontend
npm install

# 4. Wave 4 검증부터 이어서 진행
cd ../frontend && npm run build  # 프론트엔드 빌드 테스트
cd ../backend && uvicorn app.main:app --reload --port 8000  # 백엔드 실행
cd ../frontend && npm run dev  # 프론트엔드 dev 서버
```

## 핵심 환경변수 (.env에 필요한 값)
- SUPABASE_URL=https://zpqbytnddorsnxiqblko.supabase.co
- SUPABASE_ANON_KEY=(Supabase Dashboard > Settings > API)
- SUPABASE_SERVICE_ROLE_KEY=(Supabase Dashboard > Settings > API)
- CLAUDE_API_KEY=(Anthropic Console)
- CLAUDE_MODEL=claude-sonnet-4-6
