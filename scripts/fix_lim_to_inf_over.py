#!/usr/bin/env python3
"""HWP 수식 4종 raw 토큰 → LaTeX 변환.

패턴 (수식 컨텍스트 한정, 영어 단어 우연 매칭 방지):
- `lim` (독립 토큰) → `\\lim`
- `INF`/`inf` → `\\infty`  (이미 fix_unmapped 매핑 있음 — 일괄 적용 차원)
- `n -> X`, `x -> 0+` 등 수식 안 화살표 → `\\to`
- `{X} / {Y}` → `\\dfrac{X}{Y}`   (HWP `over` 가 `/` 로 떨어진 케이스)

사용:
    python3 scripts/fix_lim_to_inf_over.py --dry-run
    python3 scripts/fix_lim_to_inf_over.py
    python3 scripts/fix_lim_to_inf_over.py --cloud
"""
from __future__ import annotations

import argparse
import os
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQLITE_DB = ROOT / "db" / "mathdb.sqlite"

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


# 수식 ($...$) 안만 처리 — 한글 문장에서 우연 매칭 방지
_MATH_SPAN = re.compile(r"\$([^$]+)\$")

# 패턴들
_LIM = re.compile(r"(?<![A-Za-z\\])lim(?![A-Za-z])")
_INF_UC = re.compile(r"(?<![A-Za-z\\])INF(?![A-Za-z])")
_INF_LC = re.compile(r"(?<![A-Za-z\\])inf(?![A-Za-z])")
# `-> X` (= 화살표). `->` 가 한국어/영어 본문에 거의 안 쓰임. 수식 한정이라 안전.
_ARROW = re.compile(r"(?<![<=-])->")
_SLASH_BETWEEN = re.compile(r"\s*/\s*\{")


def _convert_over_frac(s: str) -> str:
    """`{X} / {Y}` → `\\dfrac{X}{Y}`. X·Y 안 중첩 {} 허용 (stack 균형).

    HWP `over` 가 `/` 로 잘못 변환된 케이스 복원.
    """
    out = []
    i = 0
    n = len(s)
    while i < n:
        if s[i] != "{":
            out.append(s[i]); i += 1; continue
        # 균형 {X} 추출
        depth = 1
        j = i + 1
        while j < n and depth > 0:
            if s[j] == "{": depth += 1
            elif s[j] == "}": depth -= 1
            j += 1
        if depth != 0:
            out.append(s[i]); i += 1; continue
        # 다음 ` / {` 패턴인지
        m = _SLASH_BETWEEN.match(s, j)
        if not m:
            out.append(s[i:j]); i = j; continue
        k = m.end() - 1  # 분모 시작 `{` 위치
        depth = 1
        l = k + 1
        while l < n and depth > 0:
            if s[l] == "{": depth += 1
            elif s[l] == "}": depth -= 1
            l += 1
        if depth != 0:
            out.append(s[i:j]); i = j; continue
        num = s[i+1:j-1].strip()
        denom = s[k+1:l-1].strip()
        out.append(f"\\dfrac{{{num}}}{{{denom}}}")
        i = l
    return "".join(out)


def fix_math_content(inner: str) -> str:
    """수식 한 조각 ($...$ 내부) 변환."""
    inner = _LIM.sub(r"\\lim", inner)
    inner = _INF_UC.sub(r"\\infty", inner)
    inner = _INF_LC.sub(r"\\infty", inner)
    inner = _ARROW.sub(r"\\to", inner)
    inner = _convert_over_frac(inner)
    return inner


def fix(text: str) -> str:
    if not text:
        return text
    return _MATH_SPAN.sub(lambda m: "$" + fix_math_content(m.group(1)) + "$",
                         text)


def run_sqlite(dry: bool) -> None:
    conn = sqlite3.connect(SQLITE_DB)
    cur = conn.cursor()
    for table, col, pk in [
        ("solutions", "solution_text", "solution_id"),
        ("questions", "question_text", "question_id"),
    ]:
        cur.execute(f"SELECT {pk}, {col} FROM {table}")
        upd = 0
        for pkv, txt in cur.fetchall():
            if not txt:
                continue
            new = fix(txt)
            if new != txt:
                if not dry:
                    cur.execute(
                        f"UPDATE {table} SET {col}=? WHERE {pk}=?",
                        (new, pkv),
                    )
                upd += 1
        print(f"  {table}.{col}: 수정 {upd}")
    if not dry:
        conn.commit()
    conn.close()


def run_cloud(dry: bool) -> None:
    import psycopg2
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()
    for table, col, pk in [
        ("solutions", "solution_text", "solution_id"),
        ("questions", "question_text", "question_id"),
    ]:
        cur.execute(f"SELECT {pk}, {col} FROM {table}")
        upd = 0
        for pkv, txt in cur.fetchall():
            if not txt:
                continue
            new = fix(txt)
            if new != txt:
                if not dry:
                    cur.execute(
                        f"UPDATE {table} SET {col}=%s WHERE {pk}=%s",
                        (new, pkv),
                    )
                upd += 1
        print(f"  {table}.{col}: 수정 {upd}")
    if not dry:
        conn.commit()
    conn.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    target = "CLOUD Postgres" if args.cloud else f"SQLite {SQLITE_DB}"
    print(f"[fix_lim_to_inf_over] target={target} dry-run={args.dry_run}")
    if args.cloud:
        run_cloud(args.dry_run)
    else:
        run_sqlite(args.dry_run)


if __name__ == "__main__":
    main()
