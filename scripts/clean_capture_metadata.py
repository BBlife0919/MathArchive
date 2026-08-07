"""매쓰플랫 캡처 상단의 문항번호 + 출처 박스를 흰색으로 마스킹.

원본은 무제 폴더, 결과는 무제_clean/ 에 저장.
빌더는 무제_clean 우선 사용.
"""
from __future__ import annotations
import unicodedata
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PA = ROOT / "output" / "pirate_analysis"
SRC = PA / "무제 폴더"
DST = PA / "무제_clean"


def mask(img: Image.Image) -> Image.Image:
    """좌측 상단 헤더(큰 번호 + 출처 박스) 마스킹."""
    img = img.convert("RGB")
    W, H = img.size
    draw = ImageDraw.Draw(img)
    # 좌측 큰 번호 영역
    draw.rectangle((0, 0, int(W * 0.14), int(H * 0.42)), fill="white")
    # 우측에 펼쳐진 [출처] 박스 (잔상 방지로 26%까지)
    draw.rectangle((int(W * 0.13), 0, int(W * 0.80), int(H * 0.26)), fill="white")
    return img


def main():
    DST.mkdir(exist_ok=True)
    cnt = 0
    for p in sorted(SRC.iterdir()):
        if p.suffix.lower() != ".png":
            continue
        out_name = unicodedata.normalize("NFC", p.name)
        out = DST / out_name
        img = Image.open(p)
        masked = mask(img)
        masked.save(out, optimize=True)
        cnt += 1
    print(f"masked {cnt} captures → {DST}")


if __name__ == "__main__":
    main()
