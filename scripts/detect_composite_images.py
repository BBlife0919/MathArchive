#!/usr/bin/env python3
"""합성 이미지(여러 그림이 한 파일에 합쳐진 것) 자동 감지.

원본 HWPX 가 4문항 그림을 1개 이미지로 합쳐 저장한 케이스(A·22 등)를 탐지.
방법: 회색조 → 콘텐츠(어두움) 투영 → 가운데에 전폭/전고 흰 띠가 있어 내용이
2개 이상 영역으로 갈리면 '합성'으로 판정.

교재 문항 대상으로 로컬 /images 파일을 분석해 합성 question_id 목록 출력.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
IMAGES_DIR = ROOT / "images"


def is_composite(path: Path) -> bool:
    try:
        im = Image.open(path).convert("L")
    except Exception:
        return False
    w, h = im.size
    if w < 200 or h < 150:
        return False
    # 다운스케일
    scale = 700 / max(w, h)
    if scale < 1:
        im = im.resize((int(w * scale), int(h * scale)))
    a = np.asarray(im)
    content = a < 200                      # 어두운 픽셀 = 내용
    H, W = content.shape
    row_has = content.sum(axis=1) > (W * 0.01)   # 그 행에 내용 있나
    col_has = content.sum(axis=0) > (H * 0.01)

    def groups(mask):
        # 연속된 True 구간(내용 영역) 개수 — 큰 것만
        regs = []
        s = None
        for i, v in enumerate(mask):
            if v and s is None:
                s = i
            elif not v and s is not None:
                regs.append((s, i)); s = None
        if s is not None:
            regs.append((s, len(mask)))
        big = [(a, b) for a, b in regs if (b - a) > len(mask) * 0.12]
        # 큰 영역 사이의 '흰 띠'가 충분히 넓어야 분리로 인정
        gaps = []
        for (a1, b1), (a2, b2) in zip(big, big[1:]):
            gaps.append(a2 - b1)
        return len(big), gaps

    nrow, rgaps = groups(row_has)
    ncol, cgaps = groups(col_has)
    # 세로(상하) 또는 가로(좌우)로 큰 영역 2개+ & 사이 흰 띠가 전체의 3%+ 면 합성
    split_v = nrow >= 2 and any(g > H * 0.03 for g in rgaps)
    split_h = ncol >= 2 and any(g > W * 0.03 for g in cgaps)
    return split_v or split_h


def main():
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    import psycopg2
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()
    # 교재 대상(광명 고2) 문항 + 이미지
    from build_kernel_point_book import CHAPTERS
    marks = ",".join(["%s"] * len(CHAPTERS))
    cur.execute(
        f"SELECT q.question_id, i.image_path FROM questions q "
        f"JOIN images i ON q.question_id=i.question_id "
        f"WHERE q.region='경기광명시' AND q.grade=2 AND q.chapter IN ({marks})",
        tuple(CHAPTERS),
    )
    rows = cur.fetchall()
    cur.close(); conn.close()

    # 로컬 파일 인덱스 (basename → path)
    local = {p.name: p for p in IMAGES_DIR.iterdir()}
    composite = []
    checked = 0
    for qid, url in rows:
        base = re.sub(r"^.*/", "", url)
        f = local.get(base)
        if not f:
            continue
        checked += 1
        if is_composite(f):
            composite.append(qid)
    composite = sorted(set(composite))
    out = ROOT / "output" / "composite_image_qids.json"
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(composite), encoding="utf-8")
    print(f"검사 {checked} / 합성 의심 {len(composite)}개")
    print("qids:", composite)
    print("저장:", out)


if __name__ == "__main__":
    main()
