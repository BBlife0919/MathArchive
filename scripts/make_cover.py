"""2026 1학기 기말대비 / 공통수학1 표지 PDF 생성.

크림 배경 + 딥틸(로고색) + 코랄 포인트의 친근한 톤.
"""
from __future__ import annotations

import math
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "app" / "assets" / "eum_logo.png"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)
OUT_PDF = OUT_DIR / "cover_2026_1학기_기말대비.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")     # 둥글둥글 친근
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")    # 임팩트 트렌디
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")   # 굵은 트렌디
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")             # 모던 산세리프
# fallback
FONT_TTC = "/System/Library/Fonts/AppleSDGothicNeo.ttc"

# A4 @ 300dpi
W, H = 2480, 3508

CREAM = (255, 244, 232)
DEEP_TEAL = (19, 62, 92)        # 로고색
SOFT_TEAL = (60, 110, 140)
CORAL = (232, 130, 115)
PEACH = (245, 200, 180)
SAGE = (180, 210, 195)
DUSTY_ROSE = (220, 160, 160)
INK = (45, 55, 75)
MUTED = (130, 140, 155)


def font(size: int, family: str = "cafe24") -> ImageFont.FreeTypeFont:
    """family: cafe24 / paper_black / paper_eb / aggro"""
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "paper_eb": FONT_PAPER_EB,
        "aggro": FONT_AGGRO,
    }.get(family, FONT_CAFE24)
    return ImageFont.truetype(path, size=size)


