"""중단원 평가(2-2단원) 해설 2단 페이지 빌드.

각 해설 = 원본 PDF 클립 + 새 글로벌 라벨(주황 SB 어그로). 컬럼 안에서 세로로 쌓고
컬럼이 차면 다음 컬럼/페이지로 이동. 페이지 상단 헤더(MID-CHAPTER POINT · 챕터명).
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz

from extract_jungdan_problems import CHAPTERS

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
META_JSON = OUT_DIR / "solutions_meta.json"
OUT_PDF = OUT_DIR / "solutions_2col.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

_cafe = fitz.Font(fontfile=FONT_CAFE24)

NAVY = (15/255, 25/255, 50/255)
ORANGE = (240/255, 125/255, 35/255)
GREY = (130/255, 140/255, 160/255)
GREY_LIGHT = (200/255, 205/255, 220/255)

PAGE_W = 595.0
PAGE_H = 842.0

LEFT_MARGIN = 28
RIGHT_MARGIN = 28
TOP_MARGIN = 60
BOTTOM_MARGIN = 50
COL_GAP = 18
HEADER_Y = 38
HEADER_LINE_Y = 42

COL_W = (PAGE_W - LEFT_MARGIN - RIGHT_MARGIN - COL_GAP) / 2
COL_RIGHT_X = LEFT_MARGIN + COL_W + COL_GAP
COL_TOP = TOP_MARGIN
COL_BOTTOM = PAGE_H - BOTTOM_MARGIN
COL_H = COL_BOTTOM - COL_TOP

LABEL_H = 18           # 라벨 헤더 높이
SOL_GAP = 12           # 해설 사이 갭
MAX_SOL_H = COL_H - LABEL_H  # 컬럼 안 한 해설 최대 높이


def text_at(page, x, y, text, fontname, fontfile, size, color):
    page.insert_text((x, y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size, color=color)


def draw_header(page, ch_idx: int):
    ch = CHAPTERS[ch_idx]
    text_at(page, LEFT_MARGIN, HEADER_Y,
            "TEXTBOOK POINT · A N S W E R   K E Y",
            "aggro", FONT_AGGRO, 8, NAVY)
    right = f"PART {ch_idx + 1:02d}  ·  {ch['short']}"
    tw = _cafe.text_length(right, fontsize=8)
    text_at(page, PAGE_W - RIGHT_MARGIN - tw, HEADER_Y, right,
            "cafe24", FONT_CAFE24, 8, NAVY)
    page.draw_line((LEFT_MARGIN, HEADER_LINE_Y),
                   (PAGE_W - RIGHT_MARGIN, HEADER_LINE_Y),
                   color=GREY_LIGHT, width=0.6)


def main():
    sols = json.loads(META_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(sols)} solutions")

    out = fitz.open()
    src_doc_cache: dict[str, fitz.Document] = {}

    def open_src(p):
        if p not in src_doc_cache:
            src_doc_cache[p] = fitz.open(p)
        return src_doc_cache[p]

    page = None
    page_ch_idx = None
    col_idx = 0   # 0=left, 1=right
    col_y = COL_TOP   # 현재 컬럼에서 다음 해설이 들어갈 y

    page_breaks: dict[int, int] = {}

    def new_page(ch_idx):
        nonlocal page, page_ch_idx, col_idx, col_y
        page = out.new_page(width=PAGE_W, height=PAGE_H)
        page_ch_idx = ch_idx
        col_idx = 0
        col_y = COL_TOP
        draw_header(page, ch_idx)
        if ch_idx not in page_breaks:
            page_breaks[ch_idx] = len(out) - 1

    new_page(sols[0]["chapter_idx"])

    for sol in sols:
        ch_idx = sol["chapter_idx"]
        # 챕터 바뀌면 새 페이지
        if ch_idx != page_ch_idx:
            new_page(ch_idx)

        label = sol["label"]
        cx0, cy0, cx1, cy1 = sol["clip"]
        src_w = cx1 - cx0
        src_h = cy1 - cy0

        col_x0 = LEFT_MARGIN if col_idx == 0 else COL_RIGHT_X
        col_x1 = col_x0 + COL_W
        scale = COL_W / src_w
        target_h = src_h * scale

        # 컬럼에 안 들어가면 다음 컬럼/페이지로
        remaining_h = COL_BOTTOM - col_y - LABEL_H
        if target_h > remaining_h:
            # 컬럼/페이지 이동
            if col_idx == 0:
                col_idx = 1
                col_y = COL_TOP
                col_x0 = COL_RIGHT_X
                col_x1 = col_x0 + COL_W
            else:
                new_page(ch_idx)
                col_x0 = LEFT_MARGIN
                col_x1 = col_x0 + COL_W
            remaining_h = COL_BOTTOM - col_y - LABEL_H

        # 그래도 안 들어가면 강제로 페이지 높이에 맞춰 축소
        if target_h > remaining_h:
            scale = remaining_h / src_h
            target_h = src_h * scale

        target_w = src_w * scale

        # 라벨 헤더
        text_at(page, col_x0, col_y + 12, label,
                "aggro", FONT_AGGRO, 12, ORANGE)
        # 가는 가로 라인
        page.draw_line((col_x0 + 36, col_y + 10),
                       (col_x0 + COL_W, col_y + 10),
                       color=ORANGE, width=0.6)

        # 클립 임베드
        img_top = col_y + LABEL_H
        img_left = col_x0 + (COL_W - target_w) / 2  # 살짝 가운데 정렬 (잔여)
        img_left = col_x0
        page.show_pdf_page(
            fitz.Rect(img_left, img_top, img_left + target_w, img_top + target_h),
            open_src(sol["src_pdf"]),
            sol["src_page"],
            clip=fitz.Rect(cx0, cy0, cx1, cy1),
        )

        # 원본 라벨 영역 화이트박싱 (클립 좌측 상단)
        label_cover_w = 20.0 * scale
        label_cover_h = 14.0 * scale
        page.draw_rect(
            fitz.Rect(img_left, img_top, img_left + label_cover_w, img_top + label_cover_h),
            color=(1, 1, 1), fill=(1, 1, 1), overlay=True,
        )

        col_y = img_top + target_h + SOL_GAP

    print(f"Chapter page breaks: {page_breaks}")
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n_pages = len(out)
    out.close()
    for d in src_doc_cache.values():
        d.close()
    print(f"[OK] {OUT_PDF}  ({n_pages} pages)")


if __name__ == "__main__":
    main()
