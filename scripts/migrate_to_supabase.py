#!/usr/bin/env python3
"""SQLite (db/mathdb.sqlite) → Supabase Postgres 일괄 이관.

선행 조건:
- .env 에 SUPABASE_DB_URL 설정 완료
- pip install psycopg2-binary python-dotenv
"""
from __future__ import annotations

import json
import os
import sqlite3
import sys
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
except ImportError:
    pass

import psycopg2
from psycopg2.extras import execute_values, Json

SQLITE_DB = Path(__file__).resolve().parent.parent / "db" / "mathdb.sqlite"
PG_URL = os.environ.get("SUPABASE_DB_URL")

# Postgres 용 스키마 (SQLite → Postgres 타입 매핑)
PG_SCHEMA = """
DROP TABLE IF EXISTS images CASCADE;
DROP TABLE IF EXISTS solutions CASCADE;
DROP TABLE IF EXISTS questions CASCADE;

CREATE TABLE questions (
    question_id     SERIAL PRIMARY KEY,
    file_source     TEXT NOT NULL,
    school          TEXT,
    grade           INTEGER,
    year            INTEGER,
    semester        INTEGER,
    exam_type       TEXT,
    region          TEXT,
    subject         TEXT,
    school_level    TEXT,
    chapter_range   TEXT,
    question_number INTEGER NOT NULL,
    question_text   TEXT,
    question_latex  TEXT,
    choices         JSONB,
    answer          TEXT,
    answer_type     TEXT,
    is_subjective   INTEGER DEFAULT 0,
    subjective_number INTEGER,
    points          REAL,
    chapter         TEXT,
    difficulty      TEXT,
    has_image       INTEGER DEFAULT 0,
    error_note      TEXT,
    problem_type    TEXT,
    problem_type_confidence REAL,
    problem_type_source TEXT
);

CREATE TABLE solutions (
    solution_id     SERIAL PRIMARY KEY,
    question_id     INTEGER NOT NULL REFERENCES questions(question_id),
    solution_text   TEXT,
    solution_latex  TEXT
);

CREATE TABLE images (
    image_id        SERIAL PRIMARY KEY,
    question_id     INTEGER NOT NULL REFERENCES questions(question_id),
    image_ref       TEXT,
    image_path      TEXT,
    image_order     INTEGER,
    image_type      TEXT
);

CREATE INDEX idx_questions_school ON questions(school);
CREATE INDEX idx_questions_chapter ON questions(chapter);
CREATE INDEX idx_questions_difficulty ON questions(difficulty);
CREATE INDEX idx_questions_year ON questions(year);
CREATE INDEX idx_questions_exam ON questions(year, semester, exam_type);
CREATE INDEX idx_solutions_qid ON solutions(question_id);
CREATE INDEX idx_images_qid ON images(question_id);
"""


def main():
    if not PG_URL or "[YOUR-PASSWORD]" in PG_URL:
        print("ERROR: SUPABASE_DB_URL 미설정 또는 비밀번호 placeholder 미교체.",
              file=sys.stderr)
        sys.exit(2)
    if not SQLITE_DB.exists():
        print(f"ERROR: {SQLITE_DB} 없음", file=sys.stderr)
        sys.exit(2)

    print(f"Source: {SQLITE_DB}")
    print(f"Target: {PG_URL.split('@')[1]}")

    sconn = sqlite3.connect(str(SQLITE_DB))
    sconn.row_factory = sqlite3.Row

    pconn = psycopg2.connect(PG_URL)
    pconn.autocommit = False
    pcur = pconn.cursor()

    print("\n[1/3] Postgres 스키마 생성")
    pcur.execute(PG_SCHEMA)
    pconn.commit()

    # questions
    print("[2/3] questions 이관")
    rows = list(sconn.execute("SELECT * FROM questions ORDER BY question_id"))
    cols = rows[0].keys() if rows else []
    print(f"  {len(rows):,}개")
    values = []
    for r in rows:
        d = dict(r)
        # choices JSON 문자열 → Json() wrapper (psycopg2가 JSONB로 변환)
        ch = d.get("choices")
        if ch and isinstance(ch, str):
            try:
                d["choices"] = Json(json.loads(ch))
            except Exception:
                d["choices"] = None
        elif ch is None:
            d["choices"] = None
        values.append(tuple(d.get(c) for c in cols if c != "question_id"))
    placeholders = ",".join([f"%s"] * (len(cols) - 1))
    insert_cols = ",".join([c for c in cols if c != "question_id"])
    # JSONB cast 처리를 위해 execute_values 사용
    execute_values(
        pcur,
        f"INSERT INTO questions ({insert_cols}) VALUES %s",
        values,
        page_size=500,
    )
    pconn.commit()

    # solutions
    print("[3a/3] solutions 이관")
    s_rows = list(sconn.execute("SELECT * FROM solutions ORDER BY solution_id"))
    s_cols = s_rows[0].keys() if s_rows else []
    print(f"  {len(s_rows):,}개")
    s_values = []
    for r in s_rows:
        d = dict(r)
        s_values.append(tuple(d.get(c) for c in s_cols if c != "solution_id"))
    s_insert_cols = ",".join([c for c in s_cols if c != "solution_id"])
    execute_values(
        pcur,
        f"INSERT INTO solutions ({s_insert_cols}) VALUES %s",
        s_values,
        page_size=500,
    )
    pconn.commit()

    # images
    print("[3b/3] images 이관")
    i_rows = list(sconn.execute("SELECT * FROM images ORDER BY image_id"))
    i_cols = i_rows[0].keys() if i_rows else []
    print(f"  {len(i_rows):,}개")
    i_values = []
    for r in i_rows:
        d = dict(r)
        i_values.append(tuple(d.get(c) for c in i_cols if c != "image_id"))
    i_insert_cols = ",".join([c for c in i_cols if c != "image_id"])
    execute_values(
        pcur,
        f"INSERT INTO images ({i_insert_cols}) VALUES %s",
        i_values,
        page_size=500,
    )
    pconn.commit()

    # 검증
    print("\n=== 이관 검증 ===")
    for t in ("questions", "solutions", "images"):
        n = pcur.execute(f"SELECT COUNT(*) FROM {t}").fetchone() if False else None
        pcur.execute(f"SELECT COUNT(*) FROM {t}")
        print(f"  {t}: {pcur.fetchone()[0]:,}")

    pcur.close()
    pconn.close()
    sconn.close()
    print("\n완료.")


if __name__ == "__main__":
    main()
