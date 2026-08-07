"""광북 1-1-b 프린트대비 → SUMMIT POINT 스타일 교재 빌드.

원본 프린트(2단, 문제 본문이 개별 이미지로 임베드)를 SUMMIT POINT 내지
레이아웃(골드 번호 + 풀이기록 체크 + KEY POINT + MEMO + 사이드 책갈피)으로
재구성한 뒤, 표지 / 챕터 디바이더 / 해설을 병합한다.

구조:
  1. 표지 (cover.pdf — make_gwangbuk_cover.py)
  2. PART 01 챕터 디바이더 (summit dividers page 0)
  3. 30문제 2단 내지 (A·01 ~ A·30)
  4. 정답·해설 디바이더 (summit dividers page 3)
  5. 원본 해설 페이지 (원본 PDF 15~끝)
"""
from __future__ import annotations
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import build_2col_problems as B  # 레이아웃 함수/상수 재사용

SRC_PDF = Path("/Users/youngwoolee/Downloads/260618_명문고2 대수 기말대비_원본.pdf")
OUT_DIR = ROOT / "output" / "myongmoon_modu"
OUT_DIR.mkdir(parents=True, exist_ok=True)

COVER = OUT_DIR / "cover.pdf"
DIVIDERS = OUT_DIR / "dividers.pdf"
PROBLEMS_PDF = OUT_DIR / "problems_2col.pdf"
OUT_PDF = OUT_DIR / "명문고2_대수_SUMMIT_POINT.pdf"

N_PROBLEMS = 20
PART_NO = "PART 1"
CHAPTER_SHORT = "삼각함수의 그래프~수열의 귀납적정의"

ANSWERS: list[str] = []  # 빠른정답 페이지 스킵

FONT_APPLE = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
_apple = fitz.Font(fontfile=FONT_APPLE)


def build_quick_answer_page() -> fitz.Document:
    """SUMMIT 스타일 빠른정답 페이지 — 머릿말 X, 단(세로구분) X, 큰 표, 주황 번호."""
    doc = fitz.open()
    page = doc.new_page(width=B.PAGE_W, height=B.PAGE_H)

    # SUMMIT 헤더 + 사이드 책갈피 (해설 섹션과 통일)
    B.draw_top_header(page, PART_NO, CHAPTER_SHORT)
    B.draw_side_bookmark(page, "A", PART_NO)

    # 타이틀 "빠른정답" + 양옆 골드 액센트
    title = "빠른정답"
    ts = 18
    tw = B._aggro.text_length(title, ts)
    cx = B.PAGE_W / 2
    title_y = 110
    page.insert_text((cx - tw / 2, title_y), title, fontname="aggro",
                     fontfile=B.FONT_AGGRO, fontsize=ts, color=B.NAVY)
    page.draw_line((cx - tw / 2 - 54, title_y - 6), (cx - tw / 2 - 16, title_y - 6),
                   color=B.GOLD, width=1.6)
    page.draw_line((cx + tw / 2 + 16, title_y - 6), (cx + tw / 2 + 54, title_y - 6),
                   color=B.GOLD, width=1.6)

    # 큰 그리드 3열 × 10행 (세로 구분선 없음)
    cols, rows = 3, 10
    grid_left, grid_right = 70, 525
    grid_top = 150
    row_h = 40
    grid_bottom = grid_top + rows * row_h
    col_w = (grid_right - grid_left) / cols

    page.draw_line((grid_left, grid_top), (grid_right, grid_top), color=B.NAVY, width=1.8)
    page.draw_line((grid_left, grid_bottom), (grid_right, grid_bottom), color=B.NAVY, width=1.8)
    for r in range(1, rows):
        y = grid_top + r * row_h
        page.draw_line((grid_left, y), (grid_right, y), color=B.GREY_LINE, width=0.4)

    for i, ans in enumerate(ANSWERS):
        r, c = i // cols, i % cols
        cell_x = grid_left + c * col_w
        base_y = grid_top + r * row_h + row_h / 2 + 5
        num = f"{i+1:02d}"
        nx = cell_x + 26
        page.insert_text((nx, base_y), num, fontname="aggro",
                         fontfile=B.FONT_AGGRO, fontsize=14, color=B.ORANGE)
        nw = B._aggro.text_length(num, 14)
        page.insert_text((nx + nw + 12, base_y), ans, fontname="apple",
                         fontfile=FONT_APPLE, fontsize=14, color=(0.1, 0.1, 0.12))
    return doc


