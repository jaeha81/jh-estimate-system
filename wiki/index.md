---
최종 업데이트: 2026-04-10
---

# JH-EstimateAI 위키 인덱스

> 18년 인테리어 건설 견적 도메인 전문가 설계. 2026 AI Champion 대회 제출용. 마감: 2026-04-24.

FastAPI + Next.js 14 + Supabase + Claude API 기반 인테리어 견적/입찰 업무 AI 에이전트 자동화 시스템.

---

## 페이지 목록

| 파일 | 설명 | 상태 |
|------|------|------|
| [index.md](index.md) | 이 파일 — 전체 위키 인덱스 | 유지 |
| [domain-knowledge.md](domain-knowledge.md) | 인테리어 건설 견적 도메인 지식 (공종 분류, 단가, 현장 은어, 컨펌 UX) | 완료 |
| [demo-scenario.md](demo-scenario.md) | 데모 시나리오: 한샘리하우스 34평 18개 품목 end-to-end | 완료 |
| [keyword-patterns.md](keyword-patterns.md) | 키워드 사전 확장 53개 + classifier.py 30개 제한 수정 가이드 | 완료 |
| [deploy-checklist.md](deploy-checklist.md) | Railway + Vercel 배포 체크리스트 — Vercel ✅, Railway ⏳ | 최신 |
| [known-issues.md](known-issues.md) | 버그/이슈 기록 — 해결 4건, 알려진 제약 4건 | 최신 |
| [session-log.md](session-log.md) | 세션별 작업 이력 및 버그 수정 기록 | 유지 |

---

## 현재 프로젝트 구조 (실제 존재 파일)

```text
jh-estimate-system/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI 진입점
│   │   ├── agents/
│   │   │   ├── orchestrator.py        # 메인 오케스트레이터 (ai_mode 전달)
│   │   │   ├── template_manager.py    # 엑셀 템플릿 관리
│   │   │   ├── normalizer.py          # 세부내역 정규화 (순수 파싱)
│   │   │   ├── classifier.py          # 공정 분류 (mock/api 모드 분기)
│   │   │   └── bid_formatter.py       # 입찰 양식 정리
│   │   ├── models/db.py               # Supabase ORM
│   │   ├── routers/
│   │   │   ├── sessions.py            # 업로드 + ai_mode 파라미터
│   │   │   ├── items.py               # 항목 목록 + 컨펌
│   │   │   ├── brands.py              # 브랜드 프로필
│   │   │   └── exports.py             # 엑셀 내보내기
│   │   ├── schemas/estimate.py        # Pydantic 스키마
│   │   ├── services/excel_service.py  # 엑셀 비즈니스 로직
│   │   └── utils/file_handler.py      # 파일 처리 (UUID 경로)
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── .env                           # AI_MODE=mock 설정됨
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # 홈 → /upload 리다이렉트
│   │   ├── upload/page.tsx            # 파일 업로드 + AI 모드 선택 UI
│   │   ├── confirm/[sessionId]/page.tsx  # 컨펌 루프
│   │   └── results/[sessionId]/page.tsx  # 결과 확인
│   ├── components/
│   │   ├── UploadZone.tsx
│   │   ├── ConfirmCard.tsx
│   │   └── ProgressBar.tsx
│   └── lib/api.ts                     # createSession(file, brand, aiMode)
├── database/
│   ├── schema.sql
│   └── brand_profiles_seed.sql
├── docs/demo/
│   └── 한샘_리하우스_34평_견적서_샘플.xlsx   # end-to-end 테스트용
├── scripts/import_keywords.py
└── wiki/
```

---

## AI 모드 시스템

| 모드 | 환경변수 | 동작 | 용도 |
|------|---------|------|------|
| `mock` | `AI_MODE=mock` | keyword_dict 매칭만, 미매칭→review_flag=true | 개발/테스트 (API 크레딧 미사용) |
| `api` | `AI_MODE=api` | keyword_dict 매칭 후 미매칭→Claude API 분류 | 프로덕션 |

- 서버 기본값: `.env`의 `AI_MODE` 값
- 세션별 오버라이드: 업로드 시 `ai_mode` Form 파라미터
- 프론트엔드: 업로드 화면에 모드 선택 버튼 UI 제공

---

## 의존성 주의사항 (변경 금지)

| 패키지 | 버전 | 이유 |
|--------|------|------|
| supabase | 2.9.1 | storage3 2.x는 pyiceberg 빌드 실패 |
| storage3 | 0.8.2 | supabase 2.9.1에 자동 설치되는 버전 |

---

## 에이전트 파이프라인 현황

| 에이전트 | 파일 | Phase | LLM 사용 |
|---------|------|-------|---------|
| 메인 오케스트레이터 | agents/orchestrator.py | MVP | 없음 |
| 템플릿 관리 | agents/template_manager.py | MVP | 조건부 |
| 세부내역 정규화 | agents/normalizer.py | MVP | 없음 (순수 파싱) |
| 공정 분류/단가 | agents/classifier.py | MVP | api 모드만 Claude |
| 입찰 양식 정리 | agents/bid_formatter.py | MVP | 없음 |
| PDF 도면 분석 | (미구현) | Phase 2 | Claude |
| 검수 | (미구현) | Phase 2 | 없음 |

---

## 조회 가이드

| 질문 | 읽을 파일 |
|------|---------|
| 견적/공종/인테리어 도메인 지식? | [domain-knowledge.md](domain-knowledge.md) |
| 에이전트 설계/파이프라인 구조? | 이 파일 (에이전트 파이프라인 현황 섹션) |
| 세션별 버그 수정 이력? | [session-log.md](session-log.md) |
| API 엔드포인트 목록? | backend/app/routers/ 직접 읽기 |
| DB 스키마? | database/schema.sql 직접 읽기 |
| 배포 설정? | [deploy-checklist.md](deploy-checklist.md) |
