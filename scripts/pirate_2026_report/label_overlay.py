"""참고서 이미지 좌상단에 A·NN 오렌지 카드 라벨 오버레이."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

FONT_BOLD = '/System/Library/Fonts/Supplemental/Arial Bold.ttf'
FONT_BOLD_FALLBACK = '/System/Library/Fonts/Supplemental/AppleGothic.ttf'
# 확장 폰트 후보
FONT_HEAVY_CANDIDATES = [
    '/System/Library/Fonts/Supplemental/Arial Black.ttf',
    '/System/Library/Fonts/Helvetica.ttc',
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
]


def _load_font(size: int, heavy: bool = False):
    candidates = FONT_HEAVY_CANDIDATES if heavy else [FONT_BOLD, FONT_BOLD_FALLBACK]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def make_label_card(cat: str, num: int, width: int = 200) -> Image.Image:
    """참고 이미지 스타일 라벨 카드 (흰색 배경 + 오렌지 두꺼운 C·35 + 체크박스)."""
    W = width
    H = int(width * 1.05)  # 세로가 좀 길게
    card = Image.new('RGBA', (W, H), (255, 255, 255, 255))  # 순 흰색
    draw = ImageDraw.Draw(card)
    # 큰 오렌지 라벨 C·35
    font_big = _load_font(int(W * 0.42), heavy=True)
    font_tick = _load_font(int(W * 0.11), heavy=True)
    label_text = f'{cat}·{num:02d}'
    draw.text((int(W * 0.07), int(H * 0.05)), label_text, fill=(232, 106, 42), font=font_big)
    # 1차/2차/3차 체크박스 라인
    y_check = int(H * 0.55)
    box_size = int(W * 0.08)
    x = int(W * 0.08)
    for lab in ['1차', '2차', '3차']:
        draw.rectangle([x, y_check, x + box_size, y_check + box_size],
                       outline=(90, 90, 90), width=2)
        draw.text((x + box_size + 3, y_check - 2), lab, fill=(60, 60, 60), font=font_tick)
        x += box_size + int(W * 0.18)
    # O/X 체크박스 라인
    y_ox = int(H * 0.78)
    x = int(W * 0.08)
    for lab in ['O', 'X']:
        draw.rectangle([x, y_ox, x + box_size, y_ox + box_size],
                       outline=(90, 90, 90), width=2)
        draw.text((x + box_size + 3, y_ox - 2), lab, fill=(60, 60, 60), font=font_tick)
        x += box_size + int(W * 0.20)
    return card


def overlay_on_image(src_path: Path, cat: str, num: int, dst_path: Path,
                     label_width_ratio: float = 0.18) -> None:
    """참고서 이미지 위쪽에 흰색 여백을 추가하고 문항번호 자리에 라벨 카드 배치.

    이렇게 하면 원본 이미지의 문제 텍스트는 그대로 보존되고 상단에 문항번호처럼 라벨이 표시됨.
    """
    img = Image.open(src_path).convert('RGB')
    W, H = img.size
    label_w = max(160, int(W * label_width_ratio))
    card = make_label_card(cat, num, width=label_w)
    _, card_h = card.size
    pad_top = card_h + 12
    canvas = Image.new('RGB', (W, H + pad_top), (255, 255, 255))
    canvas.paste(img, (0, pad_top))
    margin_x = int(W * 0.01)
    margin_y = 6
    canvas.paste(card, (margin_x, margin_y), card)
    canvas.save(dst_path, 'PNG', optimize=True)


if __name__ == '__main__':
    # 데모: 광명7적중.png 에 A·07 라벨 오버레이
    src = Path('/Users/youngwoolee/MathDB/output/pirate_analysis/무제_기말_2026/광명7적중.png')
    dst = Path('/tmp/광명7_labeled.png')
    overlay_on_image(src, 'A', 7, dst)
    print(f'test: {dst}')
