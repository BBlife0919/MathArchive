"""중단원 평가(2-2단원) 해설 클립 추출 — 글로벌 번호 매핑.

각 해설 = {
  'label':  '001',
  'src_pdf': '.../중단원 평가(2-2단원)_merged.pdf',
  'src_page': N,
  'clip': (x0, y0, x1, y1),
}

라벨 폰트:
  - 학습자료집(jaja) 해설: H2gtrE 10.9pt, '0N' 두 span / 'NN' 단일 span
  - 중단원평가(eval) 해설: YJ BONMOKGAK Medium 10.9pt, 단일 span

Split 페이지(74, 76): 좌측=직전 섹션, 우측=다음 섹션. 라벨의 컬럼으로 섹션 매핑.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import fitz

from extract_jungdan_problems import (
    SECTIONS, TOTAL, SRC_PDF, OUT_DIR,
)

META_JSON = OUT_DIR / "solutions_meta.json"

# 컬럼 경계 — 단원 배지/우측 데코 점선 제거.
COL_LEFT_X0 = 32.0
COL_LEFT_X1 = 282.0
COL_RIGHT_X0 = 288.0
COL_RIGHT_X1 = 522.0
COL_BOTTOM_Y = 780.0

X_OK_LEFT = (20.0, 55.0)
X_OK_RIGHT = (285.0, 315.0)

# 해설 페이지: (src_idx, [(section_idx, 'L'|'R'|'BOTH'), ...])
# S0=학습Ⅱ-2(사인), S1=사인①, S2=사인②, S3=학습Ⅲ-1(등차/등비), S4=등차/등비①, S5=등차/등비②,
# S6=학습Ⅲ-2(합), S7=수열합①, S8=수열합②, S9=학습Ⅲ-3(귀납), S10=수귀납①, S11=수귀납②
SOLUTION_PAGES: list[tuple[int, list[tuple[int, str]]]] = [
    (3,  [(0, "BOTH")]),
    (4,  [(0, "BOTH")]),
    (8,  [(3, "BOTH")]),
    (9,  [(3, "BOTH")]),
    (14, [(6, "BOTH")]),
    (15, [(6, "BOTH")]),
    (16, [(6, "BOTH")]),
    (17, [(6, "BOTH")]),
    (22, [(9, "BOTH")]),
    (23, [(9, "BOTH")]),
    (24, [(9, "BOTH")]),
    (64, [(1, "BOTH")]),
    (65, [(1, "BOTH")]),
    (66, [(2, "BOTH")]),
    (67, [(2, "BOTH")]),
    (69, [(4, "BOTH")]),
    (70, [(4, "BOTH")]),
    (71, [(5, "BOTH")]),
    (72, [(5, "BOTH")]),
    (73, [(7, "BOTH")]),
    (74, [(7, "L"), (8, "R")]),
    (75, [(8, "BOTH")]),
    (76, [(8, "L"), (10, "R")]),
    (77, [(10, "BOTH")]),
    (78, [(11, "BOTH")]),
    (79, [(11, "BOTH")]),
]


def _x_in(x: float, rng: tuple[float, float]) -> bool:
    return rng[0] <= x <= rng[1]


def _merge_adjacent(cands: list[tuple[tuple, str]]) -> list[tuple[fitz.Rect, str]]:
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


def find_jaja_sol_labels(page: fitz.Page) -> list[tuple[fitz.Rect, int]]:
    d = page.get_text("dict")
    singles, direct = [], []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "H2gtrE" not in sp["font"]:
                    continue
                if not (10.5 <= sp["size"] <= 11.5):
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


def find_eval_sol_labels(page: fitz.Page) -> list[tuple[fitz.Rect, int]]:
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

    # 섹션별 라벨 수집
    section_labels: dict[int, list[dict]] = {i: [] for i in range(len(SECTIONS))}

    for src_idx, splits in SOLUTION_PAGES:
        page = doc[src_idx]
        kind = "jaja" if src_idx < 60 else "eval"
        finder = find_jaja_sol_labels if kind == "jaja" else find_eval_sol_labels
        labels = finder(page)

        for rect, local in labels:
            col = column_of(rect)
            sec_idx_for_label = None
            for s_idx, s_col in splits:
                if s_col == "BOTH" or s_col == col:
                    sec_idx_for_label = s_idx
                    break
            if sec_idx_for_label is None:
                continue
            sec = SECTIONS[sec_idx_for_label]
            if not (1 <= local <= sec["count"]):
                continue
            section_labels[sec_idx_for_label].append({
                "src_page": src_idx,
                "col": col,
                "rect": rect,
                "local": local,
            })

    # 클립 계산: 섹션별 라벨 (page, col, y) 정렬
    solutions: list[dict] = []
    for sec_idx, sec in enumerate(SECTIONS):
        items = section_labels[sec_idx]
        items.sort(key=lambda x: (x["src_page"], 0 if x["col"] == "L" else 1, x["rect"].y0))
        n = len(items)
        for i, item in enumerate(items):
            local = item["local"]
            global_num = sec["offset"] + local
            col = item["col"]
            page_idx = item["src_page"]
            rect = item["rect"]
            col_x0 = COL_LEFT_X0 if col == "L" else COL_RIGHT_X0
            col_x1 = COL_LEFT_X1 if col == "L" else COL_RIGHT_X1
            y_top = rect.y0 - 1.0
            y_bot = COL_BOTTOM_Y
            if i + 1 < n:
                nxt = items[i + 1]
                if nxt["src_page"] == page_idx and nxt["col"] == col:
                    y_bot = nxt["rect"].y0 - 3.0
            solutions.append({
                "label": f"{global_num:03d}",
                "local": local,
                "section_idx": sec_idx,
                "section_name": sec["name"],
                "kind": sec["kind"],
                "chapter_idx": sec["chapter_idx"],
                "src_pdf": str(SRC_PDF),
                "src_page": page_idx,
                "clip": [col_x0, y_top, col_x1, y_bot],
                "label_bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
            })

    print("section coverage:")
    for sec_idx, sec in enumerate(SECTIONS):
        n_found = sum(1 for s in solutions if s["section_idx"] == sec_idx)
        flag = " " if n_found == sec["count"] else " ⚠"
        print(f" {flag} S{sec_idx:02d} {sec['name']:15} expected={sec['count']:2d}  found={n_found:2d}")
    print(f"\nTotal solutions: {len(solutions)} (expected {TOTAL})")

    META_JSON.write_text(json.dumps(solutions, ensure_ascii=False, indent=2),
                         encoding="utf-8")
    print(f"[OK] {META_JSON}")
    doc.close()


if __name__ == "__main__":
    main()
