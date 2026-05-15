"""문제 이미지 상단의 출처 텍스트 [YYYY년 M월 ...] 를 OCR → 더 크고 예쁜 폰트로 재렌더링.

문제 이미지는 항상 x=75, width=207.5 PDF pt 위치에 있고,
상단 ~8pt 구간에 출처 라인이 있음.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

import fitz
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"
USER_FONT_DIR = Path.home() / "Library" / "Fonts"

# 새 출처 텍스트 폰트 (Cafe24 — 둥글둥글 친근, 인강교재 느낌)
SRC_FONT_NAME = "cafe24"
SRC_FONT_FILE = str(USER_FONT_DIR / "Cafe24Ssurround-v2.0.ttf")
_src_font = fitz.Font(fontfile=SRC_FONT_FILE)

# 색상: 진한 회색 (인강교재 스타일 — 어두운 누드 톤)
SRC_COLOR = (90 / 255, 95 / 255, 110 / 255)

# 출처 텍스트 폰트 크기 (원본 ~8pt → 8.5pt 로 약간만 키움)
SRC_FONT_SIZE = 8.5

# 이미지 영역 상단에서 출처 라인이 차지하는 PDF pt 높이
SRC_LINE_HEIGHT = 9.0


def ocr_text(png_path: str) -> str:
    """tesseract Korean+English OCR (psm=7 = single line, oem=1 = LSTM only)."""
    with tempfile.NamedTemporaryFile(suffix="", delete=False, dir="/tmp") as tf:
        out_base = tf.name
    try:
        subprocess.run(
            ["tesseract", png_path, out_base, "-l", "kor+eng",
             "--oem", "1", "--psm", "7"],
            capture_output=True,
            cwd="/tmp",
        )
        txt = Path(out_base + ".txt").read_text(encoding="utf-8", errors="replace").strip()
        return txt
    finally:
        try:
            os.unlink(out_base + ".txt")
        except FileNotFoundError:
            pass


def find_question_source_regions(page: fitz.Page) -> list[tuple[float, float, float, float]]:
    """각 문항의 출처 라인 영역(image 블록 또는 label 위치 기반 fallback) 반환.

    1) 좌측 문제 이미지(x≈75, w≈207) 의 bbox 를 우선 사용
    2) 이미지 없는 문항은 label(NotoSansKR-Bold 20pt) 의 y 좌표 기준으로 fallback
    """
    d = page.get_text("dict")
    # 1) 이미지 블록
    image_regions = []
    for blk in d['blocks']:
        if blk.get('type') != 1:
            continue
        bx = blk['bbox']
        w = bx[2] - bx[0]
        if 70 <= bx[0] <= 80 and 200 <= w <= 215 and (bx[3] - bx[1]) > 25:
            image_regions.append(tuple(bx))

    # 2) 문항 라벨 (큰 NotoSansKR-Bold 숫자) 위치 수집
    labels = []
    for blk in d['blocks']:
        if blk.get('type') != 0:
            continue
        for line in blk['lines']:
            for sp in line['spans']:
                if 'NotoSansKR-Bold' in sp['font'] and sp['size'] == 20.0:
                    if sp['text'].strip().isdigit():
                        labels.append(tuple(sp['bbox']))

    # 라벨마다 같은 행에 image_region 이 있는지 확인 → 없으면 label 기반 fake region 생성
    regions = list(image_regions)
    for lb in labels:
        lb_y = (lb[1] + lb[3]) / 2  # 라벨 중심 y
        matched = False
        for img in image_regions:
            if img[1] - 6 <= lb_y <= img[3] + 6:
                matched = True
                break
        if not matched:
            # fallback: label 우측에 가상의 source-line 영역 (x=75 부터, 라벨 top 위치 기준)
            fake = (75.0, lb[1], 285.0, lb[3])
            regions.append(fake)

    # y 좌표 순 정렬
    regions.sort(key=lambda r: r[1])
    return regions


def extract_source_line(page: fitz.Page, img_bbox, dpi_matrix=fitz.Matrix(8, 8)) -> str:
    """이미지 상단 클립 → OCR → 출처 텍스트 반환 (실패 시 빈 문자열)."""
    x0, y0, x1, y1 = img_bbox
    clip = fitz.Rect(x0 - 5, y0 - 1, x1 + 5, y0 + SRC_LINE_HEIGHT)
    pix = page.get_pixmap(clip=clip, matrix=dpi_matrix, alpha=False)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False, dir="/tmp") as tf:
        tmp = tf.name
    try:
        pix.save(tmp)
        img = Image.open(tmp).convert("RGB")
        # 출처 라인은 클립 상단 ~75%
        top = img.crop((0, 0, img.width, int(img.height * 0.85)))
        top.save(tmp)
        text = ocr_text(tmp)
        return text
    finally:
        try:
            os.unlink(tmp)
        except FileNotFoundError:
            pass


_SRC_PATTERN = re.compile(r"\[\s*(.*?)\s*\]")

# OCR 후 일관성 보정 규칙 (출처 컨텍스트 한정)
def _fix_ocr(text: str) -> str:
    # 한글 OCR 흔한 오류 정정
    text = text.replace("ㅣ", "1").replace("Ⅰ", "I").replace("ㅇI", "이")
    # "고1/2/3" 이 "31/32/33" 으로 잘못 읽히는 케이스
    text = re.sub(r"(?<=\D)(31|32|33)(?=\s)", lambda m: "고" + m.group(1)[-1], text)
    text = re.sub(r"(?<=월 )(31|32|33)(?=\s)", lambda m: "고" + m.group(1)[-1], text)
    text = re.sub(r"(?<=월 )(311|312|313)(?=\s)", lambda m: "고" + m.group(1)[-2], text)
    # "고" → "G", "고1" → "G1" 같은 영문 오역 정정
    text = re.sub(r"\bG([123])\b", lambda m: "고" + m.group(1), text)
    text = re.sub(r"\bg([123])\b", lambda m: "고" + m.group(1), text)
    # 점수 표기 정정: "4 점" → "4점", "4전" → "4점"
    text = re.sub(r"(\d+)\s*전(\d*)\]?", lambda m: m.group(1) + "점" + m.group(2), text)
    text = re.sub(r"(\d+)\s*점", lambda m: m.group(1) + "점", text)
    # 번 표기 정정: "버/" → "번/", "버1" → "번1"
    text = re.sub(r"(\d+)\s*버(?=[/\]])", lambda m: m.group(1) + "번", text)
    text = re.sub(r"(\d+)\s*번", lambda m: m.group(1) + "번", text)
    # "/숫자전숫자" → "/숫자점" 형태
    text = re.sub(r"/(\d+)전\d*", lambda m: "/" + m.group(1) + "점", text)
    # 말미 "점숫자" → "점" (잘못 붙은 trailing digit 제거)
    text = re.sub(r"점\d+$", "점", text)
    # 말미의 "]" 누락 보정 (특정 케이스: "/4점" 으로 끝나면 "]" 추가는 clean_source 에서 처리)
    # 다중 공백 압축
    text = re.sub(r"\s+", " ", text).strip()
    return text


def clean_source(raw: str) -> str:
    """OCR 결과에서 [...] 패턴 추출, 노이즈 제거."""
    if not raw:
        return ""
    raw = raw.replace("ㅣ", "1").replace("Ⅰ", "I")
    m = _SRC_PATTERN.search(raw)
    if m:
        body = m.group(1).strip()
        body = _fix_ocr(body)
        return f"[{body}]"
    # 괄호가 OCR 누락된 경우: 연도가 들어있으면 받아들임
    if re.search(r"\d{4}", raw) or re.search(r"\d+년", raw):
        return "[" + _fix_ocr(raw.strip()) + "]"
    return ""


def replace_source_on_page(page: fitz.Page, verbose=False) -> int:
    """해당 페이지의 문제 이미지마다 출처 라인 교체. 처리한 갯수 반환."""
    count = 0
    rects = find_question_source_regions(page)
    for img_bbox in rects:
        x0, y0, x1, y1 = img_bbox
        # 1) OCR
        raw = extract_source_line(page, img_bbox)
        cleaned = clean_source(raw)
        if not cleaned:
            if verbose:
                print(f"    no source detected at bbox=({x0:.0f},{y0:.0f}): raw={raw!r}")
            continue
        # 2) White-cover the source line area
        cover = fitz.Rect(x0 - 2, y0 - 0.5, x1 + 2, y0 + SRC_LINE_HEIGHT - 0.5)
        page.draw_rect(cover, color=(1, 1, 1), fill=(1, 1, 1), overlay=True)
        # 3) Draw new source text (얇게, build_2col 에서 다시 가림)
        new_y = y0 + 7.4
        new_x = x0
        page.insert_text(
            (new_x, new_y),
            cleaned,
            fontname=SRC_FONT_NAME,
            fontfile=SRC_FONT_FILE,
            fontsize=SRC_FONT_SIZE,
            color=SRC_COLOR,
        )
        count += 1
        if verbose:
            print(f"    [{x0:.0f},{y0:.0f}] {cleaned}")
    return count


def process_pdf(in_path: str, out_path: str, problem_page_range: tuple[int, int]):
    doc = fitz.open(in_path)
    total = 0
    p0, p1 = problem_page_range
    for pi in range(p0, p1 + 1):
        n = replace_source_on_page(doc[pi])
        total += n
        if (pi - p0) % 5 == 0:
            print(f"  page {pi}: replaced {n} sources (running total {total})")
    doc.save(out_path, garbage=4, deflate=True)
    doc.close()
    print(f"  [OK] {out_path} — total {total} sources replaced")


def main():
    # 출처는 문제 페이지에만 있음 (해설 페이지 제외)
    sources = [
        (OUT_DIR / "renum_m1.pdf", OUT_DIR / "renum_m1_src.pdf", (0, 37)),
        (OUT_DIR / "renum_m2.pdf", OUT_DIR / "renum_m2_src.pdf", (0, 45)),
        (OUT_DIR / "renum_m3.pdf", OUT_DIR / "renum_m3_src.pdf", (0, 18)),
    ]
    for src, dst, rng in sources:
        print(f"Processing {src.name} pages {rng[0]}-{rng[1]}...")
        process_pdf(str(src), str(dst), rng)


if __name__ == "__main__":
    main()
