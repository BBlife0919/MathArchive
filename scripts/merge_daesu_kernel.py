"""대수 KERNEL POINT 빈출 FINAL 최종 머지.

cover + toc + (ch divider + ch 본문) × 4 + AK divider + 해설 본문
원본 PDF 본문/해설은 그대로 (4분할 본문 유지).
"""
from __future__ import annotations
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "daesu_kernel_point"

SRC_PDF = Path("/Users/youngwoolee/Downloads/수업자료/2026 1학기 수업교재/고2/대수 KERNEL POINT_빈출FINAL.pdf")

COVER = OUT_DIR / "cover.pdf"
TOC = OUT_DIR / "toc.pdf"
DIVIDERS = OUT_DIR / "dividers.pdf"  # ch1, ch2, ch3, ch4, AK
OUT_PDF = OUT_DIR / "KERNEL_POINT_대수_빈출FINAL.pdf"

# 원본 PDF 페이지 구조 (확인된 인덱스)
CHAPTER_BODY_RANGES = [
    (3, 17),    # ch1 본문 p3~p17
    (19, 38),   # ch2 본문 p19~p38
    (40, 46),   # ch3 본문 p40~p46
    (48, 66),   # ch4 본문 p48~p66
]
SOLUTION_RANGE = (68, 71)  # 해설 본문 p68~p71 (디바이더 p67 제외)


def main():
    out = fitz.open()
    cover = fitz.open(str(COVER))
    toc = fitz.open(str(TOC))
    div = fitz.open(str(DIVIDERS))
    src = fitz.open(str(SRC_PDF))

    # 1) Cover
    out.insert_pdf(cover)

    # 2) TOC
    out.insert_pdf(toc)

    # 3) Chapter divider + body
    for ch_idx, (b_start, b_end) in enumerate(CHAPTER_BODY_RANGES):
        out.insert_pdf(div, from_page=ch_idx, to_page=ch_idx)
        out.insert_pdf(src, from_page=b_start, to_page=b_end)

    # 4) AK divider
    out.insert_pdf(div, from_page=len(div) - 1, to_page=len(div) - 1)

    # 5) Solution body
    s_start, s_end = SOLUTION_RANGE
    out.insert_pdf(src, from_page=s_start, to_page=s_end)

    cover.close()
    toc.close()
    div.close()
    src.close()

    n = len(out)
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    out.close()
    print(f"[OK] Final PDF: {OUT_PDF}")
    print(f"  Total pages: {n}")


if __name__ == "__main__":
    main()
