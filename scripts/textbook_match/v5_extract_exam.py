"""새 시험 PDF (텍스트 레이어 있음)에서 문제 번호 위치로 자동 bbox 추출 + 크롭.

문제 시작 패턴: "1)" "2)" "3)" 등.
서답형: "[서답형 1]" 같은 별도 패턴.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
import fitz
from PIL import Image

ROOT_V5 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v5')
ROOT_V5.mkdir(parents=True, exist_ok=True)
EX_PAGES = ROOT_V5 / 'exam_pages'
EX_CROPS = ROOT_V5 / 'exam_crops'
EX_PAGES.mkdir(exist_ok=True)
EX_CROPS.mkdir(exist_ok=True)

SCHOOLS = {
    '광명고': ('/Users/youngwoolee/Downloads/광명고2.pdf', 'paren'),
    '광명북고': ('/Users/youngwoolee/Downloads/광명북고2.pdf', 'dot'),
}


def find_problem_positions(pdf_path: str, label_style: str = 'paren') -> list[dict]:
    """문제 번호별 (page, x, y) 위치 추출.

    label_style: 'paren' = "1)" "2)" / 'dot' = "1." "2." / 'auto' = 둘 다 시도
    """
    doc = fitz.open(pdf_path)
    items = []
    styles = [label_style] if label_style != 'auto' else ['paren', 'dot']
    for pi in range(doc.page_count):
        page = doc.load_page(pi)
        for q in range(1, 30):
            for st in styles:
                label = f'{q})' if st == 'paren' else f'{q}. '
                rects = page.search_for(label)
                # dot 의 경우 본문 중간의 "1." 도 잡힐 수 있음 → x가 페이지 좌측 영역 + 라인 시작에 가까운 것만
                for r in rects:
                    if st == 'dot' and r.x0 > page.rect.width * 0.6:
                        continue  # 본문 우측은 보통 라인 시작이 아님
                    items.append({
                        'q_no': q,
                        'page_idx': pi,
                        'x': r.x0,
                        'y': r.y0,
                        'page_w': page.rect.width,
                        'page_h': page.rect.height,
                    })
                if rects:
                    break  # 한 스타일에서 잡혔으면 다른 스타일 시도 X
        # 서답형
        for q in range(1, 10):
            for label in [f'[서답형 {q}]', f'서답형 {q}.', f'서답형{q}.']:
                rects = page.search_for(label)
                for r in rects:
                    items.append({
                        'q_no': 100 + q,
                        'page_idx': pi,
                        'x': r.x0,
                        'y': r.y0,
                        'page_w': page.rect.width,
                        'page_h': page.rect.height,
                    })
    doc.close()
    # 같은 q_no 가 여러 번 나오면 (예: 본문 + 해설) 첫 번째(작은 y)만 선택
    by_q = {}
    for it in items:
        key = it['q_no']
        if key not in by_q or (it['page_idx'], it['y']) < (by_q[key]['page_idx'], by_q[key]['y']):
            by_q[key] = it
    return sorted(by_q.values(), key=lambda x: (x['page_idx'], x['y']))


def render_pages(pdf_path: str, school: str, dpi: int = 180):
    doc = fitz.open(pdf_path)
    for i in range(doc.page_count):
        out = EX_PAGES / f'{school}_p{i+1}.png'
        if out.exists():
            continue
        pm = doc.load_page(i).get_pixmap(dpi=dpi)
        pm.save(str(out))
    doc.close()


def crop_problems(school: str, positions: list[dict]):
    """문제 시작 위치 → 다음 문제 시작 위치 직전까지를 bbox로 크롭."""
    # PDF 좌표 → 페이지 PNG 좌표 변환 (DPI 180)
    DPI = 180
    PDF_DPI = 72
    scale = DPI / PDF_DPI

    # 페이지마다 그 페이지의 문제들 모으기
    by_page = {}
    for p in positions:
        by_page.setdefault(p['page_idx'], []).append(p)
    for pi in by_page:
        # 좌상단 (y) 기준 정렬 + 컬럼 (좌/우) 고려
        # 페이지를 좌/우 컬럼으로 분리. 페이지 너비 절반 기준.
        items = by_page[pi]
        if not items:
            continue
        page_w = items[0]['page_w']
        page_h = items[0]['page_h']
        # 컬럼 판정
        for it in items:
            it['col'] = 0 if it['x'] < page_w * 0.45 else 1
        # 컬럼 내 y 순서
        items.sort(key=lambda x: (x['col'], x['y']))

    # 각 문제마다 끝 좌표 계산
    crops_meta = []
    for pi, items in by_page.items():
        page_w = items[0]['page_w']
        page_h = items[0]['page_h']
        page_png = EX_PAGES / f'{school}_p{pi+1}.png'
        img = Image.open(page_png).convert('RGB')
        IW, IH = img.size
        for i, it in enumerate(items):
            col = it['col']
            # 같은 컬럼의 다음 문제 찾기
            next_y = None
            for j in range(i+1, len(items)):
                if items[j]['col'] == col:
                    next_y = items[j]['y']
                    break
            # bbox 좌표 (PDF 단위)
            if col == 0:
                xL = 5
                xR = page_w * 0.5
            else:
                xL = page_w * 0.5
                xR = page_w - 5
            yT = it['y'] - 8  # 문제 라벨 위 여백
            yB = (next_y - 8) if next_y is not None else (page_h - 25)
            # PNG 좌표 변환
            x1 = max(0, int(xL * scale))
            y1 = max(0, int(yT * scale))
            x2 = min(IW, int(xR * scale))
            y2 = min(IH, int(yB * scale))
            crop = img.crop((x1, y1, x2, y2))
            qn = it['q_no']
            qname = f"S{qn-100}" if qn >= 100 else f"{qn:02d}"
            out = EX_CROPS / f'{school}_Q{qname}.png'
            crop.save(out)
            crops_meta.append({
                'school': school,
                'q_no': qn,
                'page': pi + 1,
                'col': col,
                'crop_file': out.name,
            })
    return crops_meta


def main():
    all_meta = []
    for school, (path, style) in SCHOOLS.items():
        print(f'=== {school} ===')
        render_pages(path, school)
        positions = find_problem_positions(path, style)
        print(f'  문제 위치: {len(positions)}개')
        meta = crop_problems(school, positions)
        all_meta.extend(meta)
        print(f'  크롭: {len(meta)}개')
    (ROOT_V5 / 'exam_crops_meta.json').write_text(json.dumps(all_meta, ensure_ascii=False, indent=2))
    print(f'\n총 {len(all_meta)}개 크롭 저장')


if __name__ == '__main__':
    main()
