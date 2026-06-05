"""대수 BASIC POINT(1학기 기말) — p28-33 제외 + 연속 리넘버링 + 해설 뒤에 일괄 배치.

원본 페이지 구조 (1-indexed):
  p1     : 표지
  p2-14  : 단원 표지/개념/문제 (사인법칙, 001-042)
  p15-20 : 수열의 뜻 (043-057)
  p21-27 : 등차수열 part1 (058-077)
  p28-33 : 등차수열 part2 (078-093) + 등비수열 개념   ← 제외
  p34-42 : 등비수열 (094-127)
  p43-48 : 합의 기호 ∑ (128-143)
  p49-59 : 여러 가지 수열의 합 (144-177)
  p60-66 : 수열의 귀납적 정의 (178-195)
  p67-74 : 수학적 귀납법 (196-208)
  p75    : 정답과 해설 표지
  p76-87 : 해설 001-077
  p88-90 : 해설 078-093                              ← 제외
  p91-115: 해설 094-208

리넘버링:
  001-077 → 001-077 (그대로)
  094-208 → 078-192 (-16)

UI (모의고사 정복 스타일):
  - 라벨 폰트: SB 어그로OTF M
  - 라벨 색상: orange (240,125,35)/255
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = Path("/Users/youngwoolee/Downloads/대수 BASIC POINT(1학기 기말).pdf")
OUT_DIR = ROOT / "output" / "basic_point_final"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "BASIC_POINT_대수_1학기기말.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

LABEL_FONT_NAME = "aggro"
LABEL_FONT_FILE = FONT_AGGRO
LABEL_COLOR = (240 / 255, 125 / 255, 35 / 255)   # orange (summit_point 와 동일)

_label_font = fitz.Font(fontfile=LABEL_FONT_FILE)

# 본문 페이지 (0-indexed) — p28-33 제외
PROBLEM_PAGES = list(range(0, 27)) + list(range(33, 74))      # 0-26, 33-73
# 해설 페이지 (0-indexed) — p88-90 제외
SOLUTION_PAGES = list(range(74, 87)) + list(range(90, 115))   # 74-86, 90-114


def renumber(old: int) -> int:
    """원본 문항번호 → 새 문항번호. 094 이상은 -16."""
    if old <= 77:
        return old
    if old >= 94:
        return old - 16
    raise ValueError(f"문항 {old:03d} 은 제외 대상 (078-093)")


def fmt_label(n: int) -> str:
    return f"{n:03d}"


def _find_label_pairs(page) -> list[tuple[fitz.Rect, str]]:
    """페이지에서 DINAlternate-Bold 17 크기의 인접 두 span 쌍을 합쳐 라벨 추출.

    반환: [(전체 bbox, 합쳐진 문자열), ...]
    """
    d = page.get_text("dict")
    candidates = []
    for blk in d["blocks"]:
        if blk.get("type") != 0:
            continue
        for line in blk["lines"]:
            for sp in line["spans"]:
                if "DINAlternate" not in sp["font"]:
                    continue
                if not (16.5 <= sp["size"] <= 17.5):
                    continue
                t = sp["text"]
                if not re.fullmatch(r"\d{1,3}", t):
                    continue
                candidates.append((tuple(sp["bbox"]), t))

    # 같은 baseline(y0 동일) 인 인접 span 페어를 묶기
    # 보통 "00" + "N" 또는 "0" + "NN" 또는 "NNN" 단일
    candidates.sort(key=lambda x: (round(x[0][1], 1), x[0][0]))
    used = [False] * len(candidates)
    pairs = []
    for i, (bb, t) in enumerate(candidates):
        if used[i]:
            continue
        x0, y0, x1, y1 = bb
        merged_text = t
        merged_x1 = x1
        merged_bb = bb
        for j in range(i + 1, len(candidates)):
            if used[j]:
                continue
            bb2, t2 = candidates[j]
            x0b, y0b, x1b, y1b = bb2
            # 같은 baseline 인지 확인 (y0 차이 < 1pt)
            if abs(y0b - y0) > 1.0:
                continue
            # 인접한지 확인 (gap < 2pt)
            if x0b - merged_x1 > 2.0:
                continue
            merged_text += t2
            merged_x1 = x1b
            merged_bb = (merged_bb[0], min(merged_bb[1], y0b),
                         x1b, max(merged_bb[3], y1b))
            used[j] = True
        used[i] = True
        # 라벨 형식 검증 — 1~3자리 숫자
        if re.fullmatch(r"\d{1,3}", merged_text):
            pairs.append((fitz.Rect(*merged_bb), merged_text))
    return pairs


def _replace_label(page, rect: fitz.Rect, new_text: str):
    """기존 라벨 위치에 흰색 덮기 + 새 라벨 삽입.

    좌측 정렬 유지 (원본이 leading-zero 포함 좌측 정렬).
    """
    pad = 1.0
    size = 17.0
    new_w = _label_font.text_length(new_text, fontsize=size)

    # 원본 라벨 위치 흰색으로 가리기 (여유 + 새 라벨 폭 만큼)
    cover = fitz.Rect(
        rect.x0 - pad,
        rect.y0 - pad,
        max(rect.x1, rect.x0 + new_w) + pad,
        rect.y1 + pad,
    )
    page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)

    # 새 라벨 삽입 (baseline 보정)
    baseline_y = rect.y1 - 0.18 * size
    page.insert_text(
        (rect.x0, baseline_y),
        new_text,
        fontname=LABEL_FONT_NAME,
        fontfile=LABEL_FONT_FILE,
        fontsize=size,
        color=LABEL_COLOR,
    )


def main():
    src = fitz.open(str(SRC_PDF))
    out = fitz.open()

    # 1) 본문 페이지 복사
    for src_idx in PROBLEM_PAGES:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)
    # 2) 해설 페이지 복사
    for src_idx in SOLUTION_PAGES:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)

    src.close()

    # 3) 모든 페이지 순회하면서 라벨 리넘버링
    total_relabeled = 0
    excluded_seen = []
    for pi, page in enumerate(out):
        pairs = _find_label_pairs(page)
        for rect, old_text in pairs:
            old_num = int(old_text)
            # 페이지 푸터 번호 등 라벨 외 숫자 필터: 라벨은 페이지 좌/우 컬럼 상단 영역
            # (x 약 34 또는 306, y 다양). 추가 검증: 1-208 범위.
            if not (1 <= old_num <= 208):
                continue
            # 제외 대상 (078-093) — 해설 페이지 통째 제외했으므로 본문에서만 발생할 수 있음
            if 78 <= old_num <= 93:
                excluded_seen.append((pi, old_num))
                continue
            new_num = renumber(old_num)
            _replace_label(page, rect, fmt_label(new_num))
            total_relabeled += 1

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    n_pages = len(out)
    out.close()

    print(f"[OK] {OUT_PDF}")
    print(f"  총 페이지: {n_pages}")
    print(f"  리넘버링된 라벨 수: {total_relabeled}")
    if excluded_seen:
        print(f"  ⚠ 제외 범위 라벨이 본문에 남음: {excluded_seen[:5]} ...")


if __name__ == "__main__":
    main()
