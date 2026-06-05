"""SUMMIT POINT 교재 최종 병합 — 2단 레이아웃 + 통합 빠른정답.

구조:
  1. 전체 표지 (cover.pdf)
  2. 챕터1 내지 → problems_2col 0~45 (A·01 ~ A·91, 46 pages)
  3. 챕터2 내지 → problems_2col 46~89 (B·01 ~ B·88, 44 pages)
  4. 챕터3 내지 → problems_2col 90~112 (C·01 ~ C·46, 23 pages)
  5. 정답해설 내지 → 통합 빠른정답 (1p) → m1/m2/m3 해설
"""
from __future__ import annotations
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"
OUT_PDF = OUT_DIR / "SUMMIT_POINT_모의고사_완전정복.pdf"

COVER = OUT_DIR / "cover.pdf"
DIVIDERS = OUT_DIR / "dividers.pdf"
PROBLEMS = OUT_DIR / "problems_2col.pdf"   # 113 pages
QUICK_ANS = OUT_DIR / "quick_answer.pdf"   # 1 page
M1 = OUT_DIR / "renum_m1_src_ui.pdf"
M2 = OUT_DIR / "renum_m2_src_ui.pdf"
M3 = OUT_DIR / "renum_m3_src_ui.pdf"

# 챕터별 problems_2col 페이지 범위 (build_2col_problems.py 출력 참조)
CHAP_PAGE_BREAKS = {"A": 0, "B": 46, "C": 90}
CHAP_PAGE_RANGES = {
    "A": (0, 45),
    "B": (46, 89),
    "C": (90, 112),
}


def main():
    out = fitz.open()

    cover = fitz.open(str(COVER))
    div = fitz.open(str(DIVIDERS))
    probs = fitz.open(str(PROBLEMS))
    qa = fitz.open(str(QUICK_ANS))
    m1 = fitz.open(str(M1))
    m2 = fitz.open(str(M2))
    m3 = fitz.open(str(M3))

    # 1) Cover
    out.insert_pdf(cover)

    # 2) Chapter dividers + 2-col problems
    for div_idx, key in enumerate(['A', 'B', 'C']):
        out.insert_pdf(div, from_page=div_idx, to_page=div_idx)
        p0, p1 = CHAP_PAGE_RANGES[key]
        out.insert_pdf(probs, from_page=p0, to_page=p1)

    # 5) Answer key divider
    out.insert_pdf(div, from_page=3, to_page=3)

    # 6) 통합 빠른정답
    out.insert_pdf(qa)

    # 7) 해설 (m1 → m2 → m3)
    out.insert_pdf(m1, from_page=39, to_page=72)   # m1 해설
    out.insert_pdf(m2, from_page=47, to_page=70)   # m2 해설
    out.insert_pdf(m3, from_page=20, to_page=30)   # m3 해설

    for d in [cover, div, probs, qa, m1, m2, m3]:
        d.close()

    n_pages = len(out)
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    out.close()
    print(f"[OK] Final PDF: {OUT_PDF}")
    print(f"  Total pages: {n_pages}")


if __name__ == "__main__":
    main()
