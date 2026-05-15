"""중단원 평가(2-2단원) 내지 디바이더 — 5 챕터 + 정답해설.

SUMMIT POINT 디바이더와 동일한 다크 네이비 + 골드 톤.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "output" / "summit_point" / "eum_logo_gold.png"
OUT_DIR = ROOT / "output" / "jungdan_eval_2_2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "dividers.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

W, H = 2480, 3508

NAVY_DEEP = (15, 25, 50)
NAVY = (24, 38, 75)
NAVY_LIGHT = (60, 90, 145)
GOLD = (210, 175, 110)
WHITE = (245, 245, 250)
GREY = (170, 180, 200)
MUTED = (110, 125, 150)
WATERMARK = (32, 48, 90)


def font(size: int, family: str = "paper_black") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "aggro": FONT_AGGRO,
    }.get(family, FONT_PAPER_BLACK)
    return ImageFont.truetype(path, size=size)


def text_left(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - bx[0], xy[1] - bx[1]), text, font=fnt, fill=fill)


def text_right(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    w = bx[2] - bx[0]
    draw.text((xy[0] - w - bx[0], xy[1] - bx[1]), text, font=fnt, fill=fill)


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def fit_text_size(draw, text: str, family: str, max_w: int,
                  start: int = 280, floor: int = 110) -> int:
    for size in range(start, floor - 1, -6):
        f = font(size, family)
        bx = draw.textbbox((0, 0), text, font=f)
        if (bx[2] - bx[0]) <= max_w:
            return size
    return floor


def add_background(img):
    draw = ImageDraw.Draw(img)
    for y in range(H):
        t = y / H
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * (1 - abs(t - 0.5) * 2))
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * (1 - abs(t - 0.5) * 2))
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * (1 - abs(t - 0.5) * 2))
        draw.line([(0, y), (W, y)], fill=(r, g, b))
    import random
    rnd = random.Random(17)
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
    f_foot = font(46, "aggro")
    text_left(draw, (220, H - 280), "TEXTBOOK POINT", f_foot, GOLD)
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


def make_chapter_page(idx: int, roman: str, part_name: str, eng_label: str) -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)

    margin_x = 220
    chapter_no = f"{idx:02d}"

    # 상단 라벨
    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 220, top_y)], fill=GOLD, width=5)
    f_label = font(48, "aggro")
    text_left(draw, (margin_x + 260, top_y - 26), f"PART · {chapter_no}", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 26), "TEXTBOOK POINT", f_label, GREY)

    # 워터마크 거대 숫자
    f_water = font(1400, "paper_black")
    bbox = draw.textbbox((0, 0), chapter_no, font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 100 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 220
    draw.text((wx, wy), chapter_no, font=f_water, fill=WATERMARK)

    # 본문
    main_y = 1080
    f_part_no = font(220, "paper_black")
    text_left(draw, (margin_x, main_y), f"{roman}.", f_part_no, GOLD)
    bbox = draw.textbbox((0, 0), f"{roman}.", font=f_part_no)
    part_no_w = bbox[2] - bbox[0]
    f_part_label_en = font(56, "aggro")
    text_left(draw, (margin_x + part_no_w + 60, main_y - 30), eng_label,
              f_part_label_en, GREY)

    line_y = main_y + 320
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=NAVY_LIGHT, width=2)
    draw_dot(draw, margin_x, line_y, 10, GOLD)
    draw_dot(draw, W - margin_x, line_y, 10, GOLD)

    title_y = line_y + 200
    max_w_title = W - margin_x * 2
    title_size = fit_text_size(draw, part_name, "cafe24", max_w_title,
                               start=280, floor=120)
    f_title = font(title_size, "cafe24")
    text_left(draw, (margin_x, title_y), part_name, f_title, WHITE)

    underline_y = title_y + title_size + 60
    draw.line([(margin_x, underline_y), (margin_x + 320, underline_y)],
              fill=GOLD, width=5)

    foot_dot_y = H - 420
    for x in range(margin_x, W - margin_x + 1, 28):
        draw_dot(draw, x, foot_dot_y, 3, NAVY_LIGHT)

    add_footer(img, draw, f"· {chapter_no} ·")
    add_frame(draw)
    return img


def make_solution_divider() -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)
    margin_x = 220

    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 220, top_y)], fill=GOLD, width=5)
    f_label = font(48, "aggro")
    text_left(draw, (margin_x + 260, top_y - 26), "ANSWER · KEY", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 26), "TEXTBOOK POINT", f_label, GREY)

    f_water = font(1500, "paper_black")
    bbox = draw.textbbox((0, 0), "AK", font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 60 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 200
    draw.text((wx, wy), "AK", font=f_water, fill=WATERMARK)

    main_y = 1280
    f_main = font(280, "cafe24")
    text_left(draw, (margin_x, main_y), "정답", f_main, GOLD)
    bbox = draw.textbbox((0, 0), "정답", font=f_main)
    main_w = bbox[2] - bbox[0]
    bullet_x = margin_x + main_w + 80
    bullet_y = main_y + 160
    draw_dot(draw, bullet_x, bullet_y, 18, GOLD)
    text_left(draw, (bullet_x + 80, main_y), "및 해설", f_main, WHITE)

    sub_y = main_y + 380
    f_sub = font(70, "aggro")
    text_left(draw, (margin_x, sub_y), "A N S W E R   &   S O L U T I O N",
              f_sub, GREY)

    line_y = sub_y + 200
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=NAVY_LIGHT, width=2)
    draw_dot(draw, margin_x, line_y, 10, GOLD)
    draw_dot(draw, W - margin_x, line_y, 10, GOLD)

    copy_y = line_y + 200
    f_copy = font(60, "cafe24")
    text_left(draw, (margin_x, copy_y), "틀린 문제는 다시 풀어보고,", f_copy, WHITE)
    text_left(draw, (margin_x, copy_y + 110), "맞힌 문제도 풀이를 점검하세요.",
              f_copy, WHITE)

    foot_dot_y = H - 420
    for x in range(margin_x, W - margin_x + 1, 28):
        draw_dot(draw, x, foot_dot_y, 3, NAVY_LIGHT)

    add_footer(img, draw, "· AK ·")
    add_frame(draw)
    return img


from extract_jungdan_problems import CHAPTERS  # noqa: E402


def main():
    pages = []
    for i, ch in enumerate(CHAPTERS, start=1):
        pages.append(make_chapter_page(i, ch["roman"], ch["name"], ch["eng"]))
    pages.append(make_solution_divider())

    first, rest = pages[0], pages[1:]
    first.save(OUT_PDF, "PDF", resolution=300.0, save_all=True, append_images=rest)

    preview_dir = OUT_DIR / "dividers_preview"
    preview_dir.mkdir(exist_ok=True)
    for i, page in enumerate(pages):
        nm = f"ch{i+1}" if i < len(CHAPTERS) else "solution"
        page.save(preview_dir / f"{nm}.png", "PNG", optimize=True)

    print(f"[OK] PDF: {OUT_PDF} ({len(pages)} pages)")


if __name__ == "__main__":
    main()
