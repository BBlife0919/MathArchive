"""SUMMIT POINT: 한 페이지에 2문제씩 (2단 컬럼) 배치 + 메모란 + 풀이기록 체크 + Key Point.

각 컬럼 구조:
  [상단 메타: 라벨 + 출처]
  [문제 본문 (원본 PDF 클립)]
  [Key Point 박스 (1줄)]
  [풀이 메모란 (가로 라인 N줄)]
  [풀이기록 체크박스: 1차 ☐ / 2차 ☐ / 3차 ☐]
"""
from __future__ import annotations
import json
from pathlib import Path

import re
import fitz


# OCR 보정: "년" 이 "14"/"1" 로 오인식 되는 케이스 흡수
_SRC_PAT = re.compile(r"(\d{4})(?:년|14|1)?\s*(\d+월)\s+(.+?)\s+(\d+번)(?:/(\d+점))?")


def parse_source(text: str) -> dict | None:
    """[2025년 9월 고1 18번/4점] → {'year','month_grade','num','score'}.

    OCR 잔여 노이즈([|, 년→14 등) 가 있어도 패턴이 보이면 추출.
    """
    if not text:
        return None
    # \xa0 → 공백 으로 먼저 정규화
    cleaned = text.replace('\xa0', ' ')
    m = _SRC_PAT.search(cleaned)
    if not m:
        return None
    year, month, grade, num, score = m.groups()
    grade = grade.strip()
    return {
        'year': f"{year}년",
        'month_grade': f"{month} {grade}",
        'num': num,
        'score': f"[{score}]" if score else "",
    }

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"
META_JSON = OUT_DIR / "problems_meta.json"
OUT_PDF = OUT_DIR / "problems_2col.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
LOGO_GOLD = OUT_DIR / "eum_logo_gold.png"

_aggro = fitz.Font(fontfile=FONT_AGGRO)
_paper = fitz.Font(fontfile=FONT_PAPER_BLACK)
_cafe = fitz.Font(fontfile=FONT_CAFE24)

# 색상
NAVY = (15/255, 25/255, 50/255)
NAVY_BAR = (35/255, 55/255, 100/255)
GOLD = (210/255, 175/255, 110/255)
GOLD_LIGHT = (240/255, 205/255, 135/255)
ORANGE = (240/255, 125/255, 35/255)
GREY = (130/255, 140/255, 160/255)
GREY_LIGHT = (200/255, 205/255, 220/255)
GREY_LINE = (170/255, 178/255, 195/255)
SRC_GRAY = (90/255, 95/255, 110/255)
KP_BG = (250/255, 248/255, 240/255)   # KP box pale cream
KP_BORDER = (230/255, 200/255, 140/255)  # gold border

# A4 (포인트)
PAGE_W = 595.0
PAGE_H = 842.0

# 레이아웃
HEADER_Y = 38           # 상단 헤더 라인 baseline (텍스트)
HEADER_LINE_Y = 42      # 헤더 가로 라인
BOOKMARK_X_LEFT = 567   # 책갈피 박스 left edge
BOOKMARK_X_RIGHT = 587

LEFT_MARGIN = 28
RIGHT_MARGIN = 28
TOP_MARGIN = 58         # 헤더 아래
BOTTOM_MARGIN = 50
COL_GAP = 18

# 컬럼당 가용 가로
COL_W = (PAGE_W - LEFT_MARGIN - RIGHT_MARGIN - COL_GAP) / 2  # ≈ 260pt
COL_RIGHT_X = LEFT_MARGIN + COL_W + COL_GAP

# 컬럼당 가용 세로
COL_H = PAGE_H - TOP_MARGIN - BOTTOM_MARGIN  # ≈ 734pt

# 컬럼 내부 슬롯 높이
KP_H = 28                # Key Point 박스
MEMO_LINES = 6           # 메모 라인 개수
MEMO_LINE_GAP = 16
MEMO_H = MEMO_LINE_GAP * MEMO_LINES + 8

# 문제 본문 슬롯 (가변 — 나머지)
GAPS = 24
PROB_MAX_H = COL_H - KP_H - MEMO_H - GAPS


def text_at(page, x, y, text, font_name, font_file, size, color):
    page.insert_text((x, y), text, fontname=font_name, fontfile=font_file,
                     fontsize=size, color=color)


def text_right(page, x_right, y, text, fobj, font_name, font_file, size, color):
    tw = fobj.text_length(text, fontsize=size)
    page.insert_text((x_right - tw, y), text, fontname=font_name, fontfile=font_file,
                     fontsize=size, color=color)


def draw_top_header(page, part_no, chapter_short):
    """상단 헤더: SUMMIT POINT · 챕터명."""
    text_at(page, LEFT_MARGIN, HEADER_Y, "SUMMIT POINT",
            "aggro", FONT_AGGRO, 8, NAVY)
    right_text = f"{part_no}  ·  {chapter_short}"
    tw = _cafe.text_length(right_text, fontsize=8)
    text_at(page, PAGE_W - RIGHT_MARGIN - tw, HEADER_Y, right_text,
            "cafe24", FONT_CAFE24, 8, NAVY)
    page.draw_line((LEFT_MARGIN, HEADER_LINE_Y), (PAGE_W - RIGHT_MARGIN, HEADER_LINE_Y),
                   color=GREY_LIGHT, width=0.6)


