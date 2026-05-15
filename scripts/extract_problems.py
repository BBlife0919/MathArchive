"""SUMMIT POINT: 각 문제의 메타 정보 + 원본 PDF 클립 좌표 추출.

각 문제 = {
  'label':  'A·01',
  'src_pdf': '.../renum_m1_src.pdf',
  'src_page': 0,
  'clip': (x0, y0, x1, y1),   # PDF 좌표 (포인트)
  'source_text': '[2025년 9월 고1 18번/4점]',
}
"""
from __future__ import annotations
import json
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "output" / "summit_point"
META_JSON = OUT_DIR / "problems_meta.json"

# 라벨 폰트 (renumber_summit.py 가 사용한 SB 어그로 M)
LABEL_FONT = 'OTSBAggroM'
LABEL_SIZE_BIG = 19.0

# 클립 좌표 가로 범위 — 이미지 본문만 (라벨 영역 제외)
CLIP_X0 = 75.0
CLIP_X1 = 290.0
# 라벨 아래로 N pt 떨어진 곳에서 클립 시작 — 라벨/출처 영역 스킵
CLIP_Y_OFFSET_FROM_LABEL = 12.0

# 페이지 본문 하단 경계 (footer 영역 제외)
PAGE_CONTENT_BOTTOM = 800.0

# 문항 사이 최소 갭 (위 라벨 사이)
INTER_PROBLEM_GAP = 5.0


SOURCES = [
    (OUT_DIR / "renum_m1_src.pdf", "A", 38),   # 38 problem pages
    (OUT_DIR / "renum_m2_src.pdf", "B", 46),
    (OUT_DIR / "renum_m3_src.pdf", "C", 19),
]


def extract_source_text(page: fitz.Page, label_y0: float, label_y1: float) -> str:
    """라벨과 같은 y 행에 그려진 출처 [...] 스팬 추출."""
    d = page.get_text("dict")
    for blk in d['blocks']:
        if blk.get('type') != 0: continue
        for line in blk['lines']:
            for sp in line['spans']:
                t = sp['text']
                if t.startswith('[') and t.rstrip().endswith(']'):
                    # 같은 y 행 (라벨 윗줄 또는 상단 이미지 위치)
                    y = sp['bbox'][1]
                    if label_y0 - 5 <= y <= label_y1 + 5:
                        return t.strip()
    return ""


def extract_problems_from_pdf(src_pdf: Path, prefix: str, n_problem_pages: int) -> list[dict]:
    """라벨 위치 기반으로 각 문제의 클립 좌표 계산."""
    doc = fitz.open(str(src_pdf))
    results = []

    for pi in range(n_problem_pages):
        page = doc[pi]
        # 페이지 내 라벨 모두 수집
        d = page.get_text("dict")
        page_labels = []
        for blk in d['blocks']:
            if blk.get('type') != 0: continue
            for line in blk['lines']:
                for sp in line['spans']:
                    if sp['font'] == LABEL_FONT and abs(sp['size'] - LABEL_SIZE_BIG) < 0.5:
                        t = sp['text'].strip()
                        if t.startswith(prefix + "·"):
                            page_labels.append((sp['bbox'], t))
        page_labels.sort(key=lambda x: x[0][1])

        for i, (bbox, label) in enumerate(page_labels):
            y0_lbl = bbox[1]
            y1_lbl = bbox[3]
            # 본문 클립 y 범위: 라벨/출처 영역 스킵하고 수식부터
            clip_y0 = y0_lbl + CLIP_Y_OFFSET_FROM_LABEL
            if i + 1 < len(page_labels):
                clip_y1 = page_labels[i + 1][0][1] - INTER_PROBLEM_GAP
            else:
                clip_y1 = PAGE_CONTENT_BOTTOM

            # 출처 텍스트
            src_text = extract_source_text(page, y0_lbl, y1_lbl)

            results.append({
                'label': label,
                'src_pdf': str(src_pdf),
                'src_page': pi,
                'clip': (CLIP_X0, clip_y0, CLIP_X1, clip_y1),
                'source_text': src_text,
            })

    doc.close()
    return results


def main():
    all_problems = []
    for src_pdf, prefix, n_pages in SOURCES:
        problems = extract_problems_from_pdf(src_pdf, prefix, n_pages)
        print(f"{src_pdf.name} ({prefix}): {len(problems)} problems")
        all_problems.extend(problems)

    META_JSON.write_text(json.dumps(all_problems, ensure_ascii=False, indent=2),
                         encoding='utf-8')
    print(f"\n[OK] {META_JSON} ({len(all_problems)} problems)")


if __name__ == "__main__":
    main()
