"""중단원 평가(2-2단원)_merged.pdf — p28-33 제외 + 해설 뒤로 + SUMMIT POINT 라벨 스타일.

원본 PDF 구조 (1-indexed):
  학습 자료집:
    p1-3   : Ⅱ-2 문제
    p4     : Ⅱ-2 빠른답
    p5     : Ⅱ-2 풀이
    p6-8   : Ⅲ-1 문제
    p9     : Ⅲ-1 빠른답
    p10    : Ⅲ-1 풀이
    p11-14 : Ⅲ-2 문제
    p15    : Ⅲ-2 빠른답
    p16-18 : Ⅲ-2 풀이
    p19-22 : Ⅲ-3 문제
    p23    : Ⅲ-3 빠른답
    p24-25 : Ⅲ-3 풀이
  중단원 평가 본문:
    p26    : Ⅱ 표지 (삼각함수)
    p27    : 성취기준
    p28-30 : 1. 삼각함수 ①회   ← 제외
    p31-33 : 1. 삼각함수 ②회   ← 제외
    p34    : 성취기준 (사인법칙)
    p35-37 : 2. 사인법칙 ①회
    p38-40 : 2. 사인법칙 ②회
    p41    : Ⅲ 표지 (수열)
    p42    : 성취기준
    p43-45 : 1. 등차/등비 ①회
    p46-48 : 1. 등차/등비 ②회
    p49    : 성취기준
    p50-51 : 2. 수열의 합 ①회
    p52-53 : 2. 수열의 합 ②회
    p54    : 성취기준
    p55-56 : 3. 수학적 귀납법 ①회
    p57-58 : 3. 수학적 귀납법 ②회
  중단원 평가 해설:
    p59    : 정답 표지 Ⅱ
    p60-64 : 1. 삼각함수 ①회+②회 풀이   ← 제외
    p65-66 : 사인법칙 ①회
    p67-68 : 사인법칙 ②회
    p69    : 정답 표지 Ⅲ
    p70-71 : 등차/등비 ①회
    p72-73 : 등차/등비 ②회
    p74-?  : 수열의 합 ①회
    ...

출력 순서:
  [본문] = 학습자료집 문제 (Ⅱ-2, Ⅲ-1, Ⅲ-2, Ⅲ-3) + 중단원평가 문제 (삼각함수 제외)
  [해설] = 학습자료집 해설 (4세트) + 중단원평가 해설 (삼각함수 제외)
"""
from __future__ import annotations

import re
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = Path("/Users/youngwoolee/Downloads/중단원 평가(2-2단원)_merged.pdf")
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "JUNGDAN_EVAL_2_2.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

LABEL_FONT_NAME = "aggro"
LABEL_FONT_FILE = FONT_AGGRO
LABEL_COLOR = (240 / 255, 125 / 255, 35 / 255)   # SUMMIT POINT orange

_label_font = fitz.Font(fontfile=LABEL_FONT_FILE)

# 0-indexed 페이지 시퀀스
# 학습자료집 문제 (총 14 페이지)
JAJALYO_PROBLEMS = (
    list(range(0, 3))    # Ⅱ-2 문제 (p1-3)
    + list(range(5, 8))  # Ⅲ-1 문제 (p6-8)
    + list(range(10, 14)) # Ⅲ-2 문제 (p11-14)
    + list(range(18, 22)) # Ⅲ-3 문제 (p19-22)
)

# 중단원 평가 본문 — p28-33 (1. 삼각함수) 제외
JUNGDAN_PROBLEMS = (
    list(range(25, 27))    # Ⅱ 표지 + 성취기준 (p26-27)
    + list(range(33, 58))  # p34-58 (사인법칙 + Ⅲ 수열 전체)
)

# 학습자료집 해설 (빠른답 + 풀이)
JAJALYO_SOLUTIONS = (
    [3, 4]      # Ⅱ-2 빠른답+풀이 (p4-5)
    + [8, 9]    # Ⅲ-1 빠른답+풀이 (p9-10)
    + [14, 15, 16, 17]  # Ⅲ-2 빠른답+풀이 (p15-18)
    + [22, 23, 24]      # Ⅲ-3 빠른답+풀이 (p23-25)
)

# 중단원 평가 해설 — p60-64 (1. 삼각함수 풀이) 제외
JUNGDAN_SOLUTIONS = (
    [58]                # Ⅱ 정답표지 (p59)
    + list(range(64, 68))  # 사인법칙 풀이 (p65-68)
    + [68]              # Ⅲ 정답표지 (p69)
    + list(range(69, 80))  # Ⅲ 수열 풀이 (p70-80)
)


