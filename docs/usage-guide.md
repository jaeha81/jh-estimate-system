---
type: reference
source: claude
project: jh-estimate-system
system: JH-Obsidian-Vault
status: done
date: 2026-04-27
tags: [견적시스템, 사용가이드, PDF, Excel, Supabase, SQLite]
summary: JH 견적시스템 전체 사용 가이드 — 설치, 실행, 파일 업로드, 공정 분류, 결과 다운로드
---

# JH 견적시스템 사용 가이드

> 인테리어/건설 견적 Excel·PDF → AI 공정 분류 자동화 시스템

---

## 빠른 시작

### 로컬 실행

1. `start-local.bat` 더블클릭
2. 브라우저에서 `http://localhost:3000` 접속

```
백엔드 API : http://localhost:8000
프론트엔드 : http://localhost:3000
API 문서   : http://localhost:8000/docs
```

### 배포 환경

프론트엔드: `https://frontend-six-bice-h5ixxwa1ij.vercel.app`  
백엔드 API: Railway 또는 로컬

---

## 전체 사용 흐름

```
[파일 업로드] → [AI 자동 분류] → [검토 필요 항목 확인] → [결과 다운로드]
     ↓                ↓                    ↓                     ↓
  /upload         PROCESSING           /confirm/{id}         /results/{id}
```

---

## 1단계 — 파일 업로드 (`/upload`)

### 지원 형식

| 형식 | 확장자 | 처리 방식 |
|------|--------|----------|
| Excel | `.xlsx`, `.xls` | 브랜드 템플릿 기반 시트 파싱 |
| PDF | `.pdf` | Claude AI 텍스트 추출 |

### 업로드 옵션

- **브랜드 선택** (선택사항): 등록된 업체 양식이면 자동 인식
- **AI 모드 선택**:

| 모드 | 설명 | 권장 상황 |
|------|------|----------|
| `api` | Claude AI 공정 분류 | 실제 업무, 정확한 분류 필요 |
| `mock` | 키워드 기반 분류 | 테스트, 빠른 확인, 인터넷 없는 환경 |

---

## 2단계 — AI 자동 분류

업로드 후 자동 파이프라인 실행:

```
파일 수신
  → Storage 저장
  → 항목 추출 (Excel: 시트 파싱 / PDF: Claude API)
  → 공정 분류 (대공정 / 소공정)
  → Inspector 신뢰도 검사
  → 결과 저장
```

**처리 결과에 따른 분기:**

| 결과 | 상태 | 이동 |
|------|------|------|
| 모든 항목 신뢰도 충족 | `DONE` | 결과 페이지 자동 이동 |
| 신뢰도 낮은 항목 존재 | `CONFIRM_WAIT` | 검토 페이지 이동 |
| 오류 발생 | `ERROR` | 오류 메시지 표시 |

---

## 3단계 — 검토 항목 확인 (`/confirm/{sessionId}`)

AI가 확신하지 못한 항목만 카드 형태로 순서대로 표시됩니다.

- **대공정 / 소공정** 직접 지정
- **표준품명** 수정 가능
- 확정 시 다음 항목 자동 이동
- 모든 항목 확정 완료 → 결과 페이지 자동 이동

> 확정 데이터는 키워드 사전(`keyword_dict`)에 누적되어 다음 분류 시 정확도가 향상됩니다.

---

## 4단계 — 결과 다운로드 (`/results/{sessionId}`)

| 입력 | 출력 |
|------|------|
| Excel 업로드 | 원본 시트 유지 + **공정분류결과** 시트 추가 |
| PDF 업로드 | 새 Excel 파일 생성 (항목명/단위/수량/단가/대공정/소공정) |

다운로드 파일 구성:
- **원본 시트**: 기존 견적 내역 그대로
- **공정분류결과 시트**: 원본행 / 품명 / 대공종 / 세부공종 / 신뢰도 / 확인여부

---

## DB 모드 전환

`backend/.env` 파일에서 설정:

```env
# 실운영 (Supabase)
DB_TYPE=supabase

# 로컬 테스트 (SQLite, 인터넷 불필요)
DB_TYPE=sqlite
```

---

## 브랜드 프로필 등록

반복되는 업체 양식을 등록하면 자동 인식됩니다.

```http
POST /api/v1/brand-profiles
Content-Type: application/json

{
  "brand_name": "한샘리하우스",
  "sheet_mapping": { "세부내역": "세부내역서" },
  "column_mapping": {
    "item_name": "B",
    "spec": "C",
    "unit": "D",
    "qty": "E",
    "unit_price": "F",
    "amount": "G",
    "data_start_row": 7
  },
  "fixed_row_count": false
}
```

---

## API 엔드포인트 요약

| 메서드 | 경로 | 설명 |
|--------|------|------|
| `POST` | `/api/v1/sessions` | 파일 업로드 + 세션 생성 |
| `GET` | `/api/v1/sessions/{id}` | 세션 상태 조회 |
| `GET` | `/api/v1/sessions/{id}/items` | 항목 목록 조회 |
| `PATCH` | `/api/v1/items/{id}/confirm` | 항목 공정 확정 |
| `POST` | `/api/v1/sessions/{id}/export` | 결과 Excel 생성 |
| `GET` | `/api/v1/brand-profiles` | 브랜드 목록 |
| `POST` | `/api/v1/brand-profiles` | 브랜드 등록 |

전체 API 문서: `http://localhost:8000/docs` (Swagger UI)

---

## 파일 크기 제한

- 최대 업로드: **50MB**
- 허용 확장자: `.xlsx`, `.xls`, `.pdf`

---

## 관련 문서

- [README](../README.md) — 프로젝트 개요
- [research.md](../research.md) — 아키텍처 분석
- [plan.md](../plan.md) — 개발 계획
