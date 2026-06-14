"""광문고 PDF를 페이지별 → 좌/우 컬럼 분리 → OCR하여 텍스트 추출."""
from __future__ import annotations
import subprocess
import tempfile
import os
import json
from pathlib import Path
import fitz
from PIL import Image

PDF = '/Users/youngwoolee/Downloads/기출분석/원본/2026-2-1-a-광문고.pdf'
OUT_DIR = Path('/Users/youngwoolee/MathDB/output/textbook_match/gmun_ocr')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def ocr(img_path: str, psm: int = 4) -> str:
    res = subprocess.run(
        ['tesseract', img_path, '-', '-l', 'kor+eng', '--psm', str(psm)],
        capture_output=True, text=True, timeout=120
    )
    return res.stdout


def main():
    doc = fitz.open(PDF)
    all_text = []
    for pi in range(doc.page_count):
        page = doc.load_page(pi)
        pm = page.get_pixmap(dpi=300)
        full_path = OUT_DIR / f'p{pi+1}.png'
        pm.save(str(full_path))
        # 컬럼 분리: 좌/우 1:1
        img = Image.open(full_path)
        w, h = img.size
        mid = w // 2 + 30  # 약간 오른쪽으로 (필요시 조정)
        left = img.crop((0, 0, mid, h))
        right = img.crop((mid - 60, 0, w, h))
        l_path = OUT_DIR / f'p{pi+1}_L.png'
        r_path = OUT_DIR / f'p{pi+1}_R.png'
        left.save(l_path)
        right.save(r_path)
        # OCR
        for label, p in [('L', l_path), ('R', r_path)]:
            txt = ocr(str(p), psm=4)
            all_text.append({
                'page': pi + 1,
                'col': label,
                'text': txt,
            })
            print(f'p{pi+1}{label}: {len(txt)} chars')
    out = OUT_DIR / 'ocr_raw.json'
    out.write_text(json.dumps(all_text, ensure_ascii=False, indent=2))
    # 합본
    combined = '\n\n'.join(f'=== p{e["page"]}{e["col"]} ===\n{e["text"]}' for e in all_text)
    (OUT_DIR / 'ocr_raw.txt').write_text(combined)
    print(f'wrote {out}')
    doc.close()


if __name__ == '__main__':
    main()
