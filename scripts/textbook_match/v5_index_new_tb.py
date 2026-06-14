"""추가 참고서 8개 인덱싱 (모두 텍스트 레이어 있음).

기존 v3 인덱싱 결과(20개)를 그대로 두고, 8개만 새로 인덱싱해서 추가.
"""
from __future__ import annotations
import json
from pathlib import Path
import fitz

ROOT_V3 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')

NEW_TBS = []
for i in range(1, 9):
    NEW_TBS.append({
        'key': f'eum_{i}',
        'short': f'이음학습지{i}',
        'label': f'이음학원 학습지 {i}.pdf (대수)',
        'path': f'/Users/youngwoolee/Downloads/260609_학습지/{i}.pdf',
    })


def index_one(meta: dict):
    out_dir = ROOT_V3 / 'pages_ocr' / meta['key']
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = out_dir / 'pages.json'
    png_dir = ROOT_V3 / 'pages_png' / meta['key']
    png_dir.mkdir(parents=True, exist_ok=True)

    doc = fitz.open(meta['path'])
    pages = []
    n = doc.page_count
    for i in range(n):
        p = doc.load_page(i)
        out_png = png_dir / f'p{i+1:04d}.png'
        if not out_png.exists():
            pm = p.get_pixmap(dpi=140)
            pm.save(str(out_png))
        pages.append({'page': i + 1, 'text': p.get_text()})
    doc.close()

    out = {'meta': meta, 'has_text_layer': True, 'pages': pages}
    cache.write_text(json.dumps(out, ensure_ascii=False))
    return n


def main():
    total = 0
    for m in NEW_TBS:
        n = index_one(m)
        total += n
        print(f'  {m["short"]:14s}  {n:4d}p')
    print(f'\ntotal: {total}p')
    print('인덱싱 완료. v3 corpus 에 통합됨.')


if __name__ == '__main__':
    main()
