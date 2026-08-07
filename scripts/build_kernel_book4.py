"""KERNEL POINT 본문 빌드 — 라벨 4개 = 2x2 그리드 셀.

각 라벨의 본문 영역(reading-order 다음 라벨 직전까지, 컬럼/페이지 경계 넘김 포함)을
한 셀에 수직 차곡차곡 임베드. 4 라벨 = 한 dest 페이지.
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz

from extract_kernel_problems import (
    SRC_PDF, OUT_DIR, CHAPTERS, PROBLEM_PAGES, find_labels,
)

OUT_PDF = OUT_DIR / "problems_4col.pdf"

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

LEFT_MARGIN = 28
RIGHT_MARGIN = 28
TOP_MARGIN = 56
BOTTOM_MARGIN = 32
COL_GAP_X = 14
ROW_GAP_Y = 14
HEADER_Y = 38
HEADER_LINE_Y = 42

COL_W = (PAGE_W - LEFT_MARGIN - RIGHT_MARGIN - COL_GAP_X) / 2
ROW_H = (PAGE_H - TOP_MARGIN - BOTTOM_MARGIN - ROW_GAP_Y) / 2

COL_X0_LEFT = LEFT_MARGIN
COL_X0_RIGHT = LEFT_MARGIN + COL_W + COL_GAP_X
ROW_Y0_TOP = TOP_MARGIN
ROW_Y0_BOT = TOP_MARGIN + ROW_H + ROW_GAP_Y

LABEL_ROW_H = 22
KP_H = 20
MEMO_LINES = 3
MEMO_LINE_GAP = 12
MEMO_H = MEMO_LINES * MEMO_LINE_GAP + 8
PROB_GAP = 4
PROB_H = ROW_H - LABEL_ROW_H - KP_H - MEMO_H - PROB_GAP * 3

# src — 가운데 점선(x=283), 우측 컬럼 좌측 세로선(x=297.6) 등 제외
SRC_L_X0 = 32.0
SRC_L_X1 = 282.0
SRC_R_X0 = 299.0
SRC_R_X1 = 522.0
SRC_TOP = 58.0
SRC_BOT = 798.0


def col_x_range(col):
    return (SRC_L_X0, SRC_L_X1) if col == "L" else (SRC_R_X0, SRC_R_X1)


def col_of(rect):
    return "L" if rect.x0 < 200 else "R"


def chapter_for_label(n):
    return 0 if n <= 134 else 1


def text_at(page, x, y, text, fontname, fontfile, size, color):
    page.insert_text((x, y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size, color=color)


def draw_top_header(page, part_no, chapter_short):
    text_at(page, LEFT_MARGIN, HEADER_Y, "KERNEL POINT",
            "aggro", FONT_AGGRO, 8, NAVY)
    right_text = f"{part_no}  ·  {chapter_short}"
    tw = _cafe.text_length(right_text, fontsize=8)
    text_at(page, PAGE_W - RIGHT_MARGIN - tw, HEADER_Y, right_text,
            "cafe24", FONT_CAFE24, 8, NAVY)
    page.draw_line((LEFT_MARGIN, HEADER_LINE_Y),
                   (PAGE_W - RIGHT_MARGIN, HEADER_LINE_Y),
                   color=GREY_LIGHT, width=0.6)


def draw_side_bookmark(page, roman, part_no):
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


def get_label_clips(label, next_label):
    """라벨의 본문 src 영역 = 라벨 위치 ~ next_label 직전 (reading order)."""
    clips = []
    cur_pg = label["src_pg"]
    cur_col = label["col"]
    cur_y = max(SRC_TOP, label["rect"].y0 - 4)

    if next_label is None:
        col_x0, col_x1 = col_x_range(cur_col)
        clips.append((cur_pg, col_x0, cur_y, col_x1, SRC_BOT))
        return clips

    end_pg = next_label["src_pg"]
    end_col = next_label["col"]
    end_y = max(SRC_TOP, next_label["rect"].y0 - 4)

    safety = 0
    while safety < 30:
        safety += 1
        if cur_pg == end_pg and cur_col == end_col:
            col_x0, col_x1 = col_x_range(cur_col)
            if end_y > cur_y:
                clips.append((cur_pg, col_x0, cur_y, col_x1, end_y))
            break
        col_x0, col_x1 = col_x_range(cur_col)
        clips.append((cur_pg, col_x0, cur_y, col_x1, SRC_BOT))
        if cur_col == "L":
            cur_col = "R"
            cur_y = SRC_TOP
        else:
            cur_col = "L"
            cur_pg += 1
            cur_y = SRC_TOP
            if cur_pg > end_pg + 3:
                break
    return clips


def draw_cell(page, cell_x0, cell_y0, label, clips, src_doc):
    n = label["n"]
    cell_x1 = cell_x0 + COL_W

    # 1) 라벨 (SB 어그로 주황) + 체크박스 한 줄
    label_y_baseline = cell_y0 + 16
    label_text = f"{n:03d}"
    text_at(page, cell_x0, label_y_baseline, label_text,
            "aggro", FONT_AGGRO, 14, ORANGE)
    label_w_dest = _aggro.text_length(label_text, fontsize=14)

    cb_size = 5
    cb_y_top = cell_y0 + 10
    cb_x = cell_x0 + label_w_dest + 14
    for lbl in ["1차", "2차", "3차"]:
        page.draw_rect(fitz.Rect(cb_x, cb_y_top, cb_x + cb_size, cb_y_top + cb_size + 1),
                       color=GREY_LINE, width=0.5)
        text_at(page, cb_x + cb_size + 2, cb_y_top + cb_size, lbl,
                "cafe24", FONT_CAFE24, 6, NAVY)
        cb_x += 18
    cb_x += 6
    for lbl in ["O", "X"]:
        page.draw_rect(fitz.Rect(cb_x, cb_y_top, cb_x + cb_size, cb_y_top + cb_size + 1),
                       color=GREY_LINE, width=0.5)
        text_at(page, cb_x + cb_size + 2, cb_y_top + cb_size, lbl,
                "cafe24", FONT_CAFE24, 6, NAVY)
        cb_x += 12

    # 2) 본문 (clips 수직 차곡차곡)
    if not clips:
        return
    src_w_max = max((c[3] - c[1]) for c in clips)
    src_h_sum = sum((c[4] - c[2]) for c in clips) or 1.0
    avail_w = COL_W
    avail_h = PROB_H
    scale = min(avail_w / src_w_max, avail_h / src_h_sum)

    ty_start = cell_y0 + LABEL_ROW_H + PROB_GAP
    ty = ty_start
    first_clip = True
    for (src_pg, x0, y0, x1, y1) in clips:
        sw = x1 - x0
        sh = y1 - y0
        if sh <= 0:
            continue
        tw = sw * scale
        th = sh * scale
        tx0 = cell_x0
        page.show_pdf_page(
            fitz.Rect(tx0, ty, tx0 + tw, ty + th),
            src_doc, src_pg, clip=fitz.Rect(x0, y0, x1, y1),
        )
        if first_clip:
            lr = label["rect"]
            if x0 <= lr.x0 <= x1 and y0 <= lr.y0 <= y1:
                dx0 = tx0 + (lr.x0 - x0) * scale
                dy0 = ty + (lr.y0 - y0) * scale
                dx1 = tx0 + (lr.x1 - x0) * scale
                dy1 = ty + (lr.y1 - y0) * scale
                pad = 1.5
                page.draw_rect(
                    fitz.Rect(dx0 - pad, dy0 - pad, dx1 + pad, dy1 + pad),
                    color=(1, 1, 1), fill=(1, 1, 1), overlay=True,
                )
            first_clip = False
        ty += th

    # 3) KEY POINT (본문 바로 아래)
    kp_y = ty + PROB_GAP * 2
    # 셀 영역 안에 맞게 — 너무 아래면 cell 하단까지
    cell_bot = cell_y0 + ROW_H
    kp_y = min(kp_y, cell_bot - KP_H - MEMO_H - PROB_GAP)
    kp_rect = fitz.Rect(cell_x0, kp_y, cell_x1, kp_y + KP_H)
    page.draw_rect(kp_rect, color=KP_BORDER, fill=KP_BG, width=0.6)
    text_at(page, cell_x0 + 6, kp_y + 8.5, "KEY POINT",
            "aggro", FONT_AGGRO, 7, GOLD)
    page.draw_line((cell_x0 + 62, kp_y + 4),
                   (cell_x0 + 62, kp_y + KP_H - 4),
                   color=KP_BORDER, width=0.5)
    text_at(page, cell_x0 + 67, kp_y + 13, "핵심 한 줄",
            "cafe24", FONT_CAFE24, 7.5, GREY)

    # 4) MEMO
    memo_top = kp_y + KP_H + 2
    text_at(page, cell_x0, memo_top + 7, "MEMO",
            "aggro", FONT_AGGRO, 6.5, GREY)
    line_start = memo_top + 16
    for i in range(MEMO_LINES):
        ly = line_start + i * MEMO_LINE_GAP
        page.draw_line((cell_x0, ly), (cell_x1, ly),
                       color=GREY_LINE, width=0.35)


CELL_POSITIONS = [
    (COL_X0_LEFT, ROW_Y0_TOP),
    (COL_X0_RIGHT, ROW_Y0_TOP),
    (COL_X0_LEFT, ROW_Y0_BOT),
    (COL_X0_RIGHT, ROW_Y0_BOT),
]


def main():
    src = fitz.open(str(SRC_PDF))

    labels_all = []
    for src_pg in PROBLEM_PAGES:
        labels = find_labels(src[src_pg])
        labels.sort(key=lambda x: (0 if x[0].x0 < 200 else 1, x[0].y0))
        for rect, n in labels:
            labels_all.append({
                "n": n,
                "src_pg": src_pg,
                "rect": rect,
                "col": col_of(rect),
            })

    out = fitz.open()
    page_breaks: dict[int, int] = {}
    i = 0
    while i < len(labels_all):
        # 현재 챕터 동일 라벨만 한 그룹
        ch_idx = chapter_for_label(labels_all[i]["n"])
        ch = CHAPTERS[ch_idx]
        part_no = f"PART {ch_idx + 1:02d}"
        page = out.new_page(width=PAGE_W, height=PAGE_H)
        if ch_idx not in page_breaks:
            page_breaks[ch_idx] = len(out) - 1
        draw_top_header(page, part_no, ch["short"])
        draw_side_bookmark(page, ch["roman"], part_no)

        # 4개씩 (같은 챕터)
        group = []
        while i < len(labels_all) and len(group) < 4 and chapter_for_label(labels_all[i]["n"]) == ch_idx:
            group.append(labels_all[i])
            i += 1

        for cell_idx, label in enumerate(group):
            # next label = group 안 다음 또는 다음 그룹 첫
            if cell_idx + 1 < len(group):
                next_label = group[cell_idx + 1]
            elif i < len(labels_all):
                next_label = labels_all[i]
            else:
                next_label = None
            clips = get_label_clips(label, next_label)
            cx, cy = CELL_POSITIONS[cell_idx]
            draw_cell(page, cx, cy, label, clips, src)

    print(f"Chapter page breaks: {page_breaks}")
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n_pages = len(out)
    out.close()
    src.close()
    (OUT_DIR / "problems_page_breaks.json").write_text(
        json.dumps(page_breaks), encoding="utf-8"
    )
    print(f"[OK] {OUT_PDF}  ({n_pages} pages)")


if __name__ == "__main__":
    main()
