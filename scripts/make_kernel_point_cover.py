"""KERNEL POINT 교재 표지 PDF — 화이트 배경 + 깔끔 톤.

BASIC POINT 와 동일한 cafe24/aggro 폰트, 두-줄 제목 카드 구조.
배경만 흰색으로 바꾸고 데코는 미니멀하게.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH_CANDIDATES = [
    ROOT / "app" / "assets" / "eum_logo.png",
    ROOT / "output" / "summit_point" / "eum_logo_gold.png",
]
LOGO_PATH = next((p for p in LOGO_PATH_CANDIDATES if p.exists()), LOGO_PATH_CANDIDATES[0])
OUT_DIR = ROOT / "output" / "kernel_point"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "cover.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")

# A4 @ 300dpi
W, H = 2480, 3508

WHITE = (255, 255, 255)
OFF_WHITE = (252, 252, 254)
INK = (30, 38, 60)        # 메인 텍스트 (네이비 다크)
NAVY = (40, 55, 95)
ACCENT = (200, 140, 60)   # 포인트 (warm gold)
ACCENT2 = (210, 170, 90)
GREY = (140, 148, 168)
GREY_LIGHT = (210, 215, 225)
MUTED = (175, 180, 195)


def font(size: int, family: str = "cafe24") -> ImageFont.FreeTypeFont:
    path = {
        "cafe24": FONT_CAFE24,
        "aggro": FONT_AGGRO,
        "paper_black": FONT_PAPER_BLACK,
    }.get(family, FONT_CAFE24)
    return ImageFont.truetype(path, size=size)


def text_centered(draw, xy, text, fnt, fill):
    bbox = draw.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text((xy[0] - w // 2 - bbox[0], xy[1] - h // 2 - bbox[1]),
              text, font=fnt, fill=fill)
    return w, h


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    draw = ImageDraw.Draw(img)

    # 상단 / 하단 얇은 라인
    draw.line([(220, 280), (W - 220, 280)], fill=GREY_LIGHT, width=2)
    draw.line([(220, H - 280), (W - 220, H - 280)], fill=GREY_LIGHT, width=2)

    # 상단 라벨
    label_y = 380
    label = "M A T H · W O R K B O O K · 2 0 2 6"
    f_label = font(54, "aggro")
    bbox = draw.textbbox((0, 0), label, font=f_label)
    label_w = bbox[2] - bbox[0]
    text_centered(draw, (W // 2, label_y), label, f_label, ACCENT)
    # 양옆 짧은 라인
    draw.line([(W // 2 - label_w // 2 - 220, label_y),
               (W // 2 - label_w // 2 - 60, label_y)],
              fill=ACCENT, width=4)
    draw.line([(W // 2 + label_w // 2 + 60, label_y),
               (W // 2 + label_w // 2 + 220, label_y)],
              fill=ACCENT, width=4)
    draw_dot(draw, W // 2 - label_w // 2 - 250, label_y, 7, ACCENT)
    draw_dot(draw, W // 2 + label_w // 2 + 250, label_y, 7, ACCENT)

    # ── 메인 제목 카드 (둥근 사각형) ───────────────────────
    card_y1 = 800
    card_y2 = 1820
    card_margin = 220
    draw.rounded_rectangle(
        (card_margin, card_y1, W - card_margin, card_y2),
        radius=70,
        fill=OFF_WHITE,
        outline=INK,
        width=6,
    )

    # 두 줄 KERNEL / POINT — 자동 폰트 fit
    card_w_inner = (W - card_margin) - card_margin
    card_h_inner = card_y2 - card_y1
    side_pad = 130
    top_pad = 90
    mid_gap = 160
    max_text_w = card_w_inner - side_pad * 2
    max_text_h = (card_h_inner - top_pad * 2 - mid_gap) // 2

    def _fit_size(words, start=460, floor=200):
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

    title_size = _fit_size(["KERNEL", "POINT"])
    f_title = font(title_size, "cafe24")
    line_h = max_text_h
    kernel_cy = card_y1 + top_pad + line_h // 2
    point_cy = card_y2 - top_pad - line_h // 2
    mid_cy = (kernel_cy + point_cy) // 2

    text_centered(draw, (W // 2, kernel_cy), "KERNEL", f_title, INK)

    # 가운데 분리 장식 - 짧은 가로 라인 + 다이아몬드
    seg_w = 220
    draw.line([(W // 2 - seg_w - 60, mid_cy), (W // 2 - 60, mid_cy)],
              fill=ACCENT, width=4)
    draw.line([(W // 2 + 60, mid_cy), (W // 2 + seg_w + 60, mid_cy)],
              fill=ACCENT, width=4)
    dsize = 18
    diamond = [(W // 2, mid_cy - dsize), (W // 2 + dsize, mid_cy),
               (W // 2, mid_cy + dsize), (W // 2 - dsize, mid_cy)]
    draw.polygon(diamond, fill=ACCENT)

    text_centered(draw, (W // 2, point_cy), "POINT", f_title, ACCENT)

    # ── 부제: 2026 3-1 내신대비 ─────────────────────────
    f_sub = font(90, "cafe24")
    text_centered(draw, (W // 2, 1980), "2026 3-1 내신대비", f_sub, INK)

    # 그 아래: 실전기출문제 — 작고 캡션 톤
    f_sub2 = font(64, "aggro")
    text_centered(draw, (W // 2, 2100), "실전 기출 문제", f_sub2, GREY)

    # 부제 양옆 작은 점
    draw_dot(draw, W // 2 - 700, 1980, 8, ACCENT)
    draw_dot(draw, W // 2 + 700, 1980, 8, ACCENT)

    # ── 중간 가는 점선 띠 ─────────────────────────────
    deco_y = 2240
    for x in range(W // 2 - 700, W // 2 + 701, 38):
        draw_dot(draw, x, deco_y, 4, MUTED)

    # ── 강사 카드: with 이영우 T ───────────────────────
    teacher_y = 2360
    card_w, card_h = 1000, 320
    cx1 = (W - card_w) // 2
    cy1 = teacher_y
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=60,
                           fill=OFF_WHITE, outline=INK, width=5)
    f_with = font(56, "aggro")
    text_centered(draw, (W // 2, cy1 + 90), "w i t h", f_with, ACCENT)
    f_teacher = font(160, "cafe24")
    text_centered(draw, (W // 2, cy1 + 215), "이영우 T", f_teacher, INK)

    # 카드 네 모서리 작은 점
    for cx, cy in [(cx1 + 60, cy1 + 60), (cx2 - 60, cy1 + 60),
                   (cx1 + 60, cy2 - 60), (cx2 - 60, cy2 - 60)]:
        draw_dot(draw, cx, cy, 6, ACCENT)

    # ── 좌하단 카피 ─────────────────────────────────
    f_corner = font(48, "aggro")
    draw.text((220, H - 380), "Math Kernel Workbook · 2026", font=f_corner, fill=ACCENT)
    f_corner_small = font(40, "cafe24")
    draw.text((220, H - 300), "핵심만 정확히, 실전으로 단단하게.", font=f_corner_small, fill=GREY)

    # ── 우하단 로고 ───────────────────────────────
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 520
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
        margin = 200
        lx = W - target_w - margin
        ly = H - target_h - margin
        img.paste(logo_resized, (lx, ly), logo_resized)
    except Exception:
        pass

    # ── 외곽 얇은 프레임 (선택적, 깔끔) ───────────────
    pad = 90
    draw.rectangle([pad, pad, W - pad, H - pad], outline=GREY_LIGHT, width=2)

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
