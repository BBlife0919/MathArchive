"""사람 상반신(머리·어깨) 영역을 HOG full-body / upper-body cascade 로 검출하여
모든 머리 영역에 블러 추가. blur_faces.py 가 놓친 영역도 함께 처리."""
from __future__ import annotations
import sys
from pathlib import Path
import cv2
import numpy as np


def detect_upper_bodies(img_bgr) -> list[tuple[int, int, int, int]]:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    boxes: list[tuple[int, int, int, int]] = []
    for cas in [
        "haarcascade_upperbody.xml",
        "haarcascade_fullbody.xml",
        "haarcascade_mcs_upperbody.xml",
    ]:
        path = cv2.data.haarcascades + cas
        if not Path(path).exists():
            continue
        clf = cv2.CascadeClassifier(path)
        rects = clf.detectMultiScale(gray, 1.05, 2, minSize=(80, 80))
        for (x, y, w, h) in rects:
            # 상반신 영역의 위쪽 1/3 = 머리 추정
            head_h = int(h * 0.45)
            boxes.append((x, y, w, head_h))
    return boxes


def pixelate(img: np.ndarray, x0: int, y0: int, x1: int, y1: int):
    roi = img[y0:y1, x0:x1]
    if roi.size == 0:
        return
    h, w = roi.shape[:2]
    small = cv2.resize(roi, (max(8, w // 22), max(8, h // 22)),
                       interpolation=cv2.INTER_LINEAR)
    pix = cv2.resize(small, (w, h), interpolation=cv2.INTER_NEAREST)
    img[y0:y1, x0:x1] = pix


def blur_extra(in_path: Path):
    img = cv2.imread(str(in_path))
    H, W = img.shape[:2]
    boxes = detect_upper_bodies(img)
    print(f"  {in_path.name}: {len(boxes)} upper-body candidates")
    for (x, y, w, h) in boxes:
        ex = int(w * 0.15)
        ey = int(h * 0.35)
        x0 = max(0, x - ex)
        y0 = max(0, y - ey)
        x1 = min(W, x + w + ex)
        y1 = min(H, y + h + ey)
        pixelate(img, x0, y0, x1, y1)
    cv2.imwrite(str(in_path), img, [cv2.IMWRITE_PNG_COMPRESSION, 6])


def manual_zones(in_path: Path, zones_pct: list[tuple[float, float, float, float]]):
    """zones_pct: [(x_pct, y_pct, w_pct, h_pct), ...]  — 0~1 비율."""
    img = cv2.imread(str(in_path))
    H, W = img.shape[:2]
    for (xp, yp, wp, hp) in zones_pct:
        x0 = int(W * xp); y0 = int(H * yp)
        x1 = min(W, x0 + int(W * wp)); y1 = min(H, y0 + int(H * hp))
        pixelate(img, x0, y0, x1, y1)
    cv2.imwrite(str(in_path), img, [cv2.IMWRITE_PNG_COMPRESSION, 6])


def main():
    if len(sys.argv) < 2:
        print("usage: blur_persons.py <img>")
        sys.exit(2)
    blur_extra(Path(sys.argv[1]))


if __name__ == "__main__":
    main()
