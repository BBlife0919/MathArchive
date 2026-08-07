"""중단원 평가(2-2단원) 빠른정답 — row 단위 세로 1열 배열.

각 줄 = 원본 빠른답 박스의 한 row(라벨 5개 가량) 를 src 그대로 임베드 (scale 2.0).
로컬 라벨(01,02,…)을 글로벌 번호(001~169)로 덮어쓰기.

답 단위로 src 클립을 분리하지 않는 이유: 원본 PDF 에서 분수 답의 분모가
다음 row 라벨과 같은 y 좌표 영역에 그려져 있어, 답 단위 분리 시 분모가
잘림. row 단위 임베드만이 답을 100% 보존하는 방법.
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

from extract_jungdan_problems import (
    SRC_PDF, OUT_DIR, SECTIONS,
)

OUT_PDF = OUT_DIR / "quick_answer.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

_aggro = fitz.Font(fontfile=FONT_AGGRO)
_cafe = fitz.Font(fontfile=FONT_CAFE24)

NAVY = (15/255, 25/255, 50/255)
ORANGE = (240/255, 125/255, 35/255)
GREY = (130/255, 140/255, 160/255)
GREY_LIGHT = (200/255, 205/255, 220/255)
GREY_LINE = (180/255, 188/255, 205/255)

PAGE_W = 595.0
PAGE_H = 842.0

LEFT_MARGIN = 24
RIGHT_MARGIN = 24
TOP_MARGIN = 56
BOTTOM_MARGIN = 36
HEADER_Y = 38
HEADER_LINE_Y = 42
ROW_GAP_Y = 6

# 박스 외곽 (src_page, x0, y0, x1, y1)
QA_REGIONS = {
    0:  (3,  20, 120, 280, 210),
    1:  (64, 25, 78,  280, 215),
    2:  (66, 25, 78,  280, 215),
    3:  (8,  20, 102, 280, 205),
    4:  (69, 25, 78,  280, 215),
    5:  (71, 25, 78,  280, 215),
    6:  (14, 20, 96,  280, 225),
    7:  (73, 25, 78,  280, 210),
    8:  (74, 285, 78, 540, 200),
    9:  (22, 20, 108, 280, 225),
    10: (76, 285, 78, 540, 200),
    11: (78, 25, 78,  280, 210),
}


def find_qa_labels(page, clip_rect: fitz.Rect, kind: str) -> list[tuple[fitz.Rect, int]]:
    d = page.get_text("dict", clip=clip_rect)
    cands = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                fnt = sp["font"]
                sz = sp["size"]
                if kind == "jaja":
                    if "H2gtrE" not in fnt: continue
                    if not (6.5 <= sz <= 7.5): continue
                else:
                    if "BONMOKGAK" not in fnt: continue
                    if not (8.5 <= sz <= 9.5): continue
                t = sp["text"].strip()
                if not re.fullmatch(r"\d{1,2}", t): continue
                cands.append((tuple(sp["bbox"]), t))

    if kind == "jaja":
        singles = [(bb, t) for bb, t in cands if len(t) == 1]
        direct = [(fitz.Rect(*bb), int(t)) for bb, t in cands if len(t) == 2]
        singles.sort(key=lambda x: (round(x[0][1], 1), x[0][0]))
        used = [False] * len(singles)
        out: list[tuple[fitz.Rect, int]] = []
        for i, (bb, t) in enumerate(singles):
            if used[i]: continue
            best_j = None
            bx0, by0, bx1, by1 = bb
            for j in range(i + 1, len(singles)):
                if used[j]: continue
                bb2, t2 = singles[j]
                if abs(bb2[1] - by0) > 1.0: continue
                if bb2[0] - bx1 > 2.0: continue
                if re.fullmatch(r"\d\d", t + t2):
                    best_j = j
                    break
            used[i] = True
            if best_j is not None:
                bb2, t2 = singles[best_j]
                merged = t + t2
                used[best_j] = True
                rect = fitz.Rect(bx0, min(by0, bb2[1]),
                                 bb2[2], max(by1, bb2[3]))
            else:
                merged = t
                rect = fitz.Rect(bx0, by0, bx1, by1)
            n = int(merged)
            if 1 <= n <= 30:
                out.append((rect, n))
        out.extend(direct)
        return out
    else:
        out = []
        for bb, t in cands:
            n = int(t)
            if 1 <= n <= 30:
                out.append((fitz.Rect(*bb), n))
        return out


def collect_rows(src_doc) -> list[dict]:
    """각 섹션을 row 단위로 쪼개기."""
    rows = []
    for sec_idx, sec in enumerate(SECTIONS):
        src_pg, cx0, cy0, cx1, cy1 = QA_REGIONS[sec_idx]
        clip_rect = fitz.Rect(cx0, cy0, cx1, cy1)
        labels = find_qa_labels(src_doc[src_pg], clip_rect, sec["kind"])
        if not labels:
            continue

        labels.sort(key=lambda x: (round(x[0].y0, 0), x[0].x0))
        groups: list[dict] = []
        for lr, n in labels:
            placed = False
            for g in groups:
                if abs(g["y"] - lr.y0) < 4.0:
                    g["items"].append((lr, n))
                    placed = True
                    break
            if not placed:
                groups.append({"y": lr.y0, "items": [(lr, n)]})
        groups.sort(key=lambda g: g["y"])
        for i, g in enumerate(groups):
            g["items"].sort(key=lambda x: x[0].x0)
            y_top = g["y"] - 3.0
            if i + 1 < len(groups):
                y_bot = groups[i + 1]["y"] - 3.0
            else:
                y_bot = cy1
            # 분수 분모 포함 여유
            y_bot = min(y_bot + 8.0, cy1)
            rows.append({
                "sec_idx": sec_idx,
                "src_pg": src_pg,
                "src_clip": (cx0, y_top, cx1, y_bot),
                "items": list(g["items"]),
                "offset": sec["offset"],
            })
    return rows


def text_at(page, x, y, text, fontname, fontfile, size, color):
    page.insert_text((x, y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size, color=color)


def draw_header(page):
    text_at(page, LEFT_MARGIN, HEADER_Y,
            "TEXTBOOK POINT · Q U I C K   A N S W E R",
            "aggro", FONT_AGGRO, 8, NAVY)
    right = "빠른정답"
    tw = _cafe.text_length(right, fontsize=8)
    text_at(page, PAGE_W - RIGHT_MARGIN - tw, HEADER_Y, right,
            "cafe24", FONT_CAFE24, 8, NAVY)
    page.draw_line((LEFT_MARGIN, HEADER_LINE_Y),
                   (PAGE_W - RIGHT_MARGIN, HEADER_LINE_Y),
                   color=GREY_LIGHT, width=0.6)


def main():
    src_doc = fitz.open(str(SRC_PDF))
    rows = collect_rows(src_doc)
    print(f"수집된 row: {len(rows)}")
    out = fitz.open()

    page = out.new_page(width=PAGE_W, height=PAGE_H)
    draw_header(page)
    cur_y = TOP_MARGIN
    page_bot = PAGE_H - BOTTOM_MARGIN

    SCALE = 2.0
    avail_w = PAGE_W - LEFT_MARGIN - RIGHT_MARGIN

    for row in rows:
        sx0, sy0, sx1, sy1 = row["src_clip"]
        src_w = sx1 - sx0
        src_h = sy1 - sy0
        # 페이지 폭에 맞추되, 최대 scale 2.0
        scale = min(SCALE, avail_w / src_w)
        tw = src_w * scale
        th = src_h * scale
        tx = (PAGE_W - tw) / 2

        if cur_y + th > page_bot:
            page = out.new_page(width=PAGE_W, height=PAGE_H)
            draw_header(page)
            cur_y = TOP_MARGIN

        page.show_pdf_page(
            fitz.Rect(tx, cur_y, tx + tw, cur_y + th),
            src_doc, row["src_pg"],
            clip=fitz.Rect(sx0, sy0, sx1, sy1),
        )

        # 로컬 라벨 → 글로벌 번호
        for lr, local in row["items"]:
            dx0 = tx + (lr.x0 - sx0) * scale
            dy0 = cur_y + (lr.y0 - sy0) * scale
            dx1 = tx + (lr.x1 - sx0) * scale
            dy1 = cur_y + (lr.y1 - sy0) * scale
            cover_w = max(dx1 - dx0, 16)
            pad = 1.5
            cover = fitz.Rect(dx0 - pad, dy0 - pad,
                              dx0 + cover_w + pad, dy1 + pad)
            page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
            global_num = row["offset"] + local
            new_text = f"{global_num:03d}"
            size = 10.0
            baseline = dy1 - 0.15 * size
            page.insert_text((dx0, baseline), new_text,
                             fontname="aggro", fontfile=FONT_AGGRO,
                             fontsize=size, color=ORANGE)

        cur_y += th + ROW_GAP_Y

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n = len(out)
    out.close()
    src_doc.close()
    print(f"[OK] {OUT_PDF}  ({n} pages, row-stack scale {SCALE}x)")


if __name__ == "__main__":
    main()
