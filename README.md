# JH-견적시스템

인테리어 견적/입찰 AI 에이전트 시스템

## 빠른 시작 (Phase 0 셋업)

### 1. GitHub 저장소 생성
```bash
# GitHub.com에서 jaeha81/jh-estimate-system 저장소 생성 후
git clone https://github.com/jaeha81/jh-estimate-system.git
cd jh-estimate-system
```

### 2. Supabase 세팅
1. [supabase.com](https://supabase.com) > New Project (Region: Northeast Asia)
2. SQL Editor에서 `database/schema.sql` 전체 실행
3. Storage > New Bucket: `estimate-files` (Private)

### 3. 환경변수 설정
```bash
cp backend/.env.example backend/.env
# backend/.env 열어서 Supabase URL, 키, Claude API 키 입력
```

### 4. 키워드 사전 임포트
```bash
pip install supabase python-dotenv
python scripts/import_keywords.py
# 확인: python scripts/import_keywords.py --dry-run
```

### 5. 브랜드 샘플 분석
- `docs/phase0/brand_sample_log.md` 양식에 따라 4~5개 브랜드 분석
- 분석 완료 후 `database/brand_profiles_seed.sql` 수정 후 Supabase에서 실행

---

## 프로젝트 구조

```
jh-estimate-system/
├── backend/          # FastAPI (Python 3.11+)
├── frontend/         # Next.js 14
├── database/         # Supabase 스키마 SQL
├── docs/phase0/      # Phase 0 분석 문서
├── scripts/          # 유틸리티 스크립트
└── CLAUDE.md         # AI 에이전트 지침
```

## 기술 스택

| | 기술 |
|---|---|
| Backend | FastAPI + Python 3.11 |
| Frontend | Next.js 14 + TypeScript |
| DB | Supabase (PostgreSQL) |
| AI | Claude API (claude-sonnet-4-6) |
| Excel | openpyxl |
| Deploy | Railway + Vercel |

## 관련 문서

- [통합 설계 문서 v2.0](docs/JH-견적시스템_통합설계문서_v2.docx)
- [Phase 0 plan.md](plan.md)
- [CLAUDE.md](CLAUDE.md) — AI 에이전트 개발 지침
