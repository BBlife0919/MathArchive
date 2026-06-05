"""KERNEL POINT 교재 최종 머지.

cover → (챕터 디바이더 + 챕터 본문) × 2 → 정답해설 디바이더 → 빠른정답
"""
from __future__ import annotations
import json
from pathlib import Path

import fitz

from extract_kernel_problems import CHAPTERS

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "kernel_point"

COVER = OUT_DIR / "cover.pdf"
DIVIDERS = OUT_DIR / "dividers.pdf"
PROBLEMS = OUT_DIR / "problems_4col.pdf"
QUICK_ANS = OUT_DIR / "quick_answer.pdf"
OUT_PDF = OUT_DIR / "KERNEL_POINT_3-1_기말대비.pdf"


def main():
    out = fitz.open()
    cover = fitz.open(str(COVER))
    div = fitz.open(str(DIVIDERS))
    probs = fitz.open(str(PROBLEMS))
    qa = fitz.open(str(QUICK_ANS))

    # build 가 저장한 chapter→page 매핑
    pb = json.loads((OUT_DIR / "problems_page_breaks.json").read_text(encoding="utf-8"))
    prob_breaks = {int(k): v for k, v in pb.items()}

    n_ch = len(CHAPTERS)

    # 1) Cover
    out.insert_pdf(cover)

    # 2) 챕터 디바이더 + 본문
    for ch_idx in range(n_ch):
        out.insert_pdf(div, from_page=ch_idx, to_page=ch_idx)
        p_start = prob_breaks[ch_idx]
        p_end = (prob_breaks[ch_idx + 1] - 1) if (ch_idx + 1) in prob_breaks else (len(probs) - 1)
        out.insert_pdf(probs, from_page=p_start, to_page=p_end)

    # 3) 정답해설 디바이더 (마지막 페이지)
    out.insert_pdf(div, from_page=len(div) - 1, to_page=len(div) - 1)

    # 4) 빠른정답
    out.insert_pdf(qa)

    cover.close()
    div.close()
    probs.close()
    qa.close()

    n_pages = len(out)
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    out.close()
    print(f"[OK] {OUT_PDF}")
    print(f"  Total pages: {n_pages}")


if __name__ == "__main__":
    main()
