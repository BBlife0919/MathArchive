"""광문고 OCR 결과를 번호별 문제로 분리한다."""
from __future__ import annotations
import json
import re
from pathlib import Path

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')

raw = json.load(open(ROOT / 'gmun_ocr/ocr_raw.json'))
# 모든 텍스트 합본 (페이지 순서대로)
raw_sorted = sorted(raw, key=lambda e: (e['page'], 0 if e['col'] == 'L' else 1))
combined = ''
for e in raw_sorted:
    combined += e['text'] + '\n'

# 문제 번호 패턴: 줄 시작에 N. 또는 NN.
# 1~17 + 논술형
prob_pat = re.compile(r'(?:^|\n)\s*(\d{1,2})\.\s', re.MULTILINE)
matches = list(prob_pat.finditer(combined))

problems = []
for i, m in enumerate(matches):
    num = int(m.group(1))
    if num < 1 or num > 25:
        continue
    start = m.end()
    end = matches[i + 1].start() if i + 1 < len(matches) else len(combined)
    body = combined[start:end].strip()
    problems.append({'q_no': num, 'q_text_ocr': body})

# 중복 번호 제거: 마지막것 유지
seen = {}
for p in problems:
    seen[p['q_no']] = p
final = sorted(seen.values(), key=lambda p: p['q_no'])

# 17번까지가 객관식 (선택형 17문항 OCR header)
# 서답형은 [논술형 1], [논술형 2], [논술형 3] 으로 분리
narr_pat = re.compile(r'\[논술형\s*(\d)\]')
last_idx = 0
narrative = []
for m in narr_pat.finditer(combined):
    pass  # 간단히 처리: 별도 추출 생략
# 결과 저장
out = ROOT / 'parsed/광문고_ocr.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps({
    'school': '광문고',
    'source': 'OCR (광문고 PDF, 손글씨 포함)',
    'questions': final,
}, ensure_ascii=False, indent=2))
print(f'extracted {len(final)} problems')
for p in final:
    head = p['q_text_ocr'][:80].replace('\n', ' ')
    print(f"Q{p['q_no']:2d}: {head}")
