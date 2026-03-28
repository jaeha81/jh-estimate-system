# JH-견적시스템 CLAUDE.md

## 글로벌 지침 상속
이 프로젝트는 JH 글로벌 지침(Custom Instructions)을 따른다.
**research.md → plan.md → 승인 → 구현** 워크플로우 준수.
승인 전 코드 작성 절대 금지.

---

## 프로젝트 개요

**시스템명:** JH-견적시스템 (JH Estimate System)
**목적:** 인테리어 견적/입찰 업무 AI 에이전트 자동화
**JH 생태계:** JH-하네스(관제) + JH-브레인(기억)과 연동

### 기술 스택
| 레이어 | 기술 |
|---|---|
| 백엔드 | FastAPI (Python 3.11+) |
| 프론트엔드 | Next.js 14 App Router + TypeScript + Tailwind CSS |
| 데이터베이스 | Supabase (PostgreSQL) |
| AI 엔진 | Claude API (claude-sonnet-4-6) |
| 엑셀 처리 | openpyxl |
| PDF 처리 | pdfplumber + PyMuPDF |
| 알림 | Kakao Alimtalk API |
| 배포 | Railway (backend) + Vercel (frontend) |

---

## 디렉터리 구조

```
jh-estimate-system/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI 앱 진입점
│   │   ├── agents/              # 에이전트 모듈
│   │   │   ├── orchestrator.py      # 메인 오케스트레이터
│   │   │   ├── template_manager.py  # 템플릿 관리
│   │   │   ├── normalizer.py        # 세부내역 정규화
│   │   │   ├── classifier.py        # 공정 분류/단가
│   │   │   ├── bid_formatter.py     # 입찰 양식 정리
│   │   │   ├── pdf_analyzer.py      # PDF 도면 분석 (Phase 2)
│   │   │   └── inspector.py         # 검수 (Phase 2)
│   │   ├── routers/             # API 라우터
│   │   ├── models/              # SQLAlchemy ORM
│   │   ├── schemas/             # Pydantic 스키마
│   │   ├── services/            # 비즈니스 로직
│   │   ├── utils/               # 엑셀/PDF 유틸
│   │   └── data/
│   │       ├── keyword_dict/    # 키워드 사전 JSON 캐시
│   │       └── brand_profiles/  # 브랜드별 매핑 프로필 JSON 캐시
│   ├── .env                     # 환경변수 (gitignore 필수)
│   ├── .env.example             # 환경변수 예시
│   ├── requirements.txt
│   └── CLAUDE.md                # 백엔드 서브 지침
├── frontend/
│   ├── app/
│   │   ├── upload/              # 파일 업로드 화면
│   │   ├── confirm/[sessionId]/ # 컨펌 루프 화면
│   │   └── results/[sessionId]/ # 결과 확인 화면
│   └── CLAUDE.md                # 프론트엔드 서브 지침
├── database/
│   └── schema.sql               # Supabase 스키마
├── docs/
│   └── phase0/
│       ├── brand_sample_log.md  # 브랜드 샘플 분석 기록
│       └── keyword_dict_v1.csv  # 키워드 사전 초안
├── scripts/
│   └── import_keywords.py       # keyword_dict CSV → DB 임포트
├── research.md
├── plan.md
└── CLAUDE.md                    ← 이 파일
```

---

## 핵심 개발 규칙

### 엑셀 처리
1. **원본 템플릿 절대 덮어쓰지 않음** — 반드시 작업본 복제 후 처리
2. **수식 셀 쓰기 금지** — openpyxl로 수식 셀 감지 후 skip
3. **행 추가 금지 (MVP)** — fixed_row_count=true 기본값 유지

### AI/에이전트
4. **review_flag=true 항목 자동 확정 금지** — 반드시 사용자 컨펌 루프 거침
5. **confidence < 0.7 → 자동 review_flag=true** — 임계값 하드코딩 금지, 환경변수로 관리
6. **불명확 항목은 item_name_raw 그대로 유지** — LLM이 임의 추정 후 확정하지 않음

### 보안
7. **Claude API 키 코드 내 하드코딩 금지** — 반드시 환경변수에서만 참조
8. **업로드 허용 확장자 화이트리스트** — .xlsx, .xls, .pdf 만 허용
9. **파일명 sanitize 필수** — 경로 traversal 방지

### 에이전트 프롬프트 구조 (7섹션)
① 역할 정의 → ② 입력 형식(JSON) → ③ 출력 형식(JSON) → ④ 처리 규칙 →
⑤ 금지 사항 → ⑥ 참고 데이터(keyword_dict 주입) → ⑦ 예외 처리

---

## 에이전트 현황

| 에이전트 | 파일 | Phase | LLM |
|---|---|---|---|
| 메인 오케스트레이터 | orchestrator.py | MVP | ❌ |
| 템플릿 관리 | template_manager.py | MVP | ⚠️ |
| 세부내역 정규화 | normalizer.py | MVP | ✅ |
| 공정분류/단가 | classifier.py | MVP | ✅ |
| 입찰 양식 정리 | bid_formatter.py | MVP | ❌ |
| PDF 도면 분석 | pdf_analyzer.py | Phase 2 | ✅ |
| 검수 | inspector.py | Phase 2 | ❌ |

---

## Wave 실행 원칙 (tmux 5-agent)

- Agent 1 (RESEARCH): research.md 전담
- Agent 2 (PLAN): plan.md 전담, 승인 전 코드 작성 금지
- Agent 3 (FRONTEND): frontend/ 구현
- Agent 4 (BACKEND): backend/ 구현
- Agent 5 (QA): 타입 체크, 검증, 코드 작성 금지
- **하나의 파일은 하나의 에이전트만 수정**
