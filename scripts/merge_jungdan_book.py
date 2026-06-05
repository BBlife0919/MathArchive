"""중단원 평가(2-2단원) 교재 최종 머지.

구조:
  cover → (챕터 디바이더 + 챕터 본문) × 4 → 정답해설 디바이더 → (챕터 해설) × 4
"""
from __future__ import annotations
from pathlib import Path

import fitz
import json

from extract_jungdan_problems import CHAPTERS

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"

COVER = OUT_DIR / "cover.pdf"
DIVIDERS = OUT_DIR / "dividers.pdf"   # ch1, ch2, ch3, ch4, AK
PROBLEMS = OUT_DIR / "problems_4col.pdf"
SOLUTIONS = OUT_DIR / "solutions_2col.pdf"
QUICK_ANS = OUT_DIR / "quick_answer.pdf"
OUT_PDF = OUT_DIR / "TEXTBOOK_POINT_대수_1학기기말대비.pdf"

PROB_META = OUT_DIR / "problems_meta.json"
SOL_META = OUT_DIR / "solutions_meta.json"


def chapter_page_ranges(meta_json: Path, n_pages_pdf: int) -> dict[int, tuple[int, int]]:
    """meta JSON 의 chapter_idx 와 페이지 구분 위치(레이아웃 빌드 결과) 추정.

    빌드 시 챕터 경계마다 새 페이지를 강제하므로, 페이지 인덱스를 차례로 챕터에
    매핑하려면 빌드와 같은 로직을 복원해야 한다 — 여기서는 각 빌더 출력을 그대로
    insert_pdf 로 챕터 단위로 자른다.
    """
    raise NotImplementedError


