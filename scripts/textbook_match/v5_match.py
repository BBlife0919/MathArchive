"""v5 매칭 - 새 시험 PDF 텍스트 + 확장된 교재(28개) corpus.

시험 텍스트는 PDF 텍스트 레이어 직접 추출 (LaTeX/PUA 없이 한글+선지+ASCII 깔끔).
매칭은 페이지 단위 token_set_ratio 후보 → top-20.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from rapidfuzz import fuzz
import fitz

ROOT_V3 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
ROOT_V5 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v5')

SCHOOLS = {
    '광명고': ('/Users/youngwoolee/Downloads/광명고2.pdf', 'paren'),
    '광명북고': ('/Users/youngwoolee/Downloads/광명북고2.pdf', 'dot'),
}

LATEX_TOK = {r'\\log': ' log ', r'\\sin': ' sin ', r'\\cos': ' cos ', r'\\tan': ' tan ',
             r'\\sqrt': ' sqrt ', r'\\pi': ' pi ', r'\\theta': ' theta '}


def normalize(text: str) -> str:
    t = text or ''
    for pat, rep in LATEX_TOK.items():
        t = re.sub(pat, rep, t)
    parts = []
    parts += re.findall(r'[가-힣]+', t)
    parts += re.findall(r'[a-zA-Z]{2,}', t.lower())
    parts += re.findall(r'[0-9]+', t)
    return ' '.join(parts)


def extract_exam_problems(pdf_path: str, school: str, style: str) -> list[dict]:
    """시험 PDF에서 문제별 텍스트 + 위치 추출."""
    doc = fitz.open(pdf_path)
    items = []
    for pi in range(doc.page_count):
        page = doc.load_page(pi)
        for q in range(1, 30):
            label = f'{q})' if style == 'paren' else f'{q}. '
            rects = page.search_for(label)
            for r in rects:
                if style == 'dot' and r.x0 > page.rect.width * 0.6:
                    continue
                items.append({
                    'q_no': q, 'page_idx': pi,
                    'x': r.x0, 'y': r.y0,
                    'page_w': page.rect.width, 'page_h': page.rect.height,
                })
                break
        for q in range(1, 10):
            for lab in [f'[서답형 {q}]', f'서답형 {q}.', f'서답형{q}.']:
                rects = page.search_for(lab)
                if rects:
                    r = rects[0]
                    items.append({
                        'q_no': 100 + q, 'page_idx': pi,
                        'x': r.x0, 'y': r.y0,
                        'page_w': page.rect.width, 'page_h': page.rect.height,
                    })
                    break
    # 같은 q_no 중복 첫 번째 (페이지 작은, y 작은)
    by_q = {}
    for it in items:
        k = it['q_no']
        if k not in by_q or (it['page_idx'], it['y']) < (by_q[k]['page_idx'], by_q[k]['y']):
            by_q[k] = it
    sorted_items = sorted(by_q.values(), key=lambda x: x['q_no'])

    # 다음 문제 시작 위치까지의 텍스트 추출
    # 동일 페이지 내 같은 컬럼 정렬 후 인접 문제로 경계 설정
    by_page = {}
    for it in sorted_items:
        by_page.setdefault(it['page_idx'], []).append(it)
    for pi, lst in by_page.items():
        page_w = lst[0]['page_w']
        for it in lst:
            it['col'] = 0 if it['x'] < page_w * 0.45 else 1
        lst.sort(key=lambda x: (x['col'], x['y']))

    # 텍스트 추출 (PyMuPDF textbox)
    problems = []
    for it in sorted_items:
        page = doc.load_page(it['page_idx'])
        page_w = it['page_w']
        page_h = it['page_h']
        col = it['col']
        # 같은 컬럼의 다음 문제 y
        col_items = [x for x in by_page[it['page_idx']] if x['col'] == col]
        next_y = None
        for x in col_items:
            if x['y'] > it['y']:
                next_y = x['y']
                break
        xL = 5 if col == 0 else page_w * 0.5
        xR = page_w * 0.5 if col == 0 else page_w - 5
        yT = it['y'] - 5
        yB = (next_y - 5) if next_y else (page_h - 25)
        clip = fitz.Rect(xL, yT, xR, yB)
        text = page.get_text(clip=clip)
        # 페이지 끝에서 다음 페이지 같은 컬럼 시작이 있으면 합치기
        # (간단히 같은 페이지만 처리)
        problems.append({
            'school': school,
            'q_no': it['q_no'],
            'q_name': f"서답형{it['q_no']-100}" if it['q_no'] >= 100 else str(it['q_no']),
            'page': it['page_idx'] + 1,
            'text': text.strip(),
        })
    doc.close()
    return problems


def load_corpus() -> list[dict]:
    pages = []
    for jf in (ROOT_V3 / 'pages_ocr').glob('*/pages.json'):
        data = json.loads(jf.read_text())
        meta = data['meta']
        for p in data['pages']:
            t = p.get('text', '')
            if not t or len(t.strip()) < 20:
                continue
            pages.append({
                'tb_key': meta['key'],
                'tb_short': meta['short'],
                'tb_label': meta['label'],
                'page': p['page'],
                'text': t,
                'norm': normalize(t),
            })
    return pages


def main():
    ROOT_V5.mkdir(parents=True, exist_ok=True)
    corpus = load_corpus()
    print(f'corpus: {len(corpus)} pages, {len(set(c["tb_key"] for c in corpus))} textbooks')

    all_results = {}
    for school, (path, style) in SCHOOLS.items():
        probs = extract_exam_problems(path, school, style)
        print(f'\n=== {school}: {len(probs)} problems ===')
        results = []
        for q in probs:
            qn = normalize(q['text'])
            if len(qn) < 4:
                results.append({**q, 'top': []})
                continue
            scored = []
            for c in corpus:
                if not c['norm']:
                    continue
                s = fuzz.token_set_ratio(qn, c['norm'])
                scored.append((s, c))
            scored.sort(key=lambda x: -x[0])
            top = scored[:20]
            results.append({
                **q,
                'top': [
                    {
                        'score': round(s, 1),
                        'tb_key': c['tb_key'],
                        'tb_short': c['tb_short'],
                        'tb_label': c['tb_label'],
                        'page': c['page'],
                        'text': c['text'][:300],
                    }
                    for s, c in top
                ],
            })
        all_results[school] = results
        print(f'  매칭 후보 추출 완료')
    (ROOT_V5 / 'text_candidates.json').write_text(json.dumps(all_results, ensure_ascii=False, indent=2))
    print('\nwrote text_candidates.json')


if __name__ == '__main__':
    main()
