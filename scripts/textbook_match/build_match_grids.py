"""각 시험문제 + top-8 후보를 하나의 grid PNG로 합성."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match')
GRID_DIR = ROOT / 'match_grids'
GRID_DIR.mkdir(parents=True, exist_ok=True)

GRID_W = 1800
EXAM_H = 360
CAND_W = 870
CAND_H = 360
GAP = 12
LABEL_H = 36
N_CAND = 8  # 2 rows × 4 cols, but using 2 cols per row x 4 rows

# 더 좋은 가독성: 1 col exam + 후보 4 rows × 2 cols = 8 후보
COLS = 2


def fit_image(img: Image.Image, w: int, h: int) -> Image.Image:
    img = img.convert('RGB')
    iw, ih = img.size
    ratio = min(w / iw, h / ih)
    new_w = int(iw * ratio)
    new_h = int(ih * ratio)
    img2 = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new('RGB', (w, h), (255, 255, 255))
    canvas.paste(img2, ((w - new_w) // 2, (h - new_h) // 2))
    return canvas


def build_grid(q_image: Path, q_label: str, candidates: list[dict]) -> Image.Image:
    n_cand = min(N_CAND, len(candidates))
    n_rows = (n_cand + COLS - 1) // COLS
    total_w = GRID_W
    total_h = LABEL_H + EXAM_H + GAP + (LABEL_H + CAND_H + GAP) * n_rows + 16
    img = Image.new('RGB', (total_w, total_h), (245, 245, 248))
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Supplemental/AppleGothic.ttf', 20)
        font_b = ImageFont.truetype('/System/Library/Fonts/Supplemental/AppleGothic.ttf', 24)
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
        # 라벨
        label = f"#{i+1}  {c['tb_short']} · {c['code']} · p.{c['page']}  (텍스트점수 {c['text_score']:.0f})"
        draw.rectangle([x, cy, x + cand_w_per, cy + LABEL_H], fill=(216, 167, 43))
        draw.text((x + 8, cy + 6), label, fill=(255, 255, 255), font=font)
        # 이미지
        ip = Path(c['image'])
        if ip.exists():
            ci = Image.open(ip)
            ci_fit = fit_image(ci, cand_w_per, CAND_H)
            img.paste(ci_fit, (x, cy + LABEL_H))
    return img


def main():
    for school in ['광명고', '광명북고', '광문고']:
        data = json.load(open(ROOT / f'agent_input/{school}.json'))
        for q in data['questions']:
            qid = f'{school}_Q{q["q_no"]:02d}'
            grid = build_grid(
                Path(q['q_image']) if Path(q['q_image']).is_absolute() else Path(__file__).resolve().parent.parent.parent / q['q_image'],
                f'{qid}: {q["q_text"][:80]}',
                [{**c, 'image': c['image'] if Path(c['image']).is_absolute() else str(Path(__file__).resolve().parent.parent.parent / c['image'])} for c in q['candidates']],
            )
            out = GRID_DIR / f'{qid}.png'
            grid.save(out, optimize=True)
        print(f'{school}: built {len(data["questions"])} grids')


if __name__ == '__main__':
    main()
