"""교재 PDF에서 [문항코드]별 문제 영역만 크롭하여 PNG 저장."""
from __future__ import annotations
import json
from pathlib import Path
import fitz

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
CROP_DIR = ROOT / 'crops_textbook'
CROP_DIR.mkdir(parents=True, exist_ok=True)

TEXTBOOKS = {
    'sk_su1': '/Users/youngwoolee/Downloads/[26008]_EBS 2027학년도 수능특강 수학영역_수학I_(181).pdf',
    'op_high': '/Users/youngwoolee/Downloads/[26477]_EBS 올림포스 고난도 대수(2022 개정)_(346).pdf',
    'op_type': '/Users/youngwoolee/Downloads/[26643]_EBS 올림포스 유형편 대수(2022 개정)_(889).pdf',
}

PAGE_MARGIN = 6  # 좌우 여백 (pt)
TOP_PAD = 10
BOT_PAD = 4


def find_problem_rect(page: fitz.Page, code: str, doc: fitz.Document | None = None) -> tuple[fitz.Rect, int] | None:
    """문항코드 위치에서 [문제]~[정답] 영역을 찾음. (rect, page_idx) 반환.
    같은 페이지 안에 [문제]가 없으면 다음 페이지를 사용."""
    code_rects = page.search_for(code)
    if not code_rects:
        return None
    code_y = code_rects[0].y1
    문제_rects = [r for r in page.search_for('[문제]') if r.y0 >= code_y - 2]
    if 문제_rects:
        p_top = 문제_rects[0].y0
        end_candidates = []
        end_candidates += [r.y0 for r in page.search_for('[정답/모범답안]') if r.y0 > p_top]
        end_candidates += [r.y0 for r in page.search_for('[해설]') if r.y0 > p_top]
        if end_candidates:
            p_bot = min(end_candidates)
        else:
            p_bot = page.rect.height - 5
        page_w = page.rect.width
        return (fitz.Rect(PAGE_MARGIN, max(0, p_top - TOP_PAD), page_w - PAGE_MARGIN, p_bot - BOT_PAD), page.number)
    # 같은 페이지에 [문제]가 없으면: 다음 페이지 상단의 [문제]가 그 문항임
    if doc is None or page.number + 1 >= doc.page_count:
        return None
    nxt = doc.load_page(page.number + 1)
    nxt_문제 = nxt.search_for('[문제]')
    if not nxt_문제:
        return None
    p_top = nxt_문제[0].y0
    end_candidates = []
    end_candidates += [r.y0 for r in nxt.search_for('[정답/모범답안]') if r.y0 > p_top]
    end_candidates += [r.y0 for r in nxt.search_for('[해설]') if r.y0 > p_top]
    if end_candidates:
        p_bot = min(end_candidates)
    else:
        p_bot = nxt.rect.height - 5
    page_w = nxt.rect.width
    return (fitz.Rect(PAGE_MARGIN, max(0, p_top - TOP_PAD), page_w - PAGE_MARGIN, p_bot - BOT_PAD), nxt.number)


def crop_problem(tb_key: str, code: str, page_idx: int, dpi: int = 200) -> Path | None:
    out = CROP_DIR / f'{code}.png'
    if out.exists():
        return out
    doc = fitz.open(TEXTBOOKS[tb_key])
    try:
        candidate_pages = [page_idx, page_idx + 1, page_idx - 1, page_idx + 2]
        result = None
        for pi in candidate_pages:
            if not (0 <= pi < doc.page_count):
                continue
            pg = doc.load_page(pi)
            r = find_problem_rect(pg, code, doc=doc)
            if r:
                result = r
                break
        if result is None:
            return None
        rect, used_page = result
        page = doc.load_page(used_page)
        zoom = dpi / 72
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, clip=rect)
        pix.save(out)
        return out
    finally:
        doc.close()


def main():
    matches = json.load(open(ROOT / 'matches.json'))
    seen = set()
    pending = []
    for school, results in matches.items():
        for r in results:
            for c in r['top']:
                key = (c['tb_key'], c['code'], c['page'])
                if key in seen:
                    continue
                seen.add(key)
                pending.append(key)
    print(f'cropping {len(pending)} unique problems...')
    ok = miss = 0
    for tb_key, code, page in pending:
        out = crop_problem(tb_key, code, page)
        if out:
            ok += 1
        else:
            miss += 1
            print(f'  miss: {tb_key} {code} p{page+1}')
    print(f'done. ok={ok} miss={miss}')


if __name__ == '__main__':
    main()
