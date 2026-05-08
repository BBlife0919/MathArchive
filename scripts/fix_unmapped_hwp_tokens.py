#!/usr/bin/env python3
"""DB 클린업 — 파서가 변환 못 한 HWP 비교연산자/화살표 토큰을 LaTeX 으로 치환.

근본 원인: SYMBOL_MAP 이 lowercase `le`/`ge`/`ne` 와 `LEQ`/`GEQ`/`NEQ`
만 다뤘고 `LE`/`GE`/`NE` (대문자 단축형) 와 `rarrow`/`RARROW`/`larrow` 같은
화살표 약어가 누락. 파서는 이미 수정됨. 이 스크립트는 DB 에 이미 들어있는
잔여 토큰만 정리한다.

사용법:
    python3 scripts/fix_unmapped_hwp_tokens.py            # 미리보기
    python3 scripts/fix_unmapped_hwp_tokens.py --apply
"""
from __future__ import annotations

import argparse
import re
import sqlite3

# (pattern, replacement). RULES_BEFORE 는 부착 분리(앞쪽 영숫자 → 공백 삽입)
# RULES_AFTER 는 토큰 치환. 두 단계로 나눠서 안전하게 정리.
#
# LE 보호: LEFT(`FT` 후행) / LEQ(`Q` 후행)
# GE 보호: GEQ(`Q` 후행)
# NE 보호: NEQ(`Q` 후행) / NEG(`G` 후행)

# 1) 토큰 치환: 영숫자 직후가 LE/GE/NE 인 케이스부터 처리 (양쪽 분리 필요)
#    - 양쪽 모두 영숫자 부착: `0LEx` → `0\leq x`
#    - 한쪽만 부착: `,LE\,` (이미 분리), `0LE\,` (앞만 부착) 등 다양
ATTACH_LEFT = [
    # 영숫자 + LE/GE/NE (부착) → 영숫자 + 공백 + LE/GE/NE
    (re.compile(r"(?<=[A-Za-z0-9])LE(?!FT|Q)"), " LE"),
    (re.compile(r"(?<=[A-Za-z0-9])GE(?!Q)"), " GE"),
    (re.compile(r"(?<=[A-Za-z0-9])NE(?!Q|G)"), " NE"),
    # 긴 화살표(lrarrow / LRARROW) 먼저 분리. 그 다음 짧은 화살표는 앞 글자가
    # L/l 일 때 분리하지 않는다(이미 lrarrow/LRARROW 의 일부일 수 있음).
    (re.compile(r"(?<=[A-Za-z0-9])(lrarrow|LRARROW)"), r" \1"),
    (re.compile(r"(?<=[A-Za-z0-9])(?<![Ll])(rarrow|RARROW)"), r" \1"),
    (re.compile(r"(?<=[A-Za-z0-9])(larrow|LARROW)"), r" \1"),
]

REPLACE = [
    # LE 다음 영문자 (예: `LE x`, `LEx`): \leq 뒤 공백
    (re.compile(r"(?<![A-Za-z\\])LE(?!FT|Q)(?=[A-Za-z])"), r"\\leq "),
    (re.compile(r"(?<![A-Za-z\\])LE(?!FT|Q)(?![A-Za-z])"), r"\\leq"),
    (re.compile(r"(?<![A-Za-z\\])GE(?!Q)(?=[A-Za-z])"), r"\\geq "),
    (re.compile(r"(?<![A-Za-z\\])GE(?!Q)(?![A-Za-z])"), r"\\geq"),
    (re.compile(r"(?<![A-Za-z\\])NE(?!Q|G)(?=[A-Za-z])"), r"\\neq "),
    (re.compile(r"(?<![A-Za-z\\])NE(?!Q|G)(?![A-Za-z])"), r"\\neq"),
    # 화살표
    (re.compile(r"(?<![A-Za-z\\])rarrow(?=[A-Za-z])"), r"\\rightarrow "),
    (re.compile(r"(?<![A-Za-z\\])rarrow(?![A-Za-z])"), r"\\rightarrow"),
    (re.compile(r"(?<![A-Za-z\\])RARROW(?=[A-Za-z])"), r"\\rightarrow "),
    (re.compile(r"(?<![A-Za-z\\])RARROW(?![A-Za-z])"), r"\\rightarrow"),
    (re.compile(r"(?<![A-Za-z\\])larrow(?=[A-Za-z])"), r"\\leftarrow "),
    (re.compile(r"(?<![A-Za-z\\])larrow(?![A-Za-z])"), r"\\leftarrow"),
    (re.compile(r"(?<![A-Za-z\\])LARROW(?=[A-Za-z])"), r"\\leftarrow "),
    (re.compile(r"(?<![A-Za-z\\])LARROW(?![A-Za-z])"), r"\\leftarrow"),
    (re.compile(r"(?<![A-Za-z\\])lrarrow(?=[A-Za-z])"), r"\\leftrightarrow "),
    (re.compile(r"(?<![A-Za-z\\])lrarrow(?![A-Za-z])"), r"\\leftrightarrow"),
    (re.compile(r"(?<![A-Za-z\\])LRARROW(?=[A-Za-z])"), r"\\leftrightarrow "),
    (re.compile(r"(?<![A-Za-z\\])LRARROW(?![A-Za-z])"), r"\\leftrightarrow"),
    # 집합 / 원소 / 합성함수 — 수식 컨텍스트 (전역 안전)
    (re.compile(r"(?<![A-Za-z\\])subset(?![A-Za-z])"), r"\\subset"),
    (re.compile(r"(?<![A-Za-z\\])SUBSET(?![A-Za-z])"), r"\\subset"),
    (re.compile(r"(?<![A-Za-z\\])supset(?![A-Za-z])"), r"\\supset"),
    (re.compile(r"(?<![A-Za-z\\])SUPSET(?![A-Za-z])"), r"\\supset"),
    (re.compile(r"(?<![A-Za-z\\])notin(?![A-Za-z])"), r"\\notin"),
    (re.compile(r"(?<![A-Za-z\\])NOTIN(?![A-Za-z])"), r"\\notin"),
    (re.compile(r"(?<![A-Za-z\\])circ(?![A-Za-z])"), r"\\circ"),
    (re.compile(r"(?<![A-Za-z\\])CIRC(?![A-Za-z])"), r"\\circ"),
    (re.compile(r"(?<![A-Za-z\\])cdots(?![A-Za-z])"), r"\\cdots"),
    (re.compile(r"(?<![A-Za-z\\])CDOTS(?![A-Za-z])"), r"\\cdots"),
    (re.compile(r"(?<![A-Za-z\\])vdots(?![A-Za-z])"), r"\\vdots"),
    (re.compile(r"(?<![A-Za-z\\])ddots(?![A-Za-z])"), r"\\ddots"),
]

