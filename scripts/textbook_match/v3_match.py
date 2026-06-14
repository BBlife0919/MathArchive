"""시험문제 ↔ 모든 교재 페이지 텍스트 매칭으로 후보 추출.

각 시험문제마다 모든 교재 페이지 텍스트와 token_set_ratio 비교 → top-20 페이지 후보.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from rapidfuzz import fuzz

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')

LATEX_TOK = {
    r'\\log': ' log ', r'\\ln': ' log ', r'\\sin': ' sin ', r'\\cos': ' cos ',
    r'\\tan': ' tan ', r'\\sqrt': ' sqrt ', r'\\pi': ' pi ', r'\\theta': ' theta ',
    r'\\dfrac|\\frac': ' frac ', r'\\circ': ' deg ', r'\\sum': ' sum ',
}


def latex_to_plain(t: str) -> str:
    if not t:
        return ''
    for pat, rep in LATEX_TOK.items():
        t = re.sub(pat, rep, t)
    t = re.sub(r'\\[a-zA-Z]+', ' ', t)
    t = t.replace('$', ' ').replace('{', ' ').replace('}', ' ').replace('^', ' ').replace('_', ' ')
    return t


def normalize(text: str, is_latex: bool = False) -> str:
    t = latex_to_plain(text) if is_latex else (text or '')
    parts = []
    parts += re.findall(r'[가-힣]+', t)
    parts += re.findall(r'[a-zA-Z]{2,}', t.lower())
    parts += re.findall(r'[0-9]+', t)
    return ' '.join(parts)


def load_textbook_pages() -> list[dict]:
    """모든 교재 페이지 텍스트를 평탄화하여 corpus 구축."""
    pages = []
    for jf in (ROOT / 'pages_ocr').glob('*/pages.json'):
        data = json.loads(jf.read_text())
        meta = data['meta']
        for p in data['pages']:
            text = p.get('text', '')
            if not text or len(text.strip()) < 20:
                continue
            pages.append({
                'tb_key': meta['key'],
                'tb_short': meta['short'],
                'tb_label': meta['label'],
                'page': p['page'],
                'text': text,
                'norm': normalize(text),
            })
    return pages


def match_school(school: str, corpus: list[dict], topk: int = 20) -> list[dict]:
    src = json.load(open(ROOT / f'exam_input/{school}.json'))
    results = []
    for q in src['questions']:
        qtext = q.get('question_text', '') or q.get('q_text_ocr', '')
        choices_text = ' '.join(c.get('text', '') for c in (q.get('choices') or []))
        full = qtext + ' ' + choices_text
        qn = normalize(full, is_latex=True)
        if len(qn) < 4:
            results.append({'q_no': q.get('question_number', q.get('q_no', 0)), 'q_text': qtext, 'q_choices': q.get('choices', []), 'q_chapter': q.get('chapter', ''), 'top': []})
            continue
        scored = []
        for c in corpus:
            if not c['norm']:
                continue
            s = fuzz.token_set_ratio(qn, c['norm'])
            scored.append((s, c))
        scored.sort(key=lambda x: -x[0])
        top = scored[:topk]
        results.append({
            'q_no': q.get('question_number', q.get('q_no', 0)),
            'q_text': qtext,
            'q_choices': q.get('choices', []),
            'q_chapter': q.get('chapter', ''),
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
    return results


def main():
    corpus = load_textbook_pages()
    print(f'corpus: {len(corpus)} pages from {len(set(c["tb_key"] for c in corpus))} textbooks')
    out = {}
    for school in ['광명고', '광명북고', '광문고', '명문고']:
        res = match_school(school, corpus, topk=20)
        out[school] = res
        # 짧은 요약
        with_top = sum(1 for r in res if r['top'] and r['top'][0]['score'] > 50)
        print(f'  {school}: {len(res)} questions, {with_top} with strong text candidates')
    (ROOT / 'text_candidates.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print('wrote text_candidates.json')


if __name__ == '__main__':
    main()
