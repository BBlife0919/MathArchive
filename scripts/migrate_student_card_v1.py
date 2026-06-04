#!/usr/bin/env python3
"""학생 카드 v1 스키마 마이그레이션 (SQLite/Postgres 양쪽 멱등).

추가/변경:
- students.tenant_id  : 멀티 테넌트 분리 대비 (기본값 'default')
- student_progress    : 진도/숙제/시험/Q-M/자가예측 기록 (학생×일 단위)
- student_log         : 보호자 연락 / 출결 / 관리 메모 로그

실행:
    python scripts/migrate_student_card_v1.py
    SUPABASE_DB_URL=postgresql://... python scripts/migrate_student_card_v1.py
"""

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


DDL_SQLITE = [
    # tenant_id 컬럼 추가 — SQLite는 IF NOT EXISTS 미지원이므로 PRAGMA 체크 후 ALTER
    """
    CREATE TABLE IF NOT EXISTS student_progress (
        progress_id     INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id      INTEGER NOT NULL REFERENCES students(student_id),
        log_date        TEXT NOT NULL,
        category        TEXT NOT NULL,
        chapter         TEXT,
        title           TEXT,
        planned         TEXT,
        actual          TEXT,
        score_raw       INTEGER,
        score_max       INTEGER,
        q_count         INTEGER,
        m_count         INTEGER,
        self_predicted  INTEGER,
        self_actual     INTEGER,
        note            TEXT,
        created_at      TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_progress_student ON student_progress(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_progress_date ON student_progress(log_date)",
    "CREATE INDEX IF NOT EXISTS idx_progress_category ON student_progress(category)",
    """
    CREATE TABLE IF NOT EXISTS student_log (
        log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id  INTEGER NOT NULL REFERENCES students(student_id),
        log_date    TEXT NOT NULL,
        log_type    TEXT NOT NULL,
        summary     TEXT,
        detail      TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_studentlog_student ON student_log(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_studentlog_date ON student_log(log_date)",
    "CREATE INDEX IF NOT EXISTS idx_studentlog_type ON student_log(log_type)",
]

DDL_POSTGRES = [
    "ALTER TABLE students ADD COLUMN IF NOT EXISTS tenant_id TEXT DEFAULT 'default'",
    "CREATE INDEX IF NOT EXISTS idx_students_tenant ON students(tenant_id)",
    """
    CREATE TABLE IF NOT EXISTS student_progress (
        progress_id     SERIAL PRIMARY KEY,
        student_id      INTEGER NOT NULL REFERENCES students(student_id),
        log_date        DATE NOT NULL,
        category        TEXT NOT NULL,
        chapter         TEXT,
        title           TEXT,
        planned         TEXT,
        actual          TEXT,
        score_raw       INTEGER,
        score_max       INTEGER,
        q_count         INTEGER,
        m_count         INTEGER,
        self_predicted  INTEGER,
        self_actual     INTEGER,
        note            TEXT,
        created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_progress_student ON student_progress(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_progress_date ON student_progress(log_date)",
    "CREATE INDEX IF NOT EXISTS idx_progress_category ON student_progress(category)",
    """
    CREATE TABLE IF NOT EXISTS student_log (
        log_id      SERIAL PRIMARY KEY,
        student_id  INTEGER NOT NULL REFERENCES students(student_id),
        log_date    DATE NOT NULL,
        log_type    TEXT NOT NULL,
        summary     TEXT,
        detail      TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_studentlog_student ON student_log(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_studentlog_date ON student_log(log_date)",
    "CREATE INDEX IF NOT EXISTS idx_studentlog_type ON student_log(log_type)",
]


def _sqlite_add_tenant_id(conn) -> None:
    """SQLite에는 ADD COLUMN IF NOT EXISTS가 없으므로 PRAGMA로 체크 후 ALTER."""
    rows = conn.execute("PRAGMA table_info(students)").fetchall()
    cols = {r[1] for r in rows}
    if "tenant_id" not in cols:
        conn.execute("ALTER TABLE students ADD COLUMN tenant_id TEXT DEFAULT 'default'")
        conn.execute("UPDATE students SET tenant_id = 'default' WHERE tenant_id IS NULL")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_students_tenant ON students(tenant_id)")


def migrate() -> None:
    cloud = is_cloud()
    conn = get_connection()
    ddl = DDL_POSTGRES if cloud else DDL_SQLITE

    if not cloud:
        _sqlite_add_tenant_id(conn)

    for stmt in ddl:
        conn.execute(stmt)

    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass

    target = "Supabase Postgres" if cloud else "로컬 SQLite"
    print(f"[OK] 학생 카드 v1 스키마 마이그레이션 완료 → {target}")
    print(f"     - students.tenant_id 컬럼 추가/확인 (default='default')")
    print(f"     - student_progress 테이블 생성/확인")
    print(f"     - student_log 테이블 생성/확인")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    migrate()
