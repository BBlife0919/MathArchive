"""CIRCUIT - 미적분1 중간고사대비 표지 + 챕터 내지 생성 + 원본 5권 병합.

라이트쎈 미적분1 5개 PDF(함수의 극한~도함수의 활용(2))를 한 권으로 묶으면서
1. 맨앞표지, 2. 챕터간내지만 새로 생성한다 (본문은 원본 그대로 사용).
흰 배경 + 소프트 그라디언트 블롭 모티프의 미니멀한 톤. 별/점 장식 없음.
페이지 크기는 원본(729x1032pt, B4)에 맞춘다.
"""
from __future__ import annotations

from pathlib import Path

import fitz
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC_DIR = Path("/Users/youngwoolee/Downloads/[미적분1] 라이트쎈")
OUT_DIR = ROOT / "output" / "essential_workbook_calc1"
OUT_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR = OUT_DIR / "assets"
LOGO_ICON = ASSETS_DIR / "eum_icon_teal.png"
LOGO_WORDMARK = ASSETS_DIR / "eum_wordmark_teal.png"
FINAL_PDF = Path("/Users/youngwoolee/클로드교재/CIRCUIT_미적분1_중간고사대비.pdf")
OLD_FINAL_PDF = Path("/Users/youngwoolee/클로드교재/ESSENTIAL_WORKBOOK_미적분1_중간고사대비.pdf")

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")
SYS_FONT_TTC = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
SDGOTHIC_INDEX = {"regular": 0, "medium": 2, "semibold": 4, "bold": 6, "light": 8}

# 원본 페이지(729x1032pt, B4)와 동일 비율, 300dpi
PT_W, PT_H = 729.0, 1032.0
DPI = 300.0
W = round(PT_W / 72.0 * DPI)
H = round(PT_H / 72.0 * DPI)

INK = (35, 35, 40)          # 거의 검정 (제목)
GRAY = (130, 132, 140)      # 보조 텍스트
GRAY_LIGHT = (200, 202, 208)  # 헤어라인
WHITE = (255, 255, 255)

# 그라디언트 블롭 3단 컬러 스톱 (블루 → 민트 → 라벤더)
C_BLUE = np.array([120, 173, 226], dtype=float)
C_MINT = np.array([196, 224, 206], dtype=float)
C_LAVENDER = np.array([196, 182, 224], dtype=float)

BRAND = "CIRCUIT"
TAGLINE_LINES = ["미적분1 중간고사대비", "클리닉워크북"]
SUBJECT_LABEL = "미적분1"

CHAPTERS = [
    ("01.", "I", "함수의 극한", "LIMITS OF FUNCTIONS"),
    ("02.", "II", "함수의 연속", "CONTINUITY OF FUNCTIONS"),
    ("03.", "III", "미분계수와 도함수", "DIFFERENTIAL COEFFICIENT & DERIVATIVE"),
    ("04.", "IV", "도함수의 활용 (1)", "APPLICATIONS OF DERIVATIVE (1)"),
    ("05.", "V", "도함수의 활용 (2)", "APPLICATIONS OF DERIVATIVE (2)"),
]


def font(size: int, family: str = "paper_black") -> ImageFont.FreeTypeFont:
    if family in SDGOTHIC_INDEX:
        return ImageFont.truetype(SYS_FONT_TTC, size=size, index=SDGOTHIC_INDEX[family])
    path = {
        "paper_black": FONT_PAPER_BLACK,
        "paper_eb": FONT_PAPER_EB,
    }.get(family, FONT_PAPER_BLACK)
    return ImageFont.truetype(path, size=size)


