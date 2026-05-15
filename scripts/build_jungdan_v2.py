"""중단원 평가(2-2단원) — 통일 교재화 v2.

요구사항:
  - 표지/성취기준/세션디바이더 페이지 전부 제외
  - 본문/해설 페이지의 상하좌우 chrome (배지·헤더·푸터·북마크) 화이트박싱
  - 문제 라벨 글로벌 연속 번호 001-169
  - 해설 라벨도 동일 글로벌 번호로 통일
  - p28-33 (1. 삼각함수) 본문 + 대응 해설(p60-64) 제외

섹션 구성 (총 169문제):
  S0  학습자료집 Ⅱ-2       : 17문항  → 001-017
  S1  학습자료집 Ⅲ-1       : 17문항  → 018-034
  S2  학습자료집 Ⅲ-2       : 22문항  → 035-056
  S3  학습자료집 Ⅲ-3       : 17문항  → 057-073
  S4  사인법칙 ①회         : 14문항  → 074-087
  S5  사인법칙 ②회         : 14문항  → 088-101
  S6  등차/등비 ①회        : 15문항  → 102-116
  S7  등차/등비 ②회        : 15문항  → 117-131
  S8  수열의 합 ①회        : 10문항  → 132-141
  S9  수열의 합 ②회        : 10문항  → 142-151
  S10 수학적 귀납법 ①회    : 9문항   → 152-160
  S11 수학적 귀납법 ②회    : 9문항   → 161-169
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = Path("/Users/youngwoolee/Downloads/중단원 평가(2-2단원)_merged.pdf")
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "JUNGDAN_EVAL_2_2_clean.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
LABEL_FONT_NAME = "aggro"
LABEL_FONT_FILE = FONT_AGGRO
LABEL_COLOR = (240 / 255, 125 / 255, 35 / 255)

_label_font = fitz.Font(fontfile=LABEL_FONT_FILE)

PAGE_W = 595.0
PAGE_H = 842.0
COL_SPLIT_X = 290.0   # 좌/우 컬럼 경계 (x < 290 = L, x >= 290 = R)

# 섹션별 문제 수 + 글로벌 오프셋
SECTIONS = [
    {"name": "학습 Ⅱ-2", "count": 17, "kind": "jaja"},
    {"name": "학습 Ⅲ-1", "count": 17, "kind": "jaja"},
    {"name": "학습 Ⅲ-2", "count": 22, "kind": "jaja"},
    {"name": "학습 Ⅲ-3", "count": 17, "kind": "jaja"},
    {"name": "사인법칙 ①",   "count": 14, "kind": "eval"},
    {"name": "사인법칙 ②",   "count": 14, "kind": "eval"},
    {"name": "등차/등비 ①",   "count": 15, "kind": "eval"},
    {"name": "등차/등비 ②",   "count": 15, "kind": "eval"},
    {"name": "수열의 합 ①",   "count": 10, "kind": "eval"},
    {"name": "수열의 합 ②",   "count": 10, "kind": "eval"},
    {"name": "수귀납 ①",     "count": 9,  "kind": "eval"},
    {"name": "수귀납 ②",     "count": 9,  "kind": "eval"},
]
# 누적 오프셋 (0-indexed 섹션 시작 번호 - 1)
_off = 0
for s in SECTIONS:
    s["offset"] = _off
    _off += s["count"]
TOTAL_PROBLEMS = _off  # 169


# 본문 페이지: (src_idx, section_idx)
PROBLEM_PAGES: list[tuple[int, int]] = [
    (0, 0), (1, 0), (2, 0),
    (5, 1), (6, 1), (7, 1),
    (10, 2), (11, 2), (12, 2), (13, 2),
    (18, 3), (19, 3), (20, 3), (21, 3),
    (34, 4), (35, 4), (36, 4),
    (37, 5), (38, 5), (39, 5),
    (42, 6), (43, 6), (44, 6),
    (45, 7), (46, 7), (47, 7),
    (49, 8), (50, 8),
    (51, 9), (52, 9),
    (54, 10), (55, 10),
    (56, 11), (57, 11),
]

# 해설 페이지: (src_idx, [(section_idx, 'L'|'R'|'BOTH'), ...])
SOLUTION_PAGES: list[tuple[int, list[tuple[int, str]]]] = [
    (3,  [(0, 'BOTH')]),
    (4,  [(0, 'BOTH')]),
    (8,  [(1, 'BOTH')]),
    (9,  [(1, 'BOTH')]),
    (14, [(2, 'BOTH')]),
    (15, [(2, 'BOTH')]),
    (16, [(2, 'BOTH')]),
    (17, [(2, 'BOTH')]),
    (22, [(3, 'BOTH')]),
    (23, [(3, 'BOTH')]),
    (24, [(3, 'BOTH')]),
    (64, [(4, 'BOTH')]),
    (65, [(4, 'BOTH')]),
    (66, [(5, 'BOTH')]),
    (67, [(5, 'BOTH')]),
    (69, [(6, 'BOTH')]),
    (70, [(6, 'BOTH')]),
    (71, [(7, 'BOTH')]),
    (72, [(7, 'BOTH')]),
    (73, [(8, 'BOTH')]),
    (74, [(8, 'L'), (9, 'R')]),    # 수열의 합 ①→② split
    (75, [(9, 'BOTH')]),
    (76, [(9, 'L'), (10, 'R')]),   # 수열의 합 ②→수귀납 ① split
    (77, [(10, 'BOTH')]),
    (78, [(11, 'BOTH')]),
    (79, [(11, 'BOTH')]),
]


# ──────────────────────────────────────────────────────────────────
# Chrome stripping
# ──────────────────────────────────────────────────────────────────

def _white_rect(page, x0, y0, x1, y1):
    page.draw_rect(fitz.Rect(x0, y0, x1, y1),
                   color=(1, 1, 1), fill=(1, 1, 1), overlay=True)


def strip_chrome_problem(page, kind: str):
    """본문 페이지의 chrome 화이트박싱."""
    if kind == "jaja":
        # 학습자료집:
        #  - 상단 배너 + 페이지번호: 0 to y=105 (full width)
        #  - 좌상단 "기초/표준/도전" 배지: x<135, y=105 to y=135 (좌측만 추가 strip)
        #  - 우측 사이드 북마크: x>540
        #  - 하단 페이지번호: y>785
        _white_rect(page, 0, 0, PAGE_W, 105)
        _white_rect(page, 0, 105, 135, 138)         # 배지 영역
        _white_rect(page, 540, 0, PAGE_W, 800)
        _white_rect(page, 0, 785, PAGE_W, PAGE_H)
    elif kind == "eval":
        # 중단원평가: 상단 헤더 (MiraeN 로고 + 평가문제 박스 + 회차 헤더) + 페이지 배경 잔류
        _white_rect(page, 0, 0, PAGE_W, 80)
        _white_rect(page, 0, 785, PAGE_W, PAGE_H)


def strip_chrome_solution(page, kind: str):
    """해설 페이지의 chrome 화이트박싱.

    학습자료집 해설은 우측 컬럼 첫 문항이 y=83 부터 시작 — 우측을 다 strip 하면 안 됨.
    좌측 컬럼은 y=125 까지 빠른답 박스 chrome 가 있음.
    """
    if kind == "jaja":
        # 1) 상단 풀폭 배너 (y=0 to 55)
        _white_rect(page, 0, 0, PAGE_W, 55)
        # 2) 좌측 컬럼: 페이지 메타 + 빠른답 박스 전체 (y=55-220, x=0-290)
        _white_rect(page, 0, 55, 290, 220)
        # 3) 우측 사이드 북마크
        _white_rect(page, 540, 0, PAGE_W, 800)
        # 4) 하단 footer
        _white_rect(page, 0, 785, PAGE_W, PAGE_H)
    elif kind == "eval":
        # 중단원평가 해설: 상단 헤더 (y=0-80) + 하단 footer
        # 빠른답 박스 (각 회차 첫 페이지 좌측 상단 / split 페이지 우측 상단) 는
        # 별도 strip 으로 main 에서 처리
        _white_rect(page, 0, 0, PAGE_W, 80)
        _white_rect(page, 0, 785, PAGE_W, PAGE_H)


def strip_split_section_header(page, side: str):
    """해설 split 페이지에서 'X. 섹션-N회' mid-page 헤더 제거.

    side='R' 인 경우 우측 컬럼 최상단의 헤더만 제거. 'L' 인 경우 좌측 최하단의 결론 영역은 그대로.
    """
    # split 페이지의 R 시작 부분에는 새로운 섹션 헤더가 그려져있음 — 보통 페이지 상단에 위치
    # 페이지 전체 상단에 적용한 strip_chrome_solution 으로 이미 처리됨
    pass


def strip_jajalyo_section_label(page):
    """학습자료집 페이지의 좌측 "기초/표준/도전" 배지 화이트박싱.

    배지는 상단 배너 strip (0-105) 에 이미 포함되지만 일부 페이지에서는
    아래쪽에도 추가 배지가 있을 수 있어 추가 정리.
    """
    pass


# ──────────────────────────────────────────────────────────────────
# Label finding
# ──────────────────────────────────────────────────────────────────

def find_eval_labels(page) -> list[tuple[fitz.Rect, int]]:
    """중단원평가 본문 문제 라벨 (YJ BONMOKGAK Medium ~14pt)."""
    d = page.get_text("dict")
    out = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "BONMOKGAK" not in sp["font"]:
                    continue
                if not (13.5 <= sp["size"] <= 14.5):
                    continue
                t = sp["text"].strip()
                if not re.fullmatch(r"\d{1,2}", t):
                    continue
                x0 = sp["bbox"][0]
                if not (35 <= x0 <= 55 or 285 <= x0 <= 310):
                    continue
                out.append((fitz.Rect(*sp["bbox"]), int(t)))
    return out


def find_eval_solution_labels(page) -> list[tuple[fitz.Rect, int]]:
    """중단원평가 해설 라벨 (YJ BONMOKGAK Medium ~10.9pt).

    빠른답 표(9pt) 는 제외. 본문 풀이 라벨(10.9pt, 좌측 x≈42 또는 우측 x≈291)만.
    """
    d = page.get_text("dict")
    out = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "BONMOKGAK" not in sp["font"]:
                    continue
                if not (10.5 <= sp["size"] <= 11.5):
                    continue
                t = sp["text"].strip()
                if not re.fullmatch(r"\d{1,2}", t):
                    continue
                x0 = sp["bbox"][0]
                if not (35 <= x0 <= 55 or 285 <= x0 <= 310):
                    continue
                num = int(t)
                if not (1 <= num <= 20):
                    continue
                out.append((fitz.Rect(*sp["bbox"]), num))
    return out


def _merge_adjacent_digit_spans(cands: list, x0_ok_ranges: list[tuple[float, float]]) -> list[tuple[fitz.Rect, int]]:
    """인접한 digit span 쌍을 "0N" 또는 "NN" 으로 병합. x0_ok_ranges 안 인 것만 채택."""
    cands.sort(key=lambda x: (round(x[0][1], 1), x[0][0]))
    used = [False] * len(cands)
    out = []
    for i, (bb, t) in enumerate(cands):
        if used[i]:
            continue
        merged = t
        bx0, by0, bx1, by1 = bb
        for j in range(i + 1, len(cands)):
            if used[j]:
                continue
            bb2, t2 = cands[j]
            if abs(bb2[1] - by0) > 1.0:
                continue
            if bb2[0] - bx1 > 2.0:
                continue
            merged += t2
            bx1 = bb2[2]
            by0 = min(by0, bb2[1])
            by1 = max(by1, bb2[3])
            used[j] = True
        used[i] = True
        if not re.fullmatch(r"\d{1,3}", merged):
            continue
        num = int(merged)
        if not (1 <= num <= 30):
            continue
        ok = any(lo <= bx0 <= hi for lo, hi in x0_ok_ranges)
        if not ok:
            continue
        out.append((fitz.Rect(bx0, by0, bx1, by1), num))
    return out


def find_jaja_labels(page) -> list[tuple[fitz.Rect, int]]:
    """학습자료집 본문 라벨 (H2gtrE ~14.76pt, "0N" 두 span)."""
    d = page.get_text("dict")
    cands = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "H2gtrE" not in sp["font"]:
                    continue
                if not (14.0 <= sp["size"] <= 15.5):
                    continue
                t = sp["text"]
                if not re.fullmatch(r"\d", t):
                    continue
                cands.append((tuple(sp["bbox"]), t))
    # 라벨 x 위치: 좌측 컬럼 (25-55) 또는 우측 컬럼 (285-315)
    return _merge_adjacent_digit_spans(cands, [(25, 55), (285, 315)])


def find_jaja_solution_labels(page) -> list[tuple[fitz.Rect, int]]:
    """학습자료집 해설 라벨 — 풀이 본문(H2gtrE ~10.92pt).

    1-9: "0N" 두 span으로 쪼개진 형태
    10+: "NN" 단일 span (예: "12", "13", ...)
    """
    d = page.get_text("dict")
    cands_single = []  # 1자리 span (병합 대상)
    direct_labels = []  # 2자리 단일 span (그대로 라벨)
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "H2gtrE" not in sp["font"]:
                    continue
                if not (10.5 <= sp["size"] <= 11.5):
                    continue
                t = sp["text"]
                bb = sp["bbox"]
                if re.fullmatch(r"\d", t):
                    cands_single.append((tuple(bb), t))
                elif re.fullmatch(r"\d{2}", t):
                    # 위치 체크 — 라벨 컬럼인지
                    x0 = bb[0]
                    if 20 <= x0 <= 40 or 285 <= x0 <= 315:
                        num = int(t)
                        if 1 <= num <= 30:
                            direct_labels.append((fitz.Rect(*bb), num))
    # 1자리 후보들 병합 → "0N" 형태 라벨
    merged = _merge_adjacent_digit_spans(cands_single, [(20, 40), (285, 315)])
    return merged + direct_labels


# ──────────────────────────────────────────────────────────────────
# Label replacement
# ──────────────────────────────────────────────────────────────────

def replace_label(page, rect: fitz.Rect, new_text: str, size: float = 11.5):
    """라벨 치환 — 우측 정렬해서 원본 라벨의 우측 끝 기준으로 배치.

    3자리 글로벌 번호가 원본 2자리보다 넓으므로 우측정렬해서 본문 텍스트
    영역으로 침범하지 않게 한다. 라벨은 원본 라벨 우측 끝(rect.x1) 에서
    좌측으로 확장되며, 좌측 마진(x<5) 으로 살짝 빠지더라도 허용.
    """
    pad = 1.0
    new_w = _label_font.text_length(new_text, fontsize=size)
    new_x = rect.x1 - new_w   # 우측 정렬
    cover = fitz.Rect(
        new_x - pad, rect.y0 - pad,
        rect.x1 + pad,
        rect.y1 + pad,
    )
    page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
    baseline_y = rect.y1 - 0.18 * size
    page.insert_text(
        (new_x, baseline_y),
        new_text,
        fontname=LABEL_FONT_NAME, fontfile=LABEL_FONT_FILE,
        fontsize=size, color=LABEL_COLOR,
    )


def col_of(rect: fitz.Rect) -> str:
    return 'L' if rect.x0 < COL_SPLIT_X else 'R'


def fmt_global(g: int) -> str:
    return f"{g:03d}"


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

def main():
    src = fitz.open(str(SRC_PDF))
    out = fitz.open()

    # === 본문 ===
    for src_idx, sec_idx in PROBLEM_PAGES:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)
        page = out[-1]
        sec = SECTIONS[sec_idx]
        strip_chrome_problem(page, sec["kind"])

        # 라벨 찾고 글로벌 번호로 치환
        if sec["kind"] == "jaja":
            labels = find_jaja_labels(page)
        else:
            labels = find_eval_labels(page)

        # 컬럼별로 정렬: L 먼저(y 오름차순) → R(y 오름차순)
        labels.sort(key=lambda x: (0 if col_of(x[0]) == 'L' else 1, x[0].y0))
        for rect, local_num in labels:
            global_num = sec["offset"] + local_num
            replace_label(page, rect, fmt_global(global_num), size=11.5)

    n_problem_pages = len(out)

    # 평가 해설에서 빠른답 박스가 있는 페이지 — 각 회차 첫 페이지
    EVAL_TABLE_LEFT = {64, 66, 69, 71, 73, 78}    # 좌측 컬럼 상단에 빠른답 박스
    EVAL_TABLE_RIGHT = {74, 76}                    # split 페이지 우측 컬럼 상단

    # === 해설 ===
    for src_idx, splits in SOLUTION_PAGES:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)
        page = out[-1]

        # kind 추정: src_idx < 60 면 학습자료집, 아니면 평가
        kind = "jaja" if src_idx < 60 else "eval"
        strip_chrome_solution(page, kind)

        # 평가 해설 빠른답 박스 strip
        if kind == "eval":
            if src_idx in EVAL_TABLE_LEFT:
                _white_rect(page, 0, 80, 290, 188)
            if src_idx in EVAL_TABLE_RIGHT:
                _white_rect(page, 290, 80, PAGE_W, 168)

        # 라벨 찾기 — 해설 페이지는 별도 함수 사용 (작은 크기 라벨)
        if kind == "jaja":
            labels = find_jaja_solution_labels(page)
        else:
            labels = find_eval_solution_labels(page)

        # split 페이지 처리: 라벨의 column 으로 어느 섹션에 속하는지 판단
        for rect, local_num in labels:
            col = col_of(rect)
            sec_idx_for_label = None
            for s_idx, s_col in splits:
                if s_col == 'BOTH' or s_col == col:
                    sec_idx_for_label = s_idx
                    break
            if sec_idx_for_label is None:
                continue
            sec = SECTIONS[sec_idx_for_label]
            # local_num 검증: 섹션 범위 안에 들어와야 함
            if not (1 <= local_num <= sec["count"]):
                continue
            global_num = sec["offset"] + local_num
            replace_label(page, rect, fmt_global(global_num), size=11.5)

    src.close()

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n_pages = len(out)
    out.close()

    print(f"[OK] {OUT_PDF}")
    print(f"  총 페이지: {n_pages}  (본문 {n_problem_pages}p, 해설 {n_pages - n_problem_pages}p)")
    print(f"  총 문제 수: {TOTAL_PROBLEMS}")


if __name__ == "__main__":
    main()