def rounded_pill(draw: ImageDraw.ImageDraw, xy, fill, outline=None, width=0):
    draw.rounded_rectangle(xy, radius=(xy[3] - xy[1]) // 2, fill=fill, outline=outline, width=width)


def text_centered(draw, xy_center, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = xy_center[0] - w // 2 - bbox[0]
    y = xy_center[1] - h // 2 - bbox[1]
    draw.text((x, y), text, font=fnt, fill=fill)
    return w, h


def draw_sparkle(draw, cx, cy, size, color):
    """4점 별 모양 ✦"""
    s = size
    pts = [
        (cx, cy - s),
        (cx + s * 0.25, cy - s * 0.25),
        (cx + s, cy),
        (cx + s * 0.25, cy + s * 0.25),
        (cx, cy + s),
        (cx - s * 0.25, cy + s * 0.25),
        (cx - s, cy),
        (cx - s * 0.25, cy - s * 0.25),
    ]
    draw.polygon(pts, fill=color)


def draw_plus(draw, cx, cy, size, color, thick=None):
    if thick is None:
        thick = max(3, size // 4)
    draw.rectangle([cx - thick // 2, cy - size, cx + thick // 2, cy + size], fill=color)
    draw.rectangle([cx - size, cy - thick // 2, cx + size, cy + thick // 2], fill=color)


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def draw_heart(draw, cx, cy, size, color):
    r = size // 2
    draw.ellipse([cx - size, cy - r, cx, cy + r], fill=color)
    draw.ellipse([cx, cy - r, cx + size, cy + r], fill=color)
    pts = [
        (cx - size, cy + r // 4),
        (cx + size, cy + r // 4),
        (cx, cy + size + r // 2),
    ]
    draw.polygon(pts, fill=color)


def draw_squiggle(draw, x1, y1, x2, color, thick=8, amp=24, periods=3):
    """물결선"""
    length = x2 - x1
    step = 6
    pts = []
    for i in range(0, length + 1, step):
        t = i / length
        y = y1 + amp * math.sin(t * math.pi * 2 * periods)
        pts.append((x1 + i, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color, width=thick)


def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # ── 상단 장식 띠 (점선 느낌의 도트) ────────────────────────
    for x in range(180, W - 180, 40):
        draw_dot(draw, x, 200, 6, PEACH)

    # ── 좌상단 라벨 "MATH NOTE 2026" ──────────────────────────
    label_y = 320
    label = "M A T H · N O T E · 2 0 2 6"
    f_label = font(56, "aggro")
    draw.text((220, label_y), label, font=f_label, fill=SOFT_TEAL)
    # 라벨 아래 짧은 선
    draw.line([(220, label_y + 110), (520, label_y + 110)], fill=CORAL, width=8)

    # ── 우상단 작은 별/도트 장식 ───────────────────────────
    draw_sparkle(draw, W - 380, 360, 28, CORAL)
    draw_sparkle(draw, W - 280, 460, 18, DEEP_TEAL)
    draw_dot(draw, W - 220, 360, 14, PEACH)
    draw_plus(draw, W - 460, 470, 20, SAGE, thick=8)

    # ── 메인 제목: "2026" 큰 숫자 + "1학기 기말대비" ──────────
    # 큰 연도 숫자 (배경 액센트 느낌)
    f_year = font(640, "paper_black")
    text_centered(draw, (W // 2, 900), "2026", f_year, DEEP_TEAL)

    # 메인 카피 — 둥글둥글 친근한 Cafe24 Ssurround
    f_main = font(280, "cafe24")
    text_centered(draw, (W // 2, 1340), "1학기 기말대비", f_main, INK)

    # 메인 카피 밑 물결선
    draw_squiggle(draw, W // 2 - 360, 1500, W // 2 + 360, CORAL, thick=10, amp=18, periods=3)

    # ── 부제 배지: "공통수학 1" ───────────────────────────
    badge_w, badge_h = 1100, 240
    bx1 = (W - badge_w) // 2
    by1 = 1640
    bx2 = bx1 + badge_w
    by2 = by1 + badge_h
    rounded_pill(draw, (bx1, by1, bx2, by2), fill=CORAL)
    f_sub = font(160, "cafe24")
    text_centered(draw, (W // 2, (by1 + by2) // 2 - 8), "공통수학 1", f_sub, (255, 250, 245))

    # 배지 양옆 작은 별
    draw_sparkle(draw, bx1 - 80, (by1 + by2) // 2, 26, DEEP_TEAL)
    draw_sparkle(draw, bx2 + 80, (by1 + by2) // 2, 26, DEEP_TEAL)

    # ── 중앙 장식 영역 (귀여운 요소 산포) ─────────────────────
    deco_y = 2080
    # 작은 동그라미 점선
    for x in range(W // 2 - 500, W // 2 + 501, 50):
        draw_dot(draw, x, deco_y, 5, MUTED)

    # 가운데 하트
    draw_heart(draw, W // 2, deco_y + 130, 36, DUSTY_ROSE)

    # 좌측 장식 그룹
    draw_sparkle(draw, 380, 2200, 32, CORAL)
    draw_dot(draw, 470, 2280, 14, SAGE)
    draw_plus(draw, 320, 2320, 22, DEEP_TEAL, thick=8)
    draw_dot(draw, 280, 2200, 10, PEACH)

    # 우측 장식 그룹
    draw_sparkle(draw, W - 380, 2240, 32, DEEP_TEAL)
    draw_dot(draw, W - 480, 2180, 12, CORAL)
    draw_plus(draw, W - 320, 2300, 22, SAGE, thick=8)
    draw_heart(draw, W - 280, 2200, 22, DUSTY_ROSE)

    # ── 강사명: "이영우 T" 친근한 핸드라이팅풍 박스 ──────────
    teacher_y = 2520
    # 카드 배경 (둥근 사각형)
    card_w, card_h = 900, 280
    cx1 = (W - card_w) // 2
    cy1 = teacher_y
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=60, fill=(255, 250, 244), outline=DEEP_TEAL, width=6)

    # 카드 안 텍스트: "with"  + "이영우 T"
    f_with = font(56, "aggro")
    text_centered(draw, (W // 2, cy1 + 80), "w i t h", f_with, MUTED)
    f_teacher = font(150, "cafe24")
    text_centered(draw, (W // 2, cy1 + 195), "이영우 T", f_teacher, DEEP_TEAL)

    # 카드 모서리 별
    draw_sparkle(draw, cx1 + 50, cy1 + 50, 18, CORAL)
    draw_sparkle(draw, cx2 - 50, cy2 - 50, 18, CORAL)

    # ── 하단 장식 라인 ───────────────────────────────────
    for x in range(180, W - 180, 40):
        draw_dot(draw, x, H - 480, 6, PEACH)

    # ── 좌하단 코너 카피 ─────────────────────────────────
    f_corner = font(50, "aggro")
    draw.text((220, H - 380), "Final Exam Prep · Spring 2026", font=f_corner, fill=SOFT_TEAL)
    f_corner_small = font(46, "cafe24")
    draw.text((220, H - 300), "함께 한 걸음씩, 끝까지.", font=f_corner_small, fill=MUTED)

    # ── 우하단 로고 ──────────────────────────────────────
    logo = Image.open(LOGO_PATH).convert("RGBA")
    target_w = 520
    ratio = target_w / logo.width
    target_h = int(logo.height * ratio)
    logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
    margin = 200
    lx = W - target_w - margin
    ly = H - target_h - margin
    img.paste(logo_resized, (lx, ly), logo_resized)

    return img


def main():
    img = make_cover()
    # PDF 저장 (단일 페이지)
    img.save(OUT_PDF, "PDF", resolution=300.0)
    # 미리보기용 PNG 도 함께
    png_path = OUT_PDF.with_suffix(".png")
    img.save(png_path, "PNG", optimize=True)
    print(f"[OK] PDF: {OUT_PDF}")
    print(f"[OK] PNG: {png_path}")


if __name__ == "__main__":
    main()