def build_styled_pages(src, pages, prefix="A·") -> fitz.Document:
    """원본 해설/답안 페이지를 래스터화 + SUMMIT UI(헤더/책갈피/주황 번호) 덧그리기.

    insert_pdf 로 복사하면 일부 뷰어(Preview)가 수식 이미지를 렌더 못 하는
    문제가 있어, 페이지를 통째로 래스터화해서 안정적으로 표시되게 한다.
    prefix="A·" → 해설(번호 A·01), prefix="" → OMR 답안지(번호 01).
    """
    out = fitz.open()
    mat = fitz.Matrix(3.0, 3.0)
    WHITE = (1, 1, 1)
    osize = 14 if prefix else 13
    box_r = 30 if prefix else 18
    for pno in pages:
        src_pg = src[pno]
        # 파란 문항번호 스팬 (color 0x00abff)
        blue = []
        for blk in src_pg.get_text("dict")["blocks"]:
            for ln in blk.get("lines", []):
                for sp in ln["spans"]:
                    if sp.get("color") == 0x00ABFF and sp["size"] > 10 and sp["text"].strip().isdigit():
                        blue.append((sp["text"].strip(), sp["bbox"]))
        min_num_y = min((b[1][1] for b in blue), default=100)
        header_cut = min_num_y - 14

        page = out.new_page(width=B.PAGE_W, height=B.PAGE_H)
        page.insert_image(fitz.Rect(0, 0, B.PAGE_W, B.PAGE_H),
                          pixmap=src_pg.get_pixmap(matrix=mat, alpha=False))

        # 원본 머릿말 / 푸터 화이트아웃
        page.draw_rect(fitz.Rect(0, 0, B.PAGE_W, header_cut), color=WHITE, fill=WHITE)
        page.draw_rect(fitz.Rect(0, 790, B.PAGE_W, B.PAGE_H), color=WHITE, fill=WHITE)
        # 파란 번호 화이트아웃 → 주황 번호 재기입
        for txt, bb in blue:
            page.draw_rect(fitz.Rect(bb[0] - 3, bb[1] - 3, bb[0] + box_r, bb[3] + 3),
                           color=WHITE, fill=WHITE)
            page.insert_text((bb[0] - 2, bb[3] - 1), f"{prefix}{txt}", fontname="aggro",
                             fontfile=B.FONT_AGGRO, fontsize=osize, color=B.ORANGE)

        B.draw_top_header(page, PART_NO, CHAPTER_SHORT)
        B.draw_side_bookmark(page, "A", PART_NO)
    return out


def collect_problem_clips(doc) -> list[dict]:
    """원본 각 페이지에서 좌→우 컬럼 문제 본문 이미지의 clip 메타를 수집."""
    metas = []
    page_no = 0
    n = 0
    while n < N_PROBLEMS and page_no < len(doc):
        pg = doc[page_no]
        cols = []
        for im in pg.get_images():
            xref = im[0]
            for r in pg.get_image_rects(xref):
                w, h = r.x1 - r.x0, r.y1 - r.y0
                if w > 500 and h > 500:      # 전면 배경
                    continue
                if w < 60 or h < 30:          # 로고/노이즈
                    continue
                cols.append((round(r.x0, 1), round(r.y0, 1),
                             round(r.x1, 1), round(r.y1, 1)))
        cols.sort(key=lambda c: c[0])          # x 기준 좌→우
        for (x0, y0, x1, y1) in cols:
            if n >= N_PROBLEMS:
                break
            metas.append({
                "label": f"A·{n+1:02d}",
                "source_text": "",            # 본문 이미지에 출처 라벨 포함 → 중복 방지
                "src_pdf": str(SRC_PDF),
                "src_page": page_no,
                "clip": [x0, y0, x1, y1],
            })
            n += 1
        page_no += 1
    return metas, page_no


def build_problems(metas):
    out = fitz.open()
    cache: dict[str, fitz.Document] = {}
    i = 0
    while i < len(metas):
        page = out.new_page(width=B.PAGE_W, height=B.PAGE_H)
        B.draw_top_header(page, PART_NO, CHAPTER_SHORT)
        B.draw_side_bookmark(page, "A", PART_NO)
        B.draw_problem_block(page, B.LEFT_MARGIN, B.TOP_MARGIN, metas[i], cache)
        if i + 1 < len(metas):
            B.draw_problem_block(page, B.COL_RIGHT_X, B.TOP_MARGIN, metas[i + 1], cache)
        i += 2
    out.save(str(PROBLEMS_PDF), garbage=4, deflate=True)
    out.close()
    for d in cache.values():
        d.close()
    return PROBLEMS_PDF


def main():
    src = fitz.open(str(SRC_PDF))
    metas, sol_start = collect_problem_clips(src)
    print(f"[clips] {len(metas)} problems, solutions start at page {sol_start}")

    build_problems(metas)
    print(f"[problems] {PROBLEMS_PDF}")

    out = fitz.open()
    cover = fitz.open(str(COVER))
    div = fitz.open(str(DIVIDERS))
    probs = fitz.open(str(PROBLEMS_PDF))

    out.insert_pdf(cover)                              # 1) 표지
    out.insert_pdf(div, from_page=0, to_page=0)        # 2) PART 01 디바이더
    out.insert_pdf(probs)                              # 3) 30문제 내지

    omr_idx = len(src) - 1                             # 원본 마지막 = OMR 답안지 (제외)

    out.insert_pdf(div, from_page=1, to_page=1)        # 4) 정답·해설 디바이더

    # 6) 상세해설 — 빠른정답[sol_start]·OMR[마지막] 제외, 래스터화 + SUMMIT UI
    sol_pages = list(range(sol_start + 1, omr_idx))
    if sol_pages:
        sols = build_styled_pages(src, sol_pages, prefix="A·")
        out.insert_pdf(sols)
        sols.close()

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    n = len(out)
    for d in [cover, div, probs, out, src]:
        d.close()
    print(f"[OK] {OUT_PDF}  ({n} pages)")


if __name__ == "__main__":
    main()
