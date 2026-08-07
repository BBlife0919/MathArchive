"""BASIC POINT 교재 표지 PDF 생성.

파스텔 라벤더+핑크 톤, 둥글둥글 귀여운 폰트로 여학생 취향의 표지.
"""
from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "app" / "assets" / "eum_logo.png"
OUT_DIR = ROOT / "output"
OUT_DIR.mkdir(exist_ok=True)
OUT_PDF = OUT_DIR / "cover_basic_point.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")     # 둥글둥글 친근
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")    # 임팩트 트렌디
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")   # 굵은 트렌디
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")            # 모던 산세리프

# A4 @ 300dpi
W, H = 2480, 3508

# ── 파스텔 컬러 팔레트 (여학생 취향) ─────────────────────────────
CREAM = (255, 248, 250)            # 살짝 핑크끼 도는 크림
LAVENDER_BG = (245, 238, 250)      # 배경 라벤더
DEEP_PLUM = (110, 70, 130)         # 진한 보라 (제목)
SOFT_PLUM = (165, 130, 185)        # 보조 보라
HOT_PINK = (235, 115, 155)         # 포인트 핑크
PEACH_PINK = (250, 200, 210)       # 부드러운 피치 핑크
MINT = (175, 220, 205)             # 민트
SKY = (185, 215, 235)              # 부드러운 하늘
CORAL = (240, 145, 145)            # 코랄
INK = (60, 50, 75)
MUTED = (155, 145, 165)
GOLD = (235, 195, 130)


def font(size: int, family: str = "cafe24") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "paper_black": FONT_PAPER_BLACK,
        "paper_eb": FONT_PAPER_EB,
        "aggro": FONT_AGGRO,
    }.get(family, FONT_CAFE24)
    return ImageFont.truetype(path, size=size)


def text_centered(draw, xy_center, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = xy_center[0] - w // 2 - bbox[0]
    y = xy_center[1] - h // 2 - bbox[1]
    draw.text((x, y), text, font=fnt, fill=fill)
    return w, h


def draw_sparkle(draw, cx, cy, size, color):
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


def draw_ring(draw, cx, cy, r, color, thick=6):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=color, width=thick)


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
    length = x2 - x1
    step = 6
    pts = []
    for i in range(0, length + 1, step):
        t = i / length
        y = y1 + amp * math.sin(t * math.pi * 2 * periods)
        pts.append((x1 + i, y))
    for i in range(len(pts) - 1):
        draw.line([pts[i], pts[i + 1]], fill=color, width=thick)


def draw_cloud(draw, cx, cy, size, color):
    """부드러운 구름 모양"""
    r = size
    draw.ellipse([cx - r * 1.6, cy - r * 0.4, cx - r * 0.4, cy + r * 0.8], fill=color)
    draw.ellipse([cx - r * 0.9, cy - r * 0.9, cx + r * 0.5, cy + r * 0.7], fill=color)
    draw.ellipse([cx + r * 0.2, cy - r * 0.5, cx + r * 1.6, cy + r * 0.7], fill=color)
    draw.rectangle([cx - r * 1.2, cy + r * 0.3, cx + r * 1.3, cy + r * 0.8], fill=color)


def draw_flower(draw, cx, cy, size, petal_color, center_color):
    """5장 꽃잎 꽃"""
    r = size
    for i in range(5):
        angle = -math.pi / 2 + i * (2 * math.pi / 5)
        px = cx + math.cos(angle) * r * 0.8
        py = cy + math.sin(angle) * r * 0.8
        draw.ellipse([px - r * 0.55, py - r * 0.55, px + r * 0.55, py + r * 0.55], fill=petal_color)
    draw.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=center_color)


