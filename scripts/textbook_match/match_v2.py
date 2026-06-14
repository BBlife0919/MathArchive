"""정밀 매칭 v2: 교재 crop OCR 텍스트 vs 시험 LaTeX 텍스트.

교재 측 PUA 문제를 OCR로 우회하여 한글+수학 모두 텍스트로 비교.
"""
from __future__ import annotations
import json
import re
from pathlib import Path
from rapidfuzz import fuzz
from difflib import SequenceMatcher

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')

LATEX_TOK_MAP = {
    r'\\log': ' log ',
    r'\\ln': ' log ',
    r'\\sin': ' sin ',
    r'\\cos': ' cos ',
    r'\\tan': ' tan ',
    r'\\sqrt': ' sqrt ',
    r'\\pi': ' pi ',
    r'\\theta': ' theta ',
    r'\\dfrac|\\frac': ' frac ',
    r'\\circ': ' deg ',
    r'\\sum': ' sum ',
    r'\\overline\{(.*?)\}': r' \1 ',
    r'\\mathrm\{(.*?)\}': r' \1 ',
    r'\\left|\\right': ' ',
    r'\\,': ' ',
}


def latex_to_plain(text: str) -> str:
    if not text:
        return ''
    t = text
    for pat, rep in LATEX_TOK_MAP.items():
        t = re.sub(pat, rep, t)
    t = re.sub(r'\\[a-zA-Z]+', ' ', t)
    t = t.replace('$', ' ').replace('{', ' ').replace('}', ' ').replace('^', ' ').replace('_', ' ')
    return t


def normalize(text: str, is_latex: bool = False) -> str:
    """한글 + 수학 ASCII 토큰만 추출 (소문자)."""
    if not text:
        return ''
    t = latex_to_plain(text) if is_latex else text
    parts = []
    parts += re.findall(r'[가-힣]+', t)
    parts += re.findall(r'[a-zA-Z]{2,}', t.lower())
    parts += re.findall(r'[0-9]+', t)
    return ' '.join(parts)


def korean_only(text: str) -> str:
    return ''.join(re.findall(r'[가-힣]+', text))


def kor_lcs_ratio(a: str, b: str) -> float:
    if not a or not b:
        return 0.0
    sm = SequenceMatcher(None, a, b, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    return matched / min(len(a), len(b))


def build_textbook_corpus() -> list[dict]:
    """교재 OCR 텍스트로 corpus 구축."""
    ocr = json.load(open(ROOT / 'textbook_ocr_index.json'))
    tb_idx = json.load(open(ROOT / 'textbooks_index.json'))
    code_to_meta = {}
    for key, info in tb_idx.items():
        for p in info['problems']:
            code_to_meta[p['code']] = {
                'tb_key': key,
                'tb_short': info['meta']['short'],
                'tb_label': info['meta']['label'],
                'page': p['page'],
            }
    corpus = []
    for code, text in ocr.items():
        meta = code_to_meta.get(code, {})
        # [문제] ~ [정답]/[해설] 사이만
        body = text
        m = re.search(r'\[문제\](.*?)(?:\[정답|\[해설|$)', body, re.DOTALL)
        if m:
            body = m.group(1)
        norm = normalize(body)
        kor = korean_only(body)
        corpus.append({
            'code': code,
            'text_ocr': body.strip(),
            'norm': norm,
            'kor': kor,
            **meta,
        })
    return corpus


def score(q_norm, c_norm, q_kor, c_kor) -> dict:
    if not q_norm or not c_norm:
        return {'score': 0.0, 'token': 0.0, 'lcs': 0.0, 'kor': 0}
    s_token = fuzz.token_set_ratio(q_norm, c_norm)
    s_partial = fuzz.partial_ratio(q_norm, c_norm)
    s_lcs = kor_lcs_ratio(q_kor, c_kor) * 100 if (q_kor and c_kor) else 0
    # 한글 길이 가중
    kor_min = min(len(q_kor), len(c_kor))
    kor_w = 1.0 if kor_min >= 12 else (kor_min / 12 if kor_min else 0.3)
    base = 0.30 * s_token + 0.30 * s_partial + 0.40 * s_lcs
    base *= (0.50 + 0.50 * kor_w)
    return {'score': base, 'token': s_token, 'partial': s_partial, 'lcs': s_lcs, 'kor': kor_min}


def match_school(school_fn: str, corpus: list[dict], topk: int = 5) -> list[dict]:
    src = json.load(open(ROOT / 'parsed' / school_fn))
    results = []
    for q in src['questions']:
        qtext = q['question_text'] or ''
        qchoices = q.get('choices') or []
        full = qtext + ' ' + ' '.join(c.get('text', '') for c in qchoices)
        qn = normalize(full, is_latex=True)
        qkor = korean_only(latex_to_plain(full))
        if len(qn) < 4:
            results.append({'q_no': q['question_number'], 'q_text': qtext, 'q_choices': qchoices,
                            'q_chapter': q.get('chapter', ''), 'top': []})
            continue
        scored = []
        for c in corpus:
            if not c['norm']:
                continue
            sc = score(qn, c['norm'], qkor, c['kor'])
            scored.append((sc['score'], sc, c))
        scored.sort(key=lambda x: -x[0])
        top = scored[:topk]
        results.append({
            'q_no': q['question_number'],
            'q_text': qtext,
            'q_choices': qchoices,
            'q_chapter': q.get('chapter', ''),
            'top': [
                {
                    'score': round(sc['score'], 1),
                    'token': round(sc['token'], 1),
                    'lcs': round(sc['lcs'], 1),
                    'partial': round(sc.get('partial', 0), 1),
                    'kor_min': sc['kor'],
                    'tb_key': c['tb_key'],
                    'tb_short': c['tb_short'],
                    'code': c['code'],
                    'page': c['page'],
                    'text_ocr': c['text_ocr'][:300],
                }
                for s, sc, c in top
            ],
        })
    return results


def main():
    corpus = build_textbook_corpus()
    print(f'corpus: {len(corpus)}')
    schools = [
        ('광명고', '광명고.json'),
        ('광명북고', '광명북고_pdf.json'),
        ('광문고', '광문고_pdf.json'),
    ]
    out = {}
    for school, fn in schools:
        res = match_school(fn, corpus, topk=20)
        out[school] = res
        strong = sum(1 for r in res if r['top'] and r['top'][0]['score'] >= 75)
        cand = sum(1 for r in res if r['top'] and 60 <= r['top'][0]['score'] < 75)
        print(f'{school}: 강매칭={strong}, 후보={cand}, 총={len(res)}')
    (ROOT / 'matches_v2.json').write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print('wrote matches_v2.json')


if __name__ == '__main__':
    main()
