#!/usr/bin/env python3
"""solutions / questions 텍스트의 줄 시작 4-space·tab 제거.

매쓰아카이브 markdown 렌더가 줄 시작 4-space/tab 을 코드블록으로
오인 → 회색 박스 출력 (scan_db_issues 의 leading_indent_codeblock).

처리:
- 본문/해설 텍스트의 각 줄에서 leading 4-space 이상 또는 tab 1개+ 만 제거
- 1~3 space (의도적 들여쓰기) 는 보존
- 라인 모두가 공백인 경우 그대로

사용:
    python3 scripts/fix_leading_indent.py --dry-run
    python3 scripts/fix_leading_indent.py
    python3 scripts/fix_leading_indent.py --cloud
"""
from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = ROOT / "db" / "mathdb.sqlite"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

LEAD = re.compile(r'^(\t+| {4,})', re.MULTILINE)


def fix(text):
    if not text:
        return text
    return LEAD.sub("", text)


def run_sqlite(dry):
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()

    stats = {}
    for table, col, pk in [
        ("solutions", "solution_text", "solution_id"),
        ("questions", "question_text", "question_id"),
    ]:
        cur.execute(
            f"SELECT {pk}, {col} FROM {table} "
            f"WHERE {col} LIKE '%' || char(10) || char(9) || '%' "
            f"   OR {col} LIKE '%' || char(10) || '    %' "
            f"   OR {col} LIKE char(9) || '%' "
            f"   OR {col} LIKE '    %'"
        )
        rows = cur.fetchall()
        updated = 0
        for pkv, txt in rows:
            new = fix(txt)
            if new != txt:
                if not dry:
                    cur.execute(
                        f"UPDATE {table} SET {col} = ? WHERE {pk} = ?",
                        (new, pkv),
                    )
                updated += 1
        stats[table] = (len(rows), updated)
        print(f"  {table}.{col}: 후보 {len(rows)}, 수정 {updated}")
    if not dry:
        conn.commit()
    conn.close()
    return stats


def run_cloud(dry):
    import psycopg2
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()
    stats = {}
    for table, col, pk in [
        ("solutions", "solution_text", "solution_id"),
        ("questions", "question_text", "question_id"),
    ]:
        cur.execute(
            f"SELECT {pk}, {col} FROM {table} "
            f"WHERE {col} ~ E'(^|\\n)(\\t|    )'"
        )
        rows = cur.fetchall()
        updated = 0
        for pkv, txt in rows:
            new = fix(txt)
            if new != txt:
                if not dry:
                    cur.execute(
                        f"UPDATE {table} SET {col} = %s WHERE {pk} = %s",
                        (new, pkv),
                    )
                updated += 1
        stats[table] = (len(rows), updated)
        print(f"  {table}.{col}: 후보 {len(rows)}, 수정 {updated}")
    if not dry:
        conn.commit()
    conn.close()
    return stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    target = "CLOUD Postgres" if args.cloud else f"SQLite {SQLITE_DB}"
    print(f"[fix_leading_indent] target={target} dry-run={args.dry_run}")
    if args.cloud:
        run_cloud(args.dry_run)
    else:
        run_sqlite(args.dry_run)


if __name__ == "__main__":
    main()
