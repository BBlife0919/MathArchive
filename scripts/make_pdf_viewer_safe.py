#!/usr/bin/env python3
"""Type3 폰트 과부하로 Acrobat/Preview 가 렌더 못 하는 PDF를 뷰어 호환으로 변환.

방법1(gs): Ghostscript 재증류 — 텍스트/벡터 유지, 폰트 정규화.
방법2(raster): 각 페이지를 이미지로 래스터화해 재구성 — 모든 뷰어 100% 렌더(텍스트X).

usage: python make_pdf_viewer_safe.py <in.pdf> [--raster] [--dpi 200]
"""
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def via_gs(src: Path, dst: Path) -> bool:
    gs = shutil.which("gs")
    if not gs:
        return False
    cmd = [gs, "-sDEVICE=pdfwrite", "-dCompatibilityLevel=1.5",
           "-dPDFSETTINGS=/printer", "-dNOPAUSE", "-dBATCH", "-dQUIET",
           "-dDetectDuplicateImages=true", "-dCompressFonts=true",
           f"-sOutputFile={dst}", str(src)]
    return subprocess.run(cmd).returncode == 0 and dst.exists()


def via_raster(src: Path, dst: Path, dpi: int = 180):
    import fitz
    d = fitz.open(str(src))
    out = fitz.open()
    mat = fitz.Matrix(dpi / 72, dpi / 72)
    for pg in d:
        pix = pg.get_pixmap(matrix=mat, alpha=False)
        jpg = pix.tobytes("jpeg", jpg_quality=82)   # JPEG 압축으로 용량 축소
        rect = pg.rect
        npg = out.new_page(width=rect.width, height=rect.height)
        npg.insert_image(rect, stream=jpg)
    out.save(str(dst), garbage=4, deflate=True)
    out.close(); d.close()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--raster", action="store_true")
    ap.add_argument("--dpi", type=int, default=200)
    args = ap.parse_args()
    src = Path(args.src)
    tmp = src.with_suffix(".viewer.pdf")
    if not args.raster and via_gs(src, tmp):
        print("[gs] 재증류 완료")
    else:
        via_raster(src, tmp, args.dpi)
        print(f"[raster] {args.dpi}dpi 래스터화 완료")
    shutil.move(str(tmp), str(src))
    print("저장:", src)


if __name__ == "__main__":
    main()
