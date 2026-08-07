"""원본 시험 문제 이미지에 저작권 블러 스트라이프 적용."""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageFilter


def apply_blur_stripes(src_path: Path, dst_path: Path,
                       ratios: tuple = (0.25, 0.55, 0.82),
                       stripe_height_frac: float = 0.08,
                       blur_radius: int = 14) -> None:
    """이미지에 지정 비율 위치 (0~1)에 가로 스트라이프 블러 적용."""
    img = Image.open(src_path).convert('RGB')
    W, H = img.size
    stripe_h = int(H * stripe_height_frac)
    for r in ratios:
        y0 = int(H * r) - stripe_h // 2
        y1 = y0 + stripe_h
        if y0 < 0: y0 = 0
        if y1 > H: y1 = H
        region = img.crop((0, y0, W, y1))
        region = region.filter(ImageFilter.GaussianBlur(radius=blur_radius))
        img.paste(region, (0, y0))
    img.save(dst_path, 'PNG', optimize=True)


if __name__ == '__main__':
    src = Path('/Users/youngwoolee/MathDB/output/pirate_analysis/무제_기말_2026_중3/철산중3_7번.png')
    dst = Path('/tmp/철산중3_7번_blur.png')
    apply_blur_stripes(src, dst)
    print(f'test: {dst}')
