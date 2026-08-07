"""BASIC POINT 교재 단원 시작(중표지) 페이지 생성.

표지와 동일한 라벤더+핑크 톤, 그러나 절제된 미니멀 레이아웃.
8개 단원을 한 PDF로 묶어 출력.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "app" / "assets" / "eum_logo.png"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)
OUT_PDF = OUT_DIR / "basic_point_chapters.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

# A4 @ 300dpi
W, H = 2480, 3508

# 톤 (표지와 통일, 더 차분하게)
BG = (252, 249, 253)
DEEP_PLUM = (110, 70, 130)
SOFT_PLUM = (165, 130, 185)
HOT_PINK = (235, 115, 155)
PEACH_PINK = (250, 200, 210)
MUTED = (155, 145, 165)
INK = (60, 50, 75)
WATERMARK = (235, 225, 240)   # 흐릿한 라일락
LINE = (210, 195, 225)


def font(size: int, family: str = "cafe24") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "paper_eb": FONT_PAPER_EB,
        "aggro": FONT_AGGRO,
    }.get(family, FONT_CAFE24)
    return ImageFont.truetype(path, size=size)


def text_left(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - bbox[0], xy[1] - bbox[1]), text, font=fnt, fill=fill)


def text_right(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((xy[0] - w - bbox[0], xy[1] - bbox[1]), text, font=fnt, fill=fill)


def text_centered(draw, xy_center, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(
        (xy_center[0] - w // 2 - bbox[0], xy_center[1] - h // 2 - bbox[1]),
        text, font=fnt, fill=fill,
    )


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def draw_sparkle(draw, cx, cy, size, color):
    s = size
    pts = [
        (cx, cy - s), (cx + s * 0.25, cy - s * 0.25),
        (cx + s, cy), (cx + s * 0.25, cy + s * 0.25),
        (cx, cy + s), (cx - s * 0.25, cy + s * 0.25),
        (cx - s, cy), (cx - s * 0.25, cy - s * 0.25),
    ]
    draw.polygon(pts, fill=color)


def fit_text_size(draw, text: str, family: str, max_w: int, start: int = 240, floor: int = 100) -> int:
    for size in range(start, floor - 1, -6):
        f = font(size, family)
        bx = draw.textbbox((0, 0), text, font=f)
        if (bx[2] - bx[0]) <= max_w:
            return size
    return floor


def make_chapter_page(idx: int, part_roman: str, part_name: str, sub_no: str, sub_name: str) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    margin_x = 260
    chapter_no = f"{idx:02d}"

    # ── 상단 가는 가로 라인 + 라벨 ───────────────────────
    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 220, top_y)], fill=HOT_PINK, width=8)
    f_label = font(48, "aggro")
    text_left(draw, (margin_x + 260, top_y - 26), f"CHAPTER · {chapter_no}", f_label, SOFT_PLUM)

    # 우상단 라벨
    text_right(draw, (W - margin_x, top_y - 26), "BASIC POINT", f_label, MUTED)

    # ── 우측 거대 워터마크 숫자 (페이지 번호처럼) ─────────
    f_water = font(1500, "paper_black")
    bbox = draw.textbbox((0, 0), chapter_no, font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 80 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 200
    draw.text((wx, wy), chapter_no, font=f_water, fill=WATERMARK)

    # ── 메인 본문 (좌측 정렬) ───────────────────────────
    # 대단원 표시: "I." 또는 "II." 큰 글자 + 단원명
    main_y = 1080

    f_part_no = font(220, "paper_black")
    text_left(draw, (margin_x, main_y), f"{part_roman}.", f_part_no, DEEP_PLUM)
    bbox = draw.textbbox((0, 0), f"{part_roman}.", font=f_part_no)
    part_no_w = bbox[2] - bbox[0]

    f_part_name = font(180, "cafe24")
    text_left(draw, (margin_x + part_no_w + 60, main_y + 40), part_name, f_part_name, DEEP_PLUM)

    # 가는 라인
    line_y = main_y + 320
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=LINE, width=4)
    # 라인 위 점 장식
    draw_dot(draw, margin_x, line_y, 12, HOT_PINK)
    draw_dot(draw, W - margin_x, line_y, 12, HOT_PINK)

    # ── 소단원 ─────────────────────────────────────────
    sub_label_y = line_y + 90
    f_sub_label = font(56, "aggro")
    text_left(draw, (margin_x, sub_label_y), f"S E C T I O N · {sub_no}", f_sub_label, HOT_PINK)

    # 소단원 제목 (긴 경우 자동 축소)
    sub_title_y = sub_label_y + 140
    max_w_title = W - margin_x * 2
    sub_size = fit_text_size(draw, sub_name, "cafe24", max_w_title, start=260, floor=140)
    f_sub_title = font(sub_size, "cafe24")
    text_left(draw, (margin_x, sub_title_y), sub_name, f_sub_title, INK)

    # ── 작은 장식 (제목 아래) ────────────────────────────
    deco_y = sub_title_y + sub_size + 90
    draw_sparkle(draw, margin_x + 18, deco_y, 16, HOT_PINK)
    draw_dot(draw, margin_x + 80, deco_y, 8, SOFT_PLUM)
    draw_dot(draw, margin_x + 130, deco_y, 6, PEACH_PINK)

    # ── 하단 도트 라인 ──────────────────────────────────
    foot_dot_y = H - 360
    for x in range(margin_x, W - margin_x + 1, 28):
        draw_dot(draw, x, foot_dot_y, 4, LINE)

    # ── 풋터: 좌측 BASIC POINT · 이영우 T / 우측 로고 + 학원명 ──
    f_foot = font(46, "aggro")
    text_left(draw, (margin_x, H - 260), "BASIC POINT", f_foot, DEEP_PLUM)
    f_foot_kr = font(40, "cafe24")
    text_left(draw, (margin_x, H - 195), "이영우 T", f_foot_kr, MUTED)

    # 로고 (작게)
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 200
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
        lx = W - margin_x - target_w
        ly = H - 280
        img.paste(logo_resized, (lx, ly), logo_resized)
    except Exception:
        pass

    # 페이지 번호 (우하단 작게, 워터마크와 별개)
    f_page = font(40, "aggro")
    text_right(draw, (W - margin_x, H - 130), f"· {chapter_no} ·", f_page, MUTED)

    return img


CHAPTERS = [
    ("I", "삼각함수", "1", "사인법칙과 코사인법칙"),
    ("II", "수열", "1", "수열의 뜻"),
    ("II", "수열", "2", "등차수열"),
    ("II", "수열", "3", "등비수열"),
    ("II", "수열", "4", "합의 기호"),
    ("II", "수열", "5", "여러 가지 수열의 합"),
    ("II", "수열", "6", "수열의 귀납적 정의"),
    ("II", "수열", "7", "수학적 귀납법"),
]


def main():
    pages = []
    for i, (part_roman, part_name, sub_no, sub_name) in enumerate(CHAPTERS, start=1):
        pages.append(make_chapter_page(i, part_roman, part_name, sub_no, sub_name))

    first, rest = pages[0], pages[1:]
    first.save(OUT_PDF, "PDF", resolution=300.0, save_all=True, append_images=rest)

    # 미리보기 PNG (각 페이지)
    preview_dir = OUT_DIR / "basic_point_chapters_preview"
    preview_dir.mkdir(exist_ok=True)
    for i, page in enumerate(pages, start=1):
        page.save(preview_dir / f"ch{i:02d}.png", "PNG", optimize=True)

    print(f"[OK] PDF: {OUT_PDF} ({len(pages)} pages)")
    print(f"[OK] Preview PNGs: {preview_dir}/")


if __name__ == "__main__":
    main()
