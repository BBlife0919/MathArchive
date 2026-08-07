"""HEIC/PNG 사진에서 얼굴 자동 검출 후 블러 처리.

Haar cascade frontal + profile 두 분류기로 검출,
검출된 영역을 주변까지 30% 확장해 GaussianBlur로 강하게 처리.
"""
from __future__ import annotations
import sys
from pathlib import Path
import cv2

CASCADES = [
    cv2.data.haarcascades + "haarcascade_frontalface_default.xml",
    cv2.data.haarcascades + "haarcascade_frontalface_alt2.xml",
    cv2.data.haarcascades + "haarcascade_profileface.xml",
]


def detect_faces(img_bgr) -> list[tuple[int, int, int, int]]:
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)
    boxes = []
    for path in CASCADES:
        clf = cv2.CascadeClassifier(path)
        faces = clf.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=4, minSize=(60, 60)
        )
        for (x, y, w, h) in faces:
            boxes.append((x, y, w, h))
    # 좌우반전으로 한 번 더 (profile 반대 방향)
    flipped = cv2.flip(gray, 1)
    H, W = gray.shape[:2]
    profile = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_profileface.xml"
    )
    fl_faces = profile.detectMultiScale(flipped, 1.1, 4, minSize=(60, 60))
    for (x, y, w, h) in fl_faces:
        boxes.append((W - x - w, y, w, h))
    return merge_boxes(boxes)


def merge_boxes(boxes: list[tuple[int, int, int, int]]) -> list[tuple[int, int, int, int]]:
    """겹치는 박스 병합."""
    if not boxes:
        return []
    boxes = sorted(boxes, key=lambda b: -b[2] * b[3])
    merged: list[tuple[int, int, int, int]] = []
    for b in boxes:
        x, y, w, h = b
        cx, cy = x + w / 2, y + h / 2
        absorbed = False
        for i, m in enumerate(merged):
            mx, my, mw, mh = m
            mcx, mcy = mx + mw / 2, my + mh / 2
            if abs(cx - mcx) < max(w, mw) * 0.5 and abs(cy - mcy) < max(h, mh) * 0.5:
                # 영역 합치기
                nx = min(x, mx)
                ny = min(y, my)
                nx2 = max(x + w, mx + mw)
                ny2 = max(y + h, my + mh)
                merged[i] = (nx, ny, nx2 - nx, ny2 - ny)
                absorbed = True
                break
        if not absorbed:
            merged.append(b)
    return merged


def blur_faces(in_path: Path, out_path: Path, expand: float = 0.30) -> int:
    img = cv2.imread(str(in_path))
    if img is None:
        raise RuntimeError(f"failed to read {in_path}")
    H, W = img.shape[:2]
    boxes = detect_faces(img)
    print(f"  {in_path.name}: {len(boxes)} faces detected")
    for (x, y, w, h) in boxes:
        ex = int(w * expand)
        ey = int(h * expand)
        x0 = max(0, x - ex)
        y0 = max(0, y - ey)
        x1 = min(W, x + w + ex)
        y1 = min(H, y + h + ey)
        roi = img[y0:y1, x0:x1]
        # 사이즈에 비례한 강한 블러
        k = max(31, ((x1 - x0) // 6) | 1)
        if k % 2 == 0:
            k += 1
        blurred = cv2.GaussianBlur(roi, (k, k), k / 2)
        # 한 번 더 pixelate
        small = cv2.resize(blurred, (max(8, (x1 - x0) // 18), max(8, (y1 - y0) // 18)),
                           interpolation=cv2.INTER_LINEAR)
        pixelated = cv2.resize(small, (x1 - x0, y1 - y0),
                               interpolation=cv2.INTER_NEAREST)
        img[y0:y1, x0:x1] = pixelated
    cv2.imwrite(str(out_path), img, [cv2.IMWRITE_PNG_COMPRESSION, 6])
    return len(boxes)


def main():
    if len(sys.argv) < 3:
        print("usage: blur_faces.py <in> <out>")
        sys.exit(2)
    in_path = Path(sys.argv[1])
    out_path = Path(sys.argv[2])
    n = blur_faces(in_path, out_path)
    print(f"blurred {n} faces → {out_path}")


if __name__ == "__main__":
    main()
