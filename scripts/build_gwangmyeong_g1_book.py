#!/usr/bin/env python3
"""경기광명시 고1 공수1 일부 단원 + 난이도 분책.

조건:
- region='경기광명시', grade=1
- chapter ∈ {고차방정식, 연립방정식, 일차부등식, 이차부등식, 부등식,
            경우의 수, 순열, 조합, 행렬의 뜻, 행렬의 연산}
- difficulty: '하' 또는 '중' (CLI 인자)
- 정렬: 단원 (curriculum 순서) → question_id
- 레이아웃: 모든 문항 full (1단 1문제 모드 X — 사용자 디자인 변경으로 2단 유지)

사용:
    python3 scripts/build_gwangmyeong_g1_book.py 하
    python3 scripts/build_gwangmyeong_g1_book.py 중
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

CHAPTERS = [
    "고차방정식",
    "연립방정식",
    "일차부등식",
    "이차부등식",
    "부등식",
    "경우의 수",
    "순열",
    "조합",
    "행렬의 뜻",
    "행렬의 연산",
]


def fetch_rows(difficulty: str):
    import sqlite3
    conn = sqlite3.connect(ROOT / "db" / "mathdb.sqlite")
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    marks = ",".join(["?"] * len(CHAPTERS))
    cur.execute(
        f"SELECT q.question_id, q.file_source, q.school, q.region, q.grade, "
        f"       q.year, q.semester, q.exam_type, q.subject, "
        f"       q.question_number, q.question_text, q.choices, "
        f"       q.answer, q.answer_type, q.points, q.chapter, "
        f"       q.difficulty, q.has_image, q.is_subjective, "
        f"       s.solution_text "
        f"FROM questions q "
        f"LEFT JOIN solutions s ON q.question_id = s.question_id "
        f"WHERE q.region = ? AND q.grade = ? AND q.difficulty = ? "
        f"  AND q.chapter IN ({marks})",
        ("경기광명시", 1, difficulty, *CHAPTERS),
    )
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ("하", "중"):
        print("사용: python3 scripts/build_gwangmyeong_g1_book.py [하|중]",
              file=sys.stderr)
        sys.exit(1)
    difficulty = sys.argv[1]

    print(f"[1/4] DB 조회 (난이도 {difficulty})...")
    rows = fetch_rows(difficulty)
    print(f"  매칭 문항: {len(rows)}")
    if not rows:
        print("문항 없음.")
        sys.exit(1)

    chap_idx = {c: i for i, c in enumerate(CHAPTERS)}
    rows.sort(key=lambda r: (
        chap_idx.get(r["chapter"], 999),
        r["question_id"],
    ))

    import json
    for r in rows:
        ch = r.get("choices")
        if ch is not None and not isinstance(ch, str):
            r["choices"] = json.dumps(ch, ensure_ascii=False)

    print("[2/4] 분포:")
    from collections import Counter
    by_chap = Counter(r["chapter"] for r in rows)
    for c in CHAPTERS:
        if by_chap.get(c, 0):
            print(f"  {c:15s} {by_chap.get(c, 0)}")

    overrides = {r["question_id"]: "full" for r in rows}
    logo_path = APP / "assets" / "eum_logo.png"

    title = f"공통수학1 · 난이도 {difficulty}"
    subtitle = "경기광명시 고1 내신기출"

    print("[3/4] PDF 생성...")
    from pdf_engine import generate_book_pdf
    pdf_bytes = generate_book_pdf(
        rows,
        title=title,
        subtitle=subtitle,
        include_source=True,
        overrides=overrides,
        logo_path=str(logo_path) if logo_path.exists() else None,
        kicker_mark=None,
        kicker_text=None,
        divider_meta_top=f"공수1 · 난이도 {difficulty}",
        divider_footer_title=f"공통수학1 · 경기광명 고1 · 난이도 {difficulty}",
        divider_footer_sub="이음학원",
        cover_main_title="공통수학1",
        cover_tagline=f"경기광명 고1 · 난이도 {difficulty}",
        cover_big_word=difficulty.upper(),
        cover_kicker="MATH WORKBOOK · 2026",
        cover_footer_main=f"공수1 · 난이도 {difficulty}",
        cover_footer_sub="이음학원",
        page_running_left=f"공수1 · {difficulty}",
    )

    out_path = Path(
        f"/Users/youngwoolee/Downloads/공통수학1_경기광명_난이도{difficulty}.pdf"
    )
    out_path.write_bytes(pdf_bytes)
    print(f"[4/4] 저장: {out_path}  ({len(pdf_bytes)/1024:.0f} KB)")


if __name__ == "__main__":
    main()
