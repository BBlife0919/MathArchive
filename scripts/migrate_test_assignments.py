#!/usr/bin/env python3
"""TEST 관리 출제 흐름 재설계 — test_assignments(학습지↔학생 배정) 테이블.

"학생관리 안에서 반 전체에 즉석 출제" 대신 "시험지 생성기에서 학습지를
만들어두고, '내 학습지' 목록에서 반/학생을 골라 출제"하는 흐름으로 바뀌면서
(2026-10-28 사용자 피드백), tests.class_id 로 반 전체에만 묶이던 걸 학생
단위 다대다 배정으로 바꾼다. tests.class_id 컬럼은 건드리지 않는다
(하위호환, 이제 안 쓰지만 지우지 않음).

실행:
    python scripts/migrate_test_assignments.py --local   # 로컬 SQLite만
    python scripts/migrate_test_assignments.py           # .env 보고 자동판단
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


DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS test_assignments (
    assignment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_id       INTEGER NOT NULL REFERENCES tests(test_id),
    student_id    INTEGER NOT NULL REFERENCES students(student_id),
    assigned_at   TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, student_id)
)
"""

DDL_SQLITE_IDX = "CREATE INDEX IF NOT EXISTS idx_testassign_student ON test_assignments(student_id)"

DDL_POSTGRES = """
CREATE TABLE IF NOT EXISTS test_assignments (
    assignment_id SERIAL PRIMARY KEY,
    test_id       INTEGER NOT NULL REFERENCES tests(test_id),
    student_id    INTEGER NOT NULL REFERENCES students(student_id),
    assigned_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(test_id, student_id)
)
"""

DDL_POSTGRES_IDX = "CREATE INDEX IF NOT EXISTS idx_testassign_student ON test_assignments(student_id)"


def migrate(force_local: bool = False) -> None:
    if force_local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    from db import get_connection, is_cloud  # noqa: E402

    cloud = is_cloud()
    conn = get_connection()
    conn.execute(DDL_POSTGRES if cloud else DDL_SQLITE)
    conn.execute(DDL_POSTGRES_IDX if cloud else DDL_SQLITE_IDX)

    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass

    target = "Supabase Postgres" if cloud else "로컬 SQLite"
    print(f"[OK] test_assignments 테이블 마이그레이션 완료 → {target}")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="강제로 SQLite(운영 DB 안 건드림)")
    args = ap.parse_args()
    migrate(force_local=args.local)


if __name__ == "__main__":
    main()