def main():
    out = fitz.open()
    cover = fitz.open(str(COVER))
    div = fitz.open(str(DIVIDERS))
    probs = fitz.open(str(PROBLEMS))
    sols = fitz.open(str(SOLUTIONS))

    n_ch = len(CHAPTERS)

    # 빌드된 problems_2col 의 챕터 페이지 경계 — build_jungdan_book.py 가 page_breaks 출력
    # 다시 추적: meta 에서 chapter_idx 변경 시 새 페이지. 동일 챕터 안에서는 2문제/페이지.
    pmeta = json.loads(PROB_META.read_text(encoding="utf-8"))
    smeta = json.loads(SOL_META.read_text(encoding="utf-8"))

    def chapter_page_breaks(meta: list[dict], total_pages: int,
                            per_page: int | None = None) -> dict[int, int]:
        """chapter_idx 가 바뀌는 시점의 페이지 인덱스 추정."""
        if per_page in (2, 4):
            # build_jungdan_book4.py 와 동일 로직 (각 페이지마다 같은 chapter 의 문제만 채움)
            pages = []
            i = 0
            while i < len(meta):
                ch = meta[i]["chapter_idx"]
                pages.append(ch)
                # 한 페이지에 per_page 개의 same-chapter 문제 채우기
                placed = 1
                while placed < per_page and i + 1 < len(meta) and meta[i + 1]["chapter_idx"] == ch:
                    i += 1
                    placed += 1
                i += 1
            breaks = {}
            for pi, ch in enumerate(pages):
                if ch not in breaks:
                    breaks[ch] = pi
            return breaks
        else:
            # build_jungdan_solutions.py 와 동일하게는 추정 불가 — 별도 로직 필요
            # 여기서는 빌더가 인쇄한 값에 의존하지 말고 chapter 별 다시 빌드 안 함.
            raise NotImplementedError

    # build 가 저장한 정확한 chapter→page 매핑 사용
    prob_breaks_path = OUT_DIR / "problems_page_breaks.json"
    if prob_breaks_path.exists():
        raw = json.loads(prob_breaks_path.read_text(encoding="utf-8"))
        prob_breaks = {int(k): v for k, v in raw.items()}
    else:
        prob_breaks = chapter_page_breaks(pmeta, len(probs), per_page=4)
    # solutions: stack 기반이라 추적 어려움 — solutions 빌더가 챕터 바뀌면 새 페이지 시작하므로
    # solutions_2col.pdf 의 각 페이지 헤더를 보고 매핑하지 말고, 해설 클립을 직접 머지
    # 하지 말고 챕터 단위로 페이지 범위를 별도 계산.
    # 간단한 방법: solutions_meta 의 같은 chapter_idx 가 그룹별로 몇 페이지 걸치는지 카운트.
    # build_jungdan_solutions.py 가 출력한 page_breaks 값을 캐싱하지 않았으므로 다시 호출.

    # 더 안전한 접근: solutions_2col 의 페이지마다 헤더에서 PART 표기를 추출하는 대신
    # solutions builder 가 출력한 chapter_breaks 를 다시 import 실행 결과를 활용.
    # 여기선 간단히 build_jungdan_solutions 모듈을 import 해서 page_breaks 를 직접 산출.

    from build_jungdan_solutions import (
        CHAPTERS as _C, COL_BOTTOM, COL_TOP, COL_W, LABEL_H, PAGE_W as _PW,  # noqa
        SOL_GAP,
    )

    def solution_page_breaks(meta: list[dict]) -> dict[int, int]:
        """build_jungdan_solutions.py 의 페이지 시작 로직을 다시 재현."""
        page_breaks: dict[int, int] = {}
        n_pages = 0
        col_idx = 0
        col_y = COL_TOP
        cur_ch = None
        for sol in meta:
            ch = sol["chapter_idx"]
            cx0, cy0, cx1, cy1 = sol["clip"]
            src_h = cy1 - cy0
            src_w = cx1 - cx0
            scale = COL_W / src_w
            target_h = src_h * scale

            if ch != cur_ch:
                # 새 페이지
                n_pages += 1
                col_idx = 0
                col_y = COL_TOP
                cur_ch = ch
                if ch not in page_breaks:
                    page_breaks[ch] = n_pages - 1

            remaining = COL_BOTTOM - col_y - LABEL_H
            if target_h > remaining:
                if col_idx == 0:
                    col_idx = 1
                    col_y = COL_TOP
                    remaining = COL_BOTTOM - col_y - LABEL_H
                else:
                    n_pages += 1
                    col_idx = 0
                    col_y = COL_TOP
                    remaining = COL_BOTTOM - col_y - LABEL_H
            if target_h > remaining:
                scale = remaining / src_h
                target_h = src_h * scale
            col_y += LABEL_H + target_h + SOL_GAP
        return page_breaks

    sol_breaks = solution_page_breaks(smeta)
    print(f"Problem chapter breaks: {prob_breaks}")
    print(f"Solution chapter breaks: {sol_breaks}")

    # 1) Cover
    out.insert_pdf(cover)

    # 2) Chapter dividers + problems
    for ch_idx in range(n_ch):
        out.insert_pdf(div, from_page=ch_idx, to_page=ch_idx)
        # problems 페이지 범위
        p_start = prob_breaks[ch_idx]
        p_end = (prob_breaks[ch_idx + 1] - 1) if (ch_idx + 1) in prob_breaks else (len(probs) - 1)
        out.insert_pdf(probs, from_page=p_start, to_page=p_end)

    # 3) Solution divider (dividers 의 마지막 페이지 = AK)
    out.insert_pdf(div, from_page=len(div) - 1, to_page=len(div) - 1)

    # 4) Solutions (챕터별 페이지 범위 차례로)
    for ch_idx in range(n_ch):
        s_start = sol_breaks[ch_idx]
        s_end = (sol_breaks[ch_idx + 1] - 1) if (ch_idx + 1) in sol_breaks else (len(sols) - 1)
        out.insert_pdf(sols, from_page=s_start, to_page=s_end)

    cover.close()
    div.close()
    probs.close()
    sols.close()

    n_pages = len(out)
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    out.close()
    print(f"[OK] Final PDF: {OUT_PDF}")
    print(f"  Total pages: {n_pages}")


if __name__ == "__main__":
    main()
