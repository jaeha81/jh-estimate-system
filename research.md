# jh-estimate-system Research (2026-04-25)

---

## 프로젝트 개요

**시스템명:** JH-EstimateAI (JH-견적시스템)
**목적:** 인테리어 건설 견적/입찰 업무 AI 에이전트 자동화 — 엑셀 견적서 업로드 → AI 공정 분류 → 사용자 컨펌 → 결과 엑셀 내보내기
**대회 마감:** 2026-04-24 (대회 제출은 완료된 것으로 보임, 최근 커밋 20e233d 기준)
**진행도:** 약 40%

---

## 기술 스택

| 레이어 | 기술 | 버전 |
|--------|------|------|
| 백엔드 | FastAPI (Python) | fastapi>=0.115.0, uvicorn |
| 프론트엔드 | Next.js App Router + TypeScript + Tailwind CSS | Next.js 14.2.35 (15→14 다운그레이드) |
| DB | Supabase (PostgreSQL) | supabase>=2.9.1, storage3==0.8.2 고정 |
| AI 엔진 | Claude API | anthropic>=0.34.2 (claude-sonnet-4-6) |
| 엑셀 처리 | openpyxl | >=3.1.5 |
| 배포 | Railway (백엔드) + Vercel (프론트엔드) | |

**의존성 고정 주의:**
- `supabase==2.9.1` + `storage3==0.8.2` — 이 조합을 바꾸면 pyiceberg 빌드 실패
- Next.js 14.2.35 고정 — 15.x는 Windows SWC 빌드 블로커 존재

---

## 현재 구조 (파일 트리 요약)

```
jh-estimate-system/
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI 진입점, CORS, 4개 라우터
│   │   ├── agents/
│   │   │   ├── orchestrator.py      # 메인 파이프라인 (10단계 완성)
│   │   │   ├── template_manager.py  # 브랜드 감지 + 프로필 조회
│   │   │   ├── normalizer.py        # 세부내역 파싱 → DB 저장
│   │   │   ├── classifier.py        # keyword_dict + Claude API 분류 (mock/api 분기)
│   │   │   └── bid_formatter.py     # 원본 복사 → 분류결과 시트 추가 → Storage 업로드
│   │   ├── routers/
│   │   │   ├── sessions.py          # POST /sessions (업로드), GET /sessions/{id}
│   │   │   ├── items.py             # GET /items, PATCH /items/{id}/confirm
│   │   │   ├── exports.py           # POST /sessions/{id}/export
│   │   │   └── brands.py            # GET/POST /brand-profiles
│   │   ├── models/db.py             # Supabase 클라이언트 싱글톤
│   │   ├── schemas/estimate.py      # Pydantic 스키마
│   │   ├── services/excel_service.py # openpyxl 파싱/쓰기 + 공정분류결과 시트
│   │   └── utils/file_handler.py    # 파일 UUID 경로 변환, Storage 업/다운로드
│   ├── requirements.txt
│   ├── runtime.txt                  # Python 3.11 (Railway 배포용)
│   └── .env / .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                 # / → /upload 리다이렉트
│   │   ├── upload/page.tsx          # 파일 업로드 + AI 모드 선택 UI
│   │   ├── confirm/[sessionId]/page.tsx  # 컨펌 루프 (카드 1건씩 처리)
│   │   └── results/[sessionId]/page.tsx  # 결과 확인 + 다운로드
│   ├── components/
│   │   ├── UploadZone.tsx
│   │   ├── ConfirmCard.tsx
│   │   └── ProgressBar.tsx
│   └── lib/api.ts                   # createSession, getSession, getItems, confirmItem, exportSession
├── database/
│   ├── schema.sql                   # 4개 테이블 정의
│   └── brand_profiles_seed.sql      # 5개 브랜드 초기 데이터
├── scripts/import_keywords.py       # CSV → Supabase keyword_dict 임포트
├── docs/demo/한샘_리하우스_34평_견적서_샘플.xlsx
├── wiki/                            # 6개 문서 (index, known-issues, session-log, deploy-checklist 등)
├── railway.toml
└── vercel.json
```

---

## 현재 완료된 기능

### Phase 0 — 완료
- Supabase 프로젝트 + schema.sql (4개 테이블) + brand_profiles_seed.sql (5개 브랜드)
- keyword_dict 146~150개 레코드 임포트 (로컬 dry-run 완료, Supabase 실 임포트는 인터넷 연결 후 재시도 필요)
- backend/.env 실제 키 입력 완료

### Phase 1 MVP — Wave 1~4 모두 완료 (코드 레벨)

