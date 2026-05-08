#!/usr/bin/env python3
"""수식 ($...$) 안의 백슬래시 없는 영문 단어 빈도 추출.

목적: SYMBOL_MAP / GREEK_MAP 에 누락된 HWP 토큰을 자동 발굴.
   - `$x in X$` → `in` 발견 → \in 매핑 누락 의심
   - `$g circ f$` → `circ` 발견
   - `$AB perp CD$` → `perp` 발견 (점 라벨 AB/CD 와 구별 필요)

전략:
1. 모든 question_text + solution_text 의 `$...$` 안에서 영문 단어 추출
2. 단어 앞이 `\` 면 제외 (이미 LaTeX 명령)
3. 알려진 화이트리스트(Greek/SYMBOL_MAP) 의 키 제외
4. 빈도순 정렬 → 사용자가 새 매핑 결정

사용법:
    python3 scripts/detect_bare_math_words.py            # 상위 50개
    python3 scripts/detect_bare_math_words.py --top 200
    python3 scripts/detect_bare_math_words.py --min-len 3
"""
from __future__ import annotations

import argparse
import re
import sqlite3
import sys
from collections import Counter
from pathlib import Path

# parse_hwpx 의 매핑을 import 해서 화이트리스트 만든다
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_hwpx import GREEK_MAP, SYMBOL_MAP

# 알려진 LaTeX 명령 (백슬래시 빠진 채로 등장하면 SYMBOL_MAP 에 매핑돼야 함)
KNOWN_TOKENS = (
    set(GREEK_MAP.keys())
    | set(SYMBOL_MAP.keys())
    | {
        # 위쪽 매핑 외에 흔한 LaTeX 명령
        "frac", "dfrac", "tfrac", "cfrac", "sqrt", "root",
        "left", "right", "begin", "end",
        "overline", "underline", "overrightarrow", "overleftarrow",
        "mathrm", "mathbf", "mathit", "mathbb", "mathcal",
        "hat", "vec", "tilde", "bar", "dot", "ddot",
        "boxed", "phantom", "text",
        "sin", "cos", "tan", "cot", "sec", "csc",
        "sinh", "cosh", "tanh", "log", "ln", "lim", "exp",
        "max", "min", "sup", "inf", "arg", "det", "dim", "ker",
        "Pr", "deg", "gcd",
        "leqq", "geqq", "lll", "ggg",
        "subseteq", "supseteq", "subsetneq", "supsetneq",
        "leftrightarrow", "Leftarrow", "Rightarrow", "Leftrightarrow",
        "longleftarrow", "longrightarrow", "longleftrightarrow",
        "mapsto", "rightleftharpoons",
        "ne", "le", "ge",
        "rfloor", "lfloor", "rceil", "lceil",
        "land", "lor", "lnot", "neg",
        "implies", "iff",
        # 환경명 (\begin{...}\end{...} 안에 등장)
        "cases", "matrix", "pmatrix", "bmatrix", "vmatrix", "Bmatrix",
        "smallmatrix", "array", "align", "aligned", "gather", "gathered",
        "equation", "eqnarray", "split",
        # 흔한 KaTeX/LaTeX 문법
        "not", "color", "textbf", "textit", "rm",
    }
)

# 단순 변수 / 좌표 라벨 (수학에서 흔한 짧은 영문) — 보고에서 제외
COMMON_VARS = {
    # 단일 알파벳은 별도 처리 (길이 1 자동 제외)
    "AB", "BC", "CD", "DE", "EF", "AC", "BD", "AE", "AD", "BE",
    "PQ", "PR", "PS", "QR", "OQ", "OP", "OA", "OB", "OC", "OH",
    "ABC", "ABD", "BCD", "ACD", "ABCD", "PQR", "ABCDE", "OAB",
    "ABCDEF", "BCDE",
    "PRS",
    "AH", "AI", "AM", "AN", "AP", "BC", "BD", "BH", "CD", "CH",
    "DM", "EH", "FG",
}


def extract_bare_words(text: str, min_len: int) -> Counter:
    """`$...$` 안의 백슬래시 없는 영문 단어 빈도.

    `\\command` 전체를 먼저 소비한 뒤 남는 영문 런만 bare word 로 카운트.
    이렇게 안 하면 `\\left` 의 `eft`, `\\mathrm` 의 `athrm` 같은 잔여가
    잡혀 결과가 오염됨.
    """
    if not text or "$" not in text:
        return Counter()
    cnt = Counter()
    for m in re.finditer(r"\$([^$]+)\$", text):
        span = m.group(1)
        # 토큰화: \command 또는 bare word
        for wm in re.finditer(r"\\[A-Za-z]+|([A-Za-z]+)", span):
            w = wm.group(1)
            if w and len(w) >= min_len:
                cnt[w] += 1
    return cnt


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--top", type=int, default=50)
    ap.add_argument("--min-len", type=int, default=2,
                    help="최소 단어 길이 (default 2 — 단일 알파벳은 변수로 보고 제외)")
    ap.add_argument("--include-known", action="store_true",
                    help="이미 알려진 토큰도 포함 (디버깅용)")
    ap.add_argument("--show-examples", action="store_true",
                    help="각 토큰의 등장 예시 1건씩 표시")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    total = Counter()
    qrows = cur.execute("SELECT question_text FROM questions").fetchall()
    srows = cur.execute("SELECT solution_text FROM solutions").fetchall()
    print(f"questions {len(qrows)}, solutions {len(srows)} 스캔 중...",
          file=sys.stderr)
    for (txt,) in qrows:
        total.update(extract_bare_words(txt or "", args.min_len))
    for (txt,) in srows:
        total.update(extract_bare_words(txt or "", args.min_len))

    # 화이트리스트 제거
    if not args.include_known:
        for w in list(total.keys()):
            if w in KNOWN_TOKENS or w.lower() in KNOWN_TOKENS \
                    or w.upper() in KNOWN_TOKENS:
                del total[w]
            elif w in COMMON_VARS:
                del total[w]

    print(f"\n=== 백슬래시 없는 영문 단어 (수식 안) 빈도 상위 {args.top} ===")
    print(f"{'순위':>3}  {'빈도':>6}  단어")
    print("-" * 40)
    for i, (w, n) in enumerate(total.most_common(args.top), 1):
        print(f"{i:3d}  {n:6d}  {w}")

    if args.show_examples:
        print("\n=== 예시 (각 토큰 1건) ===")
        for w, _ in total.most_common(args.top):
            row = cur.execute(
                "SELECT question_text FROM questions "
                f"WHERE question_text LIKE '%${'%' + w + '%'}$%' LIMIT 1"
            ).fetchone()
            if row:
                t = row[0]
                m = re.search(rf"\$[^$]*{re.escape(w)}[^$]*\$", t)
                if m:
                    print(f"  {w}: ...{m.group(0)}...")

    conn.close()


if __name__ == "__main__":
    main()
