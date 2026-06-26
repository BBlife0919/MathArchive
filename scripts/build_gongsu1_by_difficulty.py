#!/usr/bin/env python3
"""KERNEL POINT — 광명 고1 공수1 1학기 기말 (난이도별 분책).

조건:
- region='경기광명시', grade=1
- chapter ∈ 8개 (curriculum 순서):
  고차방정식 → 연립방정식 → 부등식 → 경우의 수 → 순열 → 조합
  → 행렬의 뜻 → 행렬의 연산
- 정렬: 단원(curriculum) 오름차순 → 난이도(하<중<상<킬) → qid
- 레이아웃: 2단, 단당 1문제 (모든 문항 full)

usage: python3 build_gongsu1_by_difficulty.py [하|중]
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
    "부등식",
    "경우의 수",
    "순열",
    "조합",
    "행렬의 뜻",
    "행렬의 연산",
]
DIFF_ORDER = {"하": 0, "중": 1, "상": 2, "킬": 3}


def fetch_rows():
    import psycopg2
    from psycopg2.extras import DictCursor
    dsn = os.environ["SUPABASE_DB_URL"]
    conn = psycopg2.connect(dsn, cursor_factory=DictCursor)
    cur = conn.cursor()
    marks = ",".join(["%s"] * len(CHAPTERS))
    cur.execute(
        f"SELECT q.question_id, q.file_source, q.school, q.region, q.grade, "
        f"       q.year, q.semester, q.exam_type, q.subject, "
        f"       q.question_number, q.question_text, q.choices, "
        f"       q.answer, q.answer_type, q.points, q.chapter, "
        f"       q.difficulty, q.has_image, q.is_subjective, "
        f"       s.solution_text "
        f"FROM questions q "
        f"LEFT JOIN solutions s ON q.question_id = s.question_id "
        f"WHERE q.region = %s AND q.grade = %s "
        f"  AND q.chapter IN ({marks})",
        ("경기광명시", 1, *CHAPTERS),
    )
    rows = [dict(r) for r in cur.fetchall()]

    qids = [r["question_id"] for r in rows]
    if qids:
        imarks = ",".join(["%s"] * len(qids))
        cur.execute(
            f"SELECT question_id, image_ref, image_path, image_type "
            f"FROM images WHERE question_id IN ({imarks})",
            tuple(qids),
        )
        img_by_q: dict = {}
        sol_by_q: dict = {}
        for ir in cur.fetchall():
            target = sol_by_q if (ir["image_type"] == "solution") else img_by_q
            target.setdefault(ir["question_id"], {})[ir["image_ref"]] = ir["image_path"]
        for r in rows:
            r["images"] = img_by_q.get(r["question_id"], {})
            if r["question_id"] in sol_by_q:
                r["images_sol"] = sol_by_q[r["question_id"]]
        import json as _json
        comp_path = ROOT / "output" / "composite_image_qids.json"
        if comp_path.exists():
            comp = set(_json.loads(comp_path.read_text()))
            for r in rows:
                if r["question_id"] in comp:
                    r["img_check"] = True

    cur.close(); conn.close()
    return rows


def main():
    diff = sys.argv[1] if len(sys.argv) > 1 else "하"
    assert diff in ("하", "중"), f"난이도는 하/중 중 하나 — {diff!r}"

    print(f"[1/4] cloud DB 조회... (난이도: {diff})")
    rows = fetch_rows()
    print(f"  매칭 문항(전체): {len(rows)}")
    rows = [r for r in rows if r.get("difficulty") == diff]
    print(f"  난이도 '{diff}' 만: {len(rows)}")

    chap_idx = {c: i for i, c in enumerate(CHAPTERS)}
    rows.sort(key=lambda r: (
        chap_idx.get(r["chapter"], 999),
        DIFF_ORDER.get(r["difficulty"], 99),
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
        print(f"  {c:25s} {by_chap.get(c, 0)}")

    overrides = {r["question_id"]: "full" for r in rows}
    logo_path = APP / "assets" / "eum_logo.png"

    print("[3/4] PDF 생성...")
    from pdf_engine import generate_book_pdf
    pdf_bytes = generate_book_pdf(
        rows,
        title="KERNEL POINT",
        subtitle=f"공수1 1학기 기말 · {diff}",
        include_source=True,
        overrides=overrides,
        logo_path=str(logo_path) if logo_path.exists() else None,
        kicker_mark=None,
        kicker_text=None,
        divider_meta_top=f"공수1 1학기 기말 · {diff} · KERNEL POINT",
        divider_footer_title=f"공수1 1학기 기말 · {diff} · KERNEL POINT",
        divider_footer_sub="이영우 T",
        cover_main_title="KERNEL POINT",
        cover_tagline=f"공수1 1학기 기말 · 난이도 {diff}",
        cover_big_word=diff,
        cover_kicker="KERNEL POINT · 2026",
        cover_footer_main=f"Gongsu 1 Final · {diff}",
        cover_footer_sub=f"난이도 {diff} 핵심 문제집",
        page_running_left=f"KERNEL POINT · {diff}",
    )

    vec_path = ROOT / "output" / f"gongsu1_diff_{diff}_vector.pdf"
    vec_path.parent.mkdir(exist_ok=True)
    vec_path.write_bytes(pdf_bytes)

    # vector PDF 그대로 저장 — 이미지화 단계 제거 (수식 가독성 통일).
    book_dir = Path.home() / "클로드교재"
    book_dir.mkdir(exist_ok=True)
    out_path = book_dir / f"공수1 1학기 기말 KERNEL POINT {diff}.pdf"
    out_path.write_bytes(pdf_bytes)
    import subprocess as _sp
    _sp.run(["xattr", "-c", str(out_path)], check=False)
    print(f"[4/4] {out_path} ({out_path.stat().st_size/1024/1024:.0f}MB)")


if __name__ == "__main__":
    main()
