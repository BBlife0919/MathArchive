#!/usr/bin/env python3
"""대수 1학기 기말 KERNEL POINT — 학교별 4종 (광명고/광명북고/명문고/광문고).

각 학교마다 표지에 학교 이름을 크게.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
APP = ROOT / "app"
sys.path.insert(0, str(APP))
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from build_kernel_point_book import fetch_rows, CHAPTERS, DIFF_ORDER

SCHOOLS = ["광명고", "광명북고", "명문고", "광문고"]


def build_one(school: str, all_rows: list):
    rows = [r for r in all_rows if r.get("school") == school]
    rows = [r for r in rows if r.get("difficulty") != "상"]
    print(f"\n=== {school}: {len(rows)}문항 ===")

    chap_idx = {c: i for i, c in enumerate(CHAPTERS)}
    rows.sort(key=lambda r: (
        chap_idx.get(r["chapter"], 999),
        DIFF_ORDER.get(r["difficulty"], 99),
        r["question_id"],
    ))

    import json
    for r in rows:
        ch = r.get("choices")
        if ch is not None and not isinstance(ch, str):
            r["choices"] = json.dumps(ch, ensure_ascii=False)

    if not rows:
        print(f"  ⚠ {school} 데이터 없음 — 스킵")
        return

    overrides = {r["question_id"]: "full" for r in rows}
    logo_path = APP / "assets" / "eum_logo.png"

    from pdf_engine import generate_book_pdf
    pdf_bytes = generate_book_pdf(
        rows,
        title="KERNEL POINT",
        subtitle=f"{school} · 대수 1학기 기말대비",
        include_source=True,
        overrides=overrides,
        logo_path=str(logo_path) if logo_path.exists() else None,
        kicker_mark=None,
        kicker_text=None,
        divider_meta_top=f"{school} · 대수 1학기 기말 · KERNEL POINT",
        divider_footer_title=f"{school} · 대수 1학기 기말 · KERNEL POINT",
        divider_footer_sub="이영우 T",
        cover_main_title=school,
        cover_tagline="대수 1학기 기말대비",
        cover_big_word="FINAL",
        cover_kicker="KERNEL POINT · 2026",
        cover_footer_main=f"{school} Algebra Final · 2026",
        cover_footer_sub="필수유형으로 끝내는 기말 마무리",
        page_running_left=f"{school} · KERNEL POINT",
    )

    import fitz
    src = fitz.open(stream=pdf_bytes, filetype="pdf")
    out = fitz.open()
    mat = fitz.Matrix(180 / 72, 180 / 72)
    for pg in src:
        if len(pg.get_text().strip()) < 3 and not pg.get_images() and len(pg.get_drawings()) < 3:
            continue
        pix = pg.get_pixmap(matrix=mat, alpha=False)
        npg = out.new_page(width=pg.rect.width, height=pg.rect.height)
        npg.insert_image(pg.rect, stream=pix.tobytes("jpeg", jpg_quality=82))

    book_dir = Path.home() / "클로드교재"
    book_dir.mkdir(exist_ok=True)
    out_path = book_dir / f"{school} 대수 1학기 기말 KERNEL POINT.pdf"
    out.save(str(out_path), garbage=4, deflate=True)
    out.close(); src.close()

    import subprocess
    subprocess.run(["xattr", "-c", str(out_path)], check=False)
    print(f"  [OK] {out_path} ({out_path.stat().st_size/1024/1024:.0f}MB)")


def main():
    print("[1/2] cloud DB 조회...")
    all_rows = fetch_rows()
    print(f"  전체: {len(all_rows)}")

    print("[2/2] 학교별 빌드 ×4")
    for school in SCHOOLS:
        build_one(school, all_rows)


if __name__ == "__main__":
    main()
