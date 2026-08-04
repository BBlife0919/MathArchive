"""4개 신규 KP 책 표지를 kp_cover_v2로 교체 + 파일명 통일(공수2 올인원_KERNEL POINT_단원명)."""
import sys, os, subprocess
sys.path.insert(0, "/Users/youngwoolee/MathDB/scripts/top_class_reference")
from kp_cover_v2 import kp_cover_v2_html
from playwright.sync_api import sync_playwright
import fitz

SRC_DIR = "/Users/youngwoolee/Downloads/수업자료/탑반 교재"

FILES = [
    ("올인원_직선의방정식_KERNEL+WORKBOOK_합본.pdf", "공수2 올인원_KERNEL POINT_직선의방정식.pdf"),
    ("올인원_평면좌표_KERNEL+WORKBOOK_합본.pdf", "공수2 올인원_KERNEL POINT_평면좌표.pdf"),
    ("2026 KERNEL POINT_원의방정식_고난도정복WORKBOOK제외.pdf", "공수2 올인원_KERNEL POINT_원의방정식.pdf"),
    ("도형의이동_KERNEL_고난도정복WORKBOOK제외.pdf", "공수2 올인원_KERNEL POINT_도형의이동.pdf"),
]


def html_to_pdf(html):
    with sync_playwright() as p:
        b = p.chromium.launch(); page = b.new_page()
        page.set_content(html, wait_until="networkidle")
        page.wait_for_function("document.fonts.ready")
        out = page.pdf(format="A4", print_background=True, margin={"top": "0", "bottom": "0", "left": "0", "right": "0"})
        b.close()
    return out


cover_bytes = html_to_pdf(kp_cover_v2_html())

for old_name, new_name in FILES:
    old_path = f"{SRC_DIR}/{old_name}"
    new_path = f"{SRC_DIR}/{new_name}"
    doc = fitz.open(old_path)
    doc.delete_page(0)
    cover_pdf = fitz.open("pdf", cover_bytes)
    doc.insert_pdf(cover_pdf, start_at=0)
    cover_pdf.close()
    doc.save(new_path, deflate=True, garbage=4)
    doc.close()
    subprocess.run(["xattr", "-c", new_path])
    if old_path != new_path:
        os.remove(old_path)
    print(f"[OK] {old_name} -> {new_name}")
