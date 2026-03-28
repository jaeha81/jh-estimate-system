# Plan: JH-견적시스템 Phase 0 — 데이터 기반 준비

## 진행 상황 (2026-03-28)

### Wave 1 — ✅ 완료
- [x] **[BACKEND]** GitHub 저장소 폴더 구조 생성
- [x] **[BACKEND]** CLAUDE.md 작성
- [x] **[BACKEND]** database/schema.sql 작성 (4개 테이블 + RLS + 트리거)
- [x] **[재하]** docs/phase0/keyword_dict_v1.csv 작성 (96개 키워드)
- [ ] **[재하]** 브랜드 엑셀 샘플 4~5개 수집 ← 재하 직접 진행 필요

### Wave 2 — ✅ 완료 (파일 생성)
- [x] **[BACKEND]** backend/.env.example 작성
- [x] **[BACKEND]** scripts/import_keywords.py 작성
- [x] **[BACKEND]** .gitignore, README.md 작성
- [ ] **[재하]** docs/phase0/brand_sample_log.md 실제 분석 기록 작성
- [ ] **[재하]** backend/.env 실제 키 입력 (Supabase, Claude API)
- [ ] **[재하]** Supabase 프로젝트 생성 + schema.sql 실행
- [ ] **[재하]** python scripts/import_keywords.py 실행
- [ ] **[재하]** Railway + Vercel 프로젝트 생성

### Wave 3 — 대기
- [ ] **[재하]** database/brand_profiles_seed.sql 수정 + 실행
- [ ] **[재하]** Phase 0 이밸류에이션 체크리스트 확인

---

## 재하가 직접 해야 하는 작업 목록

### 지금 바로 할 수 있는 것
1. **GitHub 저장소 생성** → `jaeha81/jh-estimate-system`
2. **Supabase 프로젝트 생성** → [supabase.com](https://supabase.com)
3. **브랜드 엑셀 샘플 수집** → 4~5개 (이미 값 채워진 것 포함)

### 순서대로 진행
```
GitHub 저장소 생성
    ↓
Supabase 프로젝트 생성 + schema.sql 실행
    ↓
backend/.env 실제 값 입력
    ↓
python scripts/import_keywords.py 실행
    ↓
브랜드 샘플 분석 → brand_sample_log.md 작성
    ↓
brand_profiles_seed.sql 수정 + 실행
    ↓
Phase 0 완료 → Phase 1 plan.md 작성 요청
```

---

계획이 완료되었습니다.
아직 코드를 수정하지는 않았습니다.
