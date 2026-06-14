#!/usr/bin/env python3
"""카톡 발송 큐 (kakao_send_queue) 마이그레이션 — SQLite/Postgres 양쪽 멱등.

P4 카톡 자동화 v1 의 토대.

테이블 구조:
- AI 가 데이터·표를 생성하면 row 1개 draft 로 적재
- 강사가 학생별 1문장 (instructor_note) 추가 + 승인 → status='approved'
- cron 이 approved row 만 솔라피로 발송 → sent / failed
- PDF §7-3 "하이브리드 강제": instructor_note 미입력 시 발송 차단

실행:
    python scripts/migrate_kakao_queue.py            # 자동 분기
    python scripts/migrate_kakao_queue.py --local    # 강제 SQLite
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


DDL_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS kakao_send_queue (
        queue_id          INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id        INTEGER NOT NULL REFERENCES students(student_id),
        target_phone      TEXT NOT NULL,
        template_code     TEXT NOT NULL,
        ai_draft          TEXT,
        instructor_note   TEXT,
        status            TEXT NOT NULL DEFAULT 'draft'
                          CHECK (status IN ('draft','approved','sent','failed')),
        scheduled_at      TEXT,
        sent_at           TEXT,
        solapi_msg_id     TEXT,
        error_log         TEXT,
        created_at        TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_kakao_student ON kakao_send_queue(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_kakao_status  ON kakao_send_queue(status)",
    "CREATE INDEX IF NOT EXISTS idx_kakao_sched   ON kakao_send_queue(scheduled_at)",
]

DDL_POSTGRES = [
    """
    CREATE TABLE IF NOT EXISTS kakao_send_queue (
        queue_id          SERIAL PRIMARY KEY,
        student_id        INTEGER NOT NULL REFERENCES students(student_id),
        target_phone      TEXT NOT NULL,
        template_code     TEXT NOT NULL,
        ai_draft          TEXT,
        instructor_note   TEXT,
        status            TEXT NOT NULL DEFAULT 'draft'
                          CHECK (status IN ('draft','approved','sent','failed')),
        scheduled_at      TIMESTAMP,
        sent_at           TIMESTAMP,
        solapi_msg_id     TEXT,
        error_log         TEXT,
        created_at        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_kakao_student ON kakao_send_queue(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_kakao_status  ON kakao_send_queue(status)",
    "CREATE INDEX IF NOT EXISTS idx_kakao_sched   ON kakao_send_queue(scheduled_at)",
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
    print("[OK] kakao_send_queue 마이그레이션 완료 (로컬 SQLite)")


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
        print("[OK] kakao_send_queue 마이그레이션 완료 (Supabase Postgres)")
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
