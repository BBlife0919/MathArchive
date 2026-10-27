#!/usr/bin/env python3
"""반(class) 관리 + TEST 채점 기록 테이블 — SQLite/Postgres 양쪽 멱등.

신규:
- classes            반 엔티티(지금까지 students.class_name 은 자유텍스트였음)
- students.class_id  반 FK(신규 컬럼). 기존 class_name 값은 그대로 두고(하위호환),
                      distinct 값마다 classes 행을 자동 생성해 매칭 학생에 채운다.
- tests              출제한 시험/학습지 정의(문항id 목록은 JSON으로 저장)
- test_results       학생별 응시/채점 결과(총점)
- test_answers       문항별 정답/오답 기록

채점에서 오답 처리된 문항은 기존 clinic_entries 재도전 추적(D+3/7/14/30)을
그대로 탄다 — clinic_logic.ERROR_CODES 에 "test_wrong" 한 코드만 추가하면
되므로 여긴 손 안 댐(스키마 변경 없음).

실행:
    python scripts/migrate_class_test_management.py --local   # 로컬 SQLite만
    python scripts/migrate_class_test_management.py           # .env 보고 자동판단
"""
from __future__ import annotations

import argparse
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
    CREATE TABLE IF NOT EXISTS classes (
        class_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        name        TEXT NOT NULL,
        teacher     TEXT,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS tests (
        test_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        title          TEXT NOT NULL,
        class_id       INTEGER REFERENCES classes(class_id),
        question_ids   TEXT NOT NULL,
        chapter_label  TEXT,
        created_by     INTEGER REFERENCES users(user_id),
        created_at     TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_tests_class ON tests(class_id)",
    """
    CREATE TABLE IF NOT EXISTS test_results (
        result_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        test_id      INTEGER NOT NULL REFERENCES tests(test_id),
        student_id   INTEGER NOT NULL REFERENCES students(student_id),
        graded_at    TEXT,
        score        INTEGER,
        total        INTEGER,
        created_at   TEXT DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(test_id, student_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_testresults_student ON test_results(student_id)",
    """
    CREATE TABLE IF NOT EXISTS test_answers (
        answer_id    INTEGER PRIMARY KEY AUTOINCREMENT,
        result_id    INTEGER NOT NULL REFERENCES test_results(result_id),
        question_id  INTEGER NOT NULL,
        is_correct   INTEGER NOT NULL,
        created_at   TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_testanswers_result ON test_answers(result_id)",
]

DDL_POSTGRES = [
    """
    CREATE TABLE IF NOT EXISTS classes (
        class_id    SERIAL PRIMARY KEY,
        name        TEXT NOT NULL,
        teacher     TEXT,
        created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "ALTER TABLE students ADD COLUMN IF NOT EXISTS class_id INTEGER REFERENCES classes(class_id)",
    """
    CREATE TABLE IF NOT EXISTS tests (
        test_id        SERIAL PRIMARY KEY,
        title          TEXT NOT NULL,
        class_id       INTEGER REFERENCES classes(class_id),
        question_ids   TEXT NOT NULL,
        chapter_label  TEXT,
        created_by     INTEGER REFERENCES users(user_id),
        created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_tests_class ON tests(class_id)",
    """
    CREATE TABLE IF NOT EXISTS test_results (
        result_id    SERIAL PRIMARY KEY,
        test_id      INTEGER NOT NULL REFERENCES tests(test_id),
        student_id   INTEGER NOT NULL REFERENCES students(student_id),
        graded_at    TIMESTAMP,
        score        INTEGER,
        total        INTEGER,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(test_id, student_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_testresults_student ON test_results(student_id)",
    """
    CREATE TABLE IF NOT EXISTS test_answers (
        answer_id    SERIAL PRIMARY KEY,
        result_id    INTEGER NOT NULL REFERENCES test_results(result_id),
        question_id  INTEGER NOT NULL,
        is_correct   BOOLEAN NOT NULL,
        created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_testanswers_result ON test_answers(result_id)",
]


def _sqlite_add_class_id(conn) -> None:
    """SQLite에는 ADD COLUMN IF NOT EXISTS가 없으므로 PRAGMA로 체크 후 ALTER."""
    rows = conn.execute("PRAGMA table_info(students)").fetchall()
    cols = {r[1] for r in rows}
    if "class_id" not in cols:
        conn.execute("ALTER TABLE students ADD COLUMN class_id INTEGER REFERENCES classes(class_id)")


def _backfill_classes(conn, cloud: bool) -> int:
    """기존 students.class_name(자유텍스트) distinct 값마다 classes 행을
    만들고, 매칭되는 학생들의 class_id 를 채운다. 이미 class_id 가 있는
    학생은 건드리지 않는다(멱등 — 여러 번 돌려도 안전).

    cur.lastrowid 는 SQLite 전용(DB-API 비표준)이라 Postgres에서는
    OID 미지원 테이블에서 신뢰할 수 없는 값(0 등)을 돌려준다 — 반드시
    RETURNING 으로 분기해야 한다(2026-10-27 운영 마이그레이션 중 FK
    위반으로 실제 발견: class_id=0 으로 UPDATE 시도하다 실패).
    """
    names = [r[0] for r in conn.execute(
        "SELECT DISTINCT class_name FROM students "
        "WHERE class_name IS NOT NULL AND TRIM(class_name) != '' "
        "AND class_id IS NULL"
    ).fetchall()]
    n = 0
    for name in names:
        existing = conn.execute(
            "SELECT class_id FROM classes WHERE name=?", (name,)).fetchone()
        if existing:
            class_id = existing[0]
        elif cloud:
            cur = conn.execute(
                "INSERT INTO classes (name) VALUES (?) RETURNING class_id", (name,))
            class_id = cur.fetchone()[0]
        else:
            cur = conn.execute(
                "INSERT INTO classes (name) VALUES (?)", (name,))
            class_id = cur.lastrowid
        conn.execute(
            "UPDATE students SET class_id=? "
            "WHERE class_name=? AND class_id IS NULL",
            (class_id, name))
        n += 1
    return n


def migrate(force_local: bool = False) -> None:
    if force_local:
        os.environ.pop("SUPABASE_DB_URL", None)
    else:
        _load_env_file()

    cloud = is_cloud()
    conn = get_connection()
    ddl = DDL_POSTGRES if cloud else DDL_SQLITE

    if not cloud:
        # classes 먼저 만들어야 students.class_id 의 FK 대상이 생긴다.
        conn.execute(ddl[0])
        _sqlite_add_class_id(conn)
        for stmt in ddl[1:]:
            conn.execute(stmt)
    else:
        for stmt in ddl:
            conn.execute(stmt)
    backfilled = _backfill_classes(conn, cloud)

    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass

    target = "Supabase Postgres" if cloud else "로컬 SQLite"
    print(f"[OK] 반 관리 + TEST 채점 스키마 마이그레이션 완료 → {target}")
    print("     - classes 테이블 생성/확인")
    print("     - students.class_id 컬럼 추가/확인")
    print(f"     - 기존 class_name {backfilled}종 → classes 자동 생성 + 학생 매칭")
    print("     - tests / test_results / test_answers 테이블 생성/확인")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true", help="강제로 SQLite(운영 DB 안 건드림)")
    args = ap.parse_args()
    migrate(force_local=args.local)


if __name__ == "__main__":
    main()