| 영역 | 상태 | 비고 |
|------|------|------|
| 백엔드 에이전트 5개 | 코드 완성 | orchestrator, template_manager, normalizer, classifier, bid_formatter |
| API 라우터 8개 | 코드 완성 | /sessions, /items, /exports, /brand-profiles |
| 프론트엔드 3개 페이지 | 코드 완성 | upload, confirm/[id], results/[id] |
| 프론트엔드 빌드 검증 | 통과 | Next.js 14.2.35 기준 |
| mock 모드 end-to-end | 로컬 통과 | 한샘 34평 18개 항목 전량 분류 성공, 결과 Excel 3시트 생성 확인 |
| Vercel 프론트엔드 배포 | 완료 | https://frontend-six-bice-h5ixxwa1ij.vercel.app |
| AI 모드 선택 시스템 | 완료 | mock/api 분기, 업로드 화면 UI 포함 |
| 결과 Excel 공정분류결과 시트 | 완료 | 12열 헤더, 필터+헤더고정 |
| 컨펌 완료 자동 export | 완료 | 마지막 review 항목 확정 시 trigger_export() 자동 호출 |

---

## 미완성 기능

### 즉시 해결 필요 (배포 블로커)

| 항목 | 현황 | 위치 |
|------|------|------|
| Railway 백엔드 배포 | 유료 플랜 전환 대기 중 | deploy-checklist.md: Step 2 |
| Railway URL 확정 후 Vercel NEXT_PUBLIC_API_URL 업데이트 | Railway URL 미정이라 Vercel 프론트가 백엔드에 연결 불가 | deploy-checklist.md: Step 4-2 |
| keyword_dict Supabase 실 임포트 | dry-run 149개 확인됨, 실 DB 임포트 미완료 | scripts/import_keywords.py --reset |

### Phase 2 — 미구현 에이전트 (CLAUDE.md 정의는 있으나 파일 미존재)

| 에이전트 | 파일 | 기능 |
|---------|------|------|
| PDF 도면 분석 | backend/app/agents/pdf_analyzer.py — 파일 없음 | PDF 도면에서 공정 정보 추출 (Claude API 활용) |
| 검수 | backend/app/agents/inspector.py — 파일 없음 | 분류 결과 자동 검수 |

### 알림 시스템 — 미구현

- CLAUDE.md 기술 스택에 **Kakao Alimtalk API** 명시되어 있으나 코드 어디에도 구현 없음
- requirements.txt에도 kakao 관련 패키지 없음

### 기타 개선 예정

| 항목 | 현황 |
|------|------|
| Redis 캐시 / cache_invalidate 엔드포인트 | lru_cache 한계 인식, Phase 2 이후 계획 |
| 브랜드 프로필 관리 UI | 현재 API만 존재, 어드민 UI 없음 |
| 오류 로깅 / 모니터링 | logger.error로 로컬 로그만, 외부 모니터링 없음 |

---

## 다음 마일스톤 제안

### 마일스톤 1: 배포 완성 (최우선, 사용자 직접 필요)

1. Railway 유료 플랜 전환 → 백엔드 배포
2. Railway 도메인 확정 → Vercel `NEXT_PUBLIC_API_URL` 업데이트
3. Railway `CORS_ORIGINS` 환경변수 Vercel URL로 업데이트
4. `python scripts/import_keywords.py --reset` 실행 (인터넷 연결 후)
5. `docs/demo/한샘_리하우스_34평_견적서_샘플.xlsx` 업로드로 end-to-end 검증

이 단계가 완료되면 실질적 "40% → 70%" 진행도가 된다.
코드는 이미 완성되어 있고, 인프라 연결만 남은 상태다.

### 마일스톤 2: Phase 2 에이전트 (코드 작업)

1. `backend/app/agents/pdf_analyzer.py` 구현 — Claude API로 PDF 도면 파싱
2. `backend/app/agents/inspector.py` 구현 — 분류 결과 검수 로직
3. `/sessions` POST에 PDF 업로드 지원 추가 (현재 xlsx/xls만 실제 처리)

### 마일스톤 3: 알림 + 어드민 (선택적)

1. Kakao Alimtalk 연동 (requirements.txt 패키지 추가 필요)
2. 브랜드 프로필 관리 어드민 UI
3. keyword_dict 캐시 무효화 엔드포인트

---

## 블로킹 이슈

| 이슈 | 원인 | 영향 |
|------|------|------|
| Railway 백엔드 미배포 | 유료 플랜 전환 미완료 (사용자 액션 필요) | Vercel 프론트엔드가 실제 API에 연결 불가 — 전체 시스템 실사용 불가 |
| keyword_dict DB 미동기화 | Supabase DNS 연결 문제로 임포트 중단 | mock 모드는 로컬 CSV 폴백으로 동작하나, 프로덕션 mock 모드는 Supabase 의존 |
| pdf_analyzer.py / inspector.py 미존재 | Phase 2 미착수 | PDF 업로드 파이프라인 불완전 (xlsx는 정상 동작) |

---

## 참고: 핵심 파일 경로

| 역할 | 경로 |
|------|------|
| 파이프라인 진입점 | `backend/app/agents/orchestrator.py:24` (run_pipeline) |
| 분류 로직 (mock/api 분기) | `backend/app/agents/classifier.py` |
| 결과 Excel 생성 | `backend/app/services/excel_service.py` + `bid_formatter.py` |
| 배포 절차 | `wiki/deploy-checklist.md` |
| 알려진 이슈 | `wiki/known-issues.md` |
| 세션별 작업 이력 | `wiki/session-log.md` |
