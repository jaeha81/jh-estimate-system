# JH-EstimateAI

> **18년 인테리어 건설 견적 도메인 × AI 에이전트 자동화**
> 2026 AI Champion 대회 제출작

숙련 견적사가 하루 8시간 수작업하던 **엑셀 내역서 공종 분류·정규화 작업**을
5개 AI 에이전트 파이프라인이 **5분 안에 처리**합니다.

---

## 핵심 문제

인테리어 공사 견적은 브랜드마다 엑셀 양식이 다르고, 현장마다 용어가 다릅니다.

```
한샘리하우스: "세부내역서" 시트, 7행 시작, F/G/H열 = 재료비/노무비/경비
래미안인테리어: "내역서" 시트, 5행 시작, G열 = 통합 단가
관급양식: "세부내역서" 시트, 8행 시작, 열이 L열까지 — 재료비/노무비/경비 각각 단가+금액
```

같은 공종도 이렇게 불립니다:

| 의미 | 브랜드 A | 브랜드 B | 브랜드 C |
|------|---------|---------|---------|
| LVT 바닥재 | "데코타일" | "LVT시공" | "비닐타일" |
| 경량천장 | "T-BAR천장" | "경량천장" | "텍스천장" |
| 에폭시 도장 | "EP도장 2차" | "에폭시도장" | "바닥EP" |

**기존 방식:** 견적사가 눈으로 읽고, 손으로 분류하고, 복사-붙여넣기.
**이 시스템:** 파일 하나 업로드하면 자동으로 처리.

---

## 5-에이전트 파이프라인

```
엑셀 파일 업로드
        ↓
[SCANNER]  TemplateManager
           브랜드 자동 감지 + 시트/열 매핑 추출
        ↓
[PARSER]   ExcelService
           세부내역 시트 → 구조화된 행 데이터
        ↓
[NORMALIZER] Normalizer
           원본 품명 보존 + 숫자 필드 타입 변환
        ↓
[CLASSIFIER] Classifier                     ← Claude API 투입
           1단계: keyword_dict 즉시 매칭 (비용 0)
           2단계: 미매칭만 Claude sonnet-4-6 분류
           confidence < 0.7 → review_flag=true
        ↓
  ┌─────┴──────┐
  ↓ 자동 완료   ↓ review_flag 있음
[REPORTER]   [CONFIRM LOOP]  사용자 컨펌
BidFormatter  ConfirmCard UI (카드 방식)
원본 엑셀 양식에 결과 되쓰기
        ↓
 결과 파일 다운로드 (원본 양식 유지)
```

### 설계 원칙

- **keyword_dict 우선** — 현장 용어 사전으로 즉시 분류. Claude API는 불확실한 항목에만.
- **review_flag 시스템** — confidence < 0.7이면 AI가 직접 사용자에게 확인 요청.
- **학습 루프** — 사용자 컨펌 결과가 keyword_dict에 자동 누적. 쓸수록 정확해짐.
- **원본 보존** — `item_name_raw` 절대 변경 금지. 수식 셀 덮어쓰기 금지.

---

## 데모 시나리오

**케이스:** 한샘리하우스 34평 풀 인테리어 견적서 (총 22,597,500원)

| 처리 결과 | 항목 수 | 방식 |
|---------|--------|------|
| 자동 분류 완료 | 13개 | keyword_dict 즉시 매칭 (Claude 비용 없음) |
| AI 검토 후 확정 | 5개 | Claude 분류 → 사용자 컨펌 |

**review_flag 5개 케이스:**

| 품명 | 왜 애매한가 | Claude 제안 | confidence |
|------|-----------|-----------|-----------|
| 인건비 | 공종 특정 불가 | 미분류 | 0.10 |
| EP도장 2차 | 에폭시 약어 미등록 | 도장/도배공사 | 0.65 |
| 걸레받이 MDF 10T | 목공/마감 경계 | 목공사 | 0.68 |
| 기타 잡공사 | 내용 불명확 | 잡공사 | 0.40 |
| 시스템 선반 W900 | 가구/목공 경계 | 가구공사 | 0.62 |

