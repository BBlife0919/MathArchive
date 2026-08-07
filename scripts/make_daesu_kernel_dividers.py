"""대수 KERNEL POINT 내지 디바이더 — 4 챕터 + 정답해설 + 목차.

다크 네이비 + 골드. 챕터 디바이더는 큰 워터마크 숫자 + 큰 한글 타이틀.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
LOGO_PATH = ROOT / "output" / "summit_point" / "eum_logo_gold.png"
OUT_DIR = ROOT / "output" / "daesu_kernel_point"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "dividers.pdf"
TOC_PDF = OUT_DIR / "toc.pdf"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

W, H = 2480, 3508

NAVY_DEEP = (15, 25, 50)
NAVY = (24, 38, 75)
NAVY_LIGHT = (60, 90, 145)
GOLD = (210, 175, 110)
GOLD_BRIGHT = (240, 205, 135)
WHITE = (245, 245, 250)
GREY = (170, 180, 200)
MUTED = (110, 125, 150)
WATERMARK = (32, 48, 90)


CHAPTERS = [
    {"no": 1, "roman": "I",   "name": "지수와 로그",
     "eng": "EXPONENTS & LOGARITHMS",
     "topics": ["연산법칙", "정의 OX", "기본조건", "대소비교",
                "정수/자연수 될 조건", "활용", "최대최소"],
     "range": "#1 — #55", "count": 55},
    {"no": 2, "roman": "II",  "name": "지수함수와 로그함수",
     "eng": "EXPONENTIAL & LOGARITHMIC FUNCTIONS",
     "topics": ["기본 OX", "평행/대칭이동", "대소비교", "경계값 찾기",
                "최대최소", "방정식/부등식", "역함수", "실근개수",
                "그래프 해석", "활용", "넓이"],
     "range": "#56 — #116", "count": 61},
    {"no": 3, "roman": "III", "name": "삼각함수",
     "eng": "TRIGONOMETRIC FUNCTIONS",
     "topics": ["부채꼴", "기본", "동경", "연산", "하나의 삼각비 알 때"],
     "range": "#117 — #140", "count": 24},
    {"no": 4, "roman": "IV",  "name": "삼각함수의 그래프",
     "eng": "GRAPHS OF TRIG FUNCTIONS",
     "topics": ["기본 OX", "연산공식", "대칭성", "방정식/부등식", "그래프 해석",
                "실근개수", "최대최소"],
     "range": "#141 — #200", "count": 60},
]


def font(size, family="paper_black"):
    path = {"cafe24": FONT_CAFE24, "paper_black": FONT_PAPER_BLACK, "aggro": FONT_AGGRO}.get(family, FONT_PAPER_BLACK)
    return ImageFont.truetype(path, size=size)


def text_left(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - bx[0], xy[1] - bx[1]), text, font=fnt, fill=fill)


def text_right(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    w = bx[2] - bx[0]
    draw.text((xy[0] - w - bx[0], xy[1] - bx[1]), text, font=fnt, fill=fill)


def text_centered(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    w = bx[2] - bx[0]
    h = bx[3] - bx[1]
    draw.text((xy[0] - w // 2 - bx[0], xy[1] - h // 2 - bx[1]),
              text, font=fnt, fill=fill)


def draw_dot(draw, cx, cy, r, color):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=color)


def fit_text_size(draw, text, family, max_w, start=320, floor=140):
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
    for _ in range(160):
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


def add_footer(img, draw, label):
    f_foot = font(50, "aggro")
    text_left(draw, (220, H - 280), "KERNEL POINT", f_foot, GOLD)
    f_foot_kr = font(42, "cafe24")
    text_left(draw, (220, H - 200), "대수 빈출 FINAL · 이영우 T", f_foot_kr, GREY)
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        target_w = 220
        ratio = target_w / logo.width
        target_h = int(logo.height * ratio)
        logo_resized = logo.resize((target_w, target_h), Image.LANCZOS)
        lx = W - 220 - target_w
        ly = H - 310
        img.paste(logo_resized, (lx, ly), logo_resized)
    except Exception:
        pass
    f_page = font(44, "aggro")
    text_right(draw, (W - 220, H - 150), label, f_page, MUTED)


def make_chapter_page(ch):
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)
    margin_x = 220

    # 상단 라벨
    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 240, top_y)], fill=GOLD, width=5)
    f_label = font(54, "aggro")
    text_left(draw, (margin_x + 280, top_y - 30), f"CHAPTER · {ch['no']:02d}", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 30), "KERNEL POINT", f_label, GREY)

    # 워터마크 거대 숫자
    f_water = font(1500, "paper_black")
    chapter_no = f"{ch['no']:02d}"
    bbox = draw.textbbox((0, 0), chapter_no, font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 120 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 280
    draw.text((wx, wy), chapter_no, font=f_water, fill=WATERMARK)

    # 큰 본문 — 로마 숫자 + 영문
    main_y = 1100
    f_part_no = font(280, "paper_black")
    text_left(draw, (margin_x, main_y), f"{ch['roman']}.", f_part_no, GOLD)
    bbox = draw.textbbox((0, 0), f"{ch['roman']}.", font=f_part_no)
    part_no_w = bbox[2] - bbox[0]
    f_part_label_en = font(62, "aggro")
    text_left(draw, (margin_x + part_no_w + 60, main_y - 40), ch["eng"],
              f_part_label_en, GREY)

    line_y = main_y + 380
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=NAVY_LIGHT, width=2)
    draw_dot(draw, margin_x, line_y, 12, GOLD)
    draw_dot(draw, W - margin_x, line_y, 12, GOLD)

    # 한글 제목 (큼)
    title_y = line_y + 220
    max_w_title = W - margin_x * 2
    title_size = fit_text_size(draw, ch["name"], "cafe24", max_w_title,
                               start=320, floor=160)
    f_title = font(title_size, "cafe24")
    text_left(draw, (margin_x, title_y), ch["name"], f_title, WHITE)

    underline_y = title_y + title_size + 70
    draw.line([(margin_x, underline_y), (margin_x + 360, underline_y)],
              fill=GOLD, width=5)

    # 토픽 리스트 (작은 글씨)
    topics_y = underline_y + 90
    f_topic = font(54, "cafe24")
    f_bullet = font(54, "aggro")
    topic_line_h = 80
    # 2단 분할
    half = (len(ch["topics"]) + 1) // 2
    for i, t in enumerate(ch["topics"]):
        col = 0 if i < half else 1
        row = i if i < half else i - half
        tx = margin_x + col * 1000
        ty = topics_y + row * topic_line_h
        text_left(draw, (tx, ty), "·", f_bullet, GOLD)
        text_left(draw, (tx + 40, ty), t, f_topic, GREY)

    # 범위
    range_y = H - 540
    f_range = font(60, "aggro")
    text_left(draw, (margin_x, range_y), ch["range"], f_range, GOLD)
    text_left(draw, (margin_x + 480, range_y),
              f"·  {ch['count']} Problems", f_range, GREY)

    add_footer(img, draw, f"· {ch['no']:02d} ·")
    add_frame(draw)
    return img


def make_solution_divider():
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)
    margin_x = 220

    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 240, top_y)], fill=GOLD, width=5)
    f_label = font(54, "aggro")
    text_left(draw, (margin_x + 280, top_y - 30), "ANSWER · KEY", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 30), "KERNEL POINT", f_label, GREY)

    f_water = font(1500, "paper_black")
    bbox = draw.textbbox((0, 0), "AK", font=f_water)
    water_w = bbox[2] - bbox[0]
    water_h = bbox[3] - bbox[1]
    wx = W - water_w - margin_x + 60 - bbox[0]
    wy = H // 2 - water_h // 2 - bbox[1] - 200
    draw.text((wx, wy), "AK", font=f_water, fill=WATERMARK)

    main_y = 1280
    f_main = font(320, "cafe24")
    text_left(draw, (margin_x, main_y), "정답", f_main, GOLD)
    bbox = draw.textbbox((0, 0), "정답", font=f_main)
    main_w = bbox[2] - bbox[0]
    bullet_x = margin_x + main_w + 80
    bullet_y = main_y + 180
    draw_dot(draw, bullet_x, bullet_y, 20, GOLD)
    text_left(draw, (bullet_x + 80, main_y), "및 해설", f_main, WHITE)

    sub_y = main_y + 440
    f_sub = font(74, "aggro")
    text_left(draw, (margin_x, sub_y), "A N S W E R   &   S O L U T I O N",
              f_sub, GREY)

    line_y = sub_y + 220
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=NAVY_LIGHT, width=2)
    draw_dot(draw, margin_x, line_y, 12, GOLD)
    draw_dot(draw, W - margin_x, line_y, 12, GOLD)

    copy_y = line_y + 220
    f_copy = font(64, "cafe24")
    text_left(draw, (margin_x, copy_y), "서술형 문제는 풀이과정이 포함되어", f_copy, WHITE)
    text_left(draw, (margin_x, copy_y + 120), "있습니다. 부분점수에 유의하세요.",
              f_copy, WHITE)

    add_footer(img, draw, "· AK ·")
    add_frame(draw)
    return img


def make_toc_page():
    img = Image.new("RGB", (W, H), NAVY_DEEP)
    draw = add_background(img)
    margin_x = 220

    # 상단 라벨
    top_y = 360
    draw.line([(margin_x, top_y), (margin_x + 240, top_y)], fill=GOLD, width=5)
    f_label = font(54, "aggro")
    text_left(draw, (margin_x + 280, top_y - 30), "T A B L E   O F", f_label, GOLD)
    text_right(draw, (W - margin_x, top_y - 30), "KERNEL POINT", f_label, GREY)

    # 큰 제목
    title_y = 620
    f_title = font(320, "cafe24")
    text_left(draw, (margin_x, title_y), "목 차", f_title, WHITE)
    bbox = draw.textbbox((0, 0), "목 차", font=f_title)
    tw = bbox[2] - bbox[0]
    f_title_en = font(64, "aggro")
    text_left(draw, (margin_x + tw + 60, title_y + 30), "C O N T E N T S",
              f_title_en, GOLD)

    line_y = title_y + 360
    draw.line([(margin_x, line_y), (W - margin_x, line_y)], fill=GOLD, width=4)

    # 챕터 리스트
    y = line_y + 140
    f_ch_no = font(140, "paper_black")
    f_ch_name = font(110, "cafe24")
    f_ch_range = font(54, "aggro")
    f_ch_topic = font(46, "cafe24")
    f_dot = font(40, "aggro")

    for ch in CHAPTERS:
        # 로마 숫자
        text_left(draw, (margin_x, y - 40), ch["roman"] + ".", f_ch_no, GOLD)
        bbox = draw.textbbox((0, 0), ch["roman"] + ".", font=f_ch_no)
        roman_w = bbox[2] - bbox[0]

        # 한글 이름
        text_left(draw, (margin_x + roman_w + 60, y), ch["name"],
                  f_ch_name, WHITE)

        # 범위 (우측)
        text_right(draw, (W - margin_x, y + 20), ch["range"], f_ch_range, GOLD_BRIGHT)

        # 토픽 한 줄 (간략)
        topic_text = "  ·  ".join(ch["topics"][:6])
        if len(ch["topics"]) > 6:
            topic_text += "  ·  ..."
        text_left(draw, (margin_x + roman_w + 60, y + 140), topic_text,
                  f_ch_topic, GREY)

        # 점선 구분
        sep_y = y + 220
        for x in range(margin_x, W - margin_x, 30):
            draw_dot(draw, x, sep_y, 3, NAVY_LIGHT)

        y += 380

    # 정답해설
    y_ak = y
    text_left(draw, (margin_x, y_ak), "AK.", f_ch_no, GOLD)
    bbox = draw.textbbox((0, 0), "AK.", font=f_ch_no)
    ak_w = bbox[2] - bbox[0]
    text_left(draw, (margin_x + ak_w + 60, y_ak + 40), "정답 및 해설",
              f_ch_name, WHITE)
    text_right(draw, (W - margin_x, y_ak + 60),
               "A N S W E R   K E Y", f_ch_range, GOLD_BRIGHT)

    add_footer(img, draw, "· TOC ·")
    add_frame(draw)
    return img


def main():
    pages = []
    # 챕터 디바이더 4개
    for ch in CHAPTERS:
        pages.append(make_chapter_page(ch))
    # 정답해설
    pages.append(make_solution_divider())

    first, rest = pages[0], pages[1:]
    first.save(OUT_PDF, "PDF", resolution=300.0, save_all=True, append_images=rest)
    print(f"[OK] dividers: {OUT_PDF} ({len(pages)} pages)")

    # 목차 별도
    toc = make_toc_page()
    toc.save(TOC_PDF, "PDF", resolution=300.0)
    print(f"[OK] toc: {TOC_PDF}")


if __name__ == "__main__":
    main()