# 영어 단어와 충돌 위험 있는 토큰 — 수식 ($...$) 안에서만 치환
MATH_ONLY_REPLACE = [
    (re.compile(r"(?<![A-Za-z\\])in(?![A-Za-z])"), r"\\in"),
    (re.compile(r"(?<![A-Za-z\\])IN(?![A-Za-z])"), r"\\in"),
    (re.compile(r"(?<![A-Za-z\\])sum(?![A-Za-z])"), r"\\sum"),
    (re.compile(r"(?<![A-Za-z\\])SUM(?![A-Za-z])"), r"\\sum"),
    (re.compile(r"(?<![A-Za-z\\])prod(?![A-Za-z])"), r"\\prod"),
    (re.compile(r"(?<![A-Za-z\\])PROD(?![A-Za-z])"), r"\\prod"),
    (re.compile(r"(?<![A-Za-z\\])int(?![A-Za-z])"), r"\\int"),
    (re.compile(r"(?<![A-Za-z\\])INT(?![A-Za-z])"), r"\\int"),
    (re.compile(r"(?<![A-Za-z\\])forall(?![A-Za-z])"), r"\\forall"),
    (re.compile(r"(?<![A-Za-z\\])FORALL(?![A-Za-z])"), r"\\forall"),
    (re.compile(r"(?<![A-Za-z\\])exists(?![A-Za-z])"), r"\\exists"),
    (re.compile(r"(?<![A-Za-z\\])EXISTS(?![A-Za-z])"), r"\\exists"),
    (re.compile(r"(?<![A-Za-z\\])partial(?![A-Za-z])"), r"\\partial"),
    (re.compile(r"(?<![A-Za-z\\])nabla(?![A-Za-z])"), r"\\nabla"),
    (re.compile(r"(?<![A-Za-z\\])approx(?![A-Za-z])"), r"\\approx"),
    (re.compile(r"(?<![A-Za-z\\])APPROX(?![A-Za-z])"), r"\\approx"),
    (re.compile(r"(?<![A-Za-z\\])equiv(?![A-Za-z])"), r"\\equiv"),
    (re.compile(r"(?<![A-Za-z\\])EQUIV(?![A-Za-z])"), r"\\equiv"),
    (re.compile(r"(?<![A-Za-z\\])sim(?![A-Za-z])"), r"\\sim"),
    (re.compile(r"(?<![A-Za-z\\])SIM(?![A-Za-z])"), r"\\sim"),
    (re.compile(r"(?<![A-Za-z\\])therefore(?![A-Za-z])"), r"\\therefore"),
    (re.compile(r"(?<![A-Za-z\\])THEREFORE(?![A-Za-z])"), r"\\therefore"),
    (re.compile(r"(?<![A-Za-z\\])because(?![A-Za-z])"), r"\\because"),
    (re.compile(r"(?<![A-Za-z\\])BECAUSE(?![A-Za-z])"), r"\\because"),
    (re.compile(r"(?<![A-Za-z\\])div(?![A-Za-z])"), r"\\div"),
    (re.compile(r"(?<![A-Za-z\\])DIV(?![A-Za-z])"), r"\\div"),
]


