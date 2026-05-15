"""SUMMIT POINT 교재 표지 PDF 생성.

남성적/모던/프리미엄 톤. 산봉우리 모티프 + 다크 네이비 + 골드 포인트.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "output" / "summit_point" / "eum_logo_gold.png"
OUT_DIR = ROOT / "output" / "summit_point"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "cover.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

# A4 @ 300dpi
W, H = 2480, 3508

# ── 다크/프리미엄 팔레트 ─────────────────────────────────────────
NAVY_DEEP = (15, 25, 50)         # 깊은 네이비 배경
NAVY = (24, 38, 75)
NAVY_MID = (35, 55, 100)
NAVY_LIGHT = (60, 90, 145)
GOLD = (210, 175, 110)           # 골드 (포인트)
GOLD_BRIGHT = (240, 205, 135)
WHITE = (245, 245, 250)
GREY = (170, 180, 200)
MUTED = (110, 125, 150)
PEAK_LINE = (90, 120, 175)
SUMMIT_TIP = (250, 220, 165)     # 정상 햇빛


def font(size: int, family: str = "paper_black") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "paper_eb": FONT_PAPER_EB,
        "aggro": FONT_AGGRO,
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


def text_right(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    draw.text((xy[0] - w - bbox[0], xy[1] - bbox[1]), text, font=fnt, fill=fill)


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = ImageDraw.Draw(img)

    # ── 배경 그라디언트 효과 (가로 띠로 분위기) ─────────────────
    # 위쪽은 약간 더 어둡게, 가운데는 살짝 밝게
    for y in range(H):
        t = y / H
        # 위 → 가운데 → 아래 톤
        r = int(NAVY_DEEP[0] + (NAVY[0] - NAVY_DEEP[0]) * (1 - abs(t - 0.5) * 2))
        g = int(NAVY_DEEP[1] + (NAVY[1] - NAVY_DEEP[1]) * (1 - abs(t - 0.5) * 2))
        b = int(NAVY_DEEP[2] + (NAVY[2] - NAVY_DEEP[2]) * (1 - abs(t - 0.5) * 2))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # ── 미세한 별/점 텍스처 (배경) ───────────────────────────
    import random
    rnd = random.Random(7)
    for _ in range(180):
        x = rnd.randint(80, W - 80)
        y = rnd.randint(80, H - 80)
        r = rnd.choice([1, 1, 1, 2, 2, 3])
        c = rnd.choice([NAVY_LIGHT, MUTED, GREY, GOLD])
        if c == GOLD and rnd.random() < 0.85:
            c = NAVY_LIGHT
        draw_dot(draw, x, y, r, c)

    # ── 산봉우리 (SUMMIT) 실루엣 ───────────────────────────
    # 세 겹의 산: 뒤 → 가운데 → 앞 (점점 진하게)
    base_y = 2280
    # 가장 뒤
    back_peaks = [
        (260, 1900), (700, 1500), (1100, 1850),
        (1500, 1480), (1850, 1750), (2220, 1900),
    ]
    poly = [(0, base_y - 40)]
    poly += back_peaks
    poly += [(W, base_y - 40)]
    draw.polygon(poly, fill=NAVY_MID)

    # 가운데
    mid_peaks = [
        (180, 2000), (560, 1730), (980, 2050),
        (1380, 1680), (1750, 1920), (2100, 1820),
    ]
    poly = [(0, base_y - 20)]
    poly += mid_peaks
    poly += [(W, base_y - 20)]
    draw.polygon(poly, fill=NAVY)

    # 앞 (가장 진함)
    front_peaks = [
        (120, 2150), (480, 1860), (820, 2150),
        (1240, 1820), (1620, 2080), (2000, 1900), (2360, 2100),
    ]
    poly = [(0, base_y)]
    poly += front_peaks
    poly += [(W, base_y)]
    draw.polygon(poly, fill=NAVY_DEEP)

    # 정상 햇빛 (가운데 가장 높은 봉우리에)
    peak_x, peak_y = 1380, 1680
    for r, c in [(80, (60, 70, 110)), (50, (90, 100, 140)), (28, GOLD), (14, SUMMIT_TIP)]:
        draw.ellipse([peak_x - r, peak_y - r, peak_x + r, peak_y + r], fill=c)

    # 햇빛 광선 (얇은 선)
    for ang_deg in range(0, 360, 30):
        ang = math.radians(ang_deg)
        x1 = peak_x + math.cos(ang) * 40
        y1 = peak_y + math.sin(ang) * 40
        x2 = peak_x + math.cos(ang) * 130
        y2 = peak_y + math.sin(ang) * 130
        draw.line([(x1, y1), (x2, y2)], fill=GOLD, width=4)

    # ── 상단 라벨 ────────────────────────────────────────
    label_y = 320
    # 좌측 라인 + 라벨 + 우측 라인
    f_label = font(56, "aggro")
    label = "MATH · MOCK EXAM · 2026"
    bbox = draw.textbbox((0, 0), label, font=f_label)
    label_w = bbox[2] - bbox[0]
    text_centered(draw, (W // 2, label_y), label, f_label, GOLD)
    lx1 = W // 2 - label_w // 2 - 80
    lx2 = W // 2 + label_w // 2 + 80
    draw.line([(lx1 - 240, label_y), (lx1, label_y)], fill=GOLD, width=5)
    draw.line([(lx2, label_y), (lx2 + 240, label_y)], fill=GOLD, width=5)
    draw_dot(draw, lx1 - 270, label_y, 8, GOLD)
    draw_dot(draw, lx2 + 270, label_y, 8, GOLD)

    # ── 메인 제목: SUMMIT POINT ──────────────────────────
    title_cx = W // 2
    summit_cy = 760

    # SUMMIT (위)
    f_summit = font(420, "paper_black")
    # 가벼운 그림자 효과
    text_centered(draw, (title_cx + 6, summit_cy + 8), "SUMMIT", f_summit, (8, 14, 30))
    text_centered(draw, (title_cx, summit_cy), "SUMMIT", f_summit, WHITE)

    # POINT (아래) — 골드 색
    point_cy = summit_cy + 380
    f_point = font(420, "paper_black")
    text_centered(draw, (title_cx + 6, point_cy + 8), "POINT", f_point, (8, 14, 30))
    text_centered(draw, (title_cx, point_cy), "POINT", f_point, GOLD)

    # 가운데 구분 장식 — 작은 다이아몬드 + 라인
    mid_cy = (summit_cy + point_cy) // 2 + 30
    line_w = 180
    draw.line([(title_cx - line_w - 80, mid_cy), (title_cx - 60, mid_cy)], fill=GOLD, width=4)
    draw.line([(title_cx + 60, mid_cy), (title_cx + line_w + 80, mid_cy)], fill=GOLD, width=4)
    # 가운데 다이아몬드
    dsize = 22
    diamond = [
        (title_cx, mid_cy - dsize),
        (title_cx + dsize, mid_cy),
        (title_cx, mid_cy + dsize),
        (title_cx - dsize, mid_cy),
    ]
    draw.polygon(diamond, fill=GOLD)
    draw_dot(draw, title_cx - line_w - 100, mid_cy, 6, GOLD)
    draw_dot(draw, title_cx + line_w + 100, mid_cy, 6, GOLD)

    # ── 부제 ─────────────────────────────────────────
    # 위쪽: 공수1 기말대비 (작고 골드, 라벨 느낌)
    badge_y = point_cy + 230
    f_badge = font(78, "cafe24")
    text_centered(draw, (W // 2, badge_y), "공수1 기말대비", f_badge, GOLD_BRIGHT)
    # 양 옆 짧은 골드 라인
    bb_w = 360
    draw.line([(W // 2 - bb_w - 50, badge_y), (W // 2 - bb_w + 30, badge_y)],
              fill=GOLD, width=3)
    draw.line([(W // 2 + bb_w - 30, badge_y), (W // 2 + bb_w + 50, badge_y)],
              fill=GOLD, width=3)

    # 메인 부제
    subtitle_y = badge_y + 130
    f_sub = font(120, "cafe24")
    text_centered(draw, (W // 2, subtitle_y), "모의고사 완전 정복", f_sub, WHITE)

    # 영문 보조 카피
    f_sub_en = font(40, "aggro")
    text_centered(draw, (W // 2, subtitle_y + 120), "C O N Q U E R   T H E   S U M M I T",
                  f_sub_en, GREY)

    # ── 강사명: 이영우 T ─────────────────────────────────
    teacher_y = 2580
    # 단순한 라인 위 강사명 (카드 없이 미니멀)
    draw.line([(W // 2 - 320, teacher_y - 100), (W // 2 + 320, teacher_y - 100)],
              fill=GOLD, width=3)
    f_teacher_label = font(46, "aggro")
    text_centered(draw, (W // 2, teacher_y - 50), "I N S T R U C T O R", f_teacher_label, GOLD)
    f_teacher = font(140, "cafe24")
    text_centered(draw, (W // 2, teacher_y + 80), "이영우 T", f_teacher, WHITE)
    draw.line([(W // 2 - 320, teacher_y + 200), (W // 2 + 320, teacher_y + 200)],
              fill=GOLD, width=3)

    # ── 하단 좌측: 카피 ─────────────────────────────────
    foot_y = H - 280
    f_foot = font(46, "aggro")
    text_left(draw, (220, foot_y), "Math Mock-Exam Workbook", f_foot, GOLD)
    f_foot_kr = font(40, "cafe24")
    text_left(draw, (220, foot_y + 80), "정상을 향한 마지막 한 걸음", f_foot_kr, GREY)

    # ── 하단 우측: 로고 ─────────────────────────────────
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

    # ── 외곽 얇은 골드 프레임 ───────────────────────────
    pad = 90
    draw.rectangle([pad, pad, W - pad, H - pad], outline=GOLD, width=3)
    # 모서리 장식
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
