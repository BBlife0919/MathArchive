"""SUMMIT POINT: 통합 빠른정답 페이지. A·01 ~ C·46 (총 225개) 한 페이지 그리드.

각 셀: 라벨 (왼쪽, 주황 굵게) + 답 (오른쪽, 원본 PDF 클립).
배경: 체커보드 (페일블루 / 화이트 교차).
"""
from __future__ import annotations
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"
OUT_PDF = OUT_DIR / "quick_answer.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")

_aggro = fitz.Font(fontfile=FONT_AGGRO)

# 색상
NAVY = (15/255, 25/255, 50/255)
GOLD = (210/255, 175/255, 110/255)
GOLD_LIGHT = (240/255, 205/255, 135/255)
ORANGE = (240/255, 125/255, 35/255)
GREY = (130/255, 140/255, 160/255)
GREY_LINE = (190/255, 200/255, 215/255)
PALE_BLUE = (235/255, 242/255, 252/255)
PALE_BLUE_DEEP = (218/255, 228/255, 246/255)
WHITE = (1, 1, 1)
NAVY_PALE = (240/255, 245/255, 252/255)

PAGE_W = 595.0
PAGE_H = 842.0

# 원본 빠른정답 페이지 정보 (라벨 위치 + 답 위치)
# 각 라벨 옆에 답이 위치 — 라벨 bbox.x1 + ~2pt 부터 ~+22pt 까지 답 셀
SOURCES = [
    ('/Users/youngwoolee/MathDB/output/summit_point/renum_m1.pdf', 38, 'A', 91),
    ('/Users/youngwoolee/MathDB/output/summit_point/renum_m2.pdf', 46, 'B', 88),
    ('/Users/youngwoolee/MathDB/output/summit_point/renum_m3.pdf', 19, 'C', 46),
]


def collect_answer_clips() -> list[dict]:
    """원본 빠른정답 페이지에서 각 답의 위치 추출."""
    items = []  # {'prefix': 'A', 'num': 1, 'src_pdf': ..., 'src_page': ..., 'clip': (...)}
    for src_pdf, page_idx, prefix, n in SOURCES:
        doc = fitz.open(src_pdf)
        page = doc[page_idx]
        d = page.get_text("dict")
        # 새 라벨은 SB 어그로 (renum_m1.pdf 등에서 텍스트 'A·01' 등)
        labels = []
        for blk in d['blocks']:
            if blk.get('type') != 0: continue
            for line in blk['lines']:
                for sp in line['spans']:
                    if sp['font'] == 'OTSBAggroM' and sp['size'] <= 12:
                        t = sp['text'].strip()
                        if t.startswith(prefix + "·"):
                            try:
                                num = int(t.split('·')[1])
                                labels.append((num, sp['bbox']))
                            except ValueError:
                                pass
        labels.sort(key=lambda x: x[0])
        for num, bbox in labels:
            x0, y0, x1, y1 = bbox
            # 답 영역: 라벨 오른쪽 (라벨 폭만큼 + 살짝)
            clip = (x1 - 1, y0 - 2, x1 + 22, y1 + 2)
            items.append({
                'prefix': prefix,
                'num': num,
                'label': f"{prefix}·{num:02d}",
                'src_pdf': src_pdf,
                'src_page': page_idx,
                'clip': clip,
            })
        doc.close()
    return items