def _apply_in_math_spans(text: str) -> str:
    """수식 ($...$) 안에서만 MATH_ONLY_REPLACE 적용.

    영어 단어(`in`, `sum`, `int` 등)와 충돌을 피하기 위해 수식 영역 한정.
    """
    if "$" not in text:
        return text

    out = []
    i = 0
    in_math = False
    span_start = 0
    while i < len(text):
        if text[i] == "$":
            if in_math:
                # 수식 종료 — span 처리
                span = text[span_start:i]
                for pat, repl in MATH_ONLY_REPLACE:
                    span = pat.sub(repl, span)
                out.append(span)
                out.append("$")
                in_math = False
            else:
                # 수식 시작
                out.append("$")
                span_start = i + 1
                in_math = True
            i += 1
        else:
            if not in_math:
                out.append(text[i])
            i += 1
    if in_math:
        # unbalanced $ — 마지막 span 그대로 추가 (변환 안 함)
        out.append(text[span_start:])
    return "".join(out)


def fix_text(text: str) -> str:
    if not text:
        return text
    # 1) 영숫자 부착 분리
    for pat, repl in ATTACH_LEFT:
        prev = None
        cur = text
        # 연쇄 부착(`5LExLEy`) 대비 fix-point 반복
        while prev != cur:
            prev = cur
            cur = pat.sub(repl, cur)
        text = cur
    # 2) 전역 안전 토큰 → LaTeX
    for pat, repl in REPLACE:
        text = pat.sub(repl, text)
    # 3) 영어 단어와 충돌 위험 있는 토큰 — 수식 컨텍스트 한정
    text = _apply_in_math_spans(text)
    # 4) 다중 공백 정리
    text = re.sub(r"  +", " ", text)
    return text


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=3)
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    targets = [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]

    grand = 0
    for table, idcol, txtcol in targets:
        rows = cur.execute(
            f"SELECT {idcol}, {txtcol} FROM {table} "
            f"WHERE {txtcol} GLOB '*[LGN]E*' "
            f"   OR {txtcol} GLOB '*rarrow*' "
            f"   OR {txtcol} GLOB '*RARROW*' "
            f"   OR {txtcol} GLOB '*larrow*' "
            f"   OR {txtcol} GLOB '*LARROW*' "
            f"   OR {txtcol} GLOB '*subset*' "
            f"   OR {txtcol} GLOB '*supset*' "
            f"   OR {txtcol} GLOB '*SUBSET*' "
            f"   OR {txtcol} GLOB '*SUPSET*' "
            f"   OR {txtcol} GLOB '*notin*' "
            f"   OR {txtcol} GLOB '*NOTIN*' "
            f"   OR {txtcol} GLOB '*circ*' "
            f"   OR {txtcol} GLOB '*CIRC*' "
            f"   OR {txtcol} GLOB '*cdots*' "
            f"   OR {txtcol} GLOB '*CDOTS*' "
            f"   OR {txtcol} GLOB '*vdots*' "
            f"   OR {txtcol} GLOB '*ddots*' "
            f"   OR {txtcol} GLOB '*therefore*' "
            f"   OR {txtcol} GLOB '*THEREFORE*' "
            f"   OR {txtcol} GLOB '*because*' "
            f"   OR {txtcol} GLOB '*BECAUSE*' "
            f"   OR {txtcol} GLOB '*forall*' "
            f"   OR {txtcol} GLOB '*FORALL*' "
            f"   OR {txtcol} GLOB '*exists*' "
            f"   OR {txtcol} GLOB '*EXISTS*' "
            f"   OR {txtcol} GLOB '*partial*' "
            f"   OR {txtcol} GLOB '*nabla*' "
            f"   OR {txtcol} GLOB '*approx*' "
            f"   OR {txtcol} GLOB '*equiv*' "
            f"   OR {txtcol} GLOB '*sim*' "
            f"   OR {txtcol} GLOB '*div*' "
            f"   OR {txtcol} GLOB '* sum *' "
            f"   OR {txtcol} GLOB '* int *' "
            f"   OR {txtcol} GLOB '* in *'"
        ).fetchall()
        print(f"[{table}] 후보 {len(rows)}건")
        changed = 0
        shown = 0
        for rid, txt in rows:
            new = fix_text(txt or "")
            if new != txt:
                changed += 1
                if shown < args.show:
                    diff_lines = []
                    for o, n in zip(txt.split("\n"), new.split("\n")):
                        if o != n:
                            diff_lines.append(f"    -{o[:140]}")
                            diff_lines.append(f"    +{n[:140]}")
                    print(f"\n  --- {idcol}={rid} ---")
                    print("\n".join(diff_lines[:6]))
                    shown += 1
                if args.apply:
                    cur.execute(
                        f"UPDATE {table} SET {txtcol}=? WHERE {idcol}=?",
                        (new, rid),
                    )
        print(f"[{table}] 실제 변경: {changed}/{len(rows)}건")
        grand += changed

    if args.apply:
        conn.commit()
        print(f"\n✅ 적용 완료. 총 {grand}건 갱신.")
    else:
        print(f"\n[미리보기] 총 {grand}건 변경 예정.")
    conn.close()


if __name__ == "__main__":
    main()
