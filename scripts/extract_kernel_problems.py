"""KERNEL POINT (중3-1 기말 단원별) 문제 클립 추출.

src: /Users/youngwoolee/Downloads/중3-1 기말대비교재 (단원별).pdf
라벨: Haansoft-Batang 15pt + "N." 패턴
2단 페이지 (좌 x≈42, 우 x≈309). 한 페이지 4문제 (좌상-좌하-우상-우하).
챕터 경계: 1~134 = 이차방정식, 135~323 = 이차함수.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = Path("/Users/youngwoolee/Downloads/중3-1 기말대비교재 (단원별).pdf")
OUT_DIR = ROOT / "output" / "kernel_point"
OUT_DIR.mkdir(parents=True, exist_ok=True)
META_JSON = OUT_DIR / "problems_meta.json"

PAGE_W = 595.0
PAGE_H = 842.0

# 본문 클립 (가운데 점선·우측 데코 안전하게 안쪽)
COL_LEFT_X0 = 32.0
COL_LEFT_X1 = 290.0
COL_RIGHT_X0 = 300.0
COL_RIGHT_X1 = 558.0
COL_TOP_Y = 56.0
COL_BOTTOM_Y = 790.0

# 라벨 위치 검증
X_OK_LEFT = (35.0, 70.0)
X_OK_RIGHT = (300.0, 335.0)

# 챕터 분기
CHAPTERS = [
    {"roman": "I",  "name": "이차방정식",
     "eng": "QUADRATIC EQUATIONS", "short": "이차방정식",
     "start": 1, "end": 134},
    {"roman": "II", "name": "이차함수",
     "eng": "QUADRATIC FUNCTIONS",  "short": "이차함수",
     "start": 135, "end": 323},
]

TOTAL = 323
PROBLEM_PAGES = list(range(0, 84))   # 본문 페이지 (0-83)
QUICK_ANSWER_PAGES = list(range(85, 94))  # 빠른정답 페이지 (85-93)


def find_labels(page: fitz.Page) -> list[tuple[fitz.Rect, int]]:
    """Haansoft-Batang 15pt 'N.' 라벨 검출."""
    out = []
    for blk in page.get_text("dict")["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                fnt = sp["font"]
                sz = sp["size"]
                t = sp["text"].strip()
                bb = sp["bbox"]
                if "Haansoft" not in fnt:
                    continue
                if not (14.0 < sz < 16.0):
                    continue
                m = re.fullmatch(r"(\d+)\.", t)
                if not m:
                    continue
                x0 = bb[0]
                in_left = X_OK_LEFT[0] <= x0 <= X_OK_LEFT[1]
                in_right = X_OK_RIGHT[0] <= x0 <= X_OK_RIGHT[1]
                if not (in_left or in_right):
                    continue
                n = int(m.group(1))
                if 1 <= n <= TOTAL:
                    out.append((fitz.Rect(*bb), n))
    return out


def column_of(rect: fitz.Rect) -> str:
    return "L" if rect.x0 < 200 else "R"


def chapter_for(num: int) -> int:
    for i, ch in enumerate(CHAPTERS):
        if ch["start"] <= num <= ch["end"]:
            return i
    return -1


def col_x_range(col: str) -> tuple[float, float]:
    if col == "L":
        return COL_LEFT_X0, COL_LEFT_X1
    return COL_RIGHT_X0, COL_RIGHT_X1


def main():
    doc = fitz.open(str(SRC_PDF))

    # 1) 모든 라벨을 reading order 로 수집
    # reading order: 페이지순 → 컬럼(L<R) → y순
    all_labels = []  # [(src_pg, col, rect, n)]
    for src_pg in PROBLEM_PAGES:
        page = doc[src_pg]
        for rect, n in find_labels(page):
            all_labels.append((src_pg, column_of(rect), rect, n))
    all_labels.sort(key=lambda x: (x[0], 0 if x[1] == "L" else 1, x[2].y0))

    # 2) 각 라벨의 본문 영역 = 자기 위치 → 다음 라벨 직전까지의 reading-order 영역.
    # same col same page → clip 1개
    # diff col same page → clip 2개 (현재 col 끝 + 다음 col 시작)
    # diff page → clip 2개 (현재 페이지 컬럼 끝까지 + 다음 페이지 첫 컬럼)
    problems = []
    n_all = len(all_labels)
    for i, (src_pg, col, rect, n) in enumerate(all_labels):
        cx0, cx1 = col_x_range(col)
        clips = []
        if i + 1 < n_all:
            nxt_pg, nxt_col, nxt_rect, _ = all_labels[i + 1]
        else:
            nxt_pg, nxt_col, nxt_rect = -1, None, None

        if nxt_pg == src_pg and nxt_col == col:
            # same col same page
            y_top = rect.y0 - 1.0
            y_bot = nxt_rect.y0 - 3.0
            clips.append([cx0, y_top, cx1, y_bot])
        elif nxt_pg == src_pg and nxt_col != col:
            # same page, col changes → 현재 컬럼 끝 + 다음 컬럼 시작
            y_top = rect.y0 - 1.0
            clips.append([cx0, y_top, cx1, COL_BOTTOM_Y])
            ncx0, ncx1 = col_x_range(nxt_col)
            clips.append([ncx0, COL_TOP_Y, ncx1, nxt_rect.y0 - 3.0])
        else:
            # 다음 라벨이 다른 페이지 → 현재 페이지 컬럼 끝 + (있다면) 다음 페이지 첫 컬럼
            y_top = rect.y0 - 1.0
            clips.append([cx0, y_top, cx1, COL_BOTTOM_Y])
            # 만약 현재 col=L 이면 같은 페이지 우측 컬럼도 본문 일부
            if col == "L" and nxt_pg != src_pg:
                # 우측 컬럼 전체 (자기 페이지에서 우측 컬럼에 다른 라벨이 _없는_ 경우만)
                # — 보통 같은 페이지에 다른 컬럼 라벨이 있으므로 위 elif 에서 처리됨.
                # 만약 R 컬럼 라벨이 없다면 R 컬럼은 062 의 본문 연속
                pass
            if nxt_pg != -1:
                ncx0, ncx1 = col_x_range(nxt_col)
                clips.append([ncx0, COL_TOP_Y, ncx1, nxt_rect.y0 - 3.0])

        problems.append({
            "label": f"{n:03d}",
            "local": n,
            "chapter_idx": chapter_for(n),
            "src_pdf": str(SRC_PDF),
            "src_page": src_pg,
            "clips": clips,
            "label_bbox": [rect.x0, rect.y0, rect.x1, rect.y1],
        })

    problems.sort(key=lambda p: p["local"])
    print(f"Total: {len(problems)} (expected {TOTAL})")

    # 챕터별 카운트
    for i, ch in enumerate(CHAPTERS):
        n = sum(1 for p in problems if p["chapter_idx"] == i)
        expected = ch["end"] - ch["start"] + 1
        print(f"  {ch['roman']:>3} {ch['name']:<12} expected={expected:3d} found={n:3d}")

    META_JSON.write_text(json.dumps(problems, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] {META_JSON}")
    doc.close()


if __name__ == "__main__":
    main()
