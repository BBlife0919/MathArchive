"""PDF → 페이지별 PNG 변환 유틸리티.

사용:
    python3 scripts/pdf_to_images.py <input.pdf> <output_dir> [--dpi 200]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import fitz


def convert(pdf_path: Path, out_dir: Path, dpi: int = 200) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(pdf_path)
    written: list[Path] = []
    zoom = dpi / 72.0
    mat = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc, start=1):
        pix = page.get_pixmap(matrix=mat, alpha=False)
        target = out_dir / f"page_{i:02d}.png"
        pix.save(str(target))
        written.append(target)
    doc.close()
    return written


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("pdf", type=Path)
    p.add_argument("out", type=Path)
    p.add_argument("--dpi", type=int, default=200)
    args = p.parse_args()
    if not args.pdf.exists():
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 1
    pages = convert(args.pdf, args.out, args.dpi)
    print(f"wrote {len(pages)} pages to {args.out}")
    for p_ in pages:
        print(f"  {p_.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
