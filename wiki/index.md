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
| [deploy-checklist.md](deploy-checklist.md) | Railway + Vercel end-to-end 배포 순서 및 환경변수 체크리스트 | 완료 |

---

## 현재 프로젝트 구조 (실제 존재 파일)

```
jh-estimate-system/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI 진입점
│   │   ├── agents/
│   │   │   ├── orchestrator.py        # 메인 오케스트레이터
│   │   │   ├── template_manager.py    # 엑셀 템플릿 관리
│   │   │   ├── normalizer.py          # 세부내역 정규화 (LLM)
│   │   │   ├── classifier.py          # 공정 분류/단가 (LLM)
│   │   │   └── bid_formatter.py       # 입찰 양식 정리
│   │   ├── models/db.py               # SQLAlchemy ORM
│   │   ├── routers/
│   │   │   ├── sessions.py
│   │   │   ├── items.py
│   │   │   ├── brands.py
│   │   │   └── exports.py
│   │   ├── schemas/estimate.py        # Pydantic 스키마
│   │   ├── services/excel_service.py  # 엑셀 비즈니스 로직
│   │   └── utils/file_handler.py      # 파일 처리 유틸
│   ├── requirements.txt
│   ├── runtime.txt                    # Railway 배포용 Python 버전
│   └── .env.example
├── frontend/
│   ├── app/
│   │   ├── page.tsx                   # 홈 (랜딩)
│   │   ├── upload/page.tsx            # 파일 업로드
│   │   ├── confirm/[sessionId]/page.tsx  # 컨펌 루프
│   │   └── results/[sessionId]/page.tsx  # 결과 확인
│   ├── components/
│   │   ├── UploadZone.tsx
│   │   ├── ConfirmCard.tsx
│   │   └── ProgressBar.tsx
│   └── lib/api.ts                     # API 클라이언트
├── database/
│   ├── schema.sql                     # Supabase 스키마
│   └── brand_profiles_seed.sql        # 브랜드 시드 데이터
├── docs/phase0/
│   ├── brand_sample_log.md            # 브랜드 샘플 분석 기록
│   └── keyword_dict_v1.csv            # 키워드 사전 초안
├── scripts/import_keywords.py         # CSV → DB 임포트
└── wiki/                              # 이 폴더
```

---

## 에이전트 파이프라인 현황

| 에이전트 | 파일 | Phase | LLM 사용 |
|---------|------|-------|---------|
| 메인 오케스트레이터 | agents/orchestrator.py | MVP | 없음 |
| 템플릿 관리 | agents/template_manager.py | MVP | 조건부 |
| 세부내역 정규화 | agents/normalizer.py | MVP | Claude |
| 공정 분류/단가 | agents/classifier.py | MVP | Claude |
| 입찰 양식 정리 | agents/bid_formatter.py | MVP | 없음 |
| PDF 도면 분석 | (미구현) | Phase 2 | Claude |
| 검수 | (미구현) | Phase 2 | 없음 |

---

## 조회 가이드

| 질문 | 읽을 파일 |
|------|---------|
| 견적/공종/인테리어 도메인 지식? | [domain-knowledge.md](domain-knowledge.md) |
| 에이전트 설계/파이프라인 구조? | 이 파일 (에이전트 파이프라인 현황 섹션) |
| API 엔드포인트 목록? | backend/app/routers/ 직접 읽기 |
| DB 스키마? | database/schema.sql 직접 읽기 |
| 배포 설정? | backend/runtime.txt, 루트 README.md |
