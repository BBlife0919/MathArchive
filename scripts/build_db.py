#!/usr/bin/env python3
"""파싱된 HWPX 결과를 SQLite DB로 적재한다.

사용법:
    python scripts/build_db.py                          # raw/ 전체 파싱 → DB
    python scripts/build_db.py --db db/mathdb.sqlite    # DB 경로 지정
    python scripts/build_db.py --json-dir parsed/       # 기존 JSON 사용
"""

import argparse
import json
import os
import sqlite3
import sys
from pathlib import Path

# parse_hwpx 모듈 임포트
sys.path.insert(0, os.path.join(os.path.dirname(__file__)))
from parse_hwpx import parse_hwpx

# ── DB 스키마 ─────────────────────────────────────────────────
SCHEMA = """
CREATE TABLE IF NOT EXISTS questions (
    question_id     INTEGER PRIMARY KEY AUTOINCREMENT,
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
    choices         TEXT,           -- JSON array
    answer          TEXT,
    answer_type     TEXT,
    is_subjective   INTEGER DEFAULT 0,
    subjective_number INTEGER,
    points          REAL,
    chapter         TEXT,
    difficulty      TEXT,
    has_image       INTEGER DEFAULT 0,
    error_note      TEXT
);

CREATE TABLE IF NOT EXISTS solutions (
    solution_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id     INTEGER NOT NULL,
    solution_text   TEXT,
    solution_latex  TEXT,
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);

CREATE TABLE IF NOT EXISTS images (
    image_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id     INTEGER NOT NULL,
    image_ref       TEXT,
    image_path      TEXT,
    image_order     INTEGER,
    image_type      TEXT,
    FOREIGN KEY (question_id) REFERENCES questions(question_id)
);

CREATE INDEX IF NOT EXISTS idx_questions_school ON questions(school);
CREATE INDEX IF NOT EXISTS idx_questions_chapter ON questions(chapter);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_year ON questions(year);
CREATE INDEX IF NOT EXISTS idx_questions_exam ON questions(year, semester, exam_type);
CREATE INDEX IF NOT EXISTS idx_solutions_qid ON solutions(question_id);
CREATE INDEX IF NOT EXISTS idx_images_qid ON images(question_id);
"""


