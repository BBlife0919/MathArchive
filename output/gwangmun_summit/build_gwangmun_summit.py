# -*- coding: utf-8 -*-
"""광문고 기말대비 SUMMIT POINT 교재 빌드.

명문고2 대수 SUMMIT POINT 와 동일한 디자인 (귀여운 표지 + 네이비/골드 디바이더
+ 2단 SUMMIT 내지 + 정답·해설). 단, 본문/해설은 직접 KaTeX 변환.
"""
from __future__ import annotations
import json, sys, subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import fitz

HERE = Path(__file__).resolve().parent
RENDER_DIR = HERE / "render"
MATHDB = Path("/Users/youngwoolee/MathDB")
sys.path.insert(0, str(MATHDB / "scripts"))
import build_2col_problems as B

from content import PROBLEMS

OUT = HERE / "gw_out"; OUT.mkdir(exist_ok=True)
BODIES = OUT / "bodies"; BODIES.mkdir(exist_ok=True)

TITLE_KO = "광문고 대수 기말"
SUBTITLE = f"대수 · {len(PROBLEMS)}문항"
PART_NO = "PART 1"
CHAP_SHORT = "수열"
CHAP_LONG = "등차수열·등비수열·수열의 합"
CHAP_EN = "SEQUENCES & SERIES"
INSTRUCTOR = "이영우 T"

USER_FONT = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT / "Cafe24Ssurround-v2.0.ttf")
FONT_AGGRO = str(USER_FONT / "SB 어그로OTF M.otf")
FONT_PAPER_BLACK = str(USER_FONT / "Paperlogy-9Black.ttf")
LOGO = MATHDB / "output" / "summit_point" / "eum_logo_gold.png"

W, H = 2480, 3508  # A4 @300


# ──────────────────────────────────────────────────────────────
# 1) KaTeX 본문/해설/정답 이미지 렌더
# ──────────────────────────────────────────────────────────────
def render_bodies():
    items = []
    for p in PROBLEMS:
        items.append({"id": f"prob_{p['label']}", "width": 520, "fs": 25,
                      "html": p["prob"], "figw": 300})
        items.append({"id": f"sol_{p['label']}", "width": 540, "fs": 23,
                      "html": p["sol"], "figw": 250})
        items.append({"id": f"ans_{p['label']}", "width": 430, "fs": 23,
                      "html": f"<p>{p['answer']}</p>"})
    (OUT / "items.json").write_text(json.dumps(items, ensure_ascii=False), encoding="utf-8")
    subprocess.run([sys.executable, str(RENDER_DIR / "render_items.py"),
                    str(OUT / "items.json"), str(BODIES)], check=True)


def img_dims(path):
    with Image.open(path) as im:
        return im.size  # (w,h) px


