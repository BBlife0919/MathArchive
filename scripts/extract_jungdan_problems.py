"""중단원 평가(2-2단원) 문제 클립 추출 — SUMMIT POINT 파이프라인 동일 방식.

각 문제 = {
  'label':  '001',                # 글로벌 3자리 번호
  'section_idx': 0,
  'section_name': '학습자료집 Ⅱ-2',
  'chapter_idx': 0,               # 머지 챕터 (cover/divider 단위)
  'src_pdf': '.../중단원 평가(2-2단원)_merged.pdf',
  'src_page': 0,
  'clip': (x0, y0, x1, y1),       # PDF 좌표 (포인트)
}

라벨 폰트:
  - 학습자료집(jaja) : H2gtrE 14.76pt, '0N' 두 span / 'NN' 단일 span
  - 중단원평가(eval) : YJ BONMOKGAK Medium 14.1pt, 단일 span

페이지는 2단(좌 x≈33, 우 x≈291). 클립 = (col_x0, label_y, next_label_y_in_col, col_x1).
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = Path("/Users/youngwoolee/Downloads/중단원 평가(2-2단원)_merged.pdf")
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
META_JSON = OUT_DIR / "problems_meta.json"

PAGE_W = 595.0
PAGE_H = 842.0

# 컬럼 경계 — 가운데 단원 배지 / 우측 가장자리 데코레이션 제거를 위해 타이트하게.
COL_LEFT_X0 = 32.0
COL_LEFT_X1 = 283.0
COL_RIGHT_X0 = 297.0
COL_RIGHT_X1 = 538.0
COL_TOP_Y = 78.0
COL_BOTTOM_Y = 780.0

# 라벨 위치 검증용 x 범위
X_OK_LEFT = (25.0, 55.0)
X_OK_RIGHT = (285.0, 315.0)

# ─────────────────────────────────────────────────────────
# 섹션 정의 (글로벌 오프셋 자동 계산)
# ─────────────────────────────────────────────────────────
# Topic-based grouping: each chapter mixes 학습자료집 + 중단원평가 of the same topic.
# 학습자료집 Ⅱ-2/Ⅲ-1/Ⅲ-2/Ⅲ-3 ↔ 평가 사인/등차·등비/수열의합/수귀납 매칭.
SECTIONS = [
    # 0~2: 사인법칙·코사인법칙 (45문)
    {"name": "학습자료집 Ⅱ-2",   "kind": "jaja", "count": 17, "chapter_idx": 0},
    {"name": "사인법칙 ①회",     "kind": "eval", "count": 14, "chapter_idx": 0},
    {"name": "사인법칙 ②회",     "kind": "eval", "count": 14, "chapter_idx": 0},
    # 3~5: 등차·등비수열 (47문)
    {"name": "학습자료집 Ⅲ-1",   "kind": "jaja", "count": 17, "chapter_idx": 1},
    {"name": "등차·등비 ①회",    "kind": "eval", "count": 15, "chapter_idx": 1},
    {"name": "등차·등비 ②회",    "kind": "eval", "count": 15, "chapter_idx": 1},
    # 6~8: 수열의 합 (42문)
    {"name": "학습자료집 Ⅲ-2",   "kind": "jaja", "count": 22, "chapter_idx": 2},
    {"name": "수열의 합 ①회",    "kind": "eval", "count": 10, "chapter_idx": 2},
    {"name": "수열의 합 ②회",    "kind": "eval", "count": 10, "chapter_idx": 2},
    # 9~11: 수학적 귀납법 (35문)
    {"name": "학습자료집 Ⅲ-3",   "kind": "jaja", "count": 17, "chapter_idx": 3},
    {"name": "수학적 귀납법 ①회","kind": "eval", "count": 9,  "chapter_idx": 3},
    {"name": "수학적 귀납법 ②회","kind": "eval", "count": 9,  "chapter_idx": 3},
]

CHAPTERS = [
    {"roman": "I",   "name": "사인법칙·코사인법칙",
     "eng": "LAW OF SINES & COSINES",    "short": "사인·코사인법칙"},
    {"roman": "II",  "name": "등차·등비수열",
     "eng": "ARITHMETIC & GEOMETRIC",     "short": "등차·등비수열"},
    {"roman": "III", "name": "수열의 합",
     "eng": "SERIES & SUMMATION",         "short": "수열의 합"},
    {"roman": "IV",  "name": "수학적 귀납법",
     "eng": "MATHEMATICAL INDUCTION",     "short": "수학적 귀납법"},
]
_off = 0
for s in SECTIONS:
    s["offset"] = _off
    _off += s["count"]
TOTAL = _off  # 169

# S0=학습Ⅱ-2(사인), S1=사인①, S2=사인②, S3=학습Ⅲ-1(등차/등비), S4=등차/등비①, S5=등차/등비②,
# S6=학습Ⅲ-2(합), S7=수열합①, S8=수열합②, S9=학습Ⅲ-3(귀납), S10=수귀납①, S11=수귀납②
PROBLEM_PAGES: list[tuple[int, int]] = [
    (0, 0), (1, 0), (2, 0),
    (34, 1), (35, 1), (36, 1),
    (37, 2), (38, 2), (39, 2),
    (5, 3), (6, 3), (7, 3),
    (42, 4), (43, 4), (44, 4),
    (45, 5), (46, 5), (47, 5),
    (10, 6), (11, 6), (12, 6), (13, 6),
    (49, 7), (50, 7),
    (51, 8), (52, 8),
    (18, 9), (19, 9), (20, 9), (21, 9),
    (54, 10), (55, 10),
    (56, 11), (57, 11),
]


def _merge_adjacent(cands: list[tuple[tuple, str]]) -> list[tuple[fitz.Rect, str]]:
    """같은 baseline 인접 digit span 병합 → '0N' 또는 'NN'."""
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
        out.append((fitz.Rect(bx0, by0, bx1, by1), merged))
    return out


def _x_in(x: float, rng: tuple[float, float]) -> bool:
    return rng[0] <= x <= rng[1]


def find_jaja_labels(page: fitz.Page) -> list[tuple[fitz.Rect, int]]:
    """학습자료집 H2gtrE 14-15pt 라벨 (단일·페어 모두)."""
    d = page.get_text("dict")
    singles = []
    direct = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "H2gtrE" not in sp["font"]:
                    continue
                if not (14.0 <= sp["size"] <= 15.5):
                    continue
                t = sp["text"].strip()
                bb = sp["bbox"]
                if re.fullmatch(r"\d", t):
                    singles.append((tuple(bb), t))
                elif re.fullmatch(r"\d{2}", t):
                    x0 = bb[0]
                    if _x_in(x0, X_OK_LEFT) or _x_in(x0, X_OK_RIGHT):
                        n = int(t)
                        if 1 <= n <= 30:
                            direct.append((fitz.Rect(*bb), n))
    merged = _merge_adjacent(singles)
    out = list(direct)
    for rect, text in merged:
        if not re.fullmatch(r"\d{1,3}", text):
            continue
        if not (_x_in(rect.x0, X_OK_LEFT) or _x_in(rect.x0, X_OK_RIGHT)):
            continue
        n = int(text)
        if 1 <= n <= 30:
            out.append((rect, n))
    return out


def find_eval_labels(page: fitz.Page) -> list[tuple[fitz.Rect, int]]:
    """중단원평가 YJ BONMOKGAK Medium 14pt 라벨."""
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
                bb = sp["bbox"]
                x0 = bb[0]
                if not (_x_in(x0, X_OK_LEFT) or _x_in(x0, X_OK_RIGHT)):
                    continue
                n = int(t)
                if 1 <= n <= 30:
                    out.append((fitz.Rect(*bb), n))
    return out


def column_of(rect: fitz.Rect) -> str:
    return "L" if rect.x0 < 200 else "R"


def main():
    doc = fitz.open(str(SRC_PDF))
    # 섹션별 라벨 수집: section_idx → [{src_page, col, label_rect, local_num}]
    section_labels: dict[int, list[dict]] = {i: [] for i in range(len(SECTIONS))}

    for src_idx, sec_idx in PROBLEM_PAGES:
        page = doc[src_idx]
        sec = SECTIONS[sec_idx]
        finder = find_jaja_labels if sec["kind"] == "jaja" else find_eval_labels
        labels = finder(page)
        for rect, local in labels:
            section_labels[sec_idx].append({
                "src_page": src_idx,
                "col": column_of(rect),
                "rect": rect,
                "local": local,
            })

    # 섹션별로 정렬 + 클립 계산
    problems: list[dict] = []
    for sec_idx, sec in enumerate(SECTIONS):
        items = section_labels[sec_idx]
        # 정렬: src_page → col(L<R) → y
        items.sort(key=lambda x: (x["src_page"], 0 if x["col"] == "L" else 1, x["rect"].y0))
        # 클립 계산 (같은 페이지 같은 컬럼 내 다음 라벨까지)
        n = len(items)
        for i, item in enumerate(items):
            local = item["local"]
            global_num = sec["offset"] + local
            col = item["col"]
            page_idx = item["src_page"]
            rect = item["rect"]

            col_x0 = COL_LEFT_X0 if col == "L" else COL_RIGHT_X0
            col_x1 = COL_LEFT_X1 if col == "L" else COL_RIGHT_X1
            y_top = rect.y0 - 1.0   # 라벨 상단 살짝 위
            # 다음 라벨 같은 컬럼/같은 페이지 인지
            y_bot = COL_BOTTOM_Y
            if i + 1 < n:
                nxt = items[i + 1]
                if nxt["src_page"] == page_idx and nxt["col"] == col:
                    y_bot = nxt["rect"].y0 - 3.0
                elif nxt["src_page"] == page_idx and col == "L" and nxt["col"] == "R":
                    # 같은 페이지 L의 마지막 → 컬럼 끝까지
                    y_bot = COL_BOTTOM_Y
                # 다른 페이지: 현재 컬럼 끝까지
            problems.append({
                "label": f"{global_num:03d}",
                "local": local,
                "section_idx": sec_idx,
                "section_name": sec["name"],
                "kind": sec["kind"],
                "chapter_idx": sec["chapter_idx"],
                "src_pdf": str(SRC_PDF),
                "src_page": page_idx,
                "clip": [col_x0, y_top, col_x1, y_bot],
            })

    # 검증: 섹션별 라벨 수
    print("section coverage:")
    for sec_idx, sec in enumerate(SECTIONS):
        n_found = sum(1 for p in problems if p["section_idx"] == sec_idx)
        flag = " " if n_found == sec["count"] else " ⚠"
        print(f" {flag} S{sec_idx:02d} {sec['name']:15} expected={sec['count']:2d}  found={n_found:2d}")
    print(f"\nTotal problems: {len(problems)} (expected {TOTAL})")

    META_JSON.write_text(json.dumps(problems, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"[OK] {META_JSON}")
    doc.close()


if __name__ == "__main__":
    main()
