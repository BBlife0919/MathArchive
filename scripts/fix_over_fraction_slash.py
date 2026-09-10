#!/usr/bin/env python3
"""MathArchive cloud DB — "over" 분수 변환 실패로 슬래시로 남은 것 복구.

hwp_eq_to_latex 의 과거 버그(중첩 중괄호 2단+ 분모를 {A} over {B} 로 못
잡아 최종 fallback에서 "A / B" 로 남던 것, 2026-09-10 발견·파서는 이미
수정·커밋 025a59ae) 로 이미 저장된 기존 DB 행을 복구한다.

`{균형잡힌중괄호} / {균형잡힌중괄호}` 형태(양쪽 다 슬래시 바로 옆에서
중괄호로 명확히 시작하는 경우)만 대상 — 괄호 경계가 텍스트에 그대로
남아있어 원래 분수 구조를 안전하게 복원 가능. 괄호 없는 단순 나눗셈
(단위 m/s, n!/2! 등)은 경계가 불분명해 건드리지 않는다(사용자 확인,
2026-09-10 — "괄호로 명확한 것만" 선택).

기본은 DRY-RUN: 바뀌는 행 수 + 전/후 diff 출력, 쓰기 없음.
`--apply` 시에만 UPDATE (프로덕션 쓰기 — 승인 후).
"""
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

_MATH_SPAN = re.compile(r"\$([^$\n]+)\$")


def _match_balanced_brace(s: str, start: int):
    depth = 0
    i = start
    while i < len(s):
        if s[i] == "{":
            depth += 1
        elif s[i] == "}":
            depth -= 1
            if depth == 0:
                return i + 1
        i += 1
    return None


_OWNED_BRACE_PRECEDING = re.compile(
    r"(?:[_^]|\\(?:overline|underline|overrightarrow|overleftarrow|"
    r"mathrm|mathbf|mathit|mathbb|text|mbox|sqrt|hat|vec|dot|ddot|"
    r"tilde|boxed|phantom|begin|end))$"
)


def _convert_slash_fractions(s: str) -> str:
    """`{A} / {B}` → `\\dfrac{A}{B}` (중첩 중괄호 깊이 제한 없음).

    단, `_{5}`/`^{2}`/`\\overline{AB}`처럼 첨자·단항명령의 필수 인자
    중괄호는 건드리지 않음 — 안 그러면 `{\\mathrm{P}}_{5} / {...}` 의
    `{5}`만 떨어져 나와 `{\\mathrm{P}}_\\dfrac{5}{...}` 로 깨짐
    (2026-09-10 DB 감사 중 발견, parse_hwpx.py 동일 버그와 같은 원인).
    """
    out = []
    i, n = 0, len(s)
    while i < n:
        if s[i] == "{":
            if _OWNED_BRACE_PRECEDING.search(s[:i]):
                out.append(s[i])
                i += 1
                continue
            end = _match_balanced_brace(s, i)
            if end is not None:
                m = re.match(r"[ \t]*/[ \t]*", s[end:])
                if m:
                    k = end + m.end()
                    if k < n and s[k] == "{":
                        end2 = _match_balanced_brace(s, k)
                        if end2 is not None:
                            num = _convert_slash_fractions(s[i + 1:end - 1])
                            den = _convert_slash_fractions(s[k + 1:end2 - 1])
                            out.append(r"\dfrac{" + num + "}{" + den + "}")
                            i = end2
                            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def fix_text(text: str) -> str:
    if not text or " / " not in text and "/ {" not in text and "} /" not in text:
        return text

    def _fix_span(m):
        return "$" + _convert_slash_fractions(m.group(1)) + "$"

    return _MATH_SPAN.sub(_fix_span, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="프로덕션 UPDATE 실행 (기본: dry-run)")
    ap.add_argument("--show", type=int, default=15, help="전/후 diff 표시 개수")
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
        rcur = conn.cursor(name=f"read_{table}_slashfix")
        rcur.itersize = 2000
        rcur.execute(f"SELECT {idcol}, {txtcol} FROM {table}")
        changes = []
        shown = 0
        for _id, txt in rcur:
            t = txt or ""
            nt = fix_text(t)
            if nt != t:
                changes.append((nt, _id))
                if shown < args.show:
                    print(f"  #{_id}\n    before: {t[:130]!r}\n    after : {nt[:130]!r}")
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