def _find_eval_labels(page) -> list[tuple[fitz.Rect, str]]:
    """중단원 평가 문제 라벨 (YJ BONMOKGAK Medium ~14pt) 위치 찾기."""
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
                # 라벨 위치 검증: 좌측 컬럼 (x ≈ 42) 또는 우측 컬럼 (x ≈ 294)
                x0 = sp["bbox"][0]
                if not (35 <= x0 <= 55 or 285 <= x0 <= 310):
                    continue
                out.append((fitz.Rect(*sp["bbox"]), t))
    return out


def _find_jajalyo_problem_labels(page) -> list[tuple[fitz.Rect, str]]:
    """학습자료집 라벨 (H2gtrE 14.76, "0N" 두 span 으로 쪼개진 형태) 찾기."""
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

    # 같은 baseline 인접 span 합치기
    cands.sort(key=lambda x: (round(x[0][1], 1), x[0][0]))
    used = [False] * len(cands)
    out = []
    for i, (bb, t) in enumerate(cands):
        if used[i]:
            continue
        merged_text = t
        merged_bb = list(bb)
        for j in range(i + 1, len(cands)):
            if used[j]:
                continue
            bb2, t2 = cands[j]
            # 같은 baseline (y0 차이 < 1pt) 이고 인접 (gap < 2pt)
            if abs(bb2[1] - bb[1]) > 1.0:
                continue
            if bb2[0] - merged_bb[2] > 2.0:
                continue
            merged_text += t2
            merged_bb[2] = bb2[2]
            merged_bb[1] = min(merged_bb[1], bb2[1])
            merged_bb[3] = max(merged_bb[3], bb2[3])
            used[j] = True
        used[i] = True
        if not re.fullmatch(r"\d{1,3}", merged_text):
            continue
        # 라벨 위치: 좌측 (x≈33) 또는 우측 (x≈291)
        x0 = merged_bb[0]
        if not (25 <= x0 <= 55 or 285 <= x0 <= 315):
            continue
        num = int(merged_text)
        if not (1 <= num <= 30):
            continue
        out.append((fitz.Rect(*merged_bb), merged_text))
    return out


def _replace_label_in_place(page, rect: fitz.Rect, new_text: str, size: float = 14.0):
    """기존 라벨 위치에 흰색 덮기 + 새 라벨(orange SB 어그로) 삽입."""
    pad = 1.0
    new_w = _label_font.text_length(new_text, fontsize=size)
    cover = fitz.Rect(
        rect.x0 - pad,
        rect.y0 - pad,
        max(rect.x1, rect.x0 + new_w) + pad,
        rect.y1 + pad,
    )
    page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
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

    # 1) 학습자료집 문제
    for src_idx in JAJALYO_PROBLEMS:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)
    # 2) 중단원 평가 문제
    for src_idx in JUNGDAN_PROBLEMS:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)
    n_problem_pages = len(out)

    # 3) 학습자료집 해설
    for src_idx in JAJALYO_SOLUTIONS:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)
    # 4) 중단원 평가 해설
    for src_idx in JUNGDAN_SOLUTIONS:
        out.insert_pdf(src, from_page=src_idx, to_page=src_idx)

    src.close()

    # 5a) 라벨 리스타일링 — 학습자료집 문제 페이지
    n_relabeled_jaja = 0
    for j, src_idx in enumerate(JAJALYO_PROBLEMS):
        page = out[j]
        labels = _find_jajalyo_problem_labels(page)
        for rect, old in labels:
            _replace_label_in_place(page, rect, f"{int(old):02d}", size=14.0)
            n_relabeled_jaja += 1

    # 5b) 라벨 리스타일링 — 중단원 평가 문제 페이지
    n_jajalyo = len(JAJALYO_PROBLEMS)
    # 표지/성취기준 page indexes (원본 0-indexed): 25(표지Ⅱ), 26(성취), 33(성취), 40(표지Ⅲ), 41(성취), 48(성취), 53(성취)
    cover_pages = {25, 26, 33, 40, 41, 48, 53}

    n_relabeled_eval = 0
    for j, src_idx in enumerate(JUNGDAN_PROBLEMS):
        if src_idx in cover_pages:
            continue
        page = out[n_jajalyo + j]
        labels = _find_eval_labels(page)
        for rect, old in labels:
            _replace_label_in_place(page, rect, f"{int(old):02d}", size=14.0)
            n_relabeled_eval += 1

    out.save(str(OUT_PDF), garbage=4, deflate=True)
    n_pages = len(out)
    out.close()

    print(f"[OK] {OUT_PDF}")
    print(f"  총 페이지: {n_pages}")
    print(f"    본문: {n_problem_pages}p, 해설: {n_pages - n_problem_pages}p")
    print(f"  리스타일링된 라벨: 학습자료집 {n_relabeled_jaja} + 중단원평가 {n_relabeled_eval} = {n_relabeled_jaja + n_relabeled_eval}")


if __name__ == "__main__":
    main()