def draw_side_bookmark(page, prefix, part_no):
    """우측 단원 책갈피."""
    bk_x0 = PAGE_W - 28
    bk_x1 = PAGE_W - 8
    # 상단: PART 박스 (네이비)
    page.draw_rect(fitz.Rect(bk_x0, 90, bk_x1, 230),
                   color=NAVY, fill=NAVY, overlay=True)
    part_text = part_no.replace(" ", "  ")
    page.insert_text((bk_x0 + 8, 220),
                     part_text,
                     fontname="aggro", fontfile=FONT_AGGRO,
                     fontsize=9, color=GOLD_LIGHT, rotate=90)
    # 중간: 챕터 글자 박스 (골드)
    page.draw_rect(fitz.Rect(bk_x0, 238, bk_x1, 308),
                   color=GOLD, fill=GOLD, overlay=True)
    fsize = 26
    tw = _paper.text_length(prefix, fontsize=fsize)
    cx = (bk_x0 + bk_x1) / 2
    page.insert_text((cx - tw/2, 280),
                     prefix,
                     fontname="paperblack", fontfile=FONT_PAPER_BLACK,
                     fontsize=fsize, color=(1, 1, 1))
    # 하단 골드 라인
    page.draw_line((bk_x0 + 6, 320), (bk_x0 + 6, PAGE_H - 70),
                   color=GOLD_LIGHT, width=1.2)


def draw_problem_block(page, col_x0, col_y0, prob_meta, src_doc_cache):
    """한 컬럼 (col_x0, col_y0 = 상단 좌측 시작점) 에 한 문제 + 부속을 그린다."""
    label = prob_meta['label']
    source = prob_meta['source_text']
    src_pdf = prob_meta['src_pdf']
    src_page = prob_meta['src_page']
    clip = prob_meta['clip']

    col_x1 = col_x0 + COL_W

    # 레이아웃 상수
    LEFT_BLOCK_W = 58           # 메타(라벨+체크박스) 폭
    LEFT_BLOCK_GAP = 4          # 메타와 문제 사이 여백
    SRC_BASELINE_OFFSET = 6     # 컬럼 top 에서 출처 baseline 까지
    PROB_TOP_OFFSET = 10        # 컬럼 top 에서 문제 본문 시작까지 (라벨 visual top 과 일치)

    meta_x = col_x0
    img_area_x0 = col_x0 + LEFT_BLOCK_W + LEFT_BLOCK_GAP
    img_area_w = col_x1 - img_area_x0

    # 0) 출처: 문제 첫줄 바로 위 (한 줄, 살짝)
    src_parts = parse_source(source) if source else None
    if src_parts:
        src_str = " ".join(filter(None, [
            src_parts['year'], src_parts['month_grade'],
            src_parts['num'], src_parts['score']
        ]))
    elif source:
        src_str = source.replace('\xa0', ' ').strip('[]')
    else:
        src_str = ""
    if src_str:
        text_at(page, img_area_x0, col_y0 + SRC_BASELINE_OFFSET, src_str,
                "cafe24", FONT_CAFE24, 7.8, SRC_GRAY)

    # 1) 라벨 (좌측 상단, 문제 첫줄과 평행)
    # 18pt SB 어그로 label: visual top ≈ baseline - 14
    # 문제 본문 top = col_y0 + PROB_TOP_OFFSET
    # 라벨 visual top 도 같은 위치 → baseline = col_y0 + PROB_TOP_OFFSET + 14
    label_baseline = col_y0 + PROB_TOP_OFFSET + 14
    text_at(page, meta_x, label_baseline, label,
            "aggro", FONT_AGGRO, 18, ORANGE)

    # 2) 1차/2차/3차 체크박스 (라벨 바로 밑)
    box_size = 6
    box_h = 7
    row1_y_text = label_baseline + 13   # 라벨 baseline 으로부터 13pt 아래 text baseline
    row1_y_box_top = row1_y_text - 6
    bx = meta_x
    for lbl_text in ["1차", "2차", "3차"]:
        page.draw_rect(fitz.Rect(bx, row1_y_box_top, bx + box_size, row1_y_box_top + box_h),
                       color=GREY_LINE, width=0.5)
        text_at(page, bx + box_size + 2, row1_y_text, lbl_text,
                "cafe24", FONT_CAFE24, 6.5, NAVY)
        bx += 18   # 1차☐ 다음 18pt 간격

    # 3) O/X 체크박스 (1차줄 바로 밑)
    row2_y_text = row1_y_text + 12
    row2_y_box_top = row2_y_text - 6
    bx = meta_x
    for lbl_text in ["O", "X"]:
        page.draw_rect(fitz.Rect(bx, row2_y_box_top, bx + box_size, row2_y_box_top + box_h),
                       color=GREY_LINE, width=0.5)
        text_at(page, bx + box_size + 2, row2_y_text, lbl_text,
                "cafe24", FONT_CAFE24, 6.5, NAVY)
        bx += 16

    # 4) 문제 본문 (우측, 라벨 visual top 과 평행 — 출처는 그 위에 그렸음)
    prob_top = col_y0 + PROB_TOP_OFFSET
    cx0, cy0, cx1, cy1 = clip
    src_w = cx1 - cx0
    src_h = cy1 - cy0
    scale = img_area_w / src_w
    target_h = src_h * scale
    if target_h > PROB_MAX_H:
        scale = PROB_MAX_H / src_h
    target_w = src_w * scale
    target_h = src_h * scale
    tx0 = img_area_x0
    ty0 = prob_top
    tx1 = tx0 + target_w
    ty1 = ty0 + target_h

    # show_pdf_page 로 임베드
    if src_pdf not in src_doc_cache:
        src_doc_cache[src_pdf] = fitz.open(src_pdf)
    src_doc = src_doc_cache[src_pdf]
    page.show_pdf_page(
        fitz.Rect(tx0, ty0, tx1, ty1),
        src_doc, src_page,
        clip=fitz.Rect(cx0, cy0, cx1, cy1)
    )

    # 5) Key Point 박스 (하단)
    bottom_block_y = col_y0 + COL_H - KP_H - MEMO_H - 16
    kp_y = bottom_block_y
    kp_rect = fitz.Rect(col_x0, kp_y, col_x1, kp_y + KP_H)
    page.draw_rect(kp_rect, color=KP_BORDER, fill=KP_BG, width=0.8)
    # 라벨
    text_at(page, col_x0 + 8, kp_y + 11, "KEY POINT",
            "aggro", FONT_AGGRO, 8, GOLD)
    # 가는 세로 분리선
    page.draw_line((col_x0 + 78, kp_y + 5), (col_x0 + 78, kp_y + KP_H - 5),
                   color=KP_BORDER, width=0.6)
    # KEY POINT 작성 가이드 (회색, 옅게)
    text_at(page, col_x0 + 85, kp_y + 17, "이 문제 핵심 한 줄로 정리",
            "cafe24", FONT_CAFE24, 8.5, GREY)

    # 4) 풀이 메모란 (가로 라인)
    memo_top = kp_y + KP_H + 8
    text_at(page, col_x0, memo_top + 8, "MEMO",
            "aggro", FONT_AGGRO, 7, GREY)
    line_start_y = memo_top + 18
    for i in range(MEMO_LINES):
        ly = line_start_y + i * MEMO_LINE_GAP
        page.draw_line((col_x0, ly), (col_x1, ly),
                       color=GREY_LINE, width=0.4)

    # (풀이 기록 체크박스는 라벨 밑으로 이동했으므로 여기서는 제거)


