#!/usr/bin/env python3
"""파서 prefix 처리 버그로 메타가 어긋난 행을 일괄 보정.

대상: file_source 가 `[재배포]…`, `[복사본]…` 같이 prefix bracket 으로
시작해서 brackets[0]==school_level 가정이 깨졌던 행들.

복구 방식:
- 학교급(`고`/`중`/`초`) bracket 을 anchor 로 다시 파싱하는
  parse_filename_metadata 의 새 로직을 그대로 사용해서
  file_source 에서 메타를 재추출 → questions 행 UPDATE.

사용:
    python3 scripts/fix_misparsed_filename_meta.py           # 로컬 SQLite
    SUPABASE_DB_URL=postgresql://... python3 scripts/fix_misparsed_filename_meta.py --cloud
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_hwpx import parse_filename_metadata  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass


def _safe_int(v):
    if v is None or v == "":
        return None
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def fix(conn, placeholder: str, dry_run: bool = False):
    cur = conn.cursor()
    # 학교급(고/중/초) 이 첫 bracket 이 아닌 file_source 만 후보.
    cur.execute(
        "SELECT DISTINCT file_source FROM questions "
        "WHERE file_source NOT LIKE '[고]%' "
        "AND file_source NOT LIKE '[중]%' "
        "AND file_source NOT LIKE '[초]%'"
    )
    rows = cur.fetchall()
    print(f"prefix bracket 의심 파일: {len(rows)}건")
    fixed_files = 0
    affected_rows_total = 0
    for r in rows:
        fs = r[0] if not isinstance(r, dict) else r["file_source"]
        meta = parse_filename_metadata(Path(fs).stem)
        if not meta.get("school"):
            print(f"  skip (메타 추출 실패): {fs[:80]}")
            continue
        # 해당 file_source 의 행 수 확인
        cnt_sql = (
            f"SELECT COUNT(*) FROM questions WHERE file_source={placeholder}"
        )
        cur.execute(cnt_sql, (fs,))
        n_rows = cur.fetchone()[0]
        affected_rows_total += n_rows

        prefix = "[DRY-RUN] " if dry_run else "  "
        print(f"{prefix}OK: {meta.get('school')} "
              f"({meta.get('year')}년 {meta.get('semester')}학기 "
              f"{meta.get('exam_type')}) — {n_rows}행 ← {fs[:60]}")

        if dry_run:
            fixed_files += 1
            continue

        sql = (
            f"UPDATE questions SET "
            f"school={placeholder}, school_level={placeholder}, "
            f"year={placeholder}, region={placeholder}, "
            f"grade={placeholder}, semester={placeholder}, exam_type={placeholder}, "
            f"subject={placeholder}, chapter_range={placeholder} "
            f"WHERE file_source={placeholder}"
        )
        cur.execute(sql, (
            meta.get("school"), meta.get("school_level"),
            _safe_int(meta.get("year")), meta.get("region"),
            _safe_int(meta.get("grade")), _safe_int(meta.get("semester")),
            meta.get("exam_type"),
            meta.get("subject"), meta.get("chapter_range"),
            fs,
        ))
        fixed_files += 1
    if not dry_run:
        conn.commit()
    tag = "[DRY-RUN] " if dry_run else ""
    print(f"\n{tag}수정 대상: {fixed_files} 파일, "
          f"총 {affected_rows_total} 행")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true",
                    help="Supabase Postgres 대상 (기본은 로컬 SQLite)")
    ap.add_argument("--dry-run", action="store_true",
                    help="변경 사항만 출력, 실제 UPDATE 안 함")
    args = ap.parse_args()

    if args.cloud:
        import psycopg2
        dsn = os.environ["SUPABASE_DB_URL"]
        conn = psycopg2.connect(dsn)
        fix(conn, "%s", dry_run=args.dry_run)
    else:
        db_path = Path(__file__).resolve().parent.parent / "db" / "mathdb.sqlite"
        conn = sqlite3.connect(db_path)
        fix(conn, "?", dry_run=args.dry_run)
    conn.close()


if __name__ == "__main__":
    main()
