#!/usr/bin/env python3
"""PRISM 강사 임상 평가 테이블 — SQLite/Postgres 양쪽 멱등.

매주 강사가 학생별로 5영역 결함도(1~5점)를 직접 입력하는 정성 평가.
의사의 임상 진단에 해당. clinic_entries(정량 누적)와 별개로 존재.

5영역:
- score_p (Precision)   계산실수
- score_r (Reading)     조건해석실패
- score_i (Insight)     개념누락
- score_s (Strategy)    전략선택실패
- score_m (Management)  시간관리

척도: 1=거의 없음, 5=매우 두드러짐

실행:
    python scripts/migrate_prism_assessment.py
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


DDL_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS prism_assessment (
        assessment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id     INTEGER NOT NULL REFERENCES students(student_id),
        eval_date      TEXT NOT NULL,
        score_p        INTEGER NOT NULL CHECK (score_p BETWEEN 1 AND 5),
        score_r        INTEGER NOT NULL CHECK (score_r BETWEEN 1 AND 5),
        score_i        INTEGER NOT NULL CHECK (score_i BETWEEN 1 AND 5),
        score_s        INTEGER NOT NULL CHECK (score_s BETWEEN 1 AND 5),
        score_m        INTEGER NOT NULL CHECK (score_m BETWEEN 1 AND 5),
        note           TEXT,
        created_at     TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_prism_student ON prism_assessment(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_prism_date    ON prism_assessment(eval_date)",
]

DDL_POSTGRES = [
    """
    CREATE TABLE IF NOT EXISTS prism_assessment (
        assessment_id  SERIAL PRIMARY KEY,
        student_id     INTEGER NOT NULL REFERENCES students(student_id),
        eval_date      DATE NOT NULL,
        score_p        INTEGER NOT NULL CHECK (score_p BETWEEN 1 AND 5),
        score_r        INTEGER NOT NULL CHECK (score_r BETWEEN 1 AND 5),
        score_i        INTEGER NOT NULL CHECK (score_i BETWEEN 1 AND 5),
        score_s        INTEGER NOT NULL CHECK (score_s BETWEEN 1 AND 5),
        score_m        INTEGER NOT NULL CHECK (score_m BETWEEN 1 AND 5),
        note           TEXT,
        created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_prism_student ON prism_assessment(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_prism_date    ON prism_assessment(eval_date)",
]


def _migrate_sqlite() -> None:
    conn = get_connection()
    for stmt in DDL_SQLITE:
        conn.execute(stmt)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    print("[OK] prism_assessment 생성 완료 (로컬 SQLite)")


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
        print("[OK] prism_assessment 생성 완료 (Supabase Postgres)")
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
        _migrate_sqlite()
        return
    _load_env_file()
    if is_cloud():
        _migrate_postgres()
    else:
        _migrate_sqlite()


if __name__ == "__main__":
    main()
