"""CIRCUIT 미적분1 기말고사대비: 라이트쎈 07~09 병합.

구성: 표지 → [챕터 간지 + 문제] x3 → [해설 챕터 간지 + 해설] x3
각 원본 PDF는 '[정답]'이 처음 나오는 쪽부터 해설로 분할한다.
"""
import sys, unicodedata
from pathlib import Path
import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import make_essential_workbook_calc1 as m

SRC = Path("/Users/youngwoolee/Downloads/01_수업자료/03_고2/00_참고서/[미적분1] 라이트쎈")
OUT = Path("/Users/youngwoolee/Downloads/01_수업자료/03_고2/03_미적분1/CIRCUIT_미적분1_기말고사대비.pdf")
CH = [
    ("07.부정적분", "I", "부정적분", "INDEFINITE INTEGRAL"),
    ("08.정적분", "II", "정적분", "DEFINITE INTEGRAL"),
    ("09.정적분의활용", "III", "정적분의 활용", "APPLICATIONS OF DEFINITE INTEGRAL"),
]
m.TAGLINE_LINES = ["미적분1 기말고사대비", "클리닉워크북"]


def open_src(key):
    return fitz.open(next(p for p in SRC.iterdir()
                          if unicodedata.normalize("NFC", p.name).endswith(f"{key}.pdf")))


def split_page(doc):
    return next(i for i, p in enumerate(doc) if "[정답]" in p.get_text())


w = fitz.open()
def add(img):
    s = fitz.open("pdf", m.pil_to_pdf_bytes(img)); w.insert_pdf(s); s.close()

prev = m.OUT_DIR / "preview"; prev.mkdir(exist_ok=True)
srcs = [open_src(k) for k, *_ in CH]
cuts = [split_page(s) for s in srcs]

add(m.make_cover())
for i, ((key, roman, name, eng), s, cut) in enumerate(zip(CH, srcs, cuts), 1):
    img = m.make_chapter_page(i, roman, name, eng)
    img.save(prev / f"final_divider_{i:02d}.png"); add(img)
    w.insert_pdf(s, from_page=0, to_page=cut - 1)
    print(f"문제 {name}: {cut}p")
for i, ((key, roman, name, eng), s, cut) in enumerate(zip(CH, srcs, cuts), 1):
    img = m.make_chapter_page(i, roman, f"{name} 해설", eng + " · SOLUTIONS", tag="SOLUTIONS")
    img.save(prev / f"final_sol_divider_{i:02d}.png"); add(img)
    w.insert_pdf(s, from_page=cut, to_page=s.page_count - 1)
    print(f"해설 {name}: {s.page_count - cut}p")

# ---- 유형 NN 배지 -> THEME NN (남색 알약 + 주황 원, 글자로 구분) ----
NAVY, ORANGE, WHITE = (0.12, 0.16, 0.42), (0.96, 0.55, 0.16), (1, 1, 1)
FONT_FILE = str(m.USER_FONT_DIR / "Paperlogy-9Black.ttf")
BADGE_SIZES = {(265, 116), (265, 156)}


def theme_badges(doc):
    font = fitz.Font(fontfile=FONT_FILE)
    n = 0
    for page in doc:
        page.insert_font(fontname="pl9", fontfile=FONT_FILE)
        for im in page.get_image_info():
            if (im["width"], im["height"]) not in BADGE_SIZES:
                continue
            r = fitz.Rect(im["bbox"])
            box = fitz.Rect(r.x0, r.y1 - 29, r.x1 + 1, r.y1)        # 배지 영역(집중공략 라벨은 보존)
            num = "".join(wd[4] for wd in page.get_text("words", clip=box) if wd[4].isdigit())
            assert num, (page.number, box)
            for wd in page.get_text("words", clip=box):
                if wd[4].isdigit():
                    page.add_redact_annot(fitz.Rect(wd[:4]))
            page.apply_redactions(images=fitz.PDF_REDACT_IMAGE_NONE, graphics=fitz.PDF_REDACT_LINE_ART_NONE)
            page.draw_rect(box, color=None, fill=WHITE)
            x0, y0 = r.x0, r.y1 - 29
            page.draw_rect(fitz.Rect(x0, y0 + 3, x0 + 50, y0 + 26), color=None, fill=NAVY, radius=0.5)
            tw = font.text_length("THEME", fontsize=8)
            page.insert_text((x0 + 19 - tw / 2, y0 + 17), "THEME", fontname="pl9", fontfile=FONT_FILE, fontsize=8, color=WHITE)
            cx, cy = x0 + 51.5, y0 + 14.5
            page.draw_circle((cx, cy), 14.5, color=WHITE, fill=ORANGE, width=1.6)
            fs = 12.5
            nw = font.text_length(num, fontsize=fs)
            page.insert_text((cx - nw / 2, cy + fs * 0.36), num, fontname="pl9", fontfile=FONT_FILE, fontsize=fs, color=NAVY)
            n += 1
    return n


print("THEME 배지", theme_badges(w), "개 교체")
w.save(OUT); print(OUT, len(w))
