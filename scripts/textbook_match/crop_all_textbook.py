"""교재 1416개 문제 모두 크롭."""
from __future__ import annotations
import json
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from crop_textbook import crop_problem  # type: ignore

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')


def main():
    tb = json.load(open(ROOT / 'textbooks_index.json'))
    targets = []
    for key, info in tb.items():
        for p in info['problems']:
            targets.append((key, p['code'], p['page']))
    print(f'cropping {len(targets)} problems')
    ok = miss = 0
    for i, (key, code, page) in enumerate(targets):
        if i % 200 == 0:
            print(f'  progress: {i}/{len(targets)}')
        out = crop_problem(key, code, page)
        if out:
            ok += 1
        else:
            miss += 1
    print(f'done. ok={ok} miss={miss}')


if __name__ == '__main__':
    main()