def text_centered(draw, xy_center, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = xy_center[0] - w // 2 - bbox[0]
    y = xy_center[1] - h // 2 - bbox[1]
    draw.text((x, y), text, font=fnt, fill=fill)
    return w, h


def text_left(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - bbox[0], xy[1] - bbox[1]), text, font=fnt, fill=fill)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def text_right(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((xy[0] - w - bbox[0], xy[1] - bbox[1]), text, font=fnt, fill=fill)
    return w, bbox[3] - bbox[1]


def fit_text_size(draw, text: str, family: str, max_w: int, start: int, floor: int) -> int:
    for size in range(start, floor - 1, -6):
        f = font(size, family)
        bx = draw.textbbox((0, 0), text, font=f)
        if (bx[2] - bx[0]) <= max_w:
            return size
    return floor


def make_gradient_blob(x0: int, y0: int, x1: int, y1: int) -> tuple[Image.Image, Image.Image]:
    """좌측은 플랫한 변, 우측은 반원으로 부푼 'D' 형태의 소프트 그라디언트 블롭.

    x0,y0 ~ x1,y1: 블롭이 들어갈 바운딩 박스(정사각형에 가까울 필요 없음, 높이가 지름).
    반환: (컬러 RGB 이미지, 마스크 L 이미지) — 둘 다 캔버스 전체 크기(W,H).
    """
    blob_h = y1 - y0
    r = blob_h / 2.0
    x_mid = x0 + max(0.0, (x1 - x0) - r)
    x_end = x_mid + r

    mask = Image.new("L", (W, H), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.rectangle([x0, y0, x_mid, y1], fill=255)
    mdraw.pieslice([x_mid - r, y0, x_mid + r, y1], start=-90, end=90, fill=255)

    xs = np.arange(W, dtype=float)
    ys = np.arange(H, dtype=float)
    X, Y = np.meshgrid(xs, ys)
    nx = np.clip((X - x0) / max(1.0, (x_end - x0)), 0, 1)
    ny = np.clip((Y - y0) / max(1.0, (y1 - y0)), 0, 1)
    t = np.clip(0.5 * nx + 0.5 * ny, 0, 1)

    f_low = np.clip(t * 2, 0, 1)[..., None]
    color_low = C_BLUE + (C_MINT - C_BLUE) * f_low
    f_high = np.clip((t - 0.5) * 2, 0, 1)[..., None]
    color_high = C_MINT + (C_LAVENDER - C_MINT) * f_high
    color = np.where((t < 0.5)[..., None], color_low, color_high)

    grad_img = Image.fromarray(color.astype(np.uint8), "RGB")
    return grad_img, mask


def paste_blob(img: Image.Image, x0: int, y0: int, x1: int, y1: int):
    grad_img, mask = make_gradient_blob(x0, y0, x1, y1)
    img.paste(grad_img, (0, 0), mask)


def add_bottom_bar(img: Image.Image, draw, right_label: str, show_instructor: bool = False):
    margin_x = round(0.12 * W)
    line_y = H - round(0.075 * H)
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=GRAY_LIGHT, width=2)

    bar_cy = line_y + round(0.032 * H)

    # 좌측: 아이콘 + 워드마크 로고
    try:
        icon = Image.open(LOGO_ICON).convert("RGBA")
        icon_h = round(0.034 * H)
        ratio = icon_h / icon.height
        icon_w = int(icon.width * ratio)
        icon_resized = icon.resize((icon_w, icon_h), Image.LANCZOS)
        iy = bar_cy - icon_h // 2
        img.paste(icon_resized, (margin_x, iy), icon_resized)

        wordmark = Image.open(LOGO_WORDMARK).convert("RGBA")
        wm_h = round(icon_h * 0.62)
        wratio = wm_h / wordmark.height
        wm_w = int(wordmark.width * wratio)
        wordmark_resized = wordmark.resize((wm_w, wm_h), Image.LANCZOS)
        wm_x = margin_x + icon_w + round(0.012 * W)
        wm_y = bar_cy - wm_h // 2
        img.paste(wordmark_resized, (wm_x, wm_y), wordmark_resized)
    except Exception:
        text_left(draw, (margin_x, bar_cy - round(0.014 * H)), "이음학원", font(round(0.028 * H), "semibold"), INK)

    # 중앙: 강사명
    if show_instructor:
        f_center = font(round(0.024 * H), "semibold")
        text_centered(draw, (W // 2, bar_cy), "이영우 T", f_center, INK)

    # 우측: 파이프로 감싼 라벨
    f_right = font(round(0.024 * H), "semibold")
    label = f"ㅣ {right_label} ㅣ"
    text_right(draw, (W - margin_x, bar_cy - round(0.012 * H)), label, f_right, GRAY)


def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin_x = round(0.12 * W)

    # 상단 우측 태그라인
    tag_y = round(0.075 * H)
    f_tag = font(round(0.0145 * H), "regular")
    for i, line in enumerate(TAGLINE_LINES):
        text_right(draw, (W - margin_x, tag_y + i * round(0.021 * H)), line, f_tag, GRAY)

    # 메인 블롭 (좌측 플랫, 우측 반원)
    bx0 = margin_x
    by0 = round(0.15 * H)
    by1 = round(0.68 * H)
    bx1 = round(0.62 * W)
    paste_blob(img, bx0, by0, bx1, by1)

    blob_h = by1 - by0
    r = blob_h / 2.0
    x_mid = bx0 + max(0.0, (bx1 - bx0) - r)
    x_end = x_mid + r

    # 타이틀: CIRCUIT (세로 스택, 우측 정렬), 블롭 옆 하단 여백에 배치
    letters = list(BRAND)
    title_x_right = W - margin_x
    n = len(letters)
    step = round(0.058 * H)
    max_letter_w = W - round(0.62 * W) - margin_x - round(0.02 * W)

    # 글자 높이가 줄 간격(step)에 맞도록 폰트 크기 자동 축소
    letter_size = round(0.09 * H)
    f_letter = font(letter_size, "paper_black")
    while letter_size > 40:
        bboxes = [draw.textbbox((0, 0), c, font=f_letter) for c in letters]
        widest = max(b[2] for b in bboxes)
        tallest = max(b[3] - b[1] for b in bboxes)
        if widest <= max_letter_w and tallest <= step * 0.8:
            break
        letter_size -= 4
        f_letter = font(letter_size, "paper_black")

    stack_h = step * (n - 1)
    title_bottom_limit = H - round(0.16 * H)
    title_top = min(round(0.52 * H), title_bottom_limit - stack_h)

    for i, ch in enumerate(letters):
        cy = title_top + i * step
        text_right(draw, (title_x_right, cy), ch, f_letter, INK)

    add_bottom_bar(img, draw, SUBJECT_LABEL, show_instructor=True)
    return img


def make_chapter_page(idx: int, part_roman: str, part_name: str, eng_label: str, tag: str = "PART") -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)
    margin_x = round(0.12 * W)
    chapter_no = f"{idx:02d}"

    # 상단 라벨 바 + 헤어라인
    top_y = round(0.075 * H)
    f_label = font(round(0.0155 * H), "semibold")
    text_left(draw, (margin_x, top_y), f"{tag} · {chapter_no}", f_label, GRAY)
    text_right(draw, (W - margin_x, top_y), BRAND, f_label, GRAY)
    line_y = top_y + round(0.032 * H)
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=GRAY_LIGHT, width=2)

    # 우측 상단 소형 블롭 액센트
    bx1 = W - margin_x
    by0 = line_y + round(0.03 * H)
    by1 = round(0.32 * H)
    bx0 = round(0.66 * W)
    paste_blob(img, bx0, by0, bx1, by1)

    # 메인 타이틀 블록
    main_y = round(0.46 * H)
    f_roman = font(round(0.05 * H), "paper_black")
    text_left(draw, (margin_x, main_y), f"{part_roman}.", f_roman, INK)
    bbox = draw.textbbox((0, 0), f"{part_roman}.", font=f_roman)
    roman_w = bbox[2] - bbox[0]

    f_eng = font(round(0.0125 * H), "medium")
    text_left(draw, (margin_x + roman_w + round(0.018 * W), main_y - round(0.006 * H)), eng_label, f_eng, GRAY)

    title_y = main_y + round(0.09 * H)
    max_w_title = W - margin_x * 2
    title_size = fit_text_size(draw, part_name, "paper_eb", max_w_title, start=round(0.065 * H), floor=round(0.03 * H))
    f_title = font(title_size, "paper_eb")
    text_left(draw, (margin_x, title_y), part_name, f_title, INK)

    underline_y = title_y + title_size + round(0.02 * H)
    accent = tuple(int(v) for v in C_MINT)
    draw.line([(margin_x, underline_y), (margin_x + round(0.09 * W), underline_y)], fill=accent, width=8)

    add_bottom_bar(img, draw, f"{tag} {chapter_no}")
    return img


def pil_to_pdf_bytes(img: Image.Image) -> bytes:
    import io
    buf = io.BytesIO()
    img.save(buf, "PDF", resolution=DPI)
    return buf.getvalue()


def main():
    cover_img = make_cover()
    divider_imgs = [
        make_chapter_page(i, roman, name, eng)
        for i, (_, roman, name, eng) in enumerate(CHAPTERS, start=1)
    ]

    preview_dir = OUT_DIR / "preview"
    preview_dir.mkdir(exist_ok=True)
    cover_img.save(preview_dir / "cover.png", "PNG", optimize=True)
    for i, im in enumerate(divider_imgs, start=1):
        im.save(preview_dir / f"divider_{i:02d}.png", "PNG", optimize=True)

    writer = fitz.open()

    def insert_image_page(img: Image.Image):
        pdf_bytes = pil_to_pdf_bytes(img)
        src = fitz.open("pdf", pdf_bytes)
        writer.insert_pdf(src)
        src.close()

    insert_image_page(cover_img)

    src_pdfs = sorted(SRC_DIR.glob("*.pdf"))

    for (num_prefix, roman, name, eng), divider_img in zip(CHAPTERS, divider_imgs):
        insert_image_page(divider_img)
        src_path = next(p for p in src_pdfs if f"]{num_prefix}" in p.name)
        src = fitz.open(src_path)
        page_count = src.page_count
        writer.insert_pdf(src)
        src.close()
        print(f"[OK] {roman}. {name} <- {src_path.name} ({page_count}p)")

    FINAL_PDF.parent.mkdir(parents=True, exist_ok=True)
    writer.save(FINAL_PDF)
    writer.close()
    if OLD_FINAL_PDF.exists():
        OLD_FINAL_PDF.unlink()
    print(f"[DONE] {FINAL_PDF} ({fitz.open(FINAL_PDF).page_count} pages)")


if __name__ == "__main__":
    main()