# 챕터별 prefix → (PART label, 단원 짧은 이름)
CHAPTER_META = {
    'A': ("PART 1", "여러가지 방정식·부등식"),
    'B': ("PART 2", "순열·조합"),
    'C': ("PART 3", "행렬"),
}


def main():
    problems = json.loads(META_JSON.read_text(encoding='utf-8'))
    print(f"Loaded {len(problems)} problems")

    out = fitz.open()
    src_doc_cache: dict[str, fitz.Document] = {}

    # 2문제씩 페이지에 배치 — 챕터 경계에서는 우측 컬럼 비우고 다음 챕터는 새 페이지부터
    i = 0
    page_breaks_by_chapter = {}   # prefix → first page index
    while i < len(problems):
        page = out.new_page(width=PAGE_W, height=PAGE_H)
        left_prob = problems[i]
        prefix = left_prob['label'].split('·')[0]
        part_no, chapter_short = CHAPTER_META[prefix]
        if prefix not in page_breaks_by_chapter:
            page_breaks_by_chapter[prefix] = len(out) - 1   # current page index

        # 상단 헤더 + 책갈피
        draw_top_header(page, part_no, chapter_short)
        draw_side_bookmark(page, prefix, part_no)

        # 좌측 컬럼
        draw_problem_block(page, LEFT_MARGIN, TOP_MARGIN, left_prob, src_doc_cache)

        # 우측 컬럼
        if i + 1 < len(problems):
            right_prob = problems[i + 1]
            right_prefix = right_prob['label'].split('·')[0]
            if right_prefix == prefix:
                draw_problem_block(page, COL_RIGHT_X, TOP_MARGIN, right_prob, src_doc_cache)
                i += 2
            else:
                # 챕터 경계: 우측 비우고 다음 페이지에서 새 챕터 시작
                i += 1
        else:
            i += 1

    print(f"Page breaks by chapter: {page_breaks_by_chapter}")

    n_pages = len(out)
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    out.close()
    for d in src_doc_cache.values():
        d.close()
    print(f"[OK] {OUT_PDF}  ({n_pages} pages)")


if __name__ == "__main__":
    main()
