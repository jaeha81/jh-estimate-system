---
최종 업데이트: 2026-04-10
---

# 세션 작업 이력

---

## 세션 2 (2026-04-10)

### 완료된 작업

#### 버그 수정 4건

| 파일 | 문제 | 수정 |
|------|------|------|
| `backend/app/routers/sessions.py` | 비유효 UUID 세션 조회 시 500 에러 | `except Exception → HTTPException(400)` |
| `backend/app/routers/sessions.py` | 파일 확장자/크기 오류 시 500 에러 | `ValueError → HTTPException(400)` |
| `backend/app/routers/sessions.py` | BackgroundTasks 기본값 인스턴스화 불필요 | 기본값 제거, 첫 번째 파라미터로 이동 |
| `backend/app/utils/file_handler.py` | 한글 파일명 Supabase Storage 업로드 실패 | 경로를 `UUID.ext` 형식으로 변경 |

#### 의존성 수정

- `storage3 2.28.3` → `0.8.2` 다운그레이드
  - 원인: storage3 2.x가 `pyiceberg` 요구 → Windows 빌드 실패
  - 해결: `supabase==2.9.1` 전체 재설치 (storage3==0.8.2 자동 설치)

#### AI 모드 선택 시스템 추가

- `backend/app/agents/classifier.py` — `ai_mode` 파라미터 추가 (`mock`/`api` 분기)
- `backend/app/agents/orchestrator.py` — `ai_mode` 파이프라인 전달
- `backend/app/routers/sessions.py` — `ai_mode` Form 파라미터 수신 (서버 env 오버라이드 가능)
- `backend/.env` — `AI_MODE=mock` 추가
- `backend/.env.example` — AI_MODE 항목 문서화
- `frontend/lib/api.ts` — `createSession(file, brand, aiMode)` 파라미터 추가
- `frontend/app/upload/page.tsx` — 테스트 모드/Claude AI 모드 선택 버튼 UI 추가

### 미완료 (다음 세션 이어서)

- mock 모드 end-to-end 테스트 — 인터넷 끊김으로 중단
- git commit — 이번 세션 변경사항 미커밋 상태
- 프론트엔드 포트 3000 점유 이슈 (PID 확인 후 종료 필요)
- 컨펌 루프 브라우저 동작 확인

### 발견된 환경 이슈

- Claude API 크레딧 소진 → AI_MODE=mock 으로 우회
- 포트 3000 점유 (PID 47004, node.exe) → 프론트 dev 서버가 54112로 대체 실행됨
- 인터넷 연결 불안정 → Supabase 연결 실패 (`getaddrinfo failed`)

---

## 세션 1 (2026-04-10)

### 완료된 작업

- Supabase 프로젝트 설정: schema.sql, brand_profiles_seed.sql 실행
- Storage 버킷 `estimate-files` 생성
- keyword_dict 146개 임포트 완료
- backend/.env 설정
- wiki/ 초기 구성: domain-knowledge, demo-scenario, keyword-patterns, deploy-checklist
- README.md 대회 제출용 전면 재작성
- 데모 샘플 엑셀 생성: `docs/demo/한샘_리하우스_34평_견적서_샘플.xlsx`
- railway.toml 생성
- git commit: `baa2b8c`
