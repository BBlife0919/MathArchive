#!/usr/bin/env python3
"""HWP 의 sup·int·from·to 토큰 raw 노출 → LaTeX 변환.

패턴 (안전, 영어 단어 우연 매칭 없음):
- `sup <숫자>` → `^{<숫자>}`   예: `x sup 3` → `x^{3}`
- `int from A to B` → `\\int_{A}^{B}`   예: `int from 0 to x` → `\\int_{0}^{x}`

사용:
    python3 scripts/fix_sup_intfromto.py --dry-run
    python3 scripts/fix_sup_intfromto.py
    python3 scripts/fix_sup_intfromto.py --cloud
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

SUP = re.compile(r'\bsup\s+(\d+)\b')
INT_FROM_TO = re.compile(r'\bint\s+from\s+(\S+)\s+to\s+(\S+)')


def fix(text):
    if not text:
        return text
    new = INT_FROM_TO.sub(r'\\int_{\1}^{\2}', text)
    new = SUP.sub(r'^{\1}', new)
    return new


def run_sqlite(dry):
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    for table, col, pk in [
        ("solutions", "solution_text", "solution_id"),
        ("questions", "question_text", "question_id"),
    ]:
        cur.execute(f"SELECT {pk}, {col} FROM {table}")
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
        print(f"  {table}.{col}: 수정 {updated}")
    if not dry:
        conn.commit()
    conn.close()


def run_cloud(dry):
    import psycopg2
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()
    for table, col, pk in [
        ("solutions", "solution_text", "solution_id"),
        ("questions", "question_text", "question_id"),
    ]:
        cur.execute(
            f"SELECT {pk}, {col} FROM {table} "
            f"WHERE {col} ~ E'\\\\msup\\\\s+\\\\d+|\\\\mint\\\\s+from\\\\s+\\\\S+\\\\s+to\\\\s+\\\\S+'"
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
        print(f"  {table}.{col}: 수정 {updated}")
    if not dry:
        conn.commit()
    conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    target = "CLOUD Postgres" if args.cloud else f"SQLite {SQLITE_DB}"
    print(f"[fix_sup_intfromto] target={target} dry-run={args.dry_run}")
    if args.cloud:
        run_cloud(args.dry_run)
    else:
        run_sqlite(args.dry_run)


if __name__ == "__main__":
    main()
