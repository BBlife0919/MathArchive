"""대수 1학기 기말고사 · 필수유형 FINAL — 표지 + 단원(섹션) 디바이더 교체.

흰 배경, 깔끔/모던, 네이비 잉크 + 블루 액센트. 폰트는 BASIC POINT 교재와 동일
(Paperlogy / Cafe24 / SB 어그로).  표지·디바이더 통일 디자인.
"""
from __future__ import annotations
from pathlib import Path

import fitz
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SRC_PDF = Path("/Users/youngwoolee/Downloads/_.pdf")
OUT_DIR = ROOT / "output" / "daesu_final"
OUT_DIR.mkdir(parents=True, exist_ok=True)
OUT_PDF = OUT_DIR / "대수_1학기기말_필수유형FINAL.pdf"
LOGO_PATH = ROOT / "app" / "assets" / "eum_logo.png"

USER_FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_CAFE24 = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
FONT_PAPER_BLACK = str(USER_FONT_DIR / "Paperlogy-9Black.ttf")
FONT_PAPER_EB = str(USER_FONT_DIR / "Paperlogy-8ExtraBold.ttf")
FONT_AGGRO = str(USER_FONT_DIR / "SB 어그로OTF M.otf")

W, H = 2480, 3508  # A4 @ 300dpi

WHITE = (255, 255, 255)
INK = (33, 40, 61)
ACCENT = (44, 84, 196)
ACCENT_DK = (28, 56, 150)
GHOST = (234, 239, 250)
MUTED = (146, 156, 176)
LINE = (224, 228, 237)


def font(size, family="cafe24"):
    path = {"cafe24": FONT_CAFE24, "paper_black": FONT_PAPER_BLACK,
            "paper_eb": FONT_PAPER_EB, "aggro": FONT_AGGRO}.get(family, FONT_CAFE24)
    return ImageFont.truetype(path, size=size)


def tc(draw, cx, y_center, text, fnt, fill, tracking=0):
    if tracking:
        # 글자 간격 letter-spacing
        widths = [draw.textbbox((0, 0), ch, font=fnt)[2] - draw.textbbox((0, 0), ch, font=fnt)[0] for ch in text]
        total = sum(widths) + tracking * (len(text) - 1)
        x = cx - total / 2
        for ch, w in zip(text, widths):
            b = draw.textbbox((0, 0), ch, font=fnt)
            draw.text((x - b[0], y_center - (b[3] - b[1]) / 2 - b[1]), ch, font=fnt, fill=fill)
            x += w + tracking
        return
    b = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (b[2] - b[0]) / 2 - b[0], y_center - (b[3] - b[1]) / 2 - b[1]), text, font=fnt, fill=fill)


def tl(draw, x, y, text, fnt, fill):
    b = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x - b[0], y - b[1]), text, font=fnt, fill=fill)


def tr(draw, x_right, y, text, fnt, fill):
    b = draw.textbbox((0, 0), text, font=fnt)
    draw.text((x_right - (b[2] - b[0]) - b[0], y - b[1]), text, font=fnt, fill=fill)


def paste_logo(img, cx, top, target_w):
    try:
        logo = Image.open(LOGO_PATH).convert("RGBA")
        ratio = target_w / logo.width
        lg = logo.resize((target_w, int(logo.height * ratio)), Image.LANCZOS)
        img.paste(lg, (int(cx - target_w / 2), int(top)), lg)
        return lg.height
    except Exception:
        return 0