def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), LAVENDER_BG)
    draw = ImageDraw.Draw(img)

    # ── 배경 부드러운 가로 띠 (그라디언트 대신 톤 차이) ──────────
    draw.rectangle([0, 0, W, 320], fill=CREAM)
    draw.rectangle([0, H - 320, W, H], fill=CREAM)

    # ── 상단 도트 띠 ────────────────────────────────────
    for x in range(180, W - 180, 44):
        draw_dot(draw, x, 200, 7, PEACH_PINK)

    # ── 상단 라벨 "MATH WORKBOOK · 2026" ──────────────────
    label_y = 380
    label = "M A T H · W O R K B O O K · 2 0 2 6"
    f_label = font(54, "aggro")
    bbox = draw.textbbox((0, 0), label, font=f_label)
    label_w = bbox[2] - bbox[0]
    text_centered(draw, (W // 2, label_y), label, f_label, SOFT_PLUM)
    # 라벨 양옆 작은 별
    draw_sparkle(draw, W // 2 - label_w // 2 - 60, label_y, 18, HOT_PINK)
    draw_sparkle(draw, W // 2 + label_w // 2 + 60, label_y, 18, HOT_PINK)
    # 라벨 아래 짧은 물결
    draw_squiggle(draw, W // 2 - 200, label_y + 110, W // 2 + 200, HOT_PINK, thick=8, amp=10, periods=3)

    # ── 좌상단 / 우상단 장식 (구름 + 별) ──────────────────
    draw_cloud(draw, 380, 580, 70, PEACH_PINK)
    draw_dot(draw, 280, 640, 10, MINT)
    draw_sparkle(draw, 220, 540, 22, HOT_PINK)

    draw_cloud(draw, W - 380, 600, 75, SKY)
    draw_sparkle(draw, W - 240, 540, 24, HOT_PINK)
    draw_dot(draw, W - 320, 680, 12, GOLD)
    draw_plus(draw, W - 460, 700, 18, SOFT_PLUM, thick=7)

    # ── 메인 제목 카드 (둥근 사각형 안에 BASIC POINT) ────────
    # 제목 카드 배경
    card_y1 = 950
    card_y2 = 1820
    card_margin = 220
    draw.rounded_rectangle(
        (card_margin, card_y1, W - card_margin, card_y2),
        radius=80,
        fill=CREAM,
        outline=DEEP_PLUM,
        width=8,
    )
    # 카드 좌상/우하 모서리 작은 하트·별
    draw_heart(draw, card_margin + 70, card_y1 + 70, 24, HOT_PINK)
    draw_sparkle(draw, W - card_margin - 70, card_y1 + 70, 22, HOT_PINK)
    draw_sparkle(draw, card_margin + 70, card_y2 - 70, 22, SOFT_PLUM)
    draw_heart(draw, W - card_margin - 70, card_y2 - 70, 24, SOFT_PLUM)

    # "BASIC" + "POINT" 두 줄 — 카드 안에 안전히 들어가도록 자동 피팅
    card_w_inner = (W - card_margin) - card_margin
    card_h_inner = card_y2 - card_y1
    side_pad = 130
    top_pad = 90
    mid_gap = 180  # 두 단어 사이 장식 영역
    max_text_w = card_w_inner - side_pad * 2
    max_text_h = (card_h_inner - top_pad * 2 - mid_gap) // 2

    def _fit_size(words: list[str], start: int = 440, floor: int = 200) -> int:
        for size in range(start, floor - 1, -10):
            f = font(size, "cafe24")
            ok = True
            for w_ in words:
                bx = draw.textbbox((0, 0), w_, font=f)
                if (bx[2] - bx[0]) > max_text_w or (bx[3] - bx[1]) > max_text_h:
                    ok = False
                    break
            if ok:
                return size
        return floor

    title_size = _fit_size(["BASIC", "POINT"])
    f_title = font(title_size, "cafe24")

    # 두 줄을 카드 세로 중앙 기준으로 균등 배치
    line_h = max_text_h
    basic_cy = card_y1 + top_pad + line_h // 2
    point_cy = card_y2 - top_pad - line_h // 2
    mid_cy = (basic_cy + point_cy) // 2

    text_centered(draw, (W // 2, basic_cy), "BASIC", f_title, DEEP_PLUM)

    # 가운데 작은 분리 장식: 별-하트-별
    draw_sparkle(draw, W // 2 - 110, mid_cy, 22, HOT_PINK)
    draw_heart(draw, W // 2, mid_cy, 26, HOT_PINK)
    draw_sparkle(draw, W // 2 + 110, mid_cy, 22, HOT_PINK)

    text_centered(draw, (W // 2, point_cy), "POINT", f_title, HOT_PINK)

    # ── 카드 아래 한글 부제 ─────────────────────────────
    f_kor_sub = font(86, "cafe24")
    text_centered(draw, (W // 2, 1960), "기초부터 차근차근, 핵심만 콕콕!", f_kor_sub, SOFT_PLUM)

    # 부제 양옆 꽃
    draw_flower(draw, W // 2 - 760, 1960, 28, PEACH_PINK, GOLD)
    draw_flower(draw, W // 2 + 760, 1960, 28, MINT, GOLD)

    # ── 중간 장식 라인 ─────────────────────────────────
    deco_y = 2120
    for x in range(W // 2 - 600, W // 2 + 601, 50):
        draw_dot(draw, x, deco_y, 5, MUTED)

    # ── 강사명 카드: "이영우 T" ────────────────────────────
    teacher_y = 2240
    card_w, card_h = 1000, 320
    cx1 = (W - card_w) // 2
    cy1 = teacher_y
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h
    # 둥근 카드 (핑크 톤)
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=70, fill=PEACH_PINK, outline=DEEP_PLUM, width=6)

    # 카드 안: with + 이영우 T
    f_with = font(58, "aggro")
    text_centered(draw, (W // 2, cy1 + 90), "w i t h", f_with, DEEP_PLUM)
    f_teacher = font(170, "cafe24")
    text_centered(draw, (W // 2, cy1 + 220), "이영우 T", f_teacher, DEEP_PLUM)

    # 카드 모서리 장식
    draw_sparkle(draw, cx1 + 60, cy1 + 60, 22, HOT_PINK)
    draw_heart(draw, cx2 - 60, cy1 + 60, 22, HOT_PINK)
    draw_heart(draw, cx1 + 60, cy2 - 60, 22, HOT_PINK)
    draw_sparkle(draw, cx2 - 60, cy2 - 60, 22, HOT_PINK)

    # ── 강사 카드 좌우 장식 ─────────────────────────────
    draw_cloud(draw, 380, 2400, 60, MINT)
    draw_flower(draw, 280, 2300, 26, HOT_PINK, GOLD)
    draw_dot(draw, 460, 2280, 12, SKY)
    draw_plus(draw, 220, 2440, 18, SOFT_PLUM, thick=7)
    draw_sparkle(draw, 520, 2460, 24, HOT_PINK)

    draw_cloud(draw, W - 380, 2400, 60, SKY)
    draw_flower(draw, W - 280, 2300, 26, HOT_PINK, GOLD)
    draw_dot(draw, W - 460, 2280, 12, MINT)
    draw_plus(draw, W - 220, 2440, 18, SOFT_PLUM, thick=7)
    draw_sparkle(draw, W - 520, 2460, 24, HOT_PINK)

    # ── 하단 도트 띠 ────────────────────────────────────
    for x in range(180, W - 180, 44):
        draw_dot(draw, x, H - 480, 7, PEACH_PINK)

    # ── 좌하단 카피 ─────────────────────────────────────
    f_corner = font(48, "aggro")
    draw.text((220, H - 380), "Math Basic Workbook · 2026", font=f_corner, fill=SOFT_PLUM)
    f_corner_small = font(44, "cafe24")
    draw.text((220, H - 300), "기초가 단단하면, 점수는 따라와요.", font=f_corner_small, fill=MUTED)

    # ── 우하단 로고 ────────────────────────────────────
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
    img.save(OUT_PDF, "PDF", resolution=300.0)
    png_path = OUT_PDF.with_suffix(".png")
    img.save(png_path, "PNG", optimize=True)
    print(f"[OK] PDF: {OUT_PDF}")
    print(f"[OK] PNG: {png_path}")


if __name__ == "__main__":
    main()
