"""원본사진/ 캡처에서 [중단원] / [난이도] 메타 라인을 OCR 검출 후 마스킹.

원본은 보존, 결과는 원본사진_clean/ 에 저장. 빌더가 우선 사용.
"""
from __future__ import annotations
import re
import shutil
import subprocess
import unicodedata
from pathlib import Path
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
PA = ROOT / "output" / "pirate_analysis"
SRC = PA / "원본사진"
DST = PA / "원본사진_clean"

META_RE = re.compile(r"\[\s*(중\s*단\s*원|난\s*이\s*도)\s*\]")


def ocr_lines(img_path: Path) -> list[tuple[int, int, int, int, str]]:
    """tesseract TSV → (x, y, w, h, text) 리스트 (라인별)."""
    res = subprocess.run(
        ["tesseract", str(img_path), "-", "-l", "kor", "--psm", "6", "tsv"],
        capture_output=True, text=True,
    )
    if res.returncode != 0:
        return []
    rows = res.stdout.splitlines()
    if not rows:
        return []
    header = rows[0].split("\t")
    idx = {h: i for i, h in enumerate(header)}
    # 라인 단위로 합치기 (block_num + par_num + line_num)
    lines: dict[tuple, dict] = {}
    for row in rows[1:]:
        cells = row.split("\t")
        if len(cells) < len(header):
            continue
        try:
            level = int(cells[idx["level"]])
            text = cells[idx["text"]]
        except (KeyError, ValueError):
            continue
        if level != 5 or not text.strip():
            continue
        key = (cells[idx["block_num"]], cells[idx["par_num"]], cells[idx["line_num"]])
        x = int(cells[idx["left"]])
        y = int(cells[idx["top"]])
        w = int(cells[idx["width"]])
        h = int(cells[idx["height"]])
        if key not in lines:
            lines[key] = {"x0": x, "y0": y, "x1": x + w, "y1": y + h, "text": text}
        else:
            d = lines[key]
            d["x0"] = min(d["x0"], x)
            d["y0"] = min(d["y0"], y)
            d["x1"] = max(d["x1"], x + w)
            d["y1"] = max(d["y1"], y + h)
            d["text"] += " " + text
    out = []
    for d in lines.values():
        out.append((d["x0"], d["y0"], d["x1"] - d["x0"], d["y1"] - d["y0"], d["text"]))
    return out


def mask_meta(in_path: Path, out_path: Path) -> bool:
    img = Image.open(in_path).convert("RGB")
    W, H = img.size
    lines = ocr_lines(in_path)
    if not lines:
        img.save(out_path)
        return False

    meta_ys: list[int] = []
    for x, y, w, h, text in lines:
        if META_RE.search(text):
            meta_ys.append(y)

    if not meta_ys:
        img.save(out_path)
        return False

    # 가장 위쪽 메타 y에서 끝까지 흰색 마스킹
    top = max(0, min(meta_ys) - 4)
    draw = ImageDraw.Draw(img)
    draw.rectangle((0, top, W, H), fill="white")
    img.save(out_path)
    return True


def main():
    DST.mkdir(exist_ok=True)
    cnt_done = 0
    cnt_skip = 0
    for p in sorted(SRC.iterdir()):
        if p.suffix.lower() != ".png":
            continue
        out = DST / unicodedata.normalize("NFC", p.name)
        masked = mask_meta(p, out)
        if masked:
            cnt_done += 1
            print(f"  ✓ {p.name}")
        else:
            cnt_skip += 1
    print(f"masked: {cnt_done} / no-meta: {cnt_skip} → {DST}")


if __name__ == "__main__":
    main()
