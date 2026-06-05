#!/usr/bin/env python3
"""클리닉 v3 — 확장분산 컬럼 추가 (SQLite/Postgres 양쪽 멱등).

추가 컬럼 (clinic_entries):
- retry_d30_status      TEXT DEFAULT 'pending'  (D+30 확장분산)
- retry_exam_2w_status  TEXT DEFAULT 'pending'  (시험 2주 전 재출제)

근거 (통합비전_v3.pdf §4-3·§5):
- 분산복습 D+3/7/14 → D+3/7/14/30/시험2주전 로 확장.
- 자가예측 격차는 student_progress.category='자가예측' row 로 표현 가능
  → 별도 컬럼 추가 X.

실행:
    python scripts/migrate_clinic_v3.py            # 자동 분기 (cloud or sqlite)
    python scripts/migrate_clinic_v3.py --local    # 강제 SQLite
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


NEW_COLUMNS = [
    ("retry_d30_status",     "TEXT DEFAULT 'pending'"),
    ("retry_exam_2w_status", "TEXT DEFAULT 'pending'"),
]


def _existing_columns_sqlite(conn) -> set[str]:
    rows = conn.execute("PRAGMA table_info(clinic_entries)").fetchall()
    return {r[1] if not hasattr(r, "keys") else r["name"] for r in rows}


def _existing_columns_postgres(conn) -> set[str]:
    cur = conn.cursor()
    cur.execute(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name = 'clinic_entries'"
    )
    cols = {row[0] for row in cur.fetchall()}
    cur.close()
    return cols


def _migrate_sqlite() -> None:
    conn = get_connection()
    existing = _existing_columns_sqlite(conn)
    added = []
    for col, ddl_suffix in NEW_COLUMNS:
        if col in existing:
            continue
        conn.execute(f"ALTER TABLE clinic_entries ADD COLUMN {col} {ddl_suffix}")
        added.append(col)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    print(f"[OK] 클리닉 v3 마이그레이션 완료 (로컬 SQLite)")
    if added:
        print(f"     - 추가: {', '.join(added)}")
    else:
        print(f"     - 변동 없음 (모든 컬럼 이미 존재)")


def _migrate_postgres() -> None:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL 환경변수 필요", file=sys.stderr)
        sys.exit(1)
    import psycopg2
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    existing = _existing_columns_postgres(conn)
    cur = conn.cursor()
    try:
        added = []
        for col, ddl_suffix in NEW_COLUMNS:
            if col in existing:
                continue
            cur.execute(
                f"ALTER TABLE clinic_entries ADD COLUMN IF NOT EXISTS "
                f"{col} {ddl_suffix}"
            )
            added.append(col)
        print(f"[OK] 클리닉 v3 마이그레이션 완료 (Supabase Postgres)")
        if added:
            print(f"     - 추가: {', '.join(added)}")
        else:
            print(f"     - 변동 없음 (모든 컬럼 이미 존재)")
    finally:
        cur.close()
        conn.close()


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true",
                    help="강제로 로컬 SQLite 적용 (SUPABASE_DB_URL 무시)")
    args = ap.parse_args()

    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)
        _migrate_sqlite()
        return

    _load_env_file()
    if is_cloud():
        _migrate_postgres()
    else:
        _migrate_sqlite()


if __name__ == "__main__":
    main()
