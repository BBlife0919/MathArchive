#!/usr/bin/env python3
"""과제 정밀평가표 (student_assessment) 마이그레이션 — SQLite/Postgres 양쪽 멱등.

P5 과제정밀평가표 v3 — PDF §5-2 명세 반영.

평가 유형 2가지:
- quantity    (정량, 매일)   : grade A/B/C/D 1개
- qualitative (정성, 월 2회) : 4항목 각 1~5점

정량 평가 컬럼은 정성 시 NULL, 그 반대도 마찬가지.

실행:
    python scripts/migrate_student_assessment.py            # 자동 분기
    python scripts/migrate_student_assessment.py --local    # 강제 SQLite
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


DDL_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS student_assessment (
        assessment_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id           INTEGER NOT NULL REFERENCES students(student_id),
        eval_date            TEXT NOT NULL,
        eval_type            TEXT NOT NULL
                             CHECK (eval_type IN ('quantity','qualitative')),
        quantity_grade       TEXT
                             CHECK (quantity_grade IS NULL
                                    OR quantity_grade IN ('A','B','C','D')),
        note_completion      INTEGER
                             CHECK (note_completion IS NULL
                                    OR note_completion BETWEEN 1 AND 5),
        written_completion   INTEGER
                             CHECK (written_completion IS NULL
                                    OR written_completion BETWEEN 1 AND 5),
        textbook_marking     INTEGER
                             CHECK (textbook_marking IS NULL
                                    OR textbook_marking BETWEEN 1 AND 5),
        second_solve_reason  INTEGER
                             CHECK (second_solve_reason IS NULL
                                    OR second_solve_reason BETWEEN 1 AND 5),
        note                 TEXT,
        created_at           TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_assess_student ON student_assessment(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_assess_date    ON student_assessment(eval_date)",
    "CREATE INDEX IF NOT EXISTS idx_assess_type    ON student_assessment(eval_type)",
]

DDL_POSTGRES = [
    """
    CREATE TABLE IF NOT EXISTS student_assessment (
        assessment_id        SERIAL PRIMARY KEY,
        student_id           INTEGER NOT NULL REFERENCES students(student_id),
        eval_date            DATE NOT NULL,
        eval_type            TEXT NOT NULL
                             CHECK (eval_type IN ('quantity','qualitative')),
        quantity_grade       TEXT
                             CHECK (quantity_grade IS NULL
                                    OR quantity_grade IN ('A','B','C','D')),
        note_completion      INTEGER
                             CHECK (note_completion IS NULL
                                    OR note_completion BETWEEN 1 AND 5),
        written_completion   INTEGER
                             CHECK (written_completion IS NULL
                                    OR written_completion BETWEEN 1 AND 5),
        textbook_marking     INTEGER
                             CHECK (textbook_marking IS NULL
                                    OR textbook_marking BETWEEN 1 AND 5),
        second_solve_reason  INTEGER
                             CHECK (second_solve_reason IS NULL
                                    OR second_solve_reason BETWEEN 1 AND 5),
        note                 TEXT,
        created_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_assess_student ON student_assessment(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_assess_date    ON student_assessment(eval_date)",
    "CREATE INDEX IF NOT EXISTS idx_assess_type    ON student_assessment(eval_type)",
]


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def _migrate_sqlite() -> None:
    conn = get_connection()
    for stmt in DDL_SQLITE:
        conn.execute(stmt)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    print("[OK] student_assessment 마이그레이션 완료 (로컬 SQLite)")


def _migrate_postgres() -> None:
    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        print("ERROR: SUPABASE_DB_URL 환경변수 필요", file=sys.stderr)
        sys.exit(1)
    import psycopg2
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        for stmt in DDL_POSTGRES:
            cur.execute(stmt)
        print("[OK] student_assessment 마이그레이션 완료 (Supabase Postgres)")
    finally:
        cur.close()
        conn.close()


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
