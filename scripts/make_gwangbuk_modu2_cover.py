"""광북 모고2 v2 표지 — 손그림 캐릭터 가운데 크게."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "gwangbuk_modu2"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "cover.pdf"
CHAR_IMG = Path("/Users/youngwoolee/.claude/image-cache/8316f005-83f3-4cde-953f-c612daf4bb81/192.png")

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

W, H = 2480, 3508

CREAM = (255, 250, 245)
PINK = (255, 200, 215)
PEACH = (255, 180, 160)
LAVENDER = (220, 210, 245)
MINT = (200, 240, 220)
DEEP_PINK = (235, 120, 145)
INK = (40, 40, 55)
GREY = (120, 120, 140)
GOLD = (220, 175, 110)


def font(size, family="cafe24"):
    path = FONT_CAFE24 if family == "cafe24" else FONT_AGGRO
    return ImageFont.truetype(path, size=size)


def text_centered(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    w = bx[2] - bx[0]
    h = bx[3] - bx[1]
    draw.text((xy[0] - w // 2 - bx[0], xy[1] - h // 2 - bx[1]),
              text, font=fnt, fill=fill)


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def draw_heart(draw, cx, cy, size, color):
    r = size // 2
    draw.ellipse([cx - size, cy - r, cx, cy + r], fill=color)
    draw.ellipse([cx, cy - r, cx + size, cy + r], fill=color)
    pts = [(cx - size, cy + r // 4), (cx + size, cy + r // 4),
           (cx, cy + size + r // 2)]
    draw.polygon(pts, fill=color)


def draw_sparkle(draw, cx, cy, size, color):
    s = size
    pts = [(cx, cy - s), (cx + s * 0.25, cy - s * 0.25),
           (cx + s, cy), (cx + s * 0.25, cy + s * 0.25),
           (cx, cy + s), (cx - s * 0.25, cy + s * 0.25),
           (cx - s, cy), (cx - s * 0.25, cy - s * 0.25)]
    draw.polygon(pts, fill=color)


def make_cover():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)

    # 부드러운 배경 그라데이션 (위→아래 크림→연핑크)
    for y in range(H):
        t = y / H
        r = int(CREAM[0] * (1 - t) + PINK[0] * t * 0.3 + CREAM[0] * (1 - t * 0.3))
        g = int(CREAM[1] * (1 - t) + PINK[1] * t * 0.3 + CREAM[1] * (1 - t * 0.3))
        b = int(CREAM[2] * (1 - t) + PINK[2] * t * 0.3 + CREAM[2] * (1 - t * 0.3))
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 흩뿌린 도트 (귀여운 배경)
    import random
    rnd = random.Random(7)
    for _ in range(120):
        x = rnd.randint(60, W - 60)
        y = rnd.randint(60, H - 60)
        r = rnd.choice([3, 4, 5, 6])
        c = rnd.choice([PINK, PEACH, LAVENDER, MINT, GOLD])
        draw_dot(draw, x, y, r, c)

    # 캐릭터 배치 (가운데, 크게)
    char = Image.open(CHAR_IMG).convert("RGBA")
    target_w = 1500
    ratio = target_w / char.width
    target_h = int(char.height * ratio)
    char_resized = char.resize((target_w, target_h), Image.LANCZOS)
    cx0 = (W - target_w) // 2
    cy0 = (H - target_h) // 2 - 80
    img.paste(char_resized, (cx0, cy0), char_resized)

    # 위쪽 라벨
    label_y = 320
    f_label = font(70, "aggro")
    text_centered(draw, (W // 2, label_y), "P R I N T   M A S T E R Y · 2026",
                  f_label, DEEP_PINK)

    # 라벨 양옆 하트
    draw_heart(draw, W // 2 - 720, label_y, 18, DEEP_PINK)
    draw_heart(draw, W // 2 + 720, label_y, 18, DEEP_PINK)

    # 위쪽 큰 타이틀
    title_y = 460
    f_title = font(160, "cafe24")
    text_centered(draw, (W // 2, title_y), "광북 기말 모고 ②", f_title, INK)

    # 아래 부제
    sub_y = H - 620
    f_sub = font(96, "cafe24")
    text_centered(draw, (W // 2, sub_y), "공통수학1 · 14문항", f_sub, INK)

    # 강사명 카드
    teacher_y = H - 380
    card_w, card_h = 900, 280
    cx1 = (W - card_w) // 2
    cy1 = teacher_y - card_h // 2
    cx2 = cx1 + card_w
    cy2 = cy1 + card_h
    draw.rounded_rectangle((cx1, cy1, cx2, cy2), radius=64,
                           fill=(255, 255, 255), outline=DEEP_PINK, width=6)
    f_with = font(54, "aggro")
    text_centered(draw, (W // 2, cy1 + 78), "w i t h", f_with, DEEP_PINK)
    f_teacher = font(140, "cafe24")
    text_centered(draw, (W // 2, cy1 + 200), "이영우 T", f_teacher, INK)

    # 카드 네 모서리 스파클
    for cx, cy in [(cx1 + 50, cy1 + 50), (cx2 - 50, cy1 + 50),
                   (cx1 + 50, cy2 - 50), (cx2 - 50, cy2 - 50)]:
        draw_sparkle(draw, cx, cy, 22, DEEP_PINK)

    # 외곽 둥근 프레임 (살짝)
    pad = 90
    draw.rounded_rectangle([pad, pad, W - pad, H - pad],
                           radius=80, outline=DEEP_PINK, width=4)

    return img


def main():
    img = make_cover()
    img.save(OUT_PDF, "PDF", resolution=300.0)
    img.save(OUT_PDF.with_suffix(".png"), "PNG", optimize=True)
    print(f"[OK] {OUT_PDF}")


if __name__ == "__main__":
    main()
