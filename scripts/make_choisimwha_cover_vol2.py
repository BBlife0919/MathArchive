"""최심화교재1 교재 표지 PDF.

중단원 정복(TEXTBOOK POINT) 표지와 동일한 다크 네이비 + 골드 톤.
타이틀만 '최심화 / 교재 1', 부제 '2026년 3-1 기말대비',
중앙 하단 'with 이영우T', 우측 하단 이음학원 로고.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "output" / "summit_point" / "eum_logo_gold.png"
OUT_DIR = ROOT / "output" / "choisimwha_book2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "cover.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
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
SUMMIT_TIP = (250, 220, 165)


def font(size: int, family: str = "paper_black") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "aggro": FONT_AGGRO,
    }.get(family, FONT_PAPER_BLACK)
    return ImageFont.truetype(path, size=size)


def text_centered(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((xy[0] - w // 2 - bbox[0], xy[1] - h // 2 - bbox[1]),
              text, font=fnt, fill=fill)


def text_left(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - bbox[0], xy[1] - bbox[1]), text, font=fnt, fill=fill)


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = ImageDraw.Draw(img)

    # 배경 그라디언트
    for y in range(H):
        t = y / H
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * (1 - abs(t - 0.5) * 2))
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * (1 - abs(t - 0.5) * 2))
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * (1 - abs(t - 0.5) * 2))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    import random
    rnd = random.Random(11)
    for _ in range(180):
        x = rnd.randint(80, W - 80)
        y = rnd.randint(80, H - 80)
        r = rnd.choice([1, 1, 1, 2, 2, 3])
        c = rnd.choice([NAVY_LIGHT, MUTED, GREY, GOLD])
        if c == GOLD and rnd.random() < 0.85:
            c = NAVY_LIGHT
        draw_dot(draw, x, y, r, c)

    # 산봉우리 실루엣 (3겹)
    base_y = 2280
    poly_back = [(0, base_y - 40), (260, 1900), (700, 1500), (1100, 1850),
                 (1500, 1480), (1850, 1750), (2220, 1900), (W, base_y - 40)]
    draw.polygon(poly_back, fill=NAVY_MID)
    poly_mid = [(0, base_y - 20), (180, 2000), (560, 1730), (980, 2050),
                (1380, 1680), (1750, 1920), (2100, 1820), (W, base_y - 20)]
    draw.polygon(poly_mid, fill=NAVY)
    poly_front = [(0, base_y), (120, 2150), (480, 1860), (820, 2150),
                  (1240, 1820), (1620, 2080), (2000, 1900), (2360, 2100), (W, base_y)]
    draw.polygon(poly_front, fill=NAVY_DEEP)

    peak_x, peak_y = 1380, 1680
    for r, c in [(80, (60, 70, 110)), (50, (90, 100, 140)), (28, GOLD), (14, SUMMIT_TIP)]:
        draw.ellipse([peak_x - r, peak_y - r, peak_x + r, peak_y + r], fill=c)
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg)
        x1 = peak_x + math.cos(ang) * 40
        y1 = peak_y + math.sin(ang) * 40
        x2 = peak_x + math.cos(ang) * 130
        y2 = peak_y + math.sin(ang) * 130
        draw.line([(x1, y1), (x2, y2)], fill=GOLD, width=4)

    # 상단 라벨
    label_y = 320
    f_label = font(56, "aggro")
    label = "DEEP · MASTERY · 2026"
    bbox = draw.textbbox((0, 0), label, font=f_label)
    label_w = bbox[2] - bbox[0]
    text_centered(draw, (W // 2, label_y), label, f_label, GOLD)
    lx1 = W // 2 - label_w // 2 - 80
    lx2 = W // 2 + label_w // 2 + 80
    draw.line([(lx1 - 240, label_y), (lx1, label_y)], fill=GOLD, width=5)
    draw.line([(lx2, label_y), (lx2 + 240, label_y)], fill=GOLD, width=5)
    draw_dot(draw, lx1 - 270, label_y, 8, GOLD)
    draw_dot(draw, lx2 + 270, label_y, 8, GOLD)

    # 메인 제목: 한 줄 "최심화교재 Vol.2" — 폭에 맞춰 폰트 자동 결정
    title_cx = W // 2
    title_cy = 980
    title_text = "최심화교재 Vol.2"
    max_title_w = W - 2 * 280
    # 자동 폰트 크기 (cafe24 한글)
    title_size = 440
    while title_size > 160:
        f_try = font(title_size, "cafe24")
        bbox = draw.textbbox((0, 0), title_text, font=f_try)
        if (bbox[2] - bbox[0]) <= max_title_w:
            break
        title_size -= 10
    f_main = font(title_size, "cafe24")
    text_centered(draw, (title_cx + 6, title_cy + 8), title_text,
                  f_main, (8, 14, 30))
    text_centered(draw, (title_cx, title_cy), title_text, f_main, GOLD)

    # 다이아몬드 + 양옆 라인 — 제목 아래
    mid_cy = title_cy + title_size // 2 + 130
    line_w = 220
    draw.line([(title_cx - line_w - 80, mid_cy), (title_cx - 60, mid_cy)], fill=GOLD, width=4)
    draw.line([(title_cx + 60, mid_cy), (title_cx + line_w + 80, mid_cy)], fill=GOLD, width=4)
    dsize = 22
    diamond = [(title_cx, mid_cy - dsize), (title_cx + dsize, mid_cy),
               (title_cx, mid_cy + dsize), (title_cx - dsize, mid_cy)]
    draw.polygon(diamond, fill=GOLD)
    draw_dot(draw, title_cx - line_w - 100, mid_cy, 6, GOLD)
    draw_dot(draw, title_cx + line_w + 100, mid_cy, 6, GOLD)

    # 부제 배지
    badge_y = mid_cy + 140
    f_badge = font(78, "cafe24")
    text_centered(draw, (W // 2, badge_y), "2026년 3-1 기말대비", f_badge, GOLD_BRIGHT)
    bb_w = 460
    draw.line([(W // 2 - bb_w - 50, badge_y), (W // 2 - bb_w + 30, badge_y)],
              fill=GOLD, width=3)
    draw.line([(W // 2 + bb_w - 30, badge_y), (W // 2 + bb_w + 50, badge_y)],
              fill=GOLD, width=3)

    # 강사 영역 (중앙 하단) — with 이영우T
    teacher_y = 2620
    draw.line([(W // 2 - 320, teacher_y - 100), (W // 2 + 320, teacher_y - 100)],
              fill=GOLD, width=3)
    f_teacher_label = font(46, "aggro")
    text_centered(draw, (W // 2, teacher_y - 50), "I N S T R U C T O R",
                  f_teacher_label, GOLD)
    f_teacher = font(130, "cafe24")
    text_centered(draw, (W // 2, teacher_y + 80), "with 이영우 T", f_teacher, WHITE)
    draw.line([(W // 2 - 320, teacher_y + 200), (W // 2 + 320, teacher_y + 200)],
              fill=GOLD, width=3)

    # 하단 좌측 카피
    foot_y = H - 280
    f_foot = font(46, "aggro")
    text_left(draw, (220, foot_y), "Deep Mastery Workbook", f_foot, GOLD)
    f_foot_kr = font(40, "cafe24")
    text_left(draw, (220, foot_y + 80), "최고 심화의 정점, 한 권에 정복", f_foot_kr, GREY)

    # 우측 하단 로고
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 480
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
        margin = 200
        lx = W - target_w - margin
        ly = H - target_h - 220
        img.paste(logo_resized, (lx, ly), logo_resized)
    except Exception:
        pass

    # 프레임
    pad = 90
    draw.rectangle([pad, pad, W - pad, H - pad], outline=GOLD, width=3)
    corner = 60
    for cx, cy in [(pad, pad), (W - pad, pad), (pad, H - pad), (W - pad, H - pad)]:
        draw.line([(cx - corner, cy), (cx + corner, cy)], fill=GOLD, width=6)
        draw.line([(cx, cy - corner), (cx, cy + corner)], fill=GOLD, width=6)

    return img


def main():
    img = make_cover()
    img.save(OUT_PDF, "PDF", resolution=300.0)
    png_path = OUT_PDF.with_suffix(".png")
    img.save(png_path, "PNG", optimize=True)
    print(f"[OK] PDF: {OUT_PDF}")
    print(f"[OK] PNG: {png_path}")


if __name__ == "__main__":
    main()
