#!/usr/bin/env python3
"""MathArchive cloud DB — 수식 `$` 정규화 (보수적·안전 케이스만).

normalize_math():
  1) 잘못 이스케이프된 구분자  `\\$` → `$`  (홀수 패리티를 복구하는 경우에만)
  2) 줄마다 `$` 홀수면 끝에 `$` 보충 (닫는 달러 누락)

기본은 DRY-RUN: 바뀌는 행 수 + 전/후 diff 출력, 쓰기 없음.
`--apply` 시에만 UPDATE (프로덕션 쓰기 — 승인 후).
"""
from __future__ import annotations
import argparse
import sys
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

sys.path.insert(0, str(ROOT / "app"))
from pdf_engine import _normalize_math_text  # 정규화 단일 출처

_DOLLAR = re.compile(r"(?<!\\)\$")


def normalize_math(text: str) -> str:
    """안전한 `$` 정규화 (의미 보존) — pdf_engine 와 동일 로직 + `\\$` 복구."""
    if not text:
        return text
    new = text
    # `\$` 미스이스케이프 구분자 복구 (패리티 홀수일 때만)
    if len(_DOLLAR.findall(new)) % 2 == 1 and "\\$" in new:
        candidate = new.replace("\\$", "$", 1)
        if len(_DOLLAR.findall(candidate)) % 2 == 0:
            new = candidate
    return _normalize_math_text(new)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="프로덕션 UPDATE 실행 (기본: dry-run)")
    ap.add_argument("--show", type=int, default=12, help="전/후 diff 표시 개수")
    args = ap.parse_args()

    import psycopg2
    from psycopg2.extras import execute_batch
    conn = psycopg2.connect(
        os.environ["SUPABASE_DB_URL"],
        keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=5,
    )

    for table, idcol, txtcol in [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]:
        # 서버사이드(named) 커서로 스트리밍 읽기 → 변경분만 메모리 보관
        rcur = conn.cursor(name=f"read_{table}")
        rcur.itersize = 2000
        rcur.execute(f"SELECT {idcol}, {txtcol} FROM {table}")
        changes = []  # (id, new)
        shown = 0
        for _id, txt in rcur:
            t = txt or ""
            nt = normalize_math(t)
            if nt != t:
                changes.append((nt, _id))
                if shown < args.show:
                    print(f"  #{_id}\n    before: {t[:110]!r}\n    after : {nt[:110]!r}")
                    shown += 1
        rcur.close()
        print(f"===== {table}: 변경 대상 {len(changes)} 행 =====")

        if args.apply and changes:
            wcur = conn.cursor()
            B = 500
            for i in range(0, len(changes), B):
                execute_batch(
                    wcur,
                    f"UPDATE {table} SET {txtcol}=%s WHERE {idcol}=%s",
                    changes[i:i + B],
                )
                conn.commit()
                print(f"    [APPLIED] {min(i + B, len(changes))}/{len(changes)}")
            wcur.close()

    conn.close()


if __name__ == "__main__":
    main()
