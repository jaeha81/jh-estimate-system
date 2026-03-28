"""
keyword_dict_v1.csv → Supabase keyword_dict 테이블 임포트 스크립트

사용법:
  1. backend/.env 파일에 SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY 설정
  2. pip install supabase python-dotenv
  3. python scripts/import_keywords.py

옵션:
  --dry-run     실제 삽입 없이 CSV 파일만 검증
  --reset       기존 MANUAL 데이터 전부 삭제 후 재임포트
  --csv PATH    CSV 파일 경로 지정 (기본: docs/phase0/keyword_dict_v1.csv)
"""

import argparse
import csv
import sys
from pathlib import Path

# ── 의존성 체크 ────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
except ImportError:
    print("❌ python-dotenv 미설치. 실행: pip install python-dotenv")
    sys.exit(1)

try:
    from supabase import create_client, Client
except ImportError:
    print("❌ supabase 미설치. 실행: pip install supabase")
    sys.exit(1)

import os

# ── 경로 설정 ──────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
DEFAULT_CSV = ROOT / "docs" / "phase0" / "keyword_dict_v1.csv"
ENV_FILE = ROOT / "backend" / ".env"

# ── CSV 검증 ───────────────────────────────────────────────────
REQUIRED_COLUMNS = {"keyword", "process_major", "process_minor", "source"}
VALID_SOURCES = {"MANUAL", "USER_CONFIRM"}


def validate_csv(csv_path: Path) -> list[dict]:
    """CSV 파일 유효성 검증 후 레코드 반환"""
    if not csv_path.exists():
        print(f"❌ CSV 파일 없음: {csv_path}")
        sys.exit(1)

    records = []
    errors = []

    with open(csv_path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)

        # 컬럼 확인
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            print(f"❌ CSV 필수 컬럼 누락: {missing}")
            print(f"   현재 컬럼: {reader.fieldnames}")
            sys.exit(1)

        for i, row in enumerate(reader, start=2):  # 헤더 제외하면 2번째 줄부터
            keyword = row.get("keyword", "").strip()
            process_major = row.get("process_major", "").strip()
            source = row.get("source", "").strip().upper()

            # 필수값 체크
            if not keyword:
                errors.append(f"  행 {i}: keyword 비어있음")
                continue
            if not process_major:
                errors.append(f"  행 {i}: process_major 비어있음 (keyword={keyword!r})")
                continue
            if source not in VALID_SOURCES:
                errors.append(f"  행 {i}: source={source!r} 유효하지 않음 (MANUAL|USER_CONFIRM)")
                continue

            # 합계/소계 같은 집계 행은 건너뜀
            if not process_major or process_major in ("합계", "소계", ""):
                continue

            records.append({
                "keyword": keyword,
                "process_major": process_major,
                "process_minor": row.get("process_minor", "").strip() or None,
                "source": source,
                "confirm_count": 0,
            })

    if errors:
        print(f"⚠️  CSV 유효성 경고 ({len(errors)}개):")
        for e in errors:
            print(e)

    print(f"✅ CSV 검증 완료: {len(records)}개 유효 레코드")
    return records


# ── 메인 임포트 ────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="keyword_dict CSV → Supabase 임포트")
    parser.add_argument("--dry-run", action="store_true", help="검증만 하고 삽입 안 함")
    parser.add_argument("--reset", action="store_true", help="기존 MANUAL 데이터 삭제 후 재임포트")
    parser.add_argument("--csv", type=Path, default=DEFAULT_CSV, help="CSV 파일 경로")
    args = parser.parse_args()

    # 환경변수 로드
    if ENV_FILE.exists():
        load_dotenv(ENV_FILE)
        print(f"📄 .env 로드: {ENV_FILE}")
    else:
        load_dotenv()
        print("📄 시스템 환경변수 사용")

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        print("❌ SUPABASE_URL 또는 SUPABASE_SERVICE_ROLE_KEY 환경변수 없음")
        print("   backend/.env 파일을 확인하세요")
        sys.exit(1)

    # CSV 검증
    records = validate_csv(args.csv)

    if args.dry_run:
        print("\n🔍 Dry-run 모드: 실제 삽입 안 함")
        print("\n[샘플 레코드 3개]")
        for r in records[:3]:
            print(f"  {r}")
        print(f"\n총 {len(records)}개 레코드 삽입 예정")
        return

    # Supabase 연결
    print("\n🔌 Supabase 연결 중...")
    client: Client = create_client(url, key)

    # 기존 데이터 삭제 (--reset 옵션)
    if args.reset:
        print("🗑️  기존 MANUAL 데이터 삭제 중...")
        result = client.table("keyword_dict").delete().eq("source", "MANUAL").execute()
        print(f"   삭제 완료")

    # 배치 삽입 (중복 키 충돌 시 업데이트)
    print(f"\n📥 {len(records)}개 레코드 삽입 중...")
    BATCH_SIZE = 50

    success = 0
    skipped = 0

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i + BATCH_SIZE]
        try:
            result = (
                client.table("keyword_dict")
                .upsert(batch, on_conflict="keyword")
                .execute()
            )
            success += len(batch)
            print(f"  ✅ {i + 1}~{min(i + BATCH_SIZE, len(records))}번 배치 완료")
        except Exception as e:
            print(f"  ❌ 배치 {i}~{i + BATCH_SIZE} 오류: {e}")
            skipped += len(batch)

    print(f"\n🎉 임포트 완료")
    print(f"   성공: {success}개")
    if skipped:
        print(f"   실패: {skipped}개")
    print(f"\n다음 단계: Supabase Dashboard > Table Editor > keyword_dict 에서 확인")


if __name__ == "__main__":
    main()
