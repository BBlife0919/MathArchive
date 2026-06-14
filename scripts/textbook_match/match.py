"""시험문제↔교재문제 유사도 매칭 (v3: 한글 LCS + 구조)."""
from __future__ import annotations
import json
import re
from pathlib import Path
from rapidfuzz import fuzz
from difflib import SequenceMatcher

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')

PUA_RE = re.compile(r'[-]')

LATEX_TOK_MAP = {
    r'\\log': ' log ',
    r'\\ln': ' log ',
    r'\\sin': ' sin ',
    r'\\cos': ' cos ',
    r'\\tan': ' tan ',
    r'\\sqrt': ' sqrt ',
    r'\\pi': ' pi ',
    r'\\theta': ' theta ',
    r'\\sum': ' sum ',
    r'\\dfrac|\\frac': ' frac ',
}


def latex_to_tokens(text: str) -> str:
    if not text:
        return ''
    t = text
    for pat, rep in LATEX_TOK_MAP.items():
        t = re.sub(pat, rep, t)
    t = re.sub(r'\\[a-zA-Z]+', ' ', t)
    return t


def korean_only(text: str) -> str:
    return ' '.join(re.findall(r'[가-힣]+', text))


def korean_concat(text: str) -> str:
    return ''.join(re.findall(r'[가-힣]+', text))


def kor_lcs_score(a_kor: str, b_kor: str) -> float:
    """한글 문자열 LCS 비율. 짧은 쪽 기준."""
    if not a_kor or not b_kor:
        return 0.0
    sm = SequenceMatcher(None, a_kor, b_kor, autojunk=False)
    matched = sum(b.size for b in sm.get_matching_blocks())
    shorter = min(len(a_kor), len(b_kor))
    return matched / shorter if shorter else 0.0


def normalize_full(text: str, is_latex: bool) -> str:
    t = text or ''
    if is_latex:
        t = latex_to_tokens(t)
    t = PUA_RE.sub(' ', t)
    parts = []
    parts += re.findall(r'[가-힣]+', t)
    parts += re.findall(r'[a-z]{2,}', t.lower())
    parts += re.findall(r'[0-9]+', t)
    return ' '.join(parts)


def count_choices_textbook(text: str) -> int:
    return len(re.findall(r'[①②③④⑤]', text))


def load_textbooks() -> dict:
    return json.load(open(ROOT / 'textbooks_index.json'))


def build_textbook_corpus():
    tb = load_textbooks()
    corpus = []
    for key, info in tb.items():
        for p in info['problems']:
            txt = p['text']
            corpus.append({
                'tb_key': key,
                'tb_label': info['meta']['label'],
                'tb_short': info['meta']['short'],
                'code': p['code'],
                'page': p['page'],
                'text_orig': txt,
                'norm': normalize_full(txt, is_latex=False),
                'kor': korean_concat(txt),
                'choice_n': count_choices_textbook(txt),
            })
    return corpus


def score(q_norm, c_norm, q_kor, c_kor, q_cn, c_cn) -> dict:
    s_token = fuzz.token_set_ratio(q_norm, c_norm) if q_norm and c_norm else 0
    lcs = kor_lcs_score(q_kor, c_kor) * 100 if q_kor and c_kor else 0
    # 한글 길이 가중: 둘 다 길수록 신뢰
    kor_min = min(len(q_kor), len(c_kor))
    kor_w = 1.0 if kor_min >= 15 else (kor_min / 15)
    base = 0.40 * s_token + 0.60 * lcs
    # 한글 짧으면 점수 신뢰 깎음
    base *= (0.55 + 0.45 * kor_w)
    # 선지 수 페널티
    if q_cn and c_cn and q_cn != c_cn:
        base -= 12
    elif (q_cn == 0) ^ (c_cn == 0):
        base -= 6
    return {
        'score': base,
        's_token': s_token,
        's_lcs': lcs,
        'kor_min': kor_min,
    }


def match_school(school: str, corpus: list[dict], topk: int = 5, src_filename: str | None = None) -> list[dict]:
    if src_filename is None:
        src_filename = f'{school}.json'
    src = json.load(open(ROOT / f'parsed/{src_filename}'))
    is_ocr = 'q_text_ocr' in (src['questions'][0] if src['questions'] else {})
    results = []
    for q in src['questions']:
        if is_ocr:
            qtext = q['q_text_ocr'] or ''
            qchoices = []  # OCR에서 선지 신뢰 어려움
            qcn = 0
        else:
            qtext = q['question_text'] or ''
            qchoices = q.get('choices') or []
            qcn = len(qchoices)
        ch_text = ' '.join(c.get('text', '') for c in qchoices)
        full = qtext + ' ' + ch_text
        qn = normalize_full(full, is_latex=not is_ocr)
        qkor = korean_concat(full)
        if not qn:
            continue
        scored = []
        for c in corpus:
            if not c['norm']:
                continue
            sc = score(qn, c['norm'], qkor, c['kor'], qcn, c['choice_n'])
            scored.append((sc['score'], sc, c))
        scored.sort(key=lambda x: -x[0])
        top = scored[:topk]
        results.append({
            'school': school,
            'q_no': q.get('question_number', q.get('q_no', 0)),
            'q_text': qtext,
            'q_choices': qchoices,
            'q_chapter': q.get('chapter', ''),
            'q_kor_len': len(qkor),
            'q_choice_n': qcn,
            'is_ocr': is_ocr,
            'top': [
                {
                    'score': round(sc['score'], 1),
                    's_token': round(sc['s_token'], 1),
                    's_lcs': round(sc['s_lcs'], 1),
                    'kor_min': sc['kor_min'],
                    'tb_key': c['tb_key'],
                    'tb_short': c['tb_short'],
                    'code': c['code'],
                    'page': c['page'],
                    'text_orig': c['text_orig'][:400],
                    'choice_n': c['choice_n'],
                    'kor_len': len(c['kor']),
                }
                for s, sc, c in top
            ],
        })
    return results


def main():
    corpus = build_textbook_corpus()
    print(f'corpus size: {len(corpus)}')
    all_results = {}
    schools = [
        ('광명고', '광명고.json'),
        ('광명북고', '광명북고_pdf.json'),
        ('광문고', '광문고_pdf.json'),
    ]
    for school, fn in schools:
        res = match_school(school, corpus, topk=5, src_filename=fn)
        all_results[school] = res
        print(f'\n=== {school} ===')
        for r in res:
            top = r['top'][0] if r['top'] else None
            tag = '★★' if top and top['score'] >= 80 else ('★ ' if top and top['score'] >= 60 else '  ')
            if top:
                print(f"{tag} Q{r['q_no']:2d} [s={top['score']:.0f} tok={top['s_token']:.0f} lcs={top['s_lcs']:.0f} korMin={top['kor_min']}] {top['tb_short']:6s} {top['code']} p{top['page']+1:3d}")
                print(f"     Q: {r['q_text'][:110]}")
                print(f"     M: {top['text_orig'][:110]}")
    out = ROOT / 'matches.json'
    out.write_text(json.dumps(all_results, ensure_ascii=False, indent=2))
    print(f'\nwrote {out}')


if __name__ == '__main__':
    main()
