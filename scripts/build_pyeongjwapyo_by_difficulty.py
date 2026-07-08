#!/usr/bin/env python3
"""공통수학2 · 평면좌표(도형의 방정식) 단원 — 난이도별 분책 3종 (상/중/하).

조건:
- chapter ∈ 도형의방정식 대단원 (curriculum 순서):
  평면좌표 → 직선의 방정식 → 원의 방정식 → 도형의 이동
- 학교: 아래 SCHOOLS 만 (매쏠로지 로컬 DB, 학교명 변형 포함)
- 정렬: 단원(curriculum) 오름차순 → 난이도 → qid
- 레이아웃: KERNEL POINT 표준 (KEY POINT/MEMO)

usage: python3 build_pyeongjwapyo_by_difficulty.py [상|중|하|all]
"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))

DB_PATH = ROOT / "db" / "mathdb.sqlite"

CHAPTERS = [
    "평면좌표",
    "직선의 방정식",
    "원의 방정식",
    "도형의 이동",
]

# 사용자 지정 학교 (학교명 변형 포함).
# 수도여고 = 수도여고 + 수도여자고 (동일 학교 축약/정식명).
# 영신고만 포함 (영신여고/영신여자고는 별개 학교라 제외).
# 성남고만 포함 (성남외고 제외). 신림고는 DB에 데이터 없음.
SCHOOLS = [
    "성남고",
    "수도여고", "수도여자고",
    "숭의여고",
    "당곡고",
    "대영고",
    "영신고",
    "영등포고",
    "영등포여고",
    "여의도고",
    "여의도여고",
    "장훈고",
    "성보고",
    "구암고",
]

DIFF_ORDER = {"하": 0, "중": 1, "상": 2, "킬": 3}


def diagonal_cover_html(diff: str) -> str:
    """사선 편집형 표지 (평면좌표 좌표모티프 + Black Han Sans)."""
    graphic = '''
    <svg class="motif" viewBox="0 0 600 600" preserveAspectRatio="xMidYMid meet">
      <defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
        <path d="M40 0H0V40" fill="none" stroke="#cdd6e8" stroke-width="1"/>
      </pattern></defs>
      <rect x="0" y="0" width="600" height="600" fill="url(#grid)"/>
      <line x1="0" y1="360" x2="600" y2="360" stroke="#9fb0d4" stroke-width="2.5"/>
      <line x1="240" y1="0" x2="240" y2="600" stroke="#9fb0d4" stroke-width="2.5"/>
      <path d="M40 540 Q240 40 440 540" fill="none" stroke="#4560a8" stroke-width="4"/>
      <line x1="60" y1="120" x2="560" y2="560" stroke="#4560a8" stroke-width="4"/>
      <circle cx="360" cy="250" r="120" fill="none" stroke="#4560a8" stroke-width="4"/>
    </svg>'''
    return f'''<!doctype html><html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=Gothic+A1:wght@400;600;700;900&display=swap');
@page {{ size: A4; margin: 0; }}
* {{ margin:0; padding:0; box-sizing:border-box; }}
html,body {{ width:210mm; height:297mm; }}
.cover {{ position:relative; width:210mm; height:297mm; overflow:hidden;
  background:#f4f1ea; font-family:'Gothic A1', sans-serif; color:#1b1c22; }}
.motif {{ position:absolute; right:-95mm; bottom:-70mm; width:310mm; height:310mm;
  opacity:.18; transform:rotate(-8deg); }}
.hero {{ position:absolute; top:78mm; left:20mm;
  transform:rotate(-27deg); transform-origin:left center; }}
.kicker {{ font-family:'Gothic A1'; font-weight:700; font-size:12pt; letter-spacing:.28em;
  color:#3a4a86; margin-bottom:3mm; margin-left:2mm; }}
.title {{ font-family:'Black Han Sans', sans-serif; font-size:96pt; line-height:.92;
  color:#1b1c22; letter-spacing:-.01em; }}
.rule {{ width:66mm; height:2.4pt; background:#c8342b; margin:5mm 0 4mm 2mm; }}
.tagline {{ font-family:'Gothic A1'; font-weight:600; font-size:12.5pt; letter-spacing:.02em;
  color:#4a4d59; margin-left:2mm; max-width:120mm; }}
.bottom {{ position:absolute; right:22mm; bottom:40mm; text-align:right;
  transform:rotate(-27deg); transform-origin:right center; }}
.subject {{ font-family:'Gothic A1'; font-weight:900; font-size:30pt; color:#1b1c22; }}
.level {{ display:inline-block; margin-top:6mm;
  font-family:'Gothic A1'; font-weight:700; font-size:14pt; letter-spacing:.08em;
  color:#c8342b; border:2pt solid #c8342b; border-radius:999px; padding:2.8mm 9mm; }}
.byline {{ font-family:'Gothic A1'; font-weight:600; font-size:12pt; color:#3a3c46; margin-top:8mm; }}
.byline b {{ font-weight:900; color:#1b1c22; font-size:14pt; }}
.tick {{ position:absolute; width:15mm; height:15mm; border:2pt solid #26315e; }}
.t1 {{ top:12mm; left:12mm; border-right:none; border-bottom:none; }}
.t2 {{ bottom:12mm; right:12mm; border-left:none; border-top:none; }}
.foot {{ position:absolute; left:14mm; bottom:12mm; font-family:'Gothic A1';
  font-weight:700; font-size:8.5pt; letter-spacing:.24em; color:#3a4a86; }}
</style></head>
<body><div class="cover">
  {graphic}
  <span class="tick t1"></span><span class="tick t2"></span>
  <div class="hero">
    <div class="kicker">2학기 중간대비</div>
    <div class="title">평면좌표</div>
    <div class="rule"></div>
    <div class="tagline">공통수학2 · 도형의 방정식 내신기출</div>
  </div>
  <div class="bottom">
    <div class="subject">공통수학2</div><br>
    <span class="level">난이도 {diff}</span>
    <div class="byline">심재룡 <b>T</b></div>
  </div>
  <div class="foot">MATHOLOGY · 2026</div>
</div></body></html>'''


def fetch_rows() -> list[dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cmarks = ",".join(["?"] * len(CHAPTERS))
    smarks = ",".join(["?"] * len(SCHOOLS))
    cur.execute(
        f"SELECT q.question_id, q.file_source, q.school, q.grade, "
        f"       q.year, q.semester, q.exam_type, q.subject, "
        f"       q.question_number, q.question_text, q.choices, "
        f"       q.answer, q.answer_type, q.points, q.chapter, "
        f"       q.difficulty, q.has_image, q.is_subjective, "
        f"       s.solution_text "
        f"FROM questions q "
        f"LEFT JOIN solutions s ON q.question_id = s.question_id "
        f"WHERE q.chapter IN ({cmarks}) AND q.school IN ({smarks})",
        (*CHAPTERS, *SCHOOLS),
    )
    rows = [dict(r) for r in cur.fetchall()]

    qids = [r["question_id"] for r in rows]
    if qids:
        imarks = ",".join(["?"] * len(qids))
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

        comp_path = ROOT / "output" / "composite_image_qids.json"
        if comp_path.exists():
            comp = set(json.loads(comp_path.read_text()))
            for r in rows:
                if r["question_id"] in comp:
                    r["img_check"] = True

    cur.close(); conn.close()
    return rows


def build_one(diff: str, all_rows: list[dict]):
    rows = [r for r in all_rows if r.get("difficulty") == diff]

    chap_idx = {c: i for i, c in enumerate(CHAPTERS)}
    rows.sort(key=lambda r: (
        chap_idx.get(r["chapter"], 999),
        DIFF_ORDER.get(r["difficulty"], 99),
        r["question_id"],
    ))

    print(f"\n=== 난이도 '{diff}': {len(rows)}문항 ===")
    by_chap = Counter(r["chapter"] for r in rows)
    for c in CHAPTERS:
        print(f"  {c:12s} {by_chap.get(c, 0)}")
    if not rows:
        print(f"  ⚠ 난이도 '{diff}' 데이터 없음 — 스킵")
        return

    overrides = {r["question_id"]: "full" for r in rows}

    from pdf_engine import generate_book_pdf
    pdf_bytes = generate_book_pdf(
        rows,
        title="평면좌표",
        subtitle="공통수학2 평면좌표",
        include_source=True,
        overrides=overrides,
        logo_path=None,                       # 이음학원 로고 제거
        kicker_mark=None,
        kicker_text=None,
        divider_meta_top=f"공통수학2 평면좌표 · 난이도 {diff}",
        divider_footer_title=f"공통수학2 평면좌표 · 난이도 {diff}",
        divider_footer_sub="심재룡 T",
        cover_main_title="2학기 중간대비",     # 표지 제목
        cover_tagline="공통수학2 평면좌표",     # 그 밑
        cover_big_word=f"난이도 {diff}",        # 그 밑 (큰 워드)
        cover_kicker="MATHOLOGY · 2026",
        cover_footer_main="MATHOLOGY · 2026",
        cover_footer_sub=f"2학기 중간대비 · 공통수학2 평면좌표 · 난이도 {diff}",
        page_running_left=f"공통수학2 평면좌표 · {diff}",
    )

    # 기본 표지(1p)를 사선 커스텀 표지로 교체 (PyMuPDF)
    import fitz
    from pdf_engine import html_to_pdf_bytes
    cover_bytes = html_to_pdf_bytes(diagonal_cover_html(diff))
    book = fitz.open(stream=pdf_bytes, filetype="pdf")
    cover = fitz.open(stream=cover_bytes, filetype="pdf")
    book.delete_page(0)                     # 기본 표지 제거
    book.insert_pdf(cover, start_at=0)      # 커스텀 표지 맨 앞 삽입
    pdf_bytes = book.tobytes()
    book.close(); cover.close()

    book_dir = Path.home() / "클로드교재"
    book_dir.mkdir(exist_ok=True)
    out_path = book_dir / f"공통수학2 평면좌표 {diff}.pdf"
    out_path.write_bytes(pdf_bytes)
    subprocess.run(["xattr", "-c", str(out_path)], check=False)
    print(f"  [OK] {out_path} ({out_path.stat().st_size/1024/1024:.1f}MB)")


def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "all"
    diffs = ["상", "중", "하"] if arg == "all" else [arg]
    for d in diffs:
        assert d in ("상", "중", "하"), f"난이도는 상/중/하 — {d!r}"

    print("[1/2] 로컬 DB 조회...")
    all_rows = fetch_rows()
    print(f"  매칭 문항(전체): {len(all_rows)}")

    print("[2/2] 난이도별 빌드")
    for d in diffs:
        build_one(d, all_rows)


if __name__ == "__main__":
    main()
