---
최종 업데이트: 2026-04-10
---

# Known Issues

형식: `[날짜] 문제 / 원인 / 조치 / 상태`

---

## ✅ 해결됨

### [2026-04-10] Next.js 15.3.1 + Node.js 22 Windows SWC 빌드 실패
- **문제**: `next dev` 실행 시 `data did not match any variant of untagged enum Config` 오류 / `next build` 시 `TypeError: generate is not a function`
- **원인**: Next.js 15.3.1의 `generateBuildId` 정규화 버그 + Windows Node.js 22 + SWC 바이너리 비호환
- **조치**: Next.js 14.2.35 다운그레이드 (`package.json`)
- **상태**: ✅ 해결 (build/dev 모두 정상)

### [2026-04-10] Supabase 오프라인 → keyword_dict 로드 실패
- **문제**: 인터넷 미연결 시 `classifier.py`의 `_load_keyword_dict()` 빈 dict 반환
- **원인**: Supabase `getaddrinfo failed` 예외 처리 없음
- **조치**: `_LOCAL_CSV` 폴백 추가 (`docs/phase0/keyword_dict_v1.csv`)
- **상태**: ✅ 해결

### [2026-04-10] brands/items 라우터 DB 오류 시 500 반환
- **문제**: Supabase 미연결 시 500 Internal Server Error → 프론트엔드 크래시
- **원인**: 예외 처리 없음
- **조치**: `brands.py` 오프라인 시 빈 목록 반환, `items.py` 503 + 메시지 반환
- **상태**: ✅ 해결

### [2026-04-10] layout.tsx Google Fonts TypeError
- **문제**: 인터넷 미연결 환경에서 `next/font/google` 임포트 시 TypeError
- **원인**: Geist/Geist_Mono 폰트 CDN 요청 실패
- **조치**: Google Fonts 제거, 시스템 폰트(Arial/Helvetica) 사용
- **상태**: ✅ 해결

---

## ⚠️ 알려진 제약 (해결 불필요 또는 미래 과제)

### [2026-04-10] AI_MODE=api 오프라인 불가
- **문제**: Claude API 모드는 인터넷 연결 필수
- **원인**: anthropic SDK 외부 API 호출
- **조치**: `AI_MODE=mock`으로 우회 가능 (업로드 화면에서 선택)
- **상태**: ⚠️ 의도된 동작 (Railway 배포 후 정상)

### [2026-04-10] keyword_dict lru_cache — 재시작 전까지 신규 키워드 미반영
- **문제**: `@lru_cache(maxsize=1)` 적용으로 서버 재시작 전까지 캐시 유지
- **원인**: 성능 최적화로 의도된 설계
- **조치**: 향후 Redis 캐시 또는 cache_invalidate 엔드포인트 추가 예정
- **상태**: ⚠️ Phase 2 이후 개선 예정

### [2026-04-10] 파일명 한글 → Storage 경로 ASCII UUID 변환
- **문제**: `한샘_리하우스_34평.xlsx` → `anonymous/abc123.xlsx` 로 저장
- **원인**: Supabase Storage ASCII 경로 안전성 확보
- **조치**: DB `original_file_path` 컬럼에 실제 경로 저장됨, 다운로드 URL로 접근 가능
- **상태**: ⚠️ 의도된 동작

### [2026-04-10] 포트 3000~3004 점유 시 dev 서버 자동 이동
- **문제**: `next dev` 실행 시 Port 3000 점유 경고 → 3005까지 자동 증가
- **원인**: 기존 Node 프로세스 점유
- **조치**: `npx kill-port 3000` 또는 `next dev -p 3100` 사용
- **상태**: ⚠️ 개발 환경 이슈 (배포 환경 무관)
