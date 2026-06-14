"""교재 PDF 3종을 파싱하여 문항코드/문제텍스트/페이지 인덱스를 만든다."""
from __future__ import annotations
import json
import re
from pathlib import Path
import fitz

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
ROOT.mkdir(parents=True, exist_ok=True)

TEXTBOOKS = [
    {
        'key': 'sk_su1',
        'label': '수능특강 수학I',
        'short': '수특I',
        'path': '/Users/youngwoolee/Downloads/[26008]_EBS 2027학년도 수능특강 수학영역_수학I_(181).pdf',
    },
    {
        'key': 'op_high',
        'label': '올림포스 고난도 대수',
        'short': '올림고난도',
        'path': '/Users/youngwoolee/Downloads/[26477]_EBS 올림포스 고난도 대수(2022 개정)_(346).pdf',
    },
    {
        'key': 'op_type',
        'label': '올림포스 유형편 대수',
        'short': '올림유형',
        'path': '/Users/youngwoolee/Downloads/[26643]_EBS 올림포스 유형편 대수(2022 개정)_(889).pdf',
    },
]

CODE_RE = re.compile(r'#문항코드\s*\n(\S+)')


def parse_textbook(meta: dict) -> list[dict]:
    """페이지별 텍스트를 모아 문항코드 단위로 분리. 각 문항의 시작 페이지를 기록."""
    doc = fitz.open(meta['path'])
    # 문항코드 → 첫 등장 페이지
    code_to_page: dict[str, int] = {}
    full_text_parts = []
    page_starts: list[tuple[int, int]] = []  # (offset, page_idx)
    for i, page in enumerate(doc):
        t = page.get_text()
        page_starts.append((sum(len(p) for p in full_text_parts), i))
        full_text_parts.append(t)
        for m in CODE_RE.finditer(t):
            code_to_page.setdefault(m.group(1), i)

    full = ''.join(full_text_parts)
    # 모든 문항코드 위치
    matches = list(CODE_RE.finditer(full))
    problems = []
    for idx, m in enumerate(matches):
        code = m.group(1)
        start = m.end()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(full)
        block = full[start:end]
        # [문제] ~ [정답/모범답안] 사이가 문제 본문
        problem_text = ''
        m2 = re.search(r'\[문제\]\s*\n(.*?)(?:\[정답|\Z)', block, re.DOTALL)
        if m2:
            problem_text = m2.group(1).strip()
        page_idx = code_to_page.get(code, -1)
        problems.append({
            'code': code,
            'page': page_idx,  # 0-indexed
            'text': problem_text,
        })
    doc.close()
    return problems


def main():
    out = {}
    for tb in TEXTBOOKS:
        print(f'parsing {tb["label"]}...')
        probs = parse_textbook(tb)
        non_empty = sum(1 for p in probs if p['text'])
        print(f'  problems={len(probs)} with_text={non_empty}')
        out[tb['key']] = {
            'meta': tb,
            'problems': probs,
        }
    out_path = ROOT / 'textbooks_index.json'
    out_path.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'wrote {out_path}')


if __name__ == '__main__':
    main()
