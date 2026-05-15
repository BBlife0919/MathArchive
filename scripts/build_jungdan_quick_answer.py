"""중단원 평가(2-2단원) 빠른정답 페이지 — 12 섹션 빠른답 박스를 바둑판식 배치.

각 섹션의 원본 빠른답 박스를 show_pdf_page 로 임베드하고, 로컬 라벨(01,02,…) 위에
글로벌 번호(001,002,…)를 화이트 커버 + 주황 SB 어그로 라벨로 덮어쓰기.
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

from extract_jungdan_problems import (
    SRC_PDF, OUT_DIR, SECTIONS, CHAPTERS,
)

OUT_PDF = OUT_DIR / "quick_answer.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

_aggro = fitz.Font(fontfile=FONT_AGGRO)
_cafe = fitz.Font(fontfile=FONT_CAFE24)

NAVY = (15/255, 25/255, 50/255)
ORANGE = (240/255, 125/255, 35/255)
GOLD = (210/255, 175/255, 110/255)
GREY = (130/255, 140/255, 160/255)
GREY_LIGHT = (200/255, 205/255, 220/255)

PAGE_W = 595.0
PAGE_H = 842.0

LEFT_MARGIN = 28
RIGHT_MARGIN = 28
TOP_MARGIN = 60
BOTTOM_MARGIN = 40
HEADER_Y = 38
HEADER_LINE_Y = 42
COL_GAP = 14
SEC_GAP = 12

COL_W = (PAGE_W - LEFT_MARGIN - RIGHT_MARGIN - COL_GAP) / 2

# 섹션별 빠른답 박스 위치 (src_page, clip x0, y0, x1, y1)
# y 범위는 잡것(중단원 평가 문제 헤더, 페이지 번호) 빼고 라벨만 포함.
QA_REGIONS = {
    0:  (3,  20, 120, 280, 200),  # jaja Ⅱ-2 (rows: 127,145,167,190)
    1:  (64, 25, 78,  280, 175),  # eval 사인 ①
    2:  (66, 25, 78,  280, 175),  # eval 사인 ②
    3:  (8,  20, 102, 280, 175),  # jaja Ⅲ-1 (rows: 110,129,147,165)
    4:  (69, 25, 78,  280, 175),  # eval 등차/등비 ①
    5:  (71, 25, 78,  280, 175),  # eval 등차/등비 ②
    6:  (14, 20, 96,  280, 195),  # jaja Ⅲ-2 (rows: 104,123,140,157,178)
    7:  (73, 25, 78,  280, 175),  # eval 수열의합 ①
    8:  (74, 285, 78, 540, 165),  # eval 수열의합 ② (split L→R)
    9:  (22, 20, 108, 280, 195),  # jaja Ⅲ-3 (rows: 115,138,155,168,180)
    10: (76, 285, 78, 540, 165),  # eval 수귀납 ① (split)
    11: (78, 25, 78,  280, 175),  # eval 수귀납 ②
}


# 라벨 찾기 — 원본 빠른답 박스 안의 로컬 번호 위치
def find_qa_labels(page, clip_rect: fitz.Rect, kind: str) -> list[tuple[fitz.Rect, int]]:
    """빠른답 박스 안의 라벨(로컬 번호) 위치 찾기."""
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
                    # H2gtrE 7pt
                    if "H2gtrE" not in fnt:
                        continue
                    if not (6.5 <= sz <= 7.5):
                        continue
                else:
                    # YJ BONMOKGAK Medium 9pt
                    if "BONMOKGAK" not in fnt:
                        continue
                    if not (8.5 <= sz <= 9.5):
                        continue
                t = sp["text"].strip()
                if not re.fullmatch(r"\d{1,2}", t):
                    continue
                cands.append((tuple(sp["bbox"]), t))

    # jaja 는 1자리 "0N" 페어 + 2자리 단일 span 혼재
    if kind == "jaja":
        singles = [(bb, t) for bb, t in cands if len(t) == 1]
        direct = [(fitz.Rect(*bb), int(t)) for bb, t in cands if len(t) == 2]

        singles.sort(key=lambda x: (round(x[0][1], 1), x[0][0]))
        used = [False] * len(singles)
        out: list[tuple[fitz.Rect, int]] = []
        for i, (bb, t) in enumerate(singles):
            if used[i]:
                continue
            best_j = None
            bx0, by0, bx1, by1 = bb
            for j in range(i + 1, len(singles)):
                if used[j]:
                    continue
                bb2, t2 = singles[j]
                if abs(bb2[1] - by0) > 1.0:
                    continue
                if bb2[0] - bx1 > 2.0:
                    continue
                # 후보 발견 — 병합 후 검증
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


def draw_section_block(page, x0: float, y0: float, sec_idx: int, src_doc):
    """한 섹션의 빠른답 박스를 그린다. 반환: 사용한 세로 길이."""
    sec = SECTIONS[sec_idx]
    src_pg, cx0, cy0, cx1, cy1 = QA_REGIONS[sec_idx]
    src_clip = fitz.Rect(cx0, cy0, cx1, cy1)

    # 섹션 헤더
    global_start = sec["offset"] + 1
    global_end = sec["offset"] + sec["count"]
    header = f"[{global_start:03d} – {global_end:03d}]  {sec['name']}"
    text_at(page, x0, y0 + 10, header,
            "aggro", FONT_AGGRO, 9, ORANGE)
    # 가는 라인
    page.draw_line((x0, y0 + 13), (x0 + COL_W, y0 + 13),
                   color=ORANGE, width=0.5)

    # 빠른답 박스 임베드 (col_w 에 맞게 스케일)
    body_top = y0 + 17
    src_w = cx1 - cx0
    src_h = cy1 - cy0
    scale = COL_W / src_w
    target_h = src_h * scale
    target_w = src_w * scale

    page.show_pdf_page(
        fitz.Rect(x0, body_top, x0 + target_w, body_top + target_h),
        src_doc, src_pg,
        clip=src_clip,
    )

    # 로컬 라벨 검출 → 글로벌 번호로 덮어쓰기
    kind = sec["kind"]
    src_page_obj = src_doc[src_pg]
    labels = find_qa_labels(src_page_obj, src_clip, kind)

    for rect, local in labels:
        # src → dest 변환
        # src_x: rect.x0 → dest_x: x0 + (rect.x0 - cx0) * scale
        dx0 = x0 + (rect.x0 - cx0) * scale
        dy0 = body_top + (rect.y0 - cy0) * scale
        dx1 = x0 + (rect.x1 - cx0) * scale
        dy1 = body_top + (rect.y1 - cy0) * scale
        # 화이트 커버 (살짝 마진)
        pad = 1.0
        cover = fitz.Rect(dx0 - pad, dy0 - pad,
                           max(dx1, dx0 + 18) + pad, dy1 + pad)
        page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
        # 글로벌 번호 (3자리, 주황)
        global_num = sec["offset"] + local
        new_text = f"{global_num:03d}"
        size = 7.0
        new_w = _aggro.text_length(new_text, fontsize=size)
        baseline_y = dy1 - 0.18 * size
        page.insert_text((dx0, baseline_y), new_text,
                         fontname="aggro", fontfile=FONT_AGGRO,
                         fontsize=size, color=ORANGE)

    return (body_top + target_h) - y0


def main():
    src_doc = fitz.open(str(SRC_PDF))
    out = fitz.open()

    # 2-col 채우기
    page = out.new_page(width=PAGE_W, height=PAGE_H)
    draw_header(page)

    col_x = [LEFT_MARGIN, LEFT_MARGIN + COL_W + COL_GAP]
    col_y = [TOP_MARGIN, TOP_MARGIN]
    col_idx = 0

    for sec_idx in range(len(SECTIONS)):
        # 빠른답 박스 예상 높이 (스케일 적용 전 src_h * COL_W/src_w)
        _, cx0, cy0, cx1, cy1 = QA_REGIONS[sec_idx][0:1] + QA_REGIONS[sec_idx][1:]
        src_h = cy1 - cy0
        src_w = cx1 - cx0
        scale = COL_W / src_w
        est_h = 17 + src_h * scale + SEC_GAP

        # 현재 컬럼에 안 들어가면 다른 컬럼 / 새 페이지
        if col_y[col_idx] + est_h > PAGE_H - BOTTOM_MARGIN:
            # 다음 컬럼 시도
            if col_idx == 0:
                col_idx = 1
            else:
                page = out.new_page(width=PAGE_W, height=PAGE_H)
                draw_header(page)
                col_y = [TOP_MARGIN, TOP_MARGIN]
                col_idx = 0
            if col_y[col_idx] + est_h > PAGE_H - BOTTOM_MARGIN:
                # 그래도 안 들어가면 새 페이지 + 첫 컬럼
                page = out.new_page(width=PAGE_W, height=PAGE_H)
                draw_header(page)
                col_y = [TOP_MARGIN, TOP_MARGIN]
                col_idx = 0

        used = draw_section_block(page, col_x[col_idx], col_y[col_idx],
                                  sec_idx, src_doc)
        col_y[col_idx] += used + SEC_GAP

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n = len(out)
    out.close()
    src_doc.close()
    print(f"[OK] {OUT_PDF}  ({n} pages)")


if __name__ == "__main__":
    main()
