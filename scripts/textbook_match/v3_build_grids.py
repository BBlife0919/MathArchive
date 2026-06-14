"""각 시험문제 + top-K 교재 페이지 후보를 grid PNG로 합성."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
GRID_DIR = ROOT / 'match_grids'
GRID_DIR.mkdir(parents=True, exist_ok=True)

GRID_W = 1900
EXAM_H = 360
CAND_W = 920
CAND_H = 540  # 교재 페이지 전체
GAP = 12
LABEL_H = 36
COLS = 2
N_CAND = 8

FONT_REG = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'


def fit_image(img: Image.Image, w: int, h: int) -> Image.Image:
    img = img.convert('RGB')
    iw, ih = img.size
    ratio = min(w / iw, h / ih)
    nw, nh = int(iw * ratio), int(ih * ratio)
    img2 = img.resize((nw, nh), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), (255, 255, 255))
    canvas.paste(img2, ((w - nw) // 2, (h - nh) // 2))
    return canvas


def build_grid(q_image: Path, q_label: str, candidates: list[dict]) -> Image.Image:
    n_cand = min(N_CAND, len(candidates))
    n_rows = (n_cand + COLS - 1) // COLS
    total_w = GRID_W
    total_h = LABEL_H + EXAM_H + GAP + (LABEL_H + CAND_H + GAP) * n_rows + 16
    img = Image.new('RGB', (total_w, total_h), (245, 245, 248))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype(FONT_REG, 18)
        font_b = ImageFont.truetype(FONT_REG, 22)
    except Exception:
        font = ImageFont.load_default()
        font_b = ImageFont.load_default()
    # 시험문제 라벨
    draw.rectangle([0, 0, total_w, LABEL_H], fill=(40, 64, 109))
    draw.text((12, 6), f'[시험문제] {q_label}', fill=(255, 255, 255), font=font_b)
    # 시험문제 이미지
    if q_image.exists():
        ex = Image.open(q_image)
        ex_fit = fit_image(ex, total_w - 16, EXAM_H)
        img.paste(ex_fit, (8, LABEL_H))
    y = LABEL_H + EXAM_H + GAP
    cand_w_per = (total_w - GAP * (COLS + 1)) // COLS
    for i, c in enumerate(candidates[:n_cand]):
        col = i % COLS
        row = i // COLS
        x = GAP + col * (cand_w_per + GAP)
        cy = y + row * (LABEL_H + CAND_H + GAP)
        label = f"#{i+1}  {c['tb_short']} · p.{c['page']}  (점수 {c['score']:.0f})"
        draw.rectangle([x, cy, x + cand_w_per, cy + LABEL_H], fill=(216, 167, 43))
        draw.text((x + 8, cy + 6), label, fill=(255, 255, 255), font=font)
        # 교재 페이지 PNG (renders/<tb_key>/p{page:04d}.png)
        ip = ROOT / 'pages_png' / c['tb_key'] / f'p{c["page"]:04d}.png'
        if ip.exists():
            ci = Image.open(ip)
            ci_fit = fit_image(ci, cand_w_per, CAND_H)
            img.paste(ci_fit, (x, cy + LABEL_H))
    return img


def main():
    cand = json.load(open(ROOT / 'text_candidates.json'))
    n = 0
    for school, results in cand.items():
        for q in results:
            qid = f'{school}_Q{q["q_no"]:02d}'
            qimg = ROOT / 'crops_exam' / f'{qid}.png'
            if not qimg.exists():
                continue
            grid = build_grid(qimg, f'{qid}: {q["q_text"][:70]}', q['top'])
            out = GRID_DIR / f'{qid}.png'
            grid.save(out, optimize=True)
            n += 1
        print(f'  {school}: built grids')
    print(f'total grids: {n}')


if __name__ == '__main__':
    main()