def create_db(db_path: str) -> sqlite3.Connection:
    """DB 파일을 생성하고 스키마를 적용한다."""
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def insert_parsed_result(conn: sqlite3.Connection, result: dict,
                         image_dir: str = None):
    """파싱 결과 딕셔너리를 DB에 삽입한다."""
    meta = result.get("file_metadata", {})
    file_source = result["file_source"]

    # 파일명 메타데이터
    school = meta.get("school", "")
    grade = _safe_int(meta.get("grade"))
    year = _safe_int(meta.get("year"))
    semester = _safe_int(meta.get("semester"))
    exam_type = meta.get("exam_type", "")
    region = meta.get("region", "")
    subject = meta.get("subject", "")
    school_level = meta.get("school_level", "")
    chapter_range = meta.get("chapter_range", "")

    cursor = conn.cursor()

    for q in result["questions"]:
        # questions 테이블 삽입
        choices_json = json.dumps(q["choices"], ensure_ascii=False)

        cursor.execute("""
            INSERT INTO questions (
                file_source, school, grade, year, semester, exam_type,
                region, subject, school_level, chapter_range,
                question_number, question_text, question_latex,
                choices, answer, answer_type,
                is_subjective, subjective_number,
                points, chapter, difficulty, has_image, error_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            file_source, school, grade, year, semester, exam_type,
            region, subject, school_level, chapter_range,
            q["question_number"],
            q["question_text"],
            q["question_text"],  # question_latex = question_text (이미 LaTeX 포함)
            choices_json,
            q["answer"],
            q["answer_type"],
            1 if q["is_subjective"] else 0,
            q.get("subjective_number"),
            q["points"],
            q["chapter"],
            q["difficulty"],
            1 if q["has_image"] else 0,
            q["error_note"] or None,
        ))

        question_id = cursor.lastrowid

        # solutions 테이블 삽입
        if q["solution_text"]:
            cursor.execute("""
                INSERT INTO solutions (question_id, solution_text, solution_latex)
                VALUES (?, ?, ?)
            """, (
                question_id,
                q["solution_text"],
                q["solution_text"],  # solution_latex = solution_text (이미 LaTeX 포함)
            ))

        # images 테이블 삽입
        for order, ref in enumerate(q.get("image_refs", []), 1):
            image_path = ""
            for p in q.get("image_paths", []):
                if ref in p:
                    image_path = p
                    break
            cursor.execute("""
                INSERT INTO images (question_id, image_ref, image_path, image_order, image_type)
                VALUES (?, ?, ?, ?, ?)
            """, (
                question_id,
                ref,
                image_path,
                order,
                "question",  # 워터마크는 이미 필터링됨
            ))

    conn.commit()


def _safe_int(val):
    """안전하게 정수로 변환한다."""
    if val is None:
        return None
    try:
        return int(val)
    except (ValueError, TypeError):
        return None


def print_stats(conn: sqlite3.Connection):
    """DB 통계를 출력한다."""
    cur = conn.cursor()

    print("\n" + "=" * 60)
    print("  DB 적재 결과")
    print("=" * 60)

    # 기본 통계
    total_q = cur.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    total_s = cur.execute("SELECT COUNT(*) FROM solutions").fetchone()[0]
    total_i = cur.execute("SELECT COUNT(*) FROM images").fetchone()[0]
    total_files = cur.execute("SELECT COUNT(DISTINCT file_source) FROM questions").fetchone()[0]

    print(f"\n  파일 수:    {total_files}")
    print(f"  총 문항:    {total_q}")
    print(f"  해설:       {total_s}")
    print(f"  이미지:     {total_i}")

    # 문항 유형
    choice_q = cur.execute(
        "SELECT COUNT(*) FROM questions WHERE answer_type='choice'"
    ).fetchone()[0]
    subj_q = cur.execute(
        "SELECT COUNT(*) FROM questions WHERE is_subjective=1"
    ).fetchone()[0]
    print(f"\n  선택형:     {choice_q}")
    print(f"  서답/서술형: {subj_q}")

    # 난이도 분포
    print("\n  [난이도 분포]")
    for row in cur.execute(
        "SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty ORDER BY difficulty"
    ):
        print(f"    {row[0] or '미지정':4s}: {row[1]:4d}문항")

    # 단원별 분포 (상위 10개)
    print("\n  [단원별 문항 수 (상위 10)]")
    for row in cur.execute(
        "SELECT chapter, COUNT(*) as cnt FROM questions "
        "GROUP BY chapter ORDER BY cnt DESC LIMIT 10"
    ):
        print(f"    {row[0]:20s}: {row[1]:4d}문항")

    # 학교별 분포
    print(f"\n  [학교 수: {cur.execute('SELECT COUNT(DISTINCT school) FROM questions').fetchone()[0]}]")

    # 지역별 분포
    print("\n  [지역별 분포]")
    for row in cur.execute(
        "SELECT region, COUNT(*) as cnt FROM questions "
        "GROUP BY region ORDER BY cnt DESC"
    ):
        print(f"    {row[0] or '미지정':6s}: {row[1]:4d}문항")

    # 배점 통계
    avg_pts = cur.execute(
        "SELECT AVG(points), MIN(points), MAX(points) FROM questions WHERE points IS NOT NULL"
    ).fetchone()
    if avg_pts[0]:
        print(f"\n  [배점] 평균={avg_pts[0]:.1f}  최소={avg_pts[1]:.1f}  최대={avg_pts[2]:.1f}")

    # 이미지 보유 문항
    img_q = cur.execute(
        "SELECT COUNT(*) FROM questions WHERE has_image=1"
    ).fetchone()[0]
    print(f"\n  이미지 포함 문항: {img_q}")

    # 오류 문항
    err_q = cur.execute(
        "SELECT COUNT(*) FROM questions WHERE error_note IS NOT NULL"
    ).fetchone()[0]
    print(f"  오류 표기 문항:   {err_q}")

    print("\n" + "=" * 60)


def main():
    parser = argparse.ArgumentParser(description="HWPX 파싱 결과 → SQLite DB 적재")
    parser.add_argument("--db", default="db/mathdb.sqlite",
                        help="DB 파일 경로 (기본: db/mathdb.sqlite)")
    parser.add_argument("--raw-dir", default="raw",
                        help="원본 HWPX 디렉토리 (기본: raw)")
    parser.add_argument("--image-dir", default="images",
                        help="이미지 추출 디렉토리 (기본: images)")
    parser.add_argument("--no-images", action="store_true",
                        help="이미지 추출 건너뛰기")
    parser.add_argument("--rebuild", action="store_true",
                        help="기존 DB 삭제 후 재구축")
    args = parser.parse_args()

    # DB 재구축
    if args.rebuild and os.path.exists(args.db):
        os.remove(args.db)
        print(f"기존 DB 삭제: {args.db}", file=sys.stderr)

    conn = create_db(args.db)

    # 이미 적재된 파일 확인
    existing = set()
    for row in conn.execute("SELECT DISTINCT file_source FROM questions"):
        existing.add(row[0])

    # HWPX 파일 목록
    hwpx_files = sorted([
        f for f in os.listdir(args.raw_dir)
        if f.endswith(".hwpx")
    ])

    if not hwpx_files:
        print(f"HWPX 파일이 없습니다: {args.raw_dir}", file=sys.stderr)
        sys.exit(1)

    img_dir = None if args.no_images else args.image_dir
    processed = 0
    skipped = 0
    errors = []

    for i, fname in enumerate(hwpx_files, 1):
        if fname in existing:
            skipped += 1
            continue

        path = os.path.join(args.raw_dir, fname)
        try:
            result = parse_hwpx(path, image_output_dir=img_dir)
            insert_parsed_result(conn, result, img_dir)
            processed += 1
            n = result["total_questions"]
            school = result["file_metadata"].get("school", "?")
            print(f"  [{i:2d}/{len(hwpx_files)}] {school:8s} → {n:2d}문항",
                  file=sys.stderr)
        except Exception as e:
            errors.append((fname, str(e)))
            print(f"  [{i:2d}/{len(hwpx_files)}] ERROR: {fname[:40]}... {e}",
                  file=sys.stderr)

    print(f"\n처리: {processed}  건너뜀: {skipped}  에러: {len(errors)}",
          file=sys.stderr)

    if errors:
        print("\n에러 목록:", file=sys.stderr)
        for name, err in errors:
            print(f"  {name[:50]}: {err}", file=sys.stderr)

    # 통계 출력
    print_stats(conn)
    conn.close()

    # 수식 품질 자동 스캔 (변환 누락 자동 탐지)
    print("\n" + "=" * 60, file=sys.stderr)
    print("  수식 품질 자동 스캔", file=sys.stderr)
    print("=" * 60, file=sys.stderr)
    try:
        import subprocess
        subprocess.run(
            [sys.executable,
             os.path.join(os.path.dirname(__file__), "scan_db_issues.py"),
             "--db", args.db, "--top", "3"],
            check=False,
        )
    except Exception as e:
        print(f"  (스캔 실행 실패: {e})", file=sys.stderr)


if __name__ == "__main__":
    main()
