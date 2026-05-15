"""SUMMIT POINT: 3개 모의고사 PDF의 문항번호를 연속 라벨링 + 머리말 정리.

- m1.pdf (91문제) → 1~91 (offset 0)
- m2.pdf (88문제) → 92~179 (offset 91)
- m3.pdf (46문제) → 180~225 (offset 179)

문항 라벨:
  - 본문 문제/해설 라벨: NotoSansKR-Bold size 20 (blue) -> 동일 위치 새 번호
  - 빠른정답 grid: NanumGothicBold size 10
  - 체크리스트 grid: NanumGothicBold size 13

머리말:
  - 첫 페이지(page 0): 상단 메타 헤더(y < 190) 화이트 덮기 + 단원명 삽입
  - 그 외 페이지: 러닝 헤더(y < 90) 화이트 덮기
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"
OUT_DIR.mkdir(parents=True, exist_ok=True)

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

# 문항 번호 색상 (주황)
LABEL_COLOR = (240 / 255, 125 / 255, 35 / 255)
GRID_COLOR = (240 / 255, 125 / 255, 35 / 255)

# 사용 가능한 문항 번호 폰트 (SB 어그로 M)
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
LABEL_FONT_NAME = "aggro"
LABEL_FONT_FILE = FONT_AGGRO

HEADER_FONT_NAME = "cafe24"
HEADER_FONT_FILE = FONT_CAFE24

# (src_path, prefix, chapter_title, chapter_subtitle)
SOURCES = [
    ("/tmp/m1.pdf", "A",
     "I. 여러가지 방정식 ~ 여러가지 부등식",
     "EQUATIONS & INEQUALITIES"),
    ("/tmp/m2.pdf", "B",
     "II. 순열·조합",
     "PERMUTATION & COMBINATION"),
    ("/tmp/m3.pdf", "C",
     "III. 행렬",
     "MATRIX"),
]


_label_font = fitz.Font(fontfile=LABEL_FONT_FILE)
_header_font = fitz.Font(fontfile=HEADER_FONT_FILE)


def _insert_text_at_bbox(page, bbox, text, fontname, fontfile, size, color,
                         font_obj=None, baseline_align="big"):
    """Replace label at bbox with new text.

    - 좌측 컬럼 (x0<200): 우측 정렬 — x1 에 우측 끝 고정 (왼쪽으로 확장)
    - 우측 컬럼 (x0>=200, 해설 2단 페이지): 좌측 정렬 — x0 에 좌측 끝 고정 (오른쪽으로 확장)
      → 단 경계선 침범 방지
    """
    x0, y0, x1, y1 = bbox
    fobj = font_obj or _label_font
    pad = 1.0
    new_w = fobj.text_length(text, fontsize=size)

    is_right_col = x0 >= 200

    if is_right_col:
        # 우측 컬럼: 단 경계선 침범 방지. 새 라벨을 단 구분선(x≈296) 우측 시작점 부근(x=302) 에 좌측 정렬.
        # 라벨이 길어서 우측의 정답/해설 텍스트 영역으로 살짝 뻗어 들어가더라도 둠 (가독성 확보).
        new_x = max(x0, 302.0)
        cover_x0 = new_x - pad
        cover_x1 = max(x1, new_x + new_w) + pad
    else:
        # 좌측 컬럼: 우측 정렬 (현행 유지)
        new_x = x1 - new_w
        cover_x0 = min(x0, x1 - new_w) - pad
        cover_x1 = x1 + pad

    rect = fitz.Rect(cover_x0, y0 - pad, cover_x1, y1 + pad)
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    size_used = size
    if baseline_align == "big":
        new_y = y1 - 0.18 * size_used
    else:
        new_y = y1 - 0.10 * size_used
    page.insert_text((new_x, new_y), text, fontname=fontname, fontfile=fontfile,
                     fontsize=size_used, color=color)


def _strip_header(page, y_bottom: float):
    """White-rect across the top of the page up to y_bottom (PDF coords)."""
    rect = fitz.Rect(0, 0, page.rect.width, y_bottom)
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)


def _strip_footer_page_number(page):
    """White-rect the bottom-center page number ('76|N') area."""
    rect = fitz.Rect(260, 800, 340, 838)
    page.draw_rect(rect, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)


def _add_first_page_header(page, chapter_title: str, eng_subtitle: str):
    """Add chapter-name heading at top of page after stripping original header."""
    page_w = page.rect.width
    color_navy = (15/255, 25/255, 50/255)
    color_gold = (210/255, 175/255, 110/255)

    # 영문 부제 (작게, 상단)
    eng_size = 10
    eng_w = _header_font.text_length(eng_subtitle, fontsize=eng_size)
    page.insert_text(((page_w - eng_w) / 2, 65), eng_subtitle,
                     fontname=HEADER_FONT_NAME, fontfile=HEADER_FONT_FILE,
                     fontsize=eng_size, color=color_gold)

    # 단원명 (큰 한글)
    title_size = 20
    tw = _header_font.text_length(chapter_title, fontsize=title_size)
    while tw > page_w - 120 and title_size > 12:
        title_size -= 1
        tw = _header_font.text_length(chapter_title, fontsize=title_size)
    page.insert_text(((page_w - tw) / 2, 105), chapter_title,
                     fontname=HEADER_FONT_NAME, fontfile=HEADER_FONT_FILE,
                     fontsize=title_size, color=color_navy)

    # 골드 가로 라인
    line_y = 135
    page.draw_line((page_w / 2 - 60, line_y), (page_w / 2 + 60, line_y),
                   color=color_gold, width=1.5)
    # 양 끝 점
    page.draw_circle((page_w / 2 - 70, line_y), 2, color=color_gold, fill=color_gold)
    page.draw_circle((page_w / 2 + 70, line_y), 2, color=color_gold, fill=color_gold)


def is_question_label_span(span) -> tuple[bool, str]:
    """Return (is_label, kind) where kind in {'big','grid_quick','grid_check'}."""
    t = span['text'].strip()
    font = span['font']
    size = span['size']
    if not re.fullmatch(r"\d{1,3}", t):
        return False, ""
    if 'NotoSansKR-Bold' in font and 19.5 <= size <= 20.5:
        return True, 'big'
    if 'NanumGothicBold' in font and 9.5 <= size <= 10.5:
        return True, 'grid_quick'
    if 'NanumGothicBold' in font and 12.5 <= size <= 13.5:
        return True, 'grid_check'
    return False, ""


def process_pdf(src: str, prefix: str, chapter_title: str, eng_subtitle: str) -> fitz.Document:
    doc = fitz.open(src)
    for pi, page in enumerate(doc):
        # 1) Collect question label spans
        d = page.get_text("dict")
        labels = []   # (bbox, old_num_text, kind)
        for blk in d['blocks']:
            if blk.get('type') != 0:
                continue
            for line in blk['lines']:
                for sp in line['spans']:
                    ok, kind = is_question_label_span(sp)
                    if ok:
                        labels.append((tuple(sp['bbox']), sp['text'].strip(), kind))

        # 2) Replace each label — A·01, A·02, ... 형식
        for bbox, old_text, kind in labels:
            old_num = int(old_text)
            new_text = f"{prefix}·{old_num:02d}"
            if kind == 'big':
                size = 19
                color = LABEL_COLOR
                baseline = "big"
            elif kind == 'grid_quick':
                size = 9
                color = GRID_COLOR
                baseline = "small"
            elif kind == 'grid_check':
                size = 12
                color = GRID_COLOR
                baseline = "small"
            else:
                continue
            _insert_text_at_bbox(page, bbox, new_text, LABEL_FONT_NAME, LABEL_FONT_FILE,
                                 size, color, baseline_align=baseline)

        # 3) Strip header — section-start pages have full meta block
        page_text = page.get_text()
        is_section_start = ('QR을 스캔해' in page_text) or ('빠른정답' in page_text)
        if pi == 0:
            _strip_header(page, y_bottom=185)
            _add_first_page_header(page, chapter_title, eng_subtitle)
        elif is_section_start:
            _strip_header(page, y_bottom=185)
        else:
            _strip_header(page, y_bottom=90)

        # 4) Strip footer page number (will be re-added globally during merge)
        _strip_footer_page_number(page)

    return doc


def main():
    out_docs = []
    for src, prefix, title, eng in SOURCES:
        print(f"Processing {src} (prefix={prefix})...")
        d = process_pdf(src, prefix, title, eng)
        out_path = OUT_DIR / f"renum_{Path(src).stem}.pdf"
        d.save(str(out_path), garbage=4, deflate=True)
        d.close()
        print(f"  saved {out_path}")
        out_docs.append(out_path)
    print("Done.")


if __name__ == "__main__":
    main()
