"""중단원 평가(2-2단원) 본문 4-per-page 레이아웃 (2x2 그리드).

한 페이지에 4문제 (좌상·우상·좌하·우하). 각 셀:
  - 상단: 글로벌 라벨(주황 SB 어그로) + 1차/2차/3차 + O/X (한 줄)
  - 가운데: 원본 PDF 클립 임베드
  - 하단: 컴팩트 KEY POINT 박스 + MEMO 3줄
"""
from __future__ import annotations

import json
from pathlib import Path

import fitz

from extract_jungdan_problems import CHAPTERS

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
META_JSON = OUT_DIR / "problems_meta.json"
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

# dest 본문 폰트 목표 — kind 별 일정한 src 본문 크기 가정.
TARGET_BODY_SIZE = 10.0
KIND_BODY_SIZE = {
    "jaja": 9.7,   # Haansoft Dotum
    "eval": 10.7,  # Dotum
}

LEFT_MARGIN = 28
RIGHT_MARGIN = 28
TOP_MARGIN = 56
BOTTOM_MARGIN = 40
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

# 셀 내부
LABEL_ROW_H = 20
KP_H = 20
MEMO_LINES = 3
MEMO_LINE_GAP = 12
MEMO_H = MEMO_LINES * MEMO_LINE_GAP + 8
PROB_GAP = 4
PROB_H = ROW_H - LABEL_ROW_H - KP_H - MEMO_H - PROB_GAP * 2


