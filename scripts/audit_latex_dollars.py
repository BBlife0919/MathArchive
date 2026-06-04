#!/usr/bin/env python3
"""MathArchive cloud DB — LaTeX/$ 정규화 감사 (READ ONLY).

questions.question_text + solutions.solution_text 전수 스캔하여 수식 사고 분류:
  CAT1 unbalanced  : 이스케이프 안 된 `$` 개수가 홀수 (닫는/여는 달러 누락)
  CAT2 raw_latex   : `$...$` 밖에 LaTeX 토큰(\\sin, \\,, \\frac, ^{ 등) 노출
  CAT3 hangul_math : `$...$` 안에 한글 포함 (달러 위치 오류 의심)

집계 + 샘플만 출력. 수정/쓰기 없음.
"""
from __future__ import annotations
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

# 이스케이프(\$) 아닌 달러
_DOLLAR = re.compile(r"(?<!\\)\$")
# 균형 잡힌 인라인 수식 (줄바꿈 넘어서도 매칭 → 진짜 '달러 밖' 토큰만 남김)
_MATH_SPAN = re.compile(r"(?<!\\)\$.*?(?<!\\)\$", re.DOTALL)
# 한줄 수식 (한글 포함 여부 판정용 — 줄 안에서만)
_MATH_SPAN_LINE = re.compile(r"(?<!\\)\$[^$\n]*?(?<!\\)\$")
# LaTeX 토큰 (달러 밖 노출 탐지용)
_LATEX_TOKEN = re.compile(r"\\[a-zA-Z]+|\\,|\\;|\\!|\\\\|\^\{|_\{|\\frac|\\sqrt|\\dfrac")
_HANGUL = re.compile(r"[가-힣]")


def strip_math(text: str) -> str:
    """균형 수식 span 제거 → 나머지(달러 밖) 반환."""
    return _MATH_SPAN.sub(" ", text)


def classify(text: str) -> set[str]:
    cats = set()
    if not text:
        return cats
    if len(_DOLLAR.findall(text)) % 2 == 1:
        cats.add("CAT1_unbalanced")
    outside = strip_math(text)
    if _LATEX_TOKEN.search(outside):
        cats.add("CAT2_raw_latex")
    for m in _MATH_SPAN_LINE.finditer(text):
        inner = m.group(0)[1:-1]
        # \text{...} 안의 한글은 정상 → 제거 후 판정
        inner_wo_text = re.sub(r"\\(?:text|mbox|mathrm)\s*\{[^}]*\}", "", inner)
        if _HANGUL.search(inner_wo_text):
            cats.add("CAT3_hangul_math")
            break
    return cats


def main():
    import psycopg2
    from psycopg2.extras import DictCursor
    dsn = os.environ["SUPABASE_DB_URL"]
    conn = psycopg2.connect(dsn, cursor_factory=DictCursor)
    cur = conn.cursor()

    summary = Counter()
    samples: dict[str, list] = {}
    affected_q = set()
    affected_s = set()
    totals = Counter()

    for table, idcol, txtcol, akset in [
        ("questions", "question_id", "question_text", affected_q),
        ("solutions", "solution_id", "solution_text", affected_s),
    ]:
        cur.execute(f"SELECT {idcol} AS id, {txtcol} AS txt FROM {table}")
        n = 0
        for row in cur:
            n += 1
            cats = classify(row["txt"] or "")
            if cats:
                akset.add(row["id"])
                for c in cats:
                    summary[f"{table}:{c}"] += 1
                    key = f"{table}:{c}"
                    if len(samples.setdefault(key, [])) < 4:
                        snippet = (row["txt"] or "")[:140].replace("\n", "⏎")
                        samples[key].append((row["id"], snippet))
        totals[table] = n

    cur.close()
    conn.close()

    print("=== 전체 행 수 ===")
    for t, c in totals.items():
        print(f"  {t}: {c}")
    print("\n=== 사고 분류 집계 (행 단위, 중복 가능) ===")
    for k in sorted(summary):
        print(f"  {k:32s} {summary[k]}")
    print(f"\n영향받는 questions: {len(affected_q)} / solutions: {len(affected_s)}")
    print("\n=== 샘플 ===")
    for k in sorted(samples):
        print(f"\n[{k}]")
        for _id, snip in samples[k]:
            print(f"  #{_id}: {snip}")


if __name__ == "__main__":
    main()
