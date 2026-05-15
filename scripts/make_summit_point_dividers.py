"""SUMMIT POINT 교재 내지(중표지) PDF 생성.

4장:
  1. 여러가지 방정식 ~ 여러가지 부등식
  2. 순열·조합
  3. 행렬
  4. 정답 및 해설

표지와 통일된 다크 네이비 + 골드 톤, 약간 차분하게.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "output" / "summit_point" / "eum_logo_gold.png"
OUT_DIR = ROOT / "output" / "summit_point"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "dividers.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

W, H = 2480, 3508

NAVY_DEEP = (15, 25, 50)
NAVY = (24, 38, 75)
NAVY_MID = (35, 55, 100)
NAVY_LIGHT = (60, 90, 145)
GOLD = (210, 175, 110)
GOLD_BRIGHT = (240, 205, 135)
WHITE = (245, 245, 250)
GREY = (170, 180, 200)
MUTED = (110, 125, 150)
WATERMARK = (32, 48, 90)  # 흐릿한 네이비 (배경 워터마크 숫자)


def font(size: int, family: str = "paper_black") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "paper_eb": FONT_PAPER_EB,
        "aggro": FONT_AGGRO,
    }.get(family, FONT_PAPER_BLACK)
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


def fit_text_size(draw, text: str, family: str, max_w: int, start: int = 280, floor: int = 110) -> int:
    for size in range(start, floor - 1, -6):
        f = font(size, family)
        bx = draw.textbbox((0, 0), text, font=f)
        if (bx[2] - bx[0]) <= max_w:
            return size
    return floor


def add_background(img: ImageDraw.ImageDraw):
    """다크 네이비 배경 + 미세한 별 텍스처."""
    draw = ImageDraw.Draw(img)
    # 그라디언트
    for y in range(H):
        t = y / H
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * (1 - abs(t - 0.5) * 2))
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * (1 - abs(t - 0.5) * 2))
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * (1 - abs(t - 0.5) * 2))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    import random
    rnd = random.Random(13)
    for _ in range(140):
        x = rnd.randint(60, W - 60)
        y = rnd.randint(60, H - 60)
        r = rnd.choice([1, 1, 1, 2, 2])
        c = rnd.choice([NAVY_LIGHT, MUTED, MUTED])
        draw_dot(draw, x, y, r, c)
    return draw


def add_frame(draw):
    pad = 90
    draw.rectangle([pad, pad, W - pad, H - pad], outline=GOLD, width=2)
    corner = 48
    for cx, cy in [(pad, pad), (W - pad, pad), (pad, H - pad), (W - pad, H - pad)]:
        draw.line([(cx - corner, cy), (cx + corner, cy)], fill=GOLD, width=4)
        draw.line([(cx, cy - corner), (cx, cy + corner)], fill=GOLD, width=4)


def add_footer(img, draw, label: str):
    """SUMMIT POINT · 이영우 T (좌) + 로고 (우)."""
    f_foot = font(46, "aggro")
    text_left(draw, (220, H - 280), "SUMMIT POINT", f_foot, GOLD)
    f_foot_kr = font(40, "cafe24")
    text_left(draw, (220, H - 210), "이영우 T", f_foot_kr, GREY)

    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 200
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
        lx = W - 220 - target_w
        ly = H - 300
        img.paste(logo_resized, (lx, ly), logo_resized)
    except Exception:
        pass

    f_page = font(40, "aggro")
    text_right(draw, (W - 220, H - 150), label, f_page, MUTED)


def make_chapter_page(idx: int, part_roman: str, part_name: str, eng_label: str) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)

    margin_x = 220
    chapter_no = f"{idx:02d}"

    # ── 상단 라벨 ────────────────────────────────────
    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 220, top_y)], fill=GOLD, width=5)
    f_label = font(48, "aggro")
    text_left(draw, (margin_x + 260, top_y - 26), f"PART · {chapter_no}", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 26), "SUMMIT POINT", f_label, GREY)

    # ── 우측 거대 워터마크 숫자 ─────────
    f_water = font(1400, "paper_black")
    bbox = draw.textbbox((0, 0), chapter_no, font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 100 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 220
    draw.text((wx, wy), chapter_no, font=f_water, fill=WATERMARK)

    # ── 메인 본문 ───────────────────────────
    main_y = 1080

    f_part_no = font(220, "paper_black")
    text_left(draw, (margin_x, main_y), f"{part_roman}.", f_part_no, GOLD)
    bbox = draw.textbbox((0, 0), f"{part_roman}.", font=f_part_no)
    part_no_w = bbox[2] - bbox[0]

    f_part_label_en = font(56, "aggro")
    text_left(draw, (margin_x + part_no_w + 60, main_y - 30), eng_label, f_part_label_en, GREY)

    # 가는 라인
    line_y = main_y + 320
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=NAVY_LIGHT, width=2)
    draw_dot(draw, margin_x, line_y, 10, GOLD)
    draw_dot(draw, W - margin_x, line_y, 10, GOLD)

    # ── 단원명 (긴 경우 자동 축소) ─────────────────────
    title_y = line_y + 200
    max_w_title = W - margin_x * 2
    title_size = fit_text_size(draw, part_name, "cafe24", max_w_title, start=280, floor=120)
    f_title = font(title_size, "cafe24")
    text_left(draw, (margin_x, title_y), part_name, f_title, WHITE)

    # 단원명 아래 골드 라인
    underline_y = title_y + title_size + 60
    draw.line([(margin_x, underline_y), (margin_x + 320, underline_y)], fill=GOLD, width=5)

    # ── 하단 도트 라인 ──────────────────────
    foot_dot_y = H - 420
    for x in range(margin_x, W - margin_x + 1, 28):
        draw_dot(draw, x, foot_dot_y, 3, NAVY_LIGHT)

    add_footer(img, draw, f"· {chapter_no} ·")
    add_frame(draw)
    return img


def make_solution_divider() -> Image.Image:
    """정답 및 해설 내지."""
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)

    margin_x = 220

    # ── 상단 라벨 ────────────────────────────────────
    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 220, top_y)], fill=GOLD, width=5)
    f_label = font(48, "aggro")
    text_left(draw, (margin_x + 260, top_y - 26), "ANSWER · KEY", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 26), "SUMMIT POINT", f_label, GREY)

    # ── 워터마크 큰 텍스트: A.K. ──────────
    f_water = font(1500, "paper_black")
    bbox = draw.textbbox((0, 0), "AK", font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 60 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 200
    draw.text((wx, wy), "AK", font=f_water, fill=WATERMARK)

    # ── 메인 제목 ────────────────────────
    main_y = 1280
    f_main = font(280, "cafe24")
    text_left(draw, (margin_x, main_y), "정답", f_main, GOLD)
    bbox = draw.textbbox((0, 0), "정답", font=f_main)
    main_w = bbox[2] - bbox[0]

    # 가운데 작은 점
    bullet_x = margin_x + main_w + 80
    bullet_y = main_y + 160
    draw_dot(draw, bullet_x, bullet_y, 18, GOLD)

    text_left(draw, (bullet_x + 80, main_y), "및 해설", f_main, WHITE)

    # 영문 부제
    sub_y = main_y + 380
    f_sub = font(70, "aggro")
    text_left(draw, (margin_x, sub_y), "A N S W E R   &   S O L U T I O N", f_sub, GREY)

    # 가는 라인
    line_y = sub_y + 200
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=NAVY_LIGHT, width=2)
    draw_dot(draw, margin_x, line_y, 10, GOLD)
    draw_dot(draw, W - margin_x, line_y, 10, GOLD)

    # 안내 카피
    copy_y = line_y + 200
    f_copy = font(60, "cafe24")
    text_left(draw, (margin_x, copy_y), "틀린 문제는 다시 풀어보고,", f_copy, WHITE)
    text_left(draw, (margin_x, copy_y + 110), "맞힌 문제도 풀이를 점검하세요.", f_copy, WHITE)

    # ── 하단 도트 라인 ──────────────────────
    foot_dot_y = H - 420
    for x in range(margin_x, W - margin_x + 1, 28):
        draw_dot(draw, x, foot_dot_y, 3, NAVY_LIGHT)

    add_footer(img, draw, "· AK ·")
    add_frame(draw)
    return img


CHAPTERS = [
    ("I", "여러가지 방정식 ~ 여러가지 부등식", "EQUATIONS & INEQUALITIES"),
    ("II", "순열·조합", "PERMUTATION & COMBINATION"),
    ("III", "행렬", "MATRIX"),
]


def main():
    pages = []
    for i, (roman, name, eng) in enumerate(CHAPTERS, start=1):
        pages.append(make_chapter_page(i, roman, name, eng))
    pages.append(make_solution_divider())

    first, rest = pages[0], pages[1:]
    first.save(OUT_PDF, "PDF", resolution=300.0, save_all=True, append_images=rest)

    preview_dir = OUT_DIR / "dividers_preview"
    preview_dir.mkdir(exist_ok=True)
    names = ["ch1_eq_ineq", "ch2_perm_comb", "ch3_matrix", "solution"]
    for i, page in enumerate(pages):
        page.save(preview_dir / f"{names[i]}.png", "PNG", optimize=True)

    print(f"[OK] PDF: {OUT_PDF} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