def main():
    items = collect_answer_clips()
    print(f"Collected {len(items)} answer cells")

    out = fitz.open()
    page = out.new_page(width=PAGE_W, height=PAGE_H)

    # ── 상단 헤더 ─────────────────────────────────
    # 네이비 가로 띠
    title_band_y0 = 50
    title_band_y1 = 110
    page.draw_rect(fitz.Rect(40, title_band_y0, PAGE_W - 40, title_band_y1),
                   color=NAVY, fill=NAVY, overlay=True)
    # 골드 사이드 액센트
    page.draw_rect(fitz.Rect(40, title_band_y0, 46, title_band_y1),
                   color=GOLD, fill=GOLD, overlay=True)
    page.draw_rect(fitz.Rect(PAGE_W - 46, title_band_y0, PAGE_W - 40, title_band_y1),
                   color=GOLD, fill=GOLD, overlay=True)

    # 타이틀 텍스트
    title = "빠른정답"
    f_title = 28
    tw = _aggro.text_length(title, fontsize=f_title)
    page.insert_text(((PAGE_W - tw) / 2, 88), title,
                     fontname="aggro", fontfile=FONT_AGGRO,
                     fontsize=f_title, color=GOLD_LIGHT)
    # 영문 부제 — 타이틀 양 옆에 작게
    sub = "F A S T   A N S W E R   K E Y"
    f_sub = 9
    tws = _aggro.text_length(sub, fontsize=f_sub)
    page.insert_text(((PAGE_W - tws) / 2, 102), sub,
                     fontname="aggro", fontfile=FONT_AGGRO,
                     fontsize=f_sub, color=GOLD)

    # ── 그리드: 5 columns × ~45 rows, 225 cells ─────────────
    grid_x0 = 40
    grid_x1 = PAGE_W - 40
    grid_y0 = title_band_y1 + 18
    grid_y1 = PAGE_H - 50
    cols = 5
    rows = (len(items) + cols - 1) // cols   # ceil division → 45
    grid_w = grid_x1 - grid_x0
    grid_h = grid_y1 - grid_y0
    cell_w = grid_w / cols
    cell_h = grid_h / rows

    # 라벨/답 셀 비율 (라벨 영역 60% / 답 영역 40%)
    LBL_FRAC = 0.62

    src_doc_cache = {}

    for idx, item in enumerate(items):
        row = idx // cols
        col = idx % cols
        cell_x0 = grid_x0 + col * cell_w
        cell_y0 = grid_y0 + row * cell_h
        cell_x1 = cell_x0 + cell_w
        cell_y1 = cell_y0 + cell_h

        # 체커보드 배경: (row+col) % 2 == 0 → 페일블루
        is_alt = (row + col) % 2 == 0
        bg = PALE_BLUE if is_alt else WHITE
        page.draw_rect(fitz.Rect(cell_x0, cell_y0, cell_x1, cell_y1),
                       color=None, fill=bg, overlay=True)

        # 라벨 (왼쪽)
        lbl_x = cell_x0 + 8
        lbl_y = cell_y0 + cell_h / 2 + 3.5
        page.insert_text((lbl_x, lbl_y), item['label'],
                         fontname="aggro", fontfile=FONT_AGGRO,
                         fontsize=9.5, color=ORANGE)

        # 답 영역 (오른쪽) — show_pdf_page 로 원본에서 클립
        lbl_w = cell_w * LBL_FRAC
        ans_x0 = cell_x0 + lbl_w
        ans_y0 = cell_y0 + 2
        ans_x1 = cell_x1 - 4
        ans_y1 = cell_y1 - 2

        if item['src_pdf'] not in src_doc_cache:
            src_doc_cache[item['src_pdf']] = fitz.open(item['src_pdf'])
        src_doc = src_doc_cache[item['src_pdf']]
        try:
            cx0, cy0, cx1, cy1 = item['clip']
            src_w = cx1 - cx0
            src_h = cy1 - cy0
            avail_w = ans_x1 - ans_x0
            avail_h = ans_y1 - ans_y0
            scale = min(avail_w / src_w, avail_h / src_h)
            tw_, th_ = src_w * scale, src_h * scale
            tx0 = ans_x0 + (avail_w - tw_) / 2
            ty0 = ans_y0 + (avail_h - th_) / 2
            page.show_pdf_page(
                fitz.Rect(tx0, ty0, tx0 + tw_, ty0 + th_),
                src_doc, item['src_page'],
                clip=fitz.Rect(cx0, cy0, cx1, cy1)
            )
        except Exception as e:
            print(f"Failed {item['label']}: {e}")

    # ── 그리드 경계선 ─────────────────────────────────
    for r in range(rows + 1):
        y = grid_y0 + r * cell_h
        page.draw_line((grid_x0, y), (grid_x1, y),
                       color=GREY_LINE, width=0.4)
    for c in range(cols + 1):
        x = grid_x0 + c * cell_w
        page.draw_line((x, grid_y0), (x, grid_y1),
                       color=GREY_LINE, width=0.4)
    # 외곽 굵은 라인
    page.draw_rect(fitz.Rect(grid_x0, grid_y0, grid_x1, grid_y1),
                   color=NAVY, width=1.2)

    n_pages = len(out)
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    out.close()
    for d in src_doc_cache.values():
        d.close()
    print(f"[OK] {OUT_PDF} ({n_pages} pages)")


if __name__ == "__main__":
    main()
