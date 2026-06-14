"""교재 crop 1416개를 Tesseract로 OCR하여 깨끗한 텍스트 인덱스 구축."""
from __future__ import annotations
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
CROPS = ROOT / 'crops_textbook'
OUT = ROOT / 'textbook_ocr_index.json'


def ocr_one(p: Path) -> tuple[str, str]:
    res = subprocess.run(
        ['tesseract', str(p), '-', '-l', 'kor+eng', '--psm', '6'],
        capture_output=True, text=True, timeout=60
    )
    return p.stem, res.stdout


def main():
    paths = sorted(CROPS.glob('*.png'))
    print(f'OCR-ing {len(paths)} crops')
    out = {}
    done = 0
    with ThreadPoolExecutor(max_workers=8) as ex:
        for code, text in ex.map(ocr_one, paths):
            out[code] = text
            done += 1
            if done % 100 == 0:
                print(f'  {done}/{len(paths)}')
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2))
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
