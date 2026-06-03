#!/usr/bin/env python3
"""같은 학교·시험·문항번호·본문이 똑같은 진짜 중복 행 제거.

이전 dedupe_questions.py 는 (file_source, question_number) 기준이라
같은 시험을 두 출판사 단원으로 분류해서 두 file_source 로 적재된 케이스를
못 잡음. 이 스크립트는 (school, grade, year, semester, exam_type,
question_number, question_text) 가 모두 같으면 중복으로 보고,
question_id 최소값만 keep.

사용:
    python3 scripts/dedupe_same_question.py --dry-run
    python3 scripts/dedupe_same_question.py
    python3 scripts/dedupe_same_question.py --cloud --dry-run
    python3 scripts/dedupe_same_question.py --cloud
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


KEY_COLS = "school, grade, year, semester, exam_type, question_number, question_text"


def find_duplicates(conn) -> list[int]:
    """삭제 대상 question_id (그룹별 MIN 제외)."""
    cur = conn.execute(
        f"SELECT q.question_id FROM questions q "
        f"JOIN ("
        f"  SELECT {KEY_COLS}, MIN(question_id) AS keeper "
        f"  FROM questions "
        f"  GROUP BY {KEY_COLS} "
        f"  HAVING COUNT(*) > 1"
        f") d ON "
        f"  COALESCE(q.school,'')=COALESCE(d.school,'') AND "
        f"  COALESCE(q.grade,-1)=COALESCE(d.grade,-1) AND "
        f"  COALESCE(q.year,-1)=COALESCE(d.year,-1) AND "
        f"  COALESCE(q.semester,-1)=COALESCE(d.semester,-1) AND "
        f"  COALESCE(q.exam_type,'')=COALESCE(d.exam_type,'') AND "
        f"  COALESCE(q.question_number,-1)=COALESCE(d.question_number,-1) AND "
        f"  COALESCE(q.question_text,'')=COALESCE(d.question_text,'') AND "
        f"  q.question_id != d.keeper"
    )
    return [r[0] for r in cur.fetchall()]


def delete_in_batches(conn, table: str, idcol: str, ids: list[int],
                      placeholder: str, batch: int = 1000) -> int:
    n = 0
    for i in range(0, len(ids), batch):
        chunk = ids[i:i + batch]
        marks = ",".join([placeholder] * len(chunk))
        conn.execute(
            f"DELETE FROM {table} WHERE {idcol} IN ({marks})", chunk,
        )
        n += len(chunk)
    return n


def run(conn, placeholder: str, dry_run: bool):
    dup_ids = find_duplicates(conn)
    cur = conn.execute(
        f"SELECT COUNT(*) FROM ("
        f"  SELECT 1 FROM questions GROUP BY {KEY_COLS} HAVING COUNT(*) > 1"
        f") t"
    )
    n_groups = cur.fetchone()[0]
    print(f"중복 그룹: {n_groups}")
    print(f"삭제 대상 행: {len(dup_ids)}")
    if not dup_ids or dry_run:
        if dry_run and dup_ids:
            print("[DRY-RUN] 자식 (solutions/images/flagged_problems) 도 cascade 삭제 예정")
        return

    n_sol = delete_in_batches(conn, "solutions", "question_id",
                              dup_ids, placeholder)
    n_img = delete_in_batches(conn, "images", "question_id",
                              dup_ids, placeholder)
    try:
        n_flag = delete_in_batches(conn, "flagged_problems", "question_id",
                                   dup_ids, placeholder)
    except Exception:
        n_flag = 0
    n_q = delete_in_batches(conn, "questions", "question_id",
                            dup_ids, placeholder)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    print(f"✅ 삭제: questions={n_q}, solutions={n_sol}, images={n_img}, "
          f"flagged={n_flag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cloud:
        import psycopg2

        class _Wrapper:
            def __init__(self, c):
                self._c = c
                self._cur = c.cursor()

            def execute(self, sql, params=()):
                self._cur.execute(sql, params)
                return self._cur

            def commit(self):
                self._c.commit()

        pconn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
        pconn.autocommit = False
        run(_Wrapper(pconn), "%s", args.dry_run)
        pconn.close()
    else:
        db = ROOT / "db" / "mathdb.sqlite"
        conn = sqlite3.connect(db)
        run(conn, "?", args.dry_run)
        conn.close()


if __name__ == "__main__":
    main()