# ───────────────────────── 표지 ─────────────────────────
def make_cover() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)

    # 외곽 얇은 프레임 + 코너 액센트
    pad = 96
    d.rectangle([pad, pad, W - pad, H - pad], outline=LINE, width=4)
    cl = 90
    for cx, cy in [(pad, pad), (W - pad, pad), (pad, H - pad), (W - pad, H - pad)]:
        d.line([(cx - cl, cy), (cx + cl, cy)], fill=ACCENT, width=8)
        d.line([(cx, cy - cl), (cx, cy + cl)], fill=ACCENT, width=8)

    cx = W // 2
    # 상단 라벨
    tc(d, cx, 470, "M A T H   W O R K B O O K   ·   2 0 2 6", font(50, "aggro"), ACCENT, tracking=6)
    d.line([(cx - 150, 540), (cx + 150, 540)], fill=ACCENT, width=4)

    # 제목
    tc(d, cx, 900, "대수 1학기 기말고사", font(170, "paper_eb"), INK)

    # 부제 — 필수유형 / FINAL (히어로)
    tc(d, cx, 1180, "필 수 유 형", font(132, "cafe24"), INK, tracking=10)
    tc(d, cx, 1560, "FINAL", font(440, "paper_black"), ACCENT)
    d.line([(cx - 360, 1820), (cx + 360, 1820)], fill=INK, width=6)

    # FINAL 밑 귀여운 한 줄
    tc(d, cx, 1980, "제발 부탁할게 열심히해줘 응? 진짜 부탁임..",
       font(62, "cafe24"), MUTED)

    # 강사명 (INSTRUCTOR 라벨 없이 박스 + 이영우 T)
    bw, bh = 560, 200
    by = 2440
    d.rounded_rectangle([cx - bw // 2, by, cx + bw // 2, by + bh],
                        radius=46, outline=ACCENT, width=6)
    tc(d, cx, by + bh // 2, "이영우 T", font(132, "cafe24"), INK)

    # 하단 좌측 카피
    tl(d, 200, H - 360, "Algebra Final Workbook · 2026", font(48, "aggro"), MUTED)
    tl(d, 200, H - 290, "필수유형으로 끝내는 기말 마무리", font(44, "cafe24"), MUTED)

    # 하단 우측 로고 (로고 PNG에 태그라인 포함)
    paste_logo(img, W - 360, H - 500, 300)

    return img


# ───────────────────────── 디바이더 ─────────────────────────
def make_divider(chap_roman, chap_num, chap_name, sec_num, sec_title) -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    cx = W // 2

    # 상단 헤더
    tl(d, 200, 300, f"CHAPTER · {chap_num:02d}", font(52, "aggro"), ACCENT)
    d.line([(200, 372), (430, 372)], fill=ACCENT, width=6)
    tr(d, W - 200, 300, "대수 1학기 기말 · FINAL", font(46, "cafe24"), MUTED)

    # 거대 고스트 섹션 번호
    ghost = font(1500, "paper_black")
    gb = d.textbbox((0, 0), f"{sec_num:02d}", font=ghost)
    gx = W - 230 - (gb[2] - gb[0])
    gy = 760
    d.text((gx - gb[0], gy - gb[1]), f"{sec_num:02d}", font=ghost, fill=GHOST)

    # 단원(로마) + 단원명
    base_y = 1180
    tl(d, 210, base_y, f"{chap_roman}.", font(150, "paper_black"), INK)
    rb = d.textbbox((0, 0), f"{chap_roman}.", font=font(150, "paper_black"))
    tl(d, 210 + (rb[2] - rb[0]) + 50, base_y + 30, chap_name, font(120, "cafe24"), ACCENT)

    # 구분 라인 + 양끝 점
    ly = 1480
    d.line([(210, ly), (W - 230, ly)], fill=LINE, width=4)
    d.ellipse([210 - 12, ly - 12, 210 + 12, ly + 12], fill=ACCENT)
    d.ellipse([W - 230 - 12, ly - 12, W - 230 + 12, ly + 12], fill=ACCENT)

    # SECTION 라벨 + 섹션 제목
    tl(d, 210, 1590, f"SECTION · {sec_num}", font(58, "aggro"), MUTED)
    tl(d, 206, 1740, sec_title, font(190, "paper_eb"), INK)

    # 하단 푸터
    d.line([(200, H - 360), (W - 200, H - 360)], fill=LINE, width=3)
    tl(d, 200, H - 320, "대수 1학기 기말고사 · 필수유형 FINAL", font(46, "aggro"), ACCENT)
    tl(d, 200, H - 250, "이영우 T", font(42, "cafe24"), MUTED)
    paste_logo(img, W - 300, H - 330, 150)

    return img


def make_answer_divider() -> Image.Image:
    img = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(img)
    cx = W // 2

    tl(d, 200, 300, "ANSWER · KEY", font(52, "aggro"), ACCENT)
    d.line([(200, 372), (430, 372)], fill=ACCENT, width=6)
    tr(d, W - 200, 300, "대수 1학기 기말 · FINAL", font(46, "cafe24"), MUTED)

    ghost = font(1500, "paper_black")
    gb = d.textbbox((0, 0), "A", font=ghost)
    d.text((cx - (gb[2] - gb[0]) / 2 - gb[0], 1050 - gb[1]), "A", font=ghost, fill=GHOST)

    tc(d, cx, 1620, "정답과 해설", font(240, "paper_eb"), INK)
    tc(d, cx, 1850, "A N S W E R   &   S O L U T I O N", font(58, "aggro"), MUTED, tracking=4)
    d.line([(cx - 300, 1980), (cx + 300, 1980)], fill=ACCENT, width=5)
    tc(d, cx, 2120, "틀린 문제는 반드시 다시 풀어보세요.", font(56, "cafe24"), MUTED)

    d.line([(200, H - 360), (W - 200, H - 360)], fill=LINE, width=3)
    tl(d, 200, H - 320, "대수 1학기 기말고사 · 필수유형 FINAL", font(46, "aggro"), ACCENT)
    tl(d, 200, H - 250, "이영우 T", font(42, "cafe24"), MUTED)
    paste_logo(img, W - 300, H - 330, 150)
    return img


# 교체 대상 (원본 페이지 index → 생성 이미지)
DIVIDERS = {
    1:   ("I", 1, "삼각함수", 1, "삼각함수의 그래프"),
    35:  ("I", 1, "삼각함수", 2, "사인법칙과 코사인법칙"),
    46:  ("II", 2, "수열", 1, "등차수열"),
    57:  ("II", 2, "수열", 2, "등비수열"),
    68:  ("II", 2, "수열", 3, "합의 기호 ∑"),
    76:  ("II", 2, "수열", 4, "여러 가지 수열의 합"),
    88:  ("II", 2, "수열", 5, "수열의 귀납적 정의"),
    105: ("II", 2, "수열", 6, "수학적 귀납법"),
}
ANSWER_DIV_PAGE = 117

# 개념 페이지 = 디바이더 다음 페이지
CONCEPT = {p + 1: meta for p, meta in DIVIDERS.items()}


_fz_cafe = fitz.Font(fontfile=FONT_CAFE24)
_fz_paper = fitz.Font(fontfile=FONT_PAPER_BLACK)
INK_F = (INK[0] / 255, INK[1] / 255, INK[2] / 255)
ACCENT_F = (ACCENT[0] / 255, ACCENT[1] / 255, ACCENT[2] / 255)


def restyle_banner(page):
    """상단 오렌지 배너의 텍스트 폰트를 교재 폰트로 교체.

    바(그라디언트/플랫)는 페이지를 샘플링해 그대로 재현하여 원 텍스트를 덮고,
    교재 폰트(Cafe24/Paperlogy)로 다시 그린다.  배너가 없으면 건너뜀.
    """
    import io
    import numpy as np

    # 상단 영역 배너 텍스트 스팬 수집 (y<70)
    spans = []
    for blk in page.get_text("dict")["blocks"]:
        for ln in blk.get("lines", []):
            for sp in ln["spans"]:
                if sp["bbox"][1] < 70 and sp["text"].strip():
                    spans.append(sp)
    if not spans:
        return

    S = 3
    pix = page.get_pixmap(matrix=fitz.Matrix(S, S), alpha=False)
    arr = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.height, pix.width, 3)

    def is_white(px):
        return px[0] > 250 and px[1] > 250 and px[2] > 250

    # 바 가로 범위 (텍스트 줄 y≈46 에서 비백색 밴드)
    rowy = int(46 * S)
    row = arr[rowy]
    xs = np.where(~((row[:, 0] > 250) & (row[:, 1] > 250) & (row[:, 2] > 250)))[0]
    if len(xs) < 100:
        return
    x0p, x1p = int(xs.min()), int(xs.max())
    # 바 세로 범위 (중앙 x 열에서 비백색 연속)
    midx = (x0p + x1p) // 2
    col = arr[:, midx]
    ysn = np.where(~((col[:, 0] > 250) & (col[:, 1] > 250) & (col[:, 2] > 250)))[0]
    ysn = ysn[ysn < int(90 * S)]
    if len(ysn) < 10:
        return
    y0p, y1p = int(ysn.min()), int(ysn.max())

    # 바 재현 — 깨끗한 윗줄(y0p+3px) 색을 세로로 복제
    sample_y = y0p + 3
    bar = arr[sample_y, x0p:x1p + 1, :]            # (w,3)
    barimg = np.tile(bar[None, :, :], (y1p - y0p + 1, 1, 1)).astype(np.uint8)
    from PIL import Image as _I
    pim = _I.fromarray(barimg)
    buf = io.BytesIO(); pim.save(buf, format="PNG")
    rect = fitz.Rect(x0p / S, y0p / S, (x1p + 1) / S, (y1p + 1) / S)
    page.insert_image(rect, stream=buf.getvalue())

    bar_cy = (y0p / S + (y1p + 1) / S) / 2

    # 텍스트 재기입
    for sp in spans:
        t = sp["text"].replace("\xa0", " ").strip()
        if not t:
            continue
        fn = sp["font"]; sz = sp["size"]; bb = sp["bbox"]
        if "Myeongjo" in fn and sz > 12:           # 단원별 유형학습
            fsize, ff, fname, fobj, col_ = 14, FONT_CAFE24, "cafe24", _fz_cafe, INK_F
            x = bb[0]; right = None
        elif "Myeongjo" in fn:                       # 우측 단원 라벨 (I  삼각함수)
            fsize, ff, fname, fobj, col_ = 10, FONT_CAFE24, "cafe24", _fz_cafe, INK_F
            x = None; right = bb[2]
        elif "Medium" in fn and sz > 20:             # 섹션 번호
            fsize, ff, fname, fobj, col_ = 28, FONT_PAPER_BLACK, "paper", _fz_paper, ACCENT_F
            x = bb[0]; right = None
        elif "SemiBold" in fn:                        # 섹션 제목
            fsize, ff, fname, fobj, col_ = 15, FONT_CAFE24, "cafe24", _fz_cafe, INK_F
            x = bb[0]; right = None
        else:
            continue
        baseline = bar_cy + fsize * 0.36
        if right is not None:
            x = right - fobj.text_length(t, fsize)
        page.insert_text((x, baseline), t, fontname=fname, fontfile=ff,
                         fontsize=fsize, color=col_)


NAVY = (15 / 255, 25 / 255, 50 / 255)
ACCENT_LT = (150 / 255, 178 / 255, 245 / 255)
MUTED_F = (MUTED[0] / 255, MUTED[1] / 255, MUTED[2] / 255)
GREY_LN = (200 / 255, 205 / 255, 220 / 255)
WHITE_F = (1, 1, 1)


def chapter_of(i):
    """본문 페이지 → (로마숫자, 단원명).  I 삼각함수: 1~45, II 수열: 46~116."""
    return ("I", "삼각함수") if i <= 45 else ("II", "수열")


def add_summit_ui(page, roman, chapname):
    """모든 본문 페이지: 오렌지 바 제거 → SUMMIT 슬림 헤더 + 우측 인덱스(챕터이름)."""
    pw = page.rect.width

    # 오렌지 바 화이트아웃 (문항번호 y88 위까지만)
    page.draw_rect(fitz.Rect(0, 14, pw, 82), color=WHITE_F, fill=WHITE_F)

    # 슬림 헤더: 브랜드 좌 / 단원 우 / 가는 라인
    page.insert_text((30, 34), "필수유형 FINAL", fontname="aggro",
                     fontfile=FONT_AGGRO, fontsize=9, color=INK_F)
    rt = f"{roman}  ·  {chapname}"
    rtw = _fz_cafe.text_length(rt, 9)
    page.insert_text((566 - rtw, 34), rt, fontname="cafe24",
                     fontfile=FONT_CAFE24, fontsize=9, color=INK_F)
    page.draw_line((30, 42), (566, 42), color=GREY_LN, width=0.7)

    # 우측 인덱스: 네이비(단원명 세로) + 파랑(로마숫자)
    bx0, bx1 = pw - 28, pw - 8
    page.draw_rect(fitz.Rect(bx0, 90, bx1, 236), color=NAVY, fill=NAVY)
    page.insert_text((bx0 + 8, 226), chapname, fontname="cafe24", fontfile=FONT_CAFE24,
                     fontsize=9, color=ACCENT_LT, rotate=90)
    page.draw_rect(fitz.Rect(bx0, 244, bx1, 308), color=ACCENT_F, fill=ACCENT_F)
    rw = _fz_paper.text_length(roman, 22)
    page.insert_text(((bx0 + bx1) / 2 - rw / 2, 300), roman, fontname="paper",
                     fontfile=FONT_PAPER_BLACK, fontsize=22, color=WHITE_F)
    page.draw_line((bx0 + 6, 318), (bx0 + 6, 770), color=ACCENT_LT, width=1.0)


def recolor_concept(page, sectitle):
    """개념 페이지 초록 테두리/탭 → 파랑."""
    page.draw_rect(fitz.Rect(30.4, 109.1, 565.1, 794.6), color=ACCENT_F,
                   width=3.4, radius=0.0065)
    page.draw_rect(fitz.Rect(38, 85, 131, 109.5), color=ACCENT_F, fill=ACCENT_F, radius=0.12)
    page.insert_text((49, 102), sectitle, fontname="cafe24", fontfile=FONT_CAFE24,
                     fontsize=9, color=WHITE_F)


def pil_to_pdfpage(out, img, rect):
    import io
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    page = out.new_page(width=rect.width, height=rect.height)
    page.insert_image(rect, stream=buf.getvalue())


def main(preview=False):
    if preview:
        make_cover().save(OUT_DIR / "preview_cover.png")
        make_divider(*DIVIDERS[1]).save(OUT_DIR / "preview_div.png")
        make_answer_divider().save(OUT_DIR / "preview_ans.png")
        print("previews saved")
        return

    src = fitz.open(str(SRC_PDF))
    rect = src[0].rect
    out = fitz.open()
    for i in range(len(src)):
        if i == 0:
            pil_to_pdfpage(out, make_cover(), rect)
        elif i in DIVIDERS:
            pil_to_pdfpage(out, make_divider(*DIVIDERS[i]), rect)
        elif i == ANSWER_DIV_PAGE:
            pil_to_pdfpage(out, make_answer_divider(), rect)
        else:
            out.insert_pdf(src, from_page=i, to_page=i)
            if 1 <= i <= 116:                       # 본문(문제/개념) 페이지
                roman, chapname = chapter_of(i)
                add_summit_ui(out[-1], roman, chapname)
                if i in CONCEPT:
                    recolor_concept(out[-1], CONCEPT[i][4])
    out.save(str(OUT_PDF), garbage=4, deflate=True)
    # ~/교재 자동 전달(다운로드 격리 회피)
    import sys as _sys; _sys.path.insert(0, str(Path(__file__).resolve().parent))
    from lib_deliver import deliver as _deliver; _deliver(OUT_PDF)
    print(f"[OK] {OUT_PDF} ({len(out)} pages)")
    out.close()
    src.close()


if __name__ == "__main__":
    import sys
    main(preview="--preview" in sys.argv)