**시연 5분 흐름:**
1. 파일 드래그앤드롭 → 브랜드 자동 감지 (00:30)
2. 자동 처리 결과 확인 — 13개 즉시 완료 (01:00)
3. 컨펌 카드 5장 처리 (01:30~03:30)
4. 결과 엑셀 다운로드 — 원본 한샘 양식 유지 (04:00)

---

## 기술 스택

| 레이어 | 기술 | 역할 |
|--------|------|------|
| Backend | FastAPI + Python 3.11 | 5-에이전트 파이프라인 실행 |
| Frontend | Next.js 14 App Router + TypeScript + Tailwind | 업로드/컨펌/결과 화면 |
| DB | Supabase (PostgreSQL + Storage) | 세션·항목 저장, 파일 관리 |
| AI | Claude API (claude-sonnet-4-6) | 공종 분류, keyword 주입 |
| Excel | openpyxl | 엑셀 파싱 + 결과 되쓰기 |
| Deploy | Railway (backend) + Vercel (frontend) | 프로덕션 배포 |

---

## 도메인 전문성

이 시스템은 18년 현장 경험에서 나온 규칙을 코드로 구현합니다:

- **97개 현장 용어 사전** — 철거/목공/도장/타일/바닥/설비/전기 전 공종 커버
- **브랜드별 양식 프로필** — 한샘, 래미안, 영림가구, 일반업체, 관급양식 5종 분석 완료
- **손율 적용 원칙** — 타일 5~15%, 도배지 10~20%, 강마루 5~10% (단가 계산 근거)
- **review_flag 기준** — "인건비", "기타 잡공사" 등 현장에서도 모르는 항목은 AI도 솔직하게 모른다고 표시

---

## 프로젝트 구조

```
jh-estimate-system/
├── backend/app/
│   ├── agents/
│   │   ├── orchestrator.py       # 파이프라인 조율
│   │   ├── template_manager.py   # 브랜드 감지 + 시트 매핑
│   │   ├── normalizer.py         # 데이터 정규화
│   │   ├── classifier.py         # keyword_dict + Claude 분류
│   │   └── bid_formatter.py      # 엑셀 되쓰기 + 다운로드
│   ├── routers/                  # sessions, items, brands, exports
│   ├── models/db.py              # Supabase ORM
│   └── services/excel_service.py # openpyxl 처리
├── frontend/app/
│   ├── upload/                   # 파일 업로드
│   ├── confirm/[sessionId]/      # 컨펌 루프
│   └── results/[sessionId]/      # 결과 확인
├── database/
│   ├── schema.sql                # 4개 테이블 스키마
│   └── brand_profiles_seed.sql   # 5개 브랜드 프로필
├── docs/phase0/
│   ├── brand_sample_log.md       # 5개 브랜드 분석 기록
│   └── keyword_dict_v1.csv       # 97개 현장 용어 사전
├── scripts/import_keywords.py    # CSV → DB 임포트
└── wiki/                         # 도메인 지식 위키
    ├── index.md
    ├── domain-knowledge.md
    ├── demo-scenario.md
    └── keyword-patterns.md
```

---

## 빠른 시작

### 사전 준비
- Python 3.11+
- Node.js 18+
- [Supabase](https://supabase.com) 프로젝트
- [Claude API 키](https://console.anthropic.com)

### 1. DB 세팅
```bash
# Supabase Dashboard > SQL Editor
# database/schema.sql 전체 실행 후
# database/brand_profiles_seed.sql 실행
```

### 2. 백엔드 실행
```bash
cd backend
cp .env.example .env
# .env에 SUPABASE_URL, SUPABASE_KEY, CLAUDE_API_KEY 입력

pip install -r requirements.txt
python scripts/import_keywords.py          # 키워드 사전 임포트
uvicorn app.main:app --reload --port 8000
```

### 3. 프론트엔드 실행
```bash
cd frontend
npm install
# .env.local에 NEXT_PUBLIC_API_URL=http://localhost:8000 입력
npm run dev
```

### 4. 브라우저 접속
```
http://localhost:3000
```

---

## 환경변수

**backend/.env**
```env
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=service_role_key
CLAUDE_API_KEY=sk-ant-...
CLAUDE_MODEL=claude-sonnet-4-6
CONFIDENCE_THRESHOLD=0.7
```

**frontend/.env.local**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 라이선스

MIT License — 자유롭게 사용, 수정, 배포 가능.
