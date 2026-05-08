#!/usr/bin/env python3
"""클리닉 MVP용 DB 스키마 마이그레이션 (멱등, SQLite/Postgres 양쪽 지원).

추가 테이블:
- students        : 학생 마스터
- clinic_entries  : 오답 1건 = 1행, 처방된 인출 3문항 + D+3/7/14 재도전 상태

실행:
    # 로컬 SQLite
    python scripts/migrate_clinic_schema.py

    # Streamlit Cloud / Supabase Postgres
    SUPABASE_DB_URL=postgresql://... python scripts/migrate_clinic_schema.py
"""

import argparse
import sys
from pathlib import Path

# app/ 모듈 경로 등록
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402

DDL_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id  INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        school      TEXT,
        grade       INTEGER,
        class_name  TEXT,
        note        TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_students_school ON students(school)",
    """
    CREATE TABLE IF NOT EXISTS clinic_entries (
        entry_id           INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id         INTEGER NOT NULL REFERENCES students(student_id),
        wrong_question_id  INTEGER NOT NULL REFERENCES questions(question_id),
        wrong_date         TEXT NOT NULL,
        error_code         TEXT NOT NULL,
        keyword            TEXT,
        prescribed_qids    TEXT,
        retry_d3_status    TEXT DEFAULT 'pending',
        retry_d7_status    TEXT DEFAULT 'pending',
        retry_d14_status   TEXT DEFAULT 'pending',
        created_at         TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_clinic_student ON clinic_entries(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_clinic_date ON clinic_entries(wrong_date)",
]

DDL_POSTGRES = [
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id  SERIAL PRIMARY KEY,
        name        TEXT NOT NULL,
        school      TEXT,
        grade       INTEGER,
        class_name  TEXT,
        note        TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_students_school ON students(school)",
    """
    CREATE TABLE IF NOT EXISTS clinic_entries (
        entry_id           SERIAL PRIMARY KEY,
        student_id         INTEGER NOT NULL REFERENCES students(student_id),
        wrong_question_id  INTEGER NOT NULL REFERENCES questions(question_id),
        wrong_date         DATE NOT NULL,
        error_code         TEXT NOT NULL,
        keyword            TEXT,
        prescribed_qids    JSONB,
        retry_d3_status    TEXT DEFAULT 'pending',
        retry_d7_status    TEXT DEFAULT 'pending',
        retry_d14_status   TEXT DEFAULT 'pending',
        created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_clinic_student ON clinic_entries(student_id)",
    "CREATE INDEX IF NOT EXISTS idx_clinic_date ON clinic_entries(wrong_date)",
]

ERROR_CODES = [
    "개념누락", "조건해석실패", "전략선택실패", "계산실수", "시간관리"
]


def migrate() -> None:
    cloud = is_cloud()
    conn = get_connection()
    ddl = DDL_POSTGRES if cloud else DDL_SQLITE

    for stmt in ddl:
        conn.execute(stmt)

    # SQLite는 명시적 commit 필요 (Postgres _PgConnection은 autocommit=True)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass

    target = "Supabase Postgres" if cloud else "로컬 SQLite"
    print(f"[OK] 스키마 마이그레이션 완료 → {target}")
    print(f"     - students 테이블 생성/확인")
    print(f"     - clinic_entries 테이블 생성/확인")
    print(f"     - 오류코드 5분류: {', '.join(ERROR_CODES)}")


if __name__ == "__main__":
    argparse.ArgumentParser(description=__doc__).parse_args()
    migrate()
