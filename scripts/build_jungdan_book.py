"""중단원 평가(2-2단원) 본문 2단 페이지 빌드 — SUMMIT POINT 스타일 동일.

한 페이지에 2문제 (좌/우 컬럼). 각 컬럼:
  - 좌측: 글로벌 라벨(주황 SB 어그로) + 1/2/3차 체크박스 + O/X 체크박스
  - 우측: 원본 PDF 클립 임베드 (show_pdf_page)
  - 하단: KEY POINT 박스 + MEMO 라인
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz

from extract_jungdan_problems import CHAPTERS

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
META_JSON = OUT_DIR / "problems_meta.json"
OUT_PDF = OUT_DIR / "problems_2col.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

_aggro = fitz.Font(fontfile=FONT_AGGRO)
_paper = fitz.Font(fontfile=FONT_PAPER_BLACK)
_cafe = fitz.Font(fontfile=FONT_CAFE24)

NAVY = (15/255, 25/255, 50/255)
GOLD = (210/255, 175/255, 110/255)
GOLD_LIGHT = (240/255, 205/255, 135/255)
ORANGE = (240/255, 125/255, 35/255)
GREY = (130/255, 140/255, 160/255)
GREY_LIGHT = (200/255, 205/255, 220/255)
GREY_LINE = (170/255, 178/255, 195/255)
KP_BG = (250/255, 248/255, 240/255)
KP_BORDER = (230/255, 200/255, 140/255)

PAGE_W = 595.0
PAGE_H = 842.0

HEADER_Y = 38
HEADER_LINE_Y = 42

LEFT_MARGIN = 28
RIGHT_MARGIN = 28
TOP_MARGIN = 58
BOTTOM_MARGIN = 50
COL_GAP = 18

COL_W = (PAGE_W - LEFT_MARGIN - RIGHT_MARGIN - COL_GAP) / 2
COL_RIGHT_X = LEFT_MARGIN + COL_W + COL_GAP
COL_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN

KP_H = 28
MEMO_LINES = 6
MEMO_LINE_GAP = 16
MEMO_H = MEMO_LINE_GAP * MEMO_LINES + 8

GAPS = 24
PROB_MAX_H = COL_H - KP_H - MEMO_H - GAPS


def text_at(page, x, y, text, fontname, fontfile, size, color):
    page.insert_text((x, y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size, color=color)


def draw_top_header(page, part_no: str, chapter_short: str):
    text_at(page, LEFT_MARGIN, HEADER_Y, "MID-CHAPTER POINT",
            "aggro", FONT_AGGRO, 8, NAVY)
    right_text = f"{part_no}  ·  {chapter_short}"
    tw = _cafe.text_length(right_text, fontsize=8)
    text_at(page, PAGE_W - RIGHT_MARGIN - tw, HEADER_Y, right_text,
            "cafe24", FONT_CAFE24, 8, NAVY)
    page.draw_line((LEFT_MARGIN, HEADER_LINE_Y),
                   (PAGE_W - RIGHT_MARGIN, HEADER_LINE_Y),
                   color=GREY_LIGHT, width=0.6)


def draw_side_bookmark(page, roman: str, part_no: str):
    bk_x0 = PAGE_W - 28
    bk_x1 = PAGE_W - 8
    page.draw_rect(fitz.Rect(bk_x0, 90, bk_x1, 230),
                   color=NAVY, fill=NAVY, overlay=True)
    page.insert_text((bk_x0 + 8, 220), part_no,
                     fontname="aggro", fontfile=FONT_AGGRO,
                     fontsize=9, color=GOLD_LIGHT, rotate=90)
    page.draw_rect(fitz.Rect(bk_x0, 238, bk_x1, 308),
                   color=GOLD, fill=GOLD, overlay=True)
    fsize = 22
    tw = _paper.text_length(roman, fontsize=fsize)
    cx = (bk_x0 + bk_x1) / 2
    page.insert_text((cx - tw/2, 280), roman,
                     fontname="paperblack", fontfile=FONT_PAPER_BLACK,
                     fontsize=fsize, color=(1, 1, 1))
    page.draw_line((bk_x0 + 6, 320), (bk_x0 + 6, PAGE_H - 70),
                   color=GOLD_LIGHT, width=1.2)


def draw_problem_block(page, col_x0, col_y0, meta, src_doc_cache):
    label = meta["label"]
    src_pdf = meta["src_pdf"]
    src_page = meta["src_page"]
    clip = meta["clip"]
    col_x1 = col_x0 + COL_W

    LEFT_BLOCK_W = 58
    LEFT_BLOCK_GAP = 4
    PROB_TOP_OFFSET = 10

    meta_x = col_x0
    img_area_x0 = col_x0 + LEFT_BLOCK_W + LEFT_BLOCK_GAP
    img_area_w = col_x1 - img_area_x0

    # 라벨 (orange SB 어그로 18pt, baseline 14 below visual top)
    label_baseline = col_y0 + PROB_TOP_OFFSET + 14
    text_at(page, meta_x, label_baseline, label,
            "aggro", FONT_AGGRO, 18, ORANGE)

    # 1차/2차/3차 체크박스
    box_size = 6
    box_h = 7
    row1_y_text = label_baseline + 13
    row1_y_box_top = row1_y_text - 6
    bx = meta_x
    for lbl_text in ["1차", "2차", "3차"]:
        page.draw_rect(fitz.Rect(bx, row1_y_box_top, bx + box_size,
                                  row1_y_box_top + box_h),
                       color=GREY_LINE, width=0.5)
        text_at(page, bx + box_size + 2, row1_y_text, lbl_text,
                "cafe24", FONT_CAFE24, 6.5, NAVY)
        bx += 18

    # O/X 체크박스
    row2_y_text = row1_y_text + 12
    row2_y_box_top = row2_y_text - 6
    bx = meta_x
    for lbl_text in ["O", "X"]:
        page.draw_rect(fitz.Rect(bx, row2_y_box_top, bx + box_size,
                                  row2_y_box_top + box_h),
                       color=GREY_LINE, width=0.5)
        text_at(page, bx + box_size + 2, row2_y_text, lbl_text,
                "cafe24", FONT_CAFE24, 6.5, NAVY)
        bx += 16

    # 문제 클립 임베드
    prob_top = col_y0 + PROB_TOP_OFFSET
    cx0, cy0, cx1, cy1 = clip
    src_w = cx1 - cx0
    src_h = cy1 - cy0
    scale = img_area_w / src_w
    if src_h * scale > PROB_MAX_H:
        scale = PROB_MAX_H / src_h
    target_w = src_w * scale
    target_h = src_h * scale
    tx0 = img_area_x0
    ty0 = prob_top
    tx1 = tx0 + target_w
    ty1 = ty0 + target_h

    if src_pdf not in src_doc_cache:
        src_doc_cache[src_pdf] = fitz.open(src_pdf)
    src_doc = src_doc_cache[src_pdf]
    page.show_pdf_page(
        fitz.Rect(tx0, ty0, tx1, ty1),
        src_doc, src_page,
        clip=fitz.Rect(cx0, cy0, cx1, cy1),
    )

    # 원본 라벨 위치 화이트박싱 — 클립 안의 좌측 상단(원본 "01" 같은 라벨)
    # 클립의 좌측 상단 ~22pt × ~16pt 영역
    label_cover_w = 20.0 * scale
    label_cover_h = 14.0 * scale
    page.draw_rect(fitz.Rect(tx0, ty0, tx0 + label_cover_w, ty0 + label_cover_h),
                   color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    # KEY POINT 박스
    bottom_block_y = col_y0 + COL_H - KP_H - MEMO_H - 16
    kp_y = bottom_block_y
    kp_rect = fitz.Rect(col_x0, kp_y, col_x1, kp_y + KP_H)
    page.draw_rect(kp_rect, color=KP_BORDER, fill=KP_BG, width=0.8)
    text_at(page, col_x0 + 8, kp_y + 11, "KEY POINT",
            "aggro", FONT_AGGRO, 8, GOLD)
    page.draw_line((col_x0 + 78, kp_y + 5),
                   (col_x0 + 78, kp_y + KP_H - 5),
                   color=KP_BORDER, width=0.6)
    text_at(page, col_x0 + 85, kp_y + 17, "이 문제 핵심 한 줄로 정리",
            "cafe24", FONT_CAFE24, 8.5, GREY)

    # MEMO 영역
    memo_top = kp_y + KP_H + 8
    text_at(page, col_x0, memo_top + 8, "MEMO",
            "aggro", FONT_AGGRO, 7, GREY)
    line_start_y = memo_top + 18
    for i in range(MEMO_LINES):
        ly = line_start_y + i * MEMO_LINE_GAP
        page.draw_line((col_x0, ly), (col_x1, ly),
                       color=GREY_LINE, width=0.4)


def main():
    problems = json.loads(META_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(problems)} problems")

    out = fitz.open()
    src_doc_cache: dict[str, fitz.Document] = {}

    page_breaks: dict[int, int] = {}
    i = 0
    while i < len(problems):
        page = out.new_page(width=PAGE_W, height=PAGE_H)
        left = problems[i]
        ch_idx = left["chapter_idx"]
        ch = CHAPTERS[ch_idx]
        part_no = f"PART {ch_idx + 1:02d}"
        if ch_idx not in page_breaks:
            page_breaks[ch_idx] = len(out) - 1

        draw_top_header(page, part_no, ch["short"])
        draw_side_bookmark(page, ch["roman"], part_no)

        draw_problem_block(page, LEFT_MARGIN, TOP_MARGIN, left, src_doc_cache)

        if i + 1 < len(problems):
            right = problems[i + 1]
            if right["chapter_idx"] == ch_idx:
                draw_problem_block(page, COL_RIGHT_X, TOP_MARGIN, right, src_doc_cache)
                i += 2
            else:
                # 챕터 경계: 우측 컬럼 비우고 다음 페이지 새 챕터
                i += 1
        else:
            i += 1

    print(f"Chapter page breaks: {page_breaks}")
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n_pages = len(out)
    out.close()
    for d in src_doc_cache.values():
        d.close()
    print(f"[OK] {OUT_PDF}  ({n_pages} pages)")


if __name__ == "__main__":
    main()
