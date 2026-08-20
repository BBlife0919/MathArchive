#!/usr/bin/env python3
"""출제 이력 (exam_generation_log) 마이그레이션 — SQLite/Postgres 양쪽 멱등.

시험지/교재 PDF를 실제로 다운로드할 때마다 그 문항 id들을 기록해서,
"기존 출제 문제 제외"(최근 N일 이내 출제된 문항 검색에서 제외) 필터의
근거 데이터로 쓴다. 검색/미리보기 단계에서는 기록하지 않고, 실제 PDF
다운로드가 성공한 시점에만 기록한다(pdf_service.build_exam_pdf/build_book_pdf).

날짜 비교는 SQLite/Postgres 방언 차이를 피하려고 TIMESTAMP 대신 정수
unix epoch(초)로 저장한다.

실행:
    python scripts/migrate_exam_generation_log.py            # 자동 분기
    python scripts/migrate_exam_generation_log.py --local    # 강제 SQLite
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


DDL_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS exam_generation_log (
        log_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id   INTEGER NOT NULL REFERENCES questions(question_id),
        source        TEXT NOT NULL CHECK (source IN ('exam_pdf','book_pdf')),
        generated_by  INTEGER REFERENCES users(user_id),
        generated_at  INTEGER NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_examgen_qid  ON exam_generation_log(question_id)",
    "CREATE INDEX IF NOT EXISTS idx_examgen_time ON exam_generation_log(generated_at)",
]

DDL_POSTGRES = [
    """
    CREATE TABLE IF NOT EXISTS exam_generation_log (
        log_id        SERIAL PRIMARY KEY,
        question_id   INTEGER NOT NULL REFERENCES questions(question_id),
        source        TEXT NOT NULL CHECK (source IN ('exam_pdf','book_pdf')),
        generated_by  INTEGER REFERENCES users(user_id),
        generated_at  BIGINT NOT NULL
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_examgen_qid  ON exam_generation_log(question_id)",
    "CREATE INDEX IF NOT EXISTS idx_examgen_time ON exam_generation_log(generated_at)",
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
    print("[OK] exam_generation_log 마이그레이션 완료 (로컬 SQLite)")


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
        print("[OK] exam_generation_log 마이그레이션 완료 (Supabase Postgres)")
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
