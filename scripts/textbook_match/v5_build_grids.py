"""v5 grid PNG — 깨끗한 시험 크롭(텍스트레이어 기반) + top-8 교재 페이지."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT_V3 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
ROOT_V5 = Path('/Users/youngwoolee/MathDB/output/textbook_match_v5')
EX_CROPS = ROOT_V5 / 'exam_crops'
GRID_DIR = ROOT_V5 / 'match_grids'
GRID_DIR.mkdir(exist_ok=True)

GRID_W = 1900
EXAM_H = 380
CAND_H = 480
GAP = 12
LABEL_H = 36
COLS = 2
N_CAND = 8
FONT_REG = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'


def fit(img, w, h):
    img = img.convert('RGB')
    iw, ih = img.size
    ratio = min(w / iw, h / ih)
    nw, nh = int(iw * ratio), int(ih * ratio)
    img2 = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), (255, 255, 255))
    canvas.paste(img2, ((w - nw) // 2, (h - nh) // 2))
    return canvas


def build(school: str, q: dict) -> Image.Image:
    qname = q['q_name']
    qid = f'{school}_Q{qname.zfill(2) if qname.isdigit() else qname}'
    # exam crop path (Q01.png, Q02.png ... 숫자만 zero-pad; 서답형은 SN)
    if qname.isdigit():
        exam_path = EX_CROPS / f'{school}_Q{int(qname):02d}.png'
    else:
        # 서답형N → 보기에는 SN으로
        n = qname.replace('서답형', '')
        exam_path = EX_CROPS / f'{school}_QS{n}.png'

    cands = q['top'][:N_CAND]
    n_rows = (len(cands) + COLS - 1) // COLS
    total_h = LABEL_H + EXAM_H + GAP + (LABEL_H + CAND_H + GAP) * n_rows + 16
    img = Image.new('RGB', (GRID_W, total_h), (245, 245, 248))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_REG, 18)
        font_b = ImageFont.truetype(FONT_REG, 22)
    except Exception:
        font = font_b = ImageFont.load_default()

    draw.rectangle([0, 0, GRID_W, LABEL_H], fill=(40, 64, 109))
    head = f'[시험문제] {school} Q{qname}: {q["text"][:60]}'
    draw.text((12, 6), head, fill=(255, 255, 255), font=font_b)
    if exam_path.exists():
        ex = Image.open(exam_path)
        img.paste(fit(ex, GRID_W - 16, EXAM_H), (8, LABEL_H))

    y = LABEL_H + EXAM_H + GAP
    cand_w = (GRID_W - GAP * (COLS + 1)) // COLS
    for i, c in enumerate(cands):
        col = i % COLS
        row = i // COLS
        x = GAP + col * (cand_w + GAP)
        cy = y + row * (LABEL_H + CAND_H + GAP)
        label = f"#{i+1}  {c['tb_short']} · p.{c['page']}  (점수 {c['score']:.0f})"
        draw.rectangle([x, cy, x + cand_w, cy + LABEL_H], fill=(216, 167, 43))
        draw.text((x + 8, cy + 6), label, fill=(255, 255, 255), font=font)
        ip = ROOT_V3 / 'pages_png' / c['tb_key'] / f'p{c["page"]:04d}.png'
        if ip.exists():
            ci = Image.open(ip)
            img.paste(fit(ci, cand_w, CAND_H), (x, cy + LABEL_H))
    return img


def main():
    cand = json.load(open(ROOT_V5 / 'text_candidates.json'))
    n = 0
    for school, results in cand.items():
        for q in results:
            grid = build(school, q)
            qname = q['q_name']
            qid = f"{school}_Q{qname.zfill(2) if qname.isdigit() else qname}"
            grid.save(GRID_DIR / f'{qid}.png', optimize=True)
            n += 1
        print(f'  {school}: built grids')
    print(f'total: {n}')


if __name__ == '__main__':
    main()
