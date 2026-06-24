#!/usr/bin/env python3
"""clinic_entries 외부 문제 지원 — SQLite/Postgres 양쪽 멱등.

변경:
- wrong_question_id : NOT NULL → NULL 허용
- external_label    : TEXT NULL 신규 (학교/교재/페이지/메모 자유 입력)

DB에 적재된 문제(question_id)와 적재 안 된 외부 문제(시판 교재·내신지)
둘 다 클리닉 입력 가능하도록.

실행:
    python scripts/migrate_clinic_external.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


DDL_POSTGRES = [
    "ALTER TABLE clinic_entries ALTER COLUMN wrong_question_id DROP NOT NULL",
    "ALTER TABLE clinic_entries ADD COLUMN IF NOT EXISTS external_label TEXT",
]


def _has_column(conn, table: str, col: str) -> bool:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return any(r[1] == col for r in rows)


def _sqlite_migrate(conn) -> None:
    """SQLite는 NOT NULL DROP 불가 → 테이블 재생성. external_label 도 같이 추가."""
    # 이미 external_label 있으면 멱등 종료
    if _has_column(conn, "clinic_entries", "external_label"):
        # 기존 NOT NULL 도 풀려있는지 확인
        rows = conn.execute("PRAGMA table_info(clinic_entries)").fetchall()
        wq_row = next((r for r in rows if r[1] == "wrong_question_id"), None)
        if wq_row and wq_row[3] == 0:  # notnull=0
            print("[SKIP] 이미 마이그레이션 완료")
            return

    conn.execute("BEGIN")
    try:
        conn.execute("""
            CREATE TABLE clinic_entries_new (
                entry_id             INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id           INTEGER NOT NULL REFERENCES students(student_id),
                wrong_question_id    INTEGER,
                wrong_date           TEXT NOT NULL,
                error_code           TEXT NOT NULL,
                keyword              TEXT,
                prescribed_qids      TEXT,
                external_label       TEXT,
                retry_d3_status      TEXT,
                retry_d7_status      TEXT,
                retry_d14_status     TEXT,
                retry_d30_status     TEXT,
                retry_exam_2w_status TEXT,
                created_at           TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # 기존 데이터 컬럼만 추려서 복사 (existing columns)
        existing_cols = [r[1] for r in conn.execute("PRAGMA table_info(clinic_entries)").fetchall()]
        copy_cols = [c for c in existing_cols if c in {
            "entry_id", "student_id", "wrong_question_id", "wrong_date",
            "error_code", "keyword", "prescribed_qids",
            "retry_d3_status", "retry_d7_status", "retry_d14_status",
            "retry_d30_status", "retry_exam_2w_status", "created_at",
        }]
        cols_csv = ", ".join(copy_cols)
        conn.execute(
            f"INSERT INTO clinic_entries_new ({cols_csv}) "
            f"SELECT {cols_csv} FROM clinic_entries"
        )
        conn.execute("DROP TABLE clinic_entries")
        conn.execute("ALTER TABLE clinic_entries_new RENAME TO clinic_entries")
        # 인덱스 재생성
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clinic_student ON clinic_entries(student_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_clinic_date    ON clinic_entries(wrong_date)")
        conn.execute("COMMIT")
        print("[OK] SQLite clinic_entries 재구성 완료 (NULL 허용 + external_label)")
    except Exception:
        conn.execute("ROLLBACK")
        raise


def _pg_migrate() -> None:
    import psycopg2
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL 환경변수 필요", file=sys.stderr)
        sys.exit(1)
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        for stmt in DDL_POSTGRES:
            cur.execute(stmt)
        print("[OK] Postgres clinic_entries 마이그레이션 완료 (NULL 허용 + external_label)")
    finally:
        cur.close()
        conn.close()


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="강제로 SQLite")
    args = ap.parse_args()
    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    if is_cloud():
        _pg_migrate()
    else:
        conn = get_connection()
        _sqlite_migrate(conn)


if __name__ == "__main__":
    main()