# ──────────────────────────────────────────────────────────────
# 2) 문항 내지 (2단) — B 데코 재사용, 본문은 이미지
# ──────────────────────────────────────────────────────────────
def draw_problem_block_img(page, col_x0, col_y0, meta):
    label = meta["label"]; source = meta["source"]
    img_path = str(BODIES / f"prob_{label}.png")
    iw, ih = img_dims(img_path)
    col_x1 = col_x0 + B.COL_W

    LEFT_BLOCK_W, LEFT_BLOCK_GAP = 58, 4
    SRC_OFF, PROB_TOP_OFF = 6, 10
    meta_x = col_x0
    img_x0 = col_x0 + LEFT_BLOCK_W + LEFT_BLOCK_GAP
    img_w = col_x1 - img_x0

    # 출처
    src_str = source.strip("[]").replace("\xa0", " ").strip() if source else ""
    if src_str:
        B.text_at(page, img_x0, col_y0 + SRC_OFF, f"[{src_str}]",
                  "cafe24", FONT_CAFE24, 7.6, B.SRC_GRAY)

    # 라벨
    label_baseline = col_y0 + PROB_TOP_OFF + 14
    B.text_at(page, meta_x, label_baseline, label, "aggro", FONT_AGGRO, 18, B.ORANGE)

    # 1/2/3차 체크
    box, bh = 6, 7
    r1 = label_baseline + 13; r1b = r1 - 6; bx = meta_x
    for t in ["1차", "2차", "3차"]:
        page.draw_rect(fitz.Rect(bx, r1b, bx + box, r1b + bh), color=B.GREY_LINE, width=0.5)
        B.text_at(page, bx + box + 2, r1, t, "cafe24", FONT_CAFE24, 6.5, B.NAVY)
        bx += 18
    r2 = r1 + 12; r2b = r2 - 6; bx = meta_x
    for t in ["O", "X"]:
        page.draw_rect(fitz.Rect(bx, r2b, bx + box, r2b + bh), color=B.GREY_LINE, width=0.5)
        B.text_at(page, bx + box + 2, r2, t, "cafe24", FONT_CAFE24, 6.5, B.NAVY)
        bx += 16

    # 본문 이미지
    prob_top = col_y0 + PROB_TOP_OFF
    scale = img_w / iw
    target_h = ih * scale
    if target_h > B.PROB_MAX_H:
        scale = B.PROB_MAX_H / ih
        img_w2 = iw * scale
        rect = fitz.Rect(img_x0, prob_top, img_x0 + img_w2, prob_top + ih * scale)
    else:
        rect = fitz.Rect(img_x0, prob_top, img_x0 + img_w, prob_top + target_h)
    page.insert_image(rect, filename=img_path, keep_proportion=True)

    # KEY POINT
    bottom_y = col_y0 + B.COL_H - B.KP_H - B.MEMO_H - 16
    kp_rect = fitz.Rect(col_x0, bottom_y, col_x1, bottom_y + B.KP_H)
    page.draw_rect(kp_rect, color=B.KP_BORDER, fill=B.KP_BG, width=0.8)
    B.text_at(page, col_x0 + 8, bottom_y + 11, "KEY POINT", "aggro", FONT_AGGRO, 8, B.GOLD)
    page.draw_line((col_x0 + 78, bottom_y + 5), (col_x0 + 78, bottom_y + B.KP_H - 5),
                   color=B.KP_BORDER, width=0.6)
    B.text_at(page, col_x0 + 85, bottom_y + 17, "이 문제 핵심 한 줄로 정리",
              "cafe24", FONT_CAFE24, 8.5, B.GREY)
    # MEMO
    memo_top = bottom_y + B.KP_H + 8
    B.text_at(page, col_x0, memo_top + 8, "MEMO", "aggro", FONT_AGGRO, 7, B.GREY)
    ly0 = memo_top + 18
    for i in range(B.MEMO_LINES):
        ly = ly0 + i * B.MEMO_LINE_GAP
        page.draw_line((col_x0, ly), (col_x1, ly), color=B.GREY_LINE, width=0.4)


def build_problem_pages():
    doc = fitz.open()
    i = 0
    while i < len(PROBLEMS):
        page = doc.new_page(width=B.PAGE_W, height=B.PAGE_H)
        B.draw_top_header(page, PART_NO, CHAP_SHORT)
        B.draw_side_bookmark(page, "A", PART_NO)
        draw_problem_block_img(page, B.LEFT_MARGIN, B.TOP_MARGIN, PROBLEMS[i])
        if i + 1 < len(PROBLEMS):
            draw_problem_block_img(page, B.COL_RIGHT_X, B.TOP_MARGIN, PROBLEMS[i + 1])
        i += 2
    path = OUT / "problems.pdf"
    doc.save(str(path)); doc.close()
    return path


# ──────────────────────────────────────────────────────────────
# 3) 정답·해설 (2단 흐름 배치, 긴 해설은 컬럼 분할)
# ──────────────────────────────────────────────────────────────
SOL_TOP = 70
SOL_BOTTOM = B.PAGE_H - 50
SOL_INDENT = 26
BLOCK_GAP = 16


