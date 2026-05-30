#!/usr/bin/env python3
"""(file_source, question_number) 가 같은 중복 적재 행 제거.

각 그룹에서 question_id 가 가장 작은 행만 keep, 나머지 + 자식
(solutions / images / flagged_problems) 행도 함께 삭제한다.

사용:
    python3 scripts/dedupe_questions.py --dry-run        # 로컬 SQLite
    python3 scripts/dedupe_questions.py                  # 로컬 SQLite (실행)
    python3 scripts/dedupe_questions.py --cloud --dry-run
    python3 scripts/dedupe_questions.py --cloud
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


def _find_duplicate_ids(conn, placeholder: str) -> list[int]:
    """삭제 대상 question_id 목록 (그룹별 keeper 제외).

    keeper = 그룹에서 가장 작은 question_id.
    한 번의 SELECT 로 모든 dup 을 추출 (그룹별 N+1 쿼리 회피).
    """
    p = placeholder
    cur = conn.execute(
        f"SELECT q.question_id FROM questions q "
        f"JOIN ( "
        f"  SELECT file_source, question_number, MIN(question_id) AS keeper "
        f"  FROM questions "
        f"  GROUP BY file_source, question_number "
        f"  HAVING COUNT(*) > 1 "
        f") d ON q.file_source = d.file_source "
        f"   AND q.question_number = d.question_number "
        f"   AND q.question_id != d.keeper"
    )
    return [r[0] for r in cur.fetchall()]


def _delete_in_batches(conn, table: str, idcol: str, ids: list[int],
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
    dup_ids = _find_duplicate_ids(conn, placeholder)
    total_groups = conn.execute(
        "SELECT COUNT(*) FROM ("
        " SELECT 1 FROM questions GROUP BY file_source, question_number "
        " HAVING COUNT(*) > 1)"
    ).fetchone()[0]
    print(f"중복 그룹: {total_groups}건")
    print(f"삭제 대상 행: {len(dup_ids)}건")
    if not dup_ids:
        return
    if dry_run:
        print(f"\n[DRY-RUN] 자식 테이블(solutions/images/flagged_problems) "
              f"도 동일 ID 로 cascade 삭제 예정.")
        return

    n_sol = _delete_in_batches(conn, "solutions", "question_id",
                               dup_ids, placeholder)
    n_img = _delete_in_batches(conn, "images", "question_id",
                               dup_ids, placeholder)
    try:
        n_flag = _delete_in_batches(conn, "flagged_problems",
                                    "question_id", dup_ids, placeholder)
    except Exception:
        n_flag = 0
    n_q = _delete_in_batches(conn, "questions", "question_id",
                             dup_ids, placeholder)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    print(f"삭제: questions={n_q}, solutions={n_sol}, images={n_img}, "
          f"flagged={n_flag}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cloud:
        import psycopg2
        dsn = os.environ["SUPABASE_DB_URL"]
        conn = psycopg2.connect(dsn)
        conn.autocommit = False
        with conn:
            cur = conn.cursor()

            def _exec(sql, params=()):
                cur.execute(sql, params)
                return cur

            class _Wrapper:
                def execute(self_, sql, params=()):
                    cur.execute(sql, params)
                    return cur

                def commit(self_):
                    conn.commit()

            run(_Wrapper(), "%s", args.dry_run)
        conn.close()
    else:
        db = ROOT / "db" / "mathdb.sqlite"
        conn = sqlite3.connect(db)
        run(conn, "?", args.dry_run)
        conn.close()


if __name__ == "__main__":
    main()