def text_at(page, x, y, text, fontname, fontfile, size, color):
    page.insert_text((x, y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size, color=color)


def draw_top_header(page, part_no: str, chapter_short: str):
    text_at(page, LEFT_MARGIN, HEADER_Y, "TEXTBOOK POINT",
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


def cell_size(meta) -> int:
    return 1


def draw_cell(page, cell_x0, cell_y0, meta, src_doc_cache, span_h: float = None):
    label = meta["label"]
    src_pdf = meta["src_pdf"]
    src_page = meta["src_page"]
    clip = meta["clip"]
    cell_x1 = cell_x0 + COL_W
    if span_h is None:
        span_h = ROW_H

    # 1) 라벨 + 체크박스 한 줄
    label_y_baseline = cell_y0 + 14
    text_at(page, cell_x0, label_y_baseline, label,
            "aggro", FONT_AGGRO, 14, ORANGE)
    label_w = _aggro.text_length(label, fontsize=14)

    # 체크박스 (라벨 우측에 한 줄)
    cb_size = 5
    cb_y_top = cell_y0 + 8
    cb_x = cell_x0 + label_w + 14
    for lbl in ["1차", "2차", "3차"]:
        page.draw_rect(fitz.Rect(cb_x, cb_y_top, cb_x + cb_size, cb_y_top + cb_size + 1),
                       color=GREY_LINE, width=0.5)
        text_at(page, cb_x + cb_size + 2, cb_y_top + cb_size, lbl,
                "cafe24", FONT_CAFE24, 6, NAVY)
        cb_x += 18
    # O/X
    cb_x += 6
    for lbl in ["O", "X"]:
        page.draw_rect(fitz.Rect(cb_x, cb_y_top, cb_x + cb_size, cb_y_top + cb_size + 1),
                       color=GREY_LINE, width=0.5)
        text_at(page, cb_x + cb_size + 2, cb_y_top + cb_size, lbl,
                "cafe24", FONT_CAFE24, 6, NAVY)
        cb_x += 12

    # 2) 문제 클립
    prob_top = cell_y0 + LABEL_ROW_H + PROB_GAP
    cx0, cy0, cx1, cy1 = clip
    src_w = cx1 - cx0
    src_h = cy1 - cy0

    if src_pdf not in src_doc_cache:
        src_doc_cache[src_pdf] = fitz.open(src_pdf)

    # 본문 폰트 통일: kind 별 고정 scale (eval=0.935, jaja=1.031)
    kind = meta.get("kind", "eval")
    body_src = KIND_BODY_SIZE.get(kind, 10.7)
    scale_target = TARGET_BODY_SIZE / body_src
    scale = min(scale_target, COL_W / src_w)

    # 셀 영역: span_h (1셀=ROW_H, 2셀=ROW_H*2+ROW_GAP_Y)
    avail_h_full = span_h - LABEL_ROW_H - PROB_GAP * 2
    avail_h_with_kpmemo = avail_h_full - KP_H - MEMO_H - PROB_GAP
    # KP/MEMO 자리 확보 위해 본문이 avail_h_with_kpmemo 초과 시 scale 축소
    if src_h * scale > avail_h_with_kpmemo:
        scale = avail_h_with_kpmemo / src_h
    draw_kp_memo = True

    target_w = src_w * scale
    target_h = src_h * scale
    tx0 = cell_x0
    ty0 = prob_top
    tx1 = tx0 + target_w
    ty1 = ty0 + target_h

    page.show_pdf_page(
        fitz.Rect(tx0, ty0, tx1, ty1),
        src_doc_cache[src_pdf], src_page,
        clip=fitz.Rect(cx0, cy0, cx1, cy1),
    )
    # 원본 라벨 위치 화이트박싱 — extract 단계에서 저장한 정확한 bbox 사용.
    lb = meta.get("label_bbox")
    if lb:
        lx0, ly0, lx1, ly1 = lb
        # src → dest 좌표 변환 (클립 기준)
        dx0 = tx0 + (max(lx0, cx0) - cx0) * scale
        dy0 = ty0 + (max(ly0, cy0) - cy0) * scale
        dx1 = tx0 + (min(lx1, cx1) - cx0) * scale
        dy1 = ty0 + (min(ly1, cy1) - cy0) * scale
        pad = 1.5
        page.draw_rect(
            fitz.Rect(dx0 - pad, dy0 - pad, dx1 + pad, dy1 + pad),
            color=(1, 1, 1), fill=(1, 1, 1), overlay=True,
        )
    # [성취기준N-X] 텍스트 마스킹 — jaja 페이지에만 등장
    src_doc = src_doc_cache[src_pdf]
    src_page_obj = src_doc[src_page]
    clip_rect = fitz.Rect(cx0, cy0, cx1, cy1)
    for blk in src_page_obj.get_text("dict", clip=clip_rect).get("blocks", []):
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "HCRDotum-Bold" not in sp["font"]:
                    continue
                if "성취기준" not in sp["text"]:
                    continue
                bb = sp["bbox"]
                pad = 1.5
                dx0 = tx0 + (bb[0] - cx0) * scale - pad
                dy0 = ty0 + (bb[1] - cy0) * scale - pad
                dx1 = tx0 + (bb[2] - cx0) * scale + pad
                dy1 = ty0 + (bb[3] - cy0) * scale + pad
                page.draw_rect(fitz.Rect(dx0, dy0, dx1, dy1),
                               color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    if not draw_kp_memo:
        return

    # 3) KEY POINT — 본문 바로 아래
    kp_y = ty1 + PROB_GAP * 2
    kp_rect = fitz.Rect(cell_x0, kp_y, cell_x1, kp_y + KP_H)
    page.draw_rect(kp_rect, color=KP_BORDER, fill=KP_BG, width=0.6)
    text_at(page, cell_x0 + 6, kp_y + 8.5, "KEY POINT",
            "aggro", FONT_AGGRO, 7, GOLD)
    page.draw_line((cell_x0 + 62, kp_y + 4),
                   (cell_x0 + 62, kp_y + KP_H - 4),
                   color=KP_BORDER, width=0.5)
    text_at(page, cell_x0 + 67, kp_y + 13, "핵심 한 줄",
            "cafe24", FONT_CAFE24, 7.5, GREY)

    # 4) MEMO 3 줄
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
    problems = json.loads(META_JSON.read_text(encoding="utf-8"))
    print(f"Loaded {len(problems)} problems")
    out = fitz.open()
    src_doc_cache: dict[str, fitz.Document] = {}

    page_breaks: dict[int, int] = {}
    # CELL_POSITIONS: 0=좌상, 1=우상, 2=좌하, 3=우하
    # 수직 2셀 쌍: (0,2) 좌측, (1,3) 우측
    MERGED = "__MERGED__"

    def flush_page(slots, ch_idx):
        ch = CHAPTERS[ch_idx]
        part_no = f"PART {ch_idx + 1:02d}"
        page = out.new_page(width=PAGE_W, height=PAGE_H)
        if ch_idx not in page_breaks:
            page_breaks[ch_idx] = len(out) - 1
        draw_top_header(page, part_no, ch["short"])
        draw_side_bookmark(page, ch["roman"], part_no)
        for c in range(4):
            p = slots[c]
            if p is None or p is MERGED:
                continue
            cx, cy = CELL_POSITIONS[c]
            # 수직 합쳐진 셀 (c=0 또는 1이고 c+2가 MERGED)
            if c < 2 and slots[c + 2] is MERGED:
                span = ROW_H * 2 + ROW_GAP_Y
            else:
                span = ROW_H
            draw_cell(page, cx, cy, p, src_doc_cache, span_h=span)

    slots: list = [None, None, None, None]
    cur_ch = None
    i = 0
    while i < len(problems):
        p = problems[i]
        ch_idx = p["chapter_idx"]

        # 챕터 바뀌면 현재 페이지 flush + 새 챕터
        if cur_ch is not None and ch_idx != cur_ch:
            flush_page(slots, cur_ch)
            slots = [None, None, None, None]
        cur_ch = ch_idx

        sz = cell_size(p)
        placed = False
        if sz == 1:
            for c in range(4):
                if slots[c] is None:
                    slots[c] = p
                    placed = True
                    break
        else:  # sz=2 수직
            for top, bot in [(0, 2), (1, 3)]:
                if slots[top] is None and slots[bot] is None:
                    slots[top] = p
                    slots[bot] = MERGED
                    placed = True
                    break

        if placed:
            i += 1
            # 페이지 다 차면 flush
            if all(s is not None for s in slots):
                flush_page(slots, cur_ch)
                slots = [None, None, None, None]
        else:
            # 페이지 다 차서 못 배치 → flush 후 재시도
            flush_page(slots, cur_ch)
            slots = [None, None, None, None]

    # 마지막 페이지
    if any(s is not None for s in slots):
        flush_page(slots, cur_ch)

    print(f"Chapter page breaks: {page_breaks}")
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n_pages = len(out)
    out.close()
    for d in src_doc_cache.values():
        d.close()
    (OUT_DIR / "problems_page_breaks.json").write_text(
        json.dumps(page_breaks), encoding="utf-8"
    )
    print(f"[OK] {OUT_PDF}  ({n_pages} pages)")


if __name__ == "__main__":
    main()
