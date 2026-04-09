---
최종 업데이트: 2026-04-10
---

# 배포 체크리스트 (Railway + Vercel)

> end-to-end 연결을 위한 순서. 한 번만 하면 됨.

---

## 1. Supabase 세팅

- [ ] Supabase Dashboard > New Project (Region: Northeast Asia)
- [ ] SQL Editor > `database/schema.sql` 전체 실행
- [ ] SQL Editor > `database/brand_profiles_seed.sql` 실행
- [ ] Storage > New Bucket: `estimate-files` (Private)
- [ ] Settings > API > `URL`, `anon key`, `service_role key` 복사해둠

---

## 2. Railway 배포 (백엔드)

### 2-1. GitHub 연결
- [ ] railway.com > New Project > Deploy from GitHub repo
- [ ] `jaeha81/jh-estimate-system` 선택

### 2-2. 서비스 설정
Railway가 루트의 `railway.toml`을 자동 감지함 → `backend/` 디렉터리 사용.

추가 확인:
- [ ] Settings > Build Command: `pip install -r requirements.txt`
- [ ] Settings > Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Settings > Root Directory: `backend` (railway.toml에 이미 설정됨)

### 2-3. 환경변수 등록
Railway Dashboard > Variables 탭에서 아래 설정:

```
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_SERVICE_ROLE_KEY=service_role_key_here
CLAUDE_API_KEY=sk-ant-api03-...
CLAUDE_MODEL=claude-sonnet-4-6
CONFIDENCE_THRESHOLD=0.7
MAX_UPLOAD_SIZE_MB=50
ALLOWED_EXTENSIONS=.xlsx,.xls,.pdf
SUPABASE_BUCKET=estimate-files
APP_ENV=production
LOG_LEVEL=INFO
CORS_ORIGINS=https://your-vercel-domain.vercel.app
```

> CORS_ORIGINS는 Vercel 배포 후 실제 도메인으로 업데이트 필요.

### 2-4. 배포 확인
- [ ] Deploy 완료 후 Railway에서 도메인 확인 (예: `https://jh-estimate-backend.up.railway.app`)
- [ ] `https://your-railway-url/` 접속 → `{"status":"ok"}` 응답 확인
- [ ] `https://your-railway-url/docs` 접속 → Swagger UI 확인

---

## 3. 키워드 사전 임포트

Railway 배포 완료 후, 로컬에서 Supabase에 직접 임포트:

```bash
cd jh-estimate-system
pip install supabase python-dotenv
# backend/.env에 Supabase 접속 정보 입력 후:
python scripts/import_keywords.py --reset
# 총 150개 레코드 (원본 97 + 추가 53)
```

- [ ] 임포트 완료 확인 (Supabase Dashboard > keyword_dict 테이블)

---

## 4. Vercel 배포 (프론트엔드)

### 4-1. GitHub 연결
- [ ] vercel.com > New Project > Import from GitHub
- [ ] `jaeha81/jh-estimate-system` 선택
- [ ] Root Directory: `frontend` (vercel.json에 이미 설정됨)

### 4-2. 환경변수 등록
Vercel Dashboard > Settings > Environment Variables:

```
NEXT_PUBLIC_API_URL=https://your-railway-url.up.railway.app
```

- [ ] Production, Preview, Development 모두 체크

### 4-3. 배포 확인
- [ ] Deploy 완료 후 Vercel 도메인 확인 (예: `https://jh-estimate.vercel.app`)
- [ ] `/upload` 페이지 접속 → 브랜드 목록 로드 확인 (Railway API 연결 확인)

---

## 5. CORS 최종 설정

Vercel 도메인 확정 후 Railway 환경변수 업데이트:

```
CORS_ORIGINS=https://jh-estimate.vercel.app
```

- [ ] Railway > Variables > CORS_ORIGINS 업데이트
- [ ] Railway 자동 재배포 확인

---

## 6. end-to-end 테스트

- [ ] `docs/demo/한샘_리하우스_34평_견적서_샘플.xlsx` 파일 업로드
- [ ] 브랜드 자동 감지 확인 (or "한샘리하우스" 선택)
- [ ] PROCESSING → CONFIRM_WAIT 상태 전환 확인
- [ ] 컨펌 카드 5개 처리
- [ ] DONE 상태 전환 + 다운로드 URL 발급 확인
- [ ] 결과 엑셀 파일 다운로드 및 내용 확인

---

## 7. 알려진 이슈 및 해결책

| 이슈 | 원인 | 해결 |
|------|------|------|
| Railway 빌드 실패 | requirements.txt 패키지 버전 충돌 | `python -3.11` 버전 사용 (runtime.txt 설정됨) |
| CORS 오류 | CORS_ORIGINS 미설정 | Railway 환경변수 CORS_ORIGINS에 Vercel 도메인 추가 |
| API 연결 실패 | NEXT_PUBLIC_API_URL 미설정 | Vercel 환경변수에 Railway URL 추가 |
| 분류 오류 | Claude API 키 미설정 | Railway 환경변수 CLAUDE_API_KEY 확인 |
| 파일 업로드 실패 | Supabase Storage 버킷 없음 | `estimate-files` 버킷 생성 확인 |

---

## 관련 페이지

- [index.md](index.md) — 프로젝트 전체 구조
- [demo-scenario.md](demo-scenario.md) — 테스트용 샘플 파일 위치
