"""20개 교재를 페이지 단위로 PNG 렌더 + OCR 텍스트 추출.

페이지 단위 매칭이 가장 안정적: 교재마다 문제 구분자가 달라 자동 분리는 까다롭지만
페이지는 항상 명확함. 사용자 보고서엔 "교재명 + 페이지" 까지 정확히 표기.
"""
from __future__ import annotations
import json
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
import fitz

ROOT = Path('/Users/youngwoolee/MathDB/output/textbook_match_v3')
PNG_DIR = ROOT / 'pages_png'
OCR_DIR = ROOT / 'pages_ocr'

# 교재 메타 — short 코드는 보고서 출력에 사용
TEXTBOOKS = [
    {'key': 'baekbal',     'short': '100발100중',  'label': '100발100중 대수(상)',           'path': '/Users/youngwoolee/Downloads/수특수완/(2022개정)100발100중 대수(상).pdf'},
    {'key': 'op_high',     'short': '올림고난도',   'label': 'EBS 올림포스 고난도 대수',     'path': '/Users/youngwoolee/Downloads/수특수완/[22개정][EBS 올림포스 고난도] 대수 본문[스캔본].pdf'},
    {'key': 'ilpum',       'short': '일품',         'label': '일품 대수',                      'path': '/Users/youngwoolee/Downloads/수특수완/22개정 일품 대수 문제.pdf'},
    {'key': '1grade494',   'short': '1등급494',     'label': '1등급 만들기 대수 494제',       'path': '/Users/youngwoolee/Downloads/수특수완/22개정_1등급_만들기_대수_494제 .pdf'},
    {'key': 'mt_su1',      'short': '마더텅수1',    'label': '마더텅 고3 수학1 (2026)',       'path': '/Users/youngwoolee/Downloads/수특수완/2026 마더텅 고3 수학 1 .pdf'},
    {'key': 'sw_2026',     'short': '수능완성',     'label': '수능완성 수학 (수1·수2) 2026', 'path': '/Users/youngwoolee/Downloads/수특수완/2026 수능완성 수학 (수1,수2).pdf'},
    {'key': 'op_main',     'short': '올림포스',     'label': 'EBS 올림포스 대수 본문 2026', 'path': '/Users/youngwoolee/Downloads/수특수완/2026－EBS－올림포스－대수－본문－원본PDF.pdf'},
    {'key': 'st_su1_2027', 'short': '수특I27',     'label': '수능특강 수학 I 2027',          'path': '/Users/youngwoolee/Downloads/수특수완/2027 수능특강 수학 I.pdf'},
    {'key': 'gozaengi',    'short': '고쟁이',       'label': '고쟁이 대수',                    'path': '/Users/youngwoolee/Downloads/수특수완/고쟁이 대수.pdf'},
    {'key': 'mirae_text',  'short': '미래엔교과서', 'label': '미래엔 대수 교과서',             'path': '/Users/youngwoolee/Downloads/수특수완/미래엔_대수_교과서(정답포함).pdf'},
    {'key': 'st_2026',     'short': '수특26',       'label': '수능특강 수1 2026',              'path': '/Users/youngwoolee/Downloads/수특수완/수1 2026 수특.pdf'},
    {'key': 'jeongseok_b', 'short': '정석기본',     'label': '수학의 정석 기본편 대수',        'path': '/Users/youngwoolee/Downloads/수특수완/수학의 정석 (기본편) 고등 대수.pdf'},
    {'key': 'jeongseok_p', 'short': '정석실력',     'label': '수학의 정석 실력편 대수',        'path': '/Users/youngwoolee/Downloads/수특수완/수학의 정석 (실력편) 고등 대수.pdf'},
    {'key': 'ssen',        'short': '쎈',           'label': '쎈수학 대수 (2022개정)',         'path': '/Users/youngwoolee/Downloads/수특수완/쎈수학 대수 (2022개정).pdf'},
    {'key': 'ybm_text',    'short': 'YBM교과서',    'label': '와이비엠(류희찬) 대수 교과서',  'path': '/Users/youngwoolee/Downloads/수특수완/와이비엠(류희찬)_대수_교과서.pdf'},
    {'key': 'yuhyung1',    'short': '유형ON1',     'label': '유형ON 대수 1권 교사용',        'path': '/Users/youngwoolee/Downloads/수특수완/유혀ㅇON_대수_1권_본책(교사용).pdf'},
    {'key': 'yuhyung2',    'short': '유형ON2',     'label': '유형ON 대수 2권 교사용',        'path': '/Users/youngwoolee/Downloads/수특수완/유혀ㅇON_대수_2권_본책(교사용).pdf'},
    {'key': 'cheonjae',    'short': '천재교과서',   'label': '천재(전) 대수 교과서',           'path': '/Users/youngwoolee/Downloads/수특수완/천재(전)_대수.pdf'},
    {'key': 'op_yulhap',   'short': '올림전국연합', 'label': 'EBS 올림포스 전국연합 대수 2026', 'path': '/Users/youngwoolee/Downloads/수특수완/EBS 올림포스 전국연합 대수 2026 본문.pdf'},
    {'key': 'op_type',     'short': '올림유형',     'label': 'EBS 올림포스 유형편 대수',       'path': '/Users/youngwoolee/Downloads/수특수완/EBS_올림포스_유형편_대수.pdf'},
]


