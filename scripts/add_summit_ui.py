"""SUMMIT POINT 교재 페이지에 우측 책갈피 + 상단 헤더 추가.

각 PDF (renum_m*_src.pdf) 의 모든 문제/해설 페이지에:
  - 우측 단원 책갈피: 챕터 글자 (A/B/C) + PART 표시
  - 상단 헤더: SUMMIT POINT · 챕터 짧은이름 (얇은 라인)

첫 페이지(page 0) 의 큰 단원 헤더는 유지.
"""
from __future__ import annotations

from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

_aggro = fitz.Font(fontfile=FONT_AGGRO)
_paper = fitz.Font(fontfile=FONT_PAPER_BLACK)
_cafe = fitz.Font(fontfile=FONT_CAFE24)

# 색상 팔레트
NAVY = (15/255, 25/255, 50/255)
GOLD = (210/255, 175/255, 110/255)
GOLD_LIGHT = (240/255, 205/255, 135/255)
ORANGE = (240/255, 125/255, 35/255)
GREY = (130/255, 140/255, 160/255)
GREY_LIGHT = (200/255, 205/255, 220/255)
WHITE = (1, 1, 1)
NAVY_PALE = (240/255, 244/255, 252/255)
NAVY_BAR = (35/255, 55/255, 100/255)


# (in_path, prefix, part_no, chapter_short)
SOURCES = [
    (OUT_DIR / "renum_m1_src.pdf", "A", "PART 1", "여러가지 방정식·부등식"),
    (OUT_DIR / "renum_m2_src.pdf", "B", "PART 2", "순열·조합"),
    (OUT_DIR / "renum_m3_src.pdf", "C", "PART 3", "행렬"),
]


def add_top_header(page: fitz.Page, part_no: str, chapter_short: str):
    """상단 슬림 헤더: 좌측 SUMMIT POINT · 우측 PART X · 단원명."""
    page_w = page.rect.width
    # 페이지 상단 5pt 흰색은 이미 strip_header 로 비어있음
    # 헤더 라인 (가는 회색)
    line_y = 40
    page.draw_line((34, line_y), (page_w - 34, line_y),
                   color=GREY_LIGHT, width=0.6)
    # 좌측: SUMMIT POINT
    page.insert_text((36, 32), "SUMMIT POINT",
                     fontname="aggro", fontfile=FONT_AGGRO,
                     fontsize=8, color=NAVY)
    # 우측: PART X · 단원명
    right_text = f"{part_no}  ·  {chapter_short}"
    tw = _cafe.text_length(right_text, fontsize=8)
    page.insert_text((page_w - 36 - tw, 32), right_text,
                     fontname="cafe24", fontfile=FONT_CAFE24,
                     fontsize=8, color=NAVY)


def add_side_bookmark(page: fitz.Page, prefix: str, part_no: str):
    """우측 단원 책갈피 (PART 표시 + 챕터 글자)."""
    page_w = page.rect.width
    page_h = page.rect.height

    # 우측 외곽 가로 위치 (책갈피 폭)
    bk_x0 = page_w - 28
    bk_x1 = page_w - 8

    # 상단 작은 박스: "PART N" (네이비 배경, 골드 글씨, 세로 텍스트)
    box_top_y0 = 90
    box_top_y1 = 240
    page.draw_rect(fitz.Rect(bk_x0, box_top_y0, bk_x1, box_top_y1),
                   color=NAVY, fill=NAVY, overlay=True)
    # 세로 텍스트: PART X (회전)
    # PyMuPDF: insert_text with rotate keyword. fonts work
    part_text = part_no.replace(" ", "  ")  # "PART  1"
    page.insert_text((bk_x0 + 8, box_top_y1 - 12),
                     part_text,
                     fontname="aggro", fontfile=FONT_AGGRO,
                     fontsize=9, color=GOLD_LIGHT, rotate=90)

    # 중간 큰 박스: 챕터 글자 (A/B/C) — 골드 박스, 흰 글씨
    box_mid_y0 = 248
    box_mid_y1 = 318
    page.draw_rect(fitz.Rect(bk_x0, box_mid_y0, bk_x1, box_mid_y1),
                   color=GOLD, fill=GOLD, overlay=True)
    # 큰 챕터 글자, 중앙 정렬
    fsize = 26
    tw = _paper.text_length(prefix, fontsize=fsize)
    glyph_h = 18
    cx = (bk_x0 + bk_x1) / 2
    cy = (box_mid_y0 + box_mid_y1) / 2
    page.insert_text((cx - tw/2, cy + glyph_h/2 - 2),
                     prefix,
                     fontname="paperblack", fontfile=FONT_PAPER_BLACK,
                     fontsize=fsize, color=WHITE)

    # 하단 얇은 골드 라인 + 페이지 점선 장식
    line_y = page_h - 70
    page.draw_line((bk_x0 + 6, 330), (bk_x0 + 6, line_y),
                   color=GOLD_LIGHT, width=1.2)


def is_section_start_page(page: fitz.Page) -> bool:
    """문제 첫 페이지(단원명 헤더가 있는 페이지) 인지 판별."""
    t = page.get_text()
    return ('EQUATIONS' in t) or ('PERMUTATION' in t) or ('MATRIX' in t)


def process_pdf(in_path: Path, out_path: Path, prefix: str, part_no: str, chapter_short: str):
    doc = fitz.open(str(in_path))
    for pi, page in enumerate(doc):
        text = page.get_text()
        # 빠른정답 페이지나 체크리스트는 별도 처리 — 책갈피만 추가 (헤더 X)
        is_quick = '빠른정답' in text
        # 일반 페이지: 헤더 + 책갈피
        if pi == 0:
            # 첫 페이지: 이미 단원 헤더 있음 → 책갈피만
            add_side_bookmark(page, prefix, part_no)
        elif is_quick:
            add_side_bookmark(page, prefix, part_no)
        else:
            add_top_header(page, part_no, chapter_short)
            add_side_bookmark(page, prefix, part_no)
    doc.save(str(out_path), garbage=4, deflate=True)
    doc.close()


def main():
    for src, prefix, part_no, chapter_short in SOURCES:
        dst = src.with_name(src.stem + "_ui.pdf")
        print(f"Processing {src.name} → {dst.name}")
        process_pdf(src, dst, prefix, part_no, chapter_short)
    print("Done.")


if __name__ == "__main__":
    main()
