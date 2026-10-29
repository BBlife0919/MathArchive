#!/usr/bin/env python3
"""학생 삭제 기능 — students.is_active 컬럼(소프트 삭제).

학생은 clinic_entries/prism_assessment/student_progress/student_assessment/
student_log/test_results 등 여러 테이블이 FK로 참조하고 있어, 하드 삭제는
참조 무결성 위반(Postgres) 또는 조용한 고아 레코드(SQLite)를 낳는다.
대신 is_active=0 플래그로 숨기기만 한다 — 데이터는 보존, 목록/대시보드에서만
제외(2026-10-30).

실행:
    python scripts/migrate_student_soft_delete.py --local   # 로컬 SQLite만
    python scripts/migrate_student_soft_delete.py           # .env 보고 자동판단
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


DDL_POSTGRES = (
    "ALTER TABLE students ADD COLUMN IF NOT EXISTS "
    "is_active INTEGER NOT NULL DEFAULT 1"
)


def _sqlite_add_is_active(conn) -> None:
    cols = [r[1] for r in conn.execute("PRAGMA table_info(students)").fetchall()]
    if "is_active" not in cols:
        conn.execute(
            "ALTER TABLE students ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1")


def migrate(force_local: bool = False) -> None:
    if force_local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    from db import get_connection, is_cloud  # noqa: E402

    cloud = is_cloud()
    conn = get_connection()
    if cloud:
        conn.execute(DDL_POSTGRES)
    else:
        _sqlite_add_is_active(conn)

    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass

    target = "Supabase Postgres" if cloud else "로컬 SQLite"
    print(f"[OK] students.is_active 컬럼 마이그레이션 완료 → {target}")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="강제로 SQLite(운영 DB 안 건드림)")
    args = ap.parse_args()
    migrate(force_local=args.local)


if __name__ == "__main__":
    main()