def render_pages(meta: dict, dpi: int = 130) -> int:
    """교재 모든 페이지를 PNG로 렌더링."""
    out_dir = PNG_DIR / meta['key']
    out_dir.mkdir(parents=True, exist_ok=True)
    doc = fitz.open(meta['path'])
    n = doc.page_count
    for i in range(n):
        out = out_dir / f'p{i+1:04d}.png'
        if out.exists():
            continue
        p = doc.load_page(i)
        pm = p.get_pixmap(dpi=dpi)
        pm.save(str(out))
    doc.close()
    return n


def ocr_page(png_path: Path, has_text_layer: bool, pdf_path: str | None, page_idx: int | None) -> str:
    """페이지 텍스트 추출 — text layer 있으면 PDF에서, 없으면 tesseract OCR."""
    if has_text_layer and pdf_path is not None and page_idx is not None:
        doc = fitz.open(pdf_path)
        t = doc.load_page(page_idx).get_text()
        doc.close()
        return t
    # OCR
    res = subprocess.run(
        ['tesseract', str(png_path), '-', '-l', 'kor+eng', '--psm', '6'],
        capture_output=True, text=True, timeout=90
    )
    return res.stdout


def index_textbook(meta: dict) -> dict:
    """한 교재를 페이지 단위로 인덱싱."""
    out_dir = OCR_DIR / meta['key']
    out_dir.mkdir(parents=True, exist_ok=True)
    cache = out_dir / 'pages.json'
    if cache.exists():
        return json.loads(cache.read_text())

    doc = fitz.open(meta['path'])
    n = doc.page_count
    # 텍스트 레이어 여부 (몇 페이지 샘플)
    samples = [doc.load_page(i).get_text() for i in range(min(5, n))]
    has_layer = sum(len(s) for s in samples) > 500
    doc.close()

    png_dir = PNG_DIR / meta['key']
    pages = []
    def task(i: int) -> tuple[int, str]:
        png = png_dir / f'p{i+1:04d}.png'
        text = ocr_page(png, has_layer, meta['path'], i)
        return i, text
    with ThreadPoolExecutor(max_workers=6) as ex:
        futures = [ex.submit(task, i) for i in range(n)]
        for f in as_completed(futures):
            i, t = f.result()
            pages.append({'page': i + 1, 'text': t})
    pages.sort(key=lambda x: x['page'])

    out = {'meta': meta, 'has_text_layer': has_layer, 'pages': pages}
    cache.write_text(json.dumps(out, ensure_ascii=False))
    return out


def main():
    # 1) 모든 페이지 렌더링 (병렬 교재, 직렬 페이지)
    total_pages = 0
    print('=== 페이지 렌더링 ===')
    with ThreadPoolExecutor(max_workers=4) as ex:
        futures = {ex.submit(render_pages, m): m for m in TEXTBOOKS}
        for f in as_completed(futures):
            m = futures[f]
            n = f.result()
            total_pages += n
            print(f'  rendered {m["short"]:12s}  {n:4d}p')
    print(f'  total: {total_pages}p')

    # 2) 인덱싱 (페이지 OCR)
    print('\n=== 페이지 OCR/텍스트 추출 ===')
    for m in TEXTBOOKS:
        idx = index_textbook(m)
        layer = 'TEXT' if idx['has_text_layer'] else 'OCR'
        print(f'  {layer}  {m["short"]:12s}  {len(idx["pages"]):4d}p')

    print('\n인덱싱 완료. 다음: 시험문제 추출 → 매칭')


if __name__ == '__main__':
    main()