def ink_rows(path):
    """행별 잉크량(0~255) 프로파일 반환 (분할 지점 탐색용)."""
    im = Image.open(path).convert("L")
    px = im.load()
    w, h = im.size
    prof = []
    step = max(1, w // 120)
    for y in range(h):
        s = 0
        for x in range(0, w, step):
            s += 255 - px[x, y]
        prof.append(s)
    return prof, w, h


def good_cut(prof, target_px, lo):
    """target_px 바로 위쪽(최대 70px 위) 구간에서 잉크 최소 행을 찾아 컷."""
    h = len(prof)
    t = min(target_px, h)
    a = max(lo + 30, t - 70)
    best, bestv = t, 1e18
    for y in range(a, min(t + 1, h)):
        if prof[y] < bestv:
            bestv, best = prof[y], y
    return best


def new_sol_page(doc):
    page = doc.new_page(width=B.PAGE_W, height=B.PAGE_H)
    B.draw_top_header(page, PART_NO, CHAP_SHORT)
    B.draw_side_bookmark(page, "A", PART_NO)
    return page


def build_solution_pages():
    doc = fitz.open()
    page = new_sol_page(doc)
    cols = [B.LEFT_MARGIN, B.COL_RIGHT_X]
    col_idx = 0
    y = SOL_TOP

    def advance_col():
        nonlocal col_idx, y, page
        col_idx += 1
        if col_idx > 1:
            page = new_sol_page(doc)
            col_idx = 0
        y = SOL_TOP

    for p in PROBLEMS:
        label = p["label"]
        ans_path = str(BODIES / f"ans_{label}.png")
        body_path = str(BODIES / f"sol_{label}.png")
        aw, ah = img_dims(ans_path)
        bw, bh = img_dims(body_path)

        body_w = B.COL_W - SOL_INDENT
        scale = body_w / bw
        full_h = bh * scale

        # 헤더 라인: 정답 이미지를 width=ans_w_pt 로 맞춤
        ans_w_pt = B.COL_W - 72
        a_sc = ans_w_pt / aw
        ans_h2 = ah * a_sc
        line1_h = max(16, ans_h2 + 4)
        header_h = line1_h + 6  # rule 포함
        col_x0 = cols[col_idx]
        col_x1 = col_x0 + B.COL_W

        # 헤더가 들어갈 최소 공간 확보
        if y > SOL_TOP and (SOL_BOTTOM - y) < header_h + 46:
            advance_col()
            col_x0 = cols[col_idx]; col_x1 = col_x0 + B.COL_W

        # 헤더 그리기
        ly = y + 13
        B.text_at(page, col_x0, ly, label, "aggro", FONT_AGGRO, 13, B.ORANGE)
        B.text_at(page, col_x0 + 44, ly - 1, "정답", "aggro", FONT_AGGRO, 8.5, B.NAVY)
        a_rect = fitz.Rect(col_x0 + 70, y + 1, col_x0 + 70 + ans_w_pt, y + 1 + ans_h2)
        page.insert_image(a_rect, filename=ans_path, keep_proportion=True)
        rule_y = y + line1_h
        page.draw_line((col_x0, rule_y), (col_x1, rule_y), color=B.GREY_LINE, width=0.7)
        y = rule_y + 6
        B.text_at(page, col_x0, y + 9, "해설", "aggro", FONT_AGGRO, 8, B.GREY)

        # 본문(해설) 배치 — 필요시 분할
        body_x0 = col_x0 + SOL_INDENT
        src_y = 0  # px
        prof = None
        first_chunk = True
        while src_y < bh - 1:
            avail_pt = SOL_BOTTOM - y
            if avail_pt < 50:
                advance_col()
                col_x0 = cols[col_idx]; col_x1 = col_x0 + B.COL_W
                body_x0 = col_x0 + SOL_INDENT
                avail_pt = SOL_BOTTOM - y
                first_chunk = False
            avail_px = avail_pt / scale
            remain_px = bh - src_y
            if remain_px <= avail_px:
                take = remain_px
            else:
                if prof is None:
                    prof, _, _ = ink_rows(body_path)
                take = good_cut(prof, int(src_y + avail_px), src_y) - src_y
                if take < 30:
                    take = int(avail_px)
            # 자른 조각 임시저장
            chunk = Image.open(body_path).crop((0, int(src_y), bw, int(src_y + take)))
            cpath = BODIES / f"_chunk_{label}_{src_y}.png"
            chunk.save(cpath)
            ch_h_pt = take * scale
            rect = fitz.Rect(body_x0, y, body_x0 + body_w, y + ch_h_pt)
            page.insert_image(rect, filename=str(cpath), keep_proportion=True)
            y += ch_h_pt
            src_y += take
        y += BLOCK_GAP

    path = OUT / "solutions.pdf"
    doc.save(str(path)); doc.close()
    return path


# ──────────────────────────────────────────────────────────────
# 4) 표지 (귀여운 핑크 테마)
# ──────────────────────────────────────────────────────────────
CREAM = (255, 250, 245); PINK = (255, 200, 215); PEACH = (255, 180, 160)
LAVENDER = (220, 210, 245); MINT = (200, 240, 220); DEEP_PINK = (235, 120, 145)
INK = (40, 40, 55); GREY = (120, 120, 140); GOLD = (220, 175, 110)


def cfont(size, fam="cafe24"):
    return ImageFont.truetype(FONT_CAFE24 if fam == "cafe24" else FONT_AGGRO, size)


def ctext(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    w = bx[2] - bx[0]; h = bx[3] - bx[1]
    draw.text((xy[0] - w // 2 - bx[0], xy[1] - h // 2 - bx[1]), text, font=fnt, fill=fill)


def dot(draw, cx, cy, r, c):
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c)


def heart(draw, cx, cy, s, c):
    r = s // 2
    draw.ellipse([cx - s, cy - r, cx, cy + r], fill=c)
    draw.ellipse([cx, cy - r, cx + s, cy + r], fill=c)
    draw.polygon([(cx - s, cy + r // 4), (cx + s, cy + r // 4), (cx, cy + s + r // 2)], fill=c)


def sparkle(draw, cx, cy, s, c):
    draw.polygon([(cx, cy - s), (cx + s * 0.25, cy - s * 0.25), (cx + s, cy),
                  (cx + s * 0.25, cy + s * 0.25), (cx, cy + s), (cx - s * 0.25, cy + s * 0.25),
                  (cx - s, cy), (cx - s * 0.25, cy - s * 0.25)], fill=c)


def build_cover():
    img = Image.new("RGB", (W, H), CREAM)
    draw = ImageDraw.Draw(img)
    for yy in range(H):
        t = yy / H
        r = int(CREAM[0] * (1 - t) + PINK[0] * t * 0.3 + CREAM[0] * (1 - t * 0.3))
        g = int(CREAM[1] * (1 - t) + PINK[1] * t * 0.3 + CREAM[1] * (1 - t * 0.3))
        b = int(CREAM[2] * (1 - t) + PINK[2] * t * 0.3 + CREAM[2] * (1 - t * 0.3))
        draw.line([(0, yy), (W, yy)], fill=(r, g, b))
    import random
    rnd = random.Random(11)
    for _ in range(120):
        x = rnd.randint(60, W - 60); yy = rnd.randint(60, H - 60)
        dot(draw, x, yy, rnd.choice([3, 4, 5, 6]),
            rnd.choice([PINK, PEACH, LAVENDER, MINT, GOLD]))

    # 상단 라벨
    ctext(draw, (W // 2, 320), "P R I N T   M A S T E R Y · 2026", cfont(70, "aggro"), DEEP_PINK)
    heart(draw, W // 2 - 720, 320, 18, DEEP_PINK)
    heart(draw, W // 2 + 720, 320, 18, DEEP_PINK)
    # 큰 타이틀
    ctext(draw, (W // 2, 470), TITLE_KO, cfont(170, "cafe24"), INK)

    # 가운데 귀여운 엠블럼 (캐릭터 대체)
    ecx, ecy, er = W // 2, 1620, 560
    draw.ellipse([ecx - er, ecy - er, ecx + er, ecy + er], outline=DEEP_PINK, width=10)
    draw.ellipse([ecx - er + 36, ecy - er + 36, ecx + er - 36, ecy + er - 36],
                 fill=(255, 244, 248))
    ctext(draw, (ecx, ecy - 150), "SUMMIT", cfont(150, "cafe24"), DEEP_PINK)
    ctext(draw, (ecx, ecy + 30), "POINT", cfont(150, "cafe24"), GOLD)
    ctext(draw, (ecx, ecy + 250), "수 열", cfont(120, "cafe24"), INK)
    for ang in range(0, 360, 45):
        import math
        rx = ecx + int(math.cos(math.radians(ang)) * (er + 70))
        ry = ecy + int(math.sin(math.radians(ang)) * (er + 70))
        sparkle(draw, rx, ry, 26, rnd.choice([DEEP_PINK, GOLD, PEACH]))

    # 부제
    ctext(draw, (W // 2, H - 620), SUBTITLE, cfont(96, "cafe24"), INK)
    # 강사 카드
    cw, ch = 900, 280
    cx1 = (W - cw) // 2; cy1 = (H - 380) - ch // 2
    draw.rounded_rectangle((cx1, cy1, cx1 + cw, cy1 + ch), radius=64,
                           fill=(255, 255, 255), outline=DEEP_PINK, width=6)
    ctext(draw, (W // 2, cy1 + 78), "w i t h", cfont(54, "aggro"), DEEP_PINK)
    ctext(draw, (W // 2, cy1 + 200), INSTRUCTOR, cfont(140, "cafe24"), INK)
    for sx, sy in [(cx1 + 50, cy1 + 50), (cx1 + cw - 50, cy1 + 50),
                   (cx1 + 50, cy1 + ch - 50), (cx1 + cw - 50, cy1 + ch - 50)]:
        sparkle(draw, sx, sy, 22, DEEP_PINK)
    draw.rounded_rectangle([90, 90, W - 90, H - 90], radius=80, outline=DEEP_PINK, width=4)
    path = OUT / "cover.pdf"
    img.save(path, "PDF", resolution=300.0)
    return path


# ──────────────────────────────────────────────────────────────
# 5) 디바이더 (네이비/골드) — myongmoon 스타일 단일 챕터
# ──────────────────────────────────────────────────────────────
NAVY_DEEP = (15, 25, 50); NAVY_LIGHT = (60, 90, 145); GOLD2 = (210, 175, 110)
WHITE = (245, 245, 250); GREY2 = (170, 180, 200); MUTED = (110, 125, 150)
WATERMARK = (240, 243, 248); INK2 = (28, 36, 56); SOFT = (220, 225, 232)


def dfont(size, fam="paper_black"):
    return ImageFont.truetype({"cafe24": FONT_CAFE24, "aggro": FONT_AGGRO,
                               "paper_black": FONT_PAPER_BLACK}[fam], size)


def dl(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - bx[0], xy[1] - bx[1]), text, font=fnt, fill=fill)


def dr(draw, xy, text, fnt, fill):
    bx = draw.textbbox((0, 0), text, font=fnt)
    draw.text((xy[0] - (bx[2] - bx[0]) - bx[0], xy[1] - bx[1]), text, font=fnt, fill=fill)


def dbg(img):
    draw = ImageDraw.Draw(img)
    import random
    rnd = random.Random(13)
    for _ in range(90):
        x = rnd.randint(60, W - 60); yy = rnd.randint(60, H - 60)
        dot(draw, x, yy, rnd.choice([1, 1, 2, 2]), (225, 228, 235))
    return draw


def dframe(draw):
    draw.rectangle([90, 90, W - 90, H - 90], outline=GOLD2, width=2)
    for cx, cy in [(90, 90), (W - 90, 90), (90, H - 90), (W - 90, H - 90)]:
        draw.line([(cx - 48, cy), (cx + 48, cy)], fill=GOLD2, width=4)
        draw.line([(cx, cy - 48), (cx, cy + 48)], fill=GOLD2, width=4)


def dfooter(img, draw, label):
    dl(draw, (220, H - 280), "SUMMIT POINT", dfont(46, "aggro"), GOLD2)
    dl(draw, (220, H - 210), INSTRUCTOR, dfont(40, "cafe24"), GREY2)
    try:
        logo = Image.open(LOGO).convert("RGBA")
        tw = 200; th = int(logo.height * tw / logo.width)
        img.paste(logo.resize((tw, th), Image.LANCZOS), (W - 220 - tw, H - 300),
                  logo.resize((tw, th), Image.LANCZOS))
    except Exception:
        pass
    dr(draw, (W - 220, H - 150), label, dfont(40, "aggro"), MUTED)


def chapter_page():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = dbg(img)
    mx = 220
    dl(draw, (mx, 360 - 26), "PART · 01", dfont(48, "aggro"), GOLD2)
    draw.line([(mx, 360), (mx + 220, 360)], fill=GOLD2, width=5)
    dr(draw, (W - mx, 360 - 26), "SUMMIT POINT", dfont(48, "aggro"), GREY2)
    fw = dfont(1400, "paper_black")
    bx = draw.textbbox((0, 0), "01", font=fw)
    draw.text((W - (bx[2] - bx[0]) - mx + 100 - bx[0], H // 2 - (bx[3] - bx[1]) // 2 - bx[1] - 220),
              "01", font=fw, fill=WATERMARK)
    dl(draw, (mx, 1080), "I.", dfont(220, "paper_black"), GOLD2)
    bx2 = draw.textbbox((0, 0), "I.", font=dfont(220, "paper_black"))
    dl(draw, (mx + (bx2[2] - bx2[0]) + 60, 1050), CHAP_EN, dfont(56, "aggro"), GREY2)
    ly = 1400
    draw.line([(mx, ly), (W - mx, ly)], fill=SOFT, width=2)
    dot(draw, mx, ly, 10, GOLD2); dot(draw, W - mx, ly, 10, GOLD2)
    # 단원명 자동 축소
    size = 240
    for s in range(240, 109, -6):
        if draw.textlength(CHAP_LONG, font=dfont(s, "cafe24")) <= W - mx * 2:
            size = s; break
    dl(draw, (mx, ly + 200), CHAP_LONG, dfont(size, "cafe24"), INK2)
    draw.line([(mx, ly + 200 + size + 60), (mx + 320, ly + 200 + size + 60)], fill=GOLD2, width=5)
    for x in range(mx, W - mx + 1, 28):
        dot(draw, x, H - 420, 3, SOFT)
    dfooter(img, draw, "· 01 ·")
    dframe(draw)
    return img


def solution_divider():
    img = Image.new("RGB", (W, H), (255, 255, 255))
    draw = dbg(img)
    mx = 220
    dl(draw, (mx, 360 - 26), "ANSWER · KEY", dfont(48, "aggro"), GOLD2)
    draw.line([(mx, 360), (mx + 220, 360)], fill=GOLD2, width=5)
    dr(draw, (W - mx, 360 - 26), "SUMMIT POINT", dfont(48, "aggro"), GREY2)
    fw = dfont(1500, "paper_black")
    bx = draw.textbbox((0, 0), "AK", font=fw)
    draw.text((W - (bx[2] - bx[0]) - mx + 60 - bx[0], H // 2 - (bx[3] - bx[1]) // 2 - bx[1] - 200),
              "AK", font=fw, fill=WATERMARK)
    fm = dfont(280, "cafe24")
    dl(draw, (mx, 1280), "정답", fm, GOLD2)
    mw = draw.textlength("정답", font=fm)
    dot(draw, int(mx + mw + 80), 1280 + 160, 18, GOLD2)
    dl(draw, (int(mx + mw + 160), 1280), "및 해설", fm, INK2)
    dl(draw, (mx, 1660), "A N S W E R   &   S O L U T I O N", dfont(70, "aggro"), GREY2)
    ly = 1860
    draw.line([(mx, ly), (W - mx, ly)], fill=SOFT, width=2)
    dot(draw, mx, ly, 10, GOLD2); dot(draw, W - mx, ly, 10, GOLD2)
    dl(draw, (mx, ly + 200), "틀린 문제는 다시 풀어보고,", dfont(60, "cafe24"), INK2)
    dl(draw, (mx, ly + 310), "맞힌 문제도 풀이를 점검하세요.", dfont(60, "cafe24"), INK2)
    for x in range(mx, W - mx + 1, 28):
        dot(draw, x, H - 420, 3, SOFT)
    dfooter(img, draw, "· AK ·")
    dframe(draw)
    return img


def build_dividers():
    p1 = OUT / "divider_ch.pdf"; chapter_page().save(p1, "PDF", resolution=300.0)
    p2 = OUT / "divider_sol.pdf"; solution_divider().save(p2, "PDF", resolution=300.0)
    return p1, p2


# ──────────────────────────────────────────────────────────────
# 6) 병합
# ──────────────────────────────────────────────────────────────
def merge(cover, ch_div, probs, sol_div, sols):
    out = fitz.open()
    for p in [cover, ch_div, probs, sol_div, sols]:
        d = fitz.open(str(p)); out.insert_pdf(d); d.close()
    final = OUT / "광문고_대수_기말_SUMMIT_POINT.pdf"
    out.save(str(final), garbage=4, deflate=True); out.close()
    return final


def main():
    render_bodies()
    cover = build_cover()
    ch_div, sol_div = build_dividers()
    probs = build_problem_pages()
    sols = build_solution_pages()
    final = merge(cover, ch_div, probs, sol_div, sols)
    print("FINAL", final, fitz.open(str(final)).page_count, "pages")


if __name__ == "__main__":
    main()
