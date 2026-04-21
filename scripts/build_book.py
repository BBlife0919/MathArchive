"""
선정된 문제로 2단 레이아웃 유형서 HTML·PDF 생성.

레이아웃:
- 표지: 제목(큰 글씨) + '이영우T' + 우측 하단 '이음학원 로고'
- 목차 겸 분석 리포트 1페이지
- 본문: 단원 → 유형 별 페이지. 한 페이지에 2단, 단당 1문제.
- 빠른정답 (placeholder, Phase 2에서 채움)
- 해설 (placeholder)

산출물:
- output/book_하.html, output/book_하.pdf
- output/book_중.html, output/book_중.pdf
"""

from __future__ import annotations

import base64
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from playwright.sync_api import sync_playwright

SELECTION = Path("output/crops/selection_diverse.json")
LOGO_PATH = Path("/Users/youngwoolee/Downloads/잡다/이음학원 로고.png")
OUT_DIR = Path("output")

CHAPTER_ORDER = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]

TYPE_ORDER = {
    "다항식의 연산": [
        "다항식의 덧셈·뺄셈",
        "곱셈공식과 곱셈",
        "다항식의 나눗셈·조립제법",
    ],
    "항등식과 나머지정리": [
        "항등식과 미정계수",
        "나머지정리·인수정리",
    ],
    "인수분해": [
        "인수분해 기본",
        "복이차식·치환 인수분해",
        "삼차·고차 인수분해",
    ],
    "복소수": [
        "복소수 상등·사칙연산",
        "켤레복소수",
        "i의 거듭제곱·규칙",
    ],
    "이차방정식": [
        "근의 공식·풀이",
        "판별식·근의 조건",
        "근과 계수의 관계",
        "이차방정식의 작성",
    ],
    "이차함수": [
        "이차함수 그래프·꼭짓점",
        "이차함수 최대·최소",
        "이차함수와 이차방정식",
        "이차함수와 직선",
    ],
}


def img_data_uri(path: Path) -> str:
    b = path.read_bytes()
    return "data:image/png;base64," + base64.b64encode(b).decode("ascii")


CSS = """
@page {
    size: A4;
    margin: 18mm 14mm;
}
@page cover { margin: 0; }
@page toc { margin: 20mm 16mm; }

html { font-family: "AppleSDGothicNeo-Regular", "Apple SD Gothic Neo", "Nanum Gothic", sans-serif; }
body { margin: 0; color: #1a1a1a; }

.cover {
    page: cover;
    height: 297mm;
    position: relative;
    background: linear-gradient(180deg, #0b3b6f 0%, #0e5fa3 100%);
    color: #fff;
    page-break-after: always;
}
.cover .top-band { height: 30mm; }
.cover h1 {
    font-size: 56pt; font-weight: 800; letter-spacing: -1.5px;
    text-align: center; margin: 80mm 0 10mm; line-height: 1.1;
}
.cover .subtitle {
    text-align: center; font-size: 22pt; font-weight: 500;
    color: #f2d37a; letter-spacing: 2px;
}
.cover .diff-badge {
    margin-top: 20mm;
    text-align: center; font-size: 40pt; font-weight: 800;
    color: #fff; border-top: 2px solid rgba(255,255,255,.5);
    border-bottom: 2px solid rgba(255,255,255,.5); padding: 8mm 0;
    width: 80mm; margin-left: auto; margin-right: auto;
}
.cover .instructor {
    position: absolute; left: 20mm; bottom: 20mm;
    font-size: 20pt; font-weight: 700; color: #f2d37a;
}
.cover .instructor small { display: block; font-size: 12pt; color: #cfe0f5; font-weight: 400; margin-top: 2mm; }
.cover .logo-box {
    position: absolute; right: 20mm; bottom: 20mm;
    width: 46mm; height: 46mm; background: #fff;
    border-radius: 6mm; padding: 5mm;
    display: flex; align-items: center; justify-content: center;
}
.cover .logo-box img { max-width: 100%; max-height: 100%; }

.toc {
    page: toc;
    page-break-after: always;
}
.toc h2 { font-size: 22pt; color: #0b3b6f; margin-top: 0; }
.toc table { width: 100%; border-collapse: collapse; font-size: 11pt; }
.toc th { text-align: left; border-bottom: 2px solid #0b3b6f; padding: 6px; background: #e8effa; }
.toc td { border-bottom: 1px solid #d9d9d9; padding: 5px 6px; }
.toc td.chap { font-weight: 700; color: #0b3b6f; }
.toc td.cnt { text-align: right; font-variant-numeric: tabular-nums; }
.toc .intro { margin: 8mm 0; padding: 6mm; background: #f7f9fc; border-left: 4px solid #0b3b6f; font-size: 10.5pt; line-height: 1.6; }

.chapter-title {
    page-break-before: always;
    text-align: center;
    color: #0b3b6f;
    margin: 20mm 0 6mm;
}
.chapter-title .kicker { font-size: 11pt; letter-spacing: 3px; color: #888; }
.chapter-title h2 { font-size: 30pt; margin: 4mm 0; font-weight: 800; }
.chapter-title .rule { width: 40mm; height: 3px; background: #f2a93b; margin: 0 auto; }

.type-header {
    page-break-before: always;
    background: #0b3b6f;
    color: #fff;
    padding: 6mm 8mm;
    margin-bottom: 6mm;
    border-radius: 2mm;
}
.type-header .chap { font-size: 10pt; letter-spacing: 2px; color: #f2d37a; }
.type-header h3 { font-size: 18pt; margin: 2mm 0 0; font-weight: 700; }

.problem-grid {
    column-count: 2;
    column-gap: 8mm;
    column-rule: 1px solid #d9d9d9;
}
.problem-cell {
    break-inside: avoid;
    padding: 4mm 2mm 6mm;
    margin-bottom: 4mm;
    border-bottom: 1px dashed #bbb;
}
.problem-cell:last-child { border-bottom: none; }
.problem-cell .pnum {
    font-size: 11pt; font-weight: 700; color: #0b3b6f;
    margin-bottom: 2mm;
}
.problem-cell img { width: 100%; max-width: 100%; height: auto; display: block; object-fit: contain; }

.section-divider {
    page-break-before: always;
    text-align: center;
    padding: 80mm 0;
    color: #0b3b6f;
}
.section-divider h2 { font-size: 32pt; margin: 0; font-weight: 800; }
.section-divider p { font-size: 12pt; color: #666; margin-top: 4mm; }

.placeholder-note {
    margin: 8mm auto; padding: 10mm;
    border: 2px dashed #aaa; border-radius: 4mm;
    max-width: 140mm; text-align: center; color: #666;
    font-size: 11pt; line-height: 1.8;
}
"""


def build_html(diff: str, items: list[dict], stats_by_chapter_type: dict) -> str:
    logo_uri = img_data_uri(LOGO_PATH) if LOGO_PATH.exists() else ""

    # 표지
    parts = [
        "<!doctype html><html><head><meta charset='utf-8'>",
        "<title>공수1 빈출 유형 정리 FINAL — ",
        diff,
        "난이도</title>",
        f"<style>{CSS}</style></head><body>",
        "<section class='cover'>",
        "<div class='top-band'></div>",
        "<h1>공수1<br/>빈출 유형 정리</h1>",
        "<div class='subtitle'>FINAL</div>",
        f"<div class='diff-badge'>{diff}난이도</div>",
        "<div class='instructor'>이영우 T<small>EUM ACADEMY · 이음학원</small></div>",
    ]
    if logo_uri:
        parts.append(f"<div class='logo-box'><img src='{logo_uri}' /></div>")
    parts.append("</section>")

    # 목차 겸 분석 리포트
    today = date.today().strftime("%Y.%m.%d")
    total = len(items)
    parts.append("<section class='toc'>")
    parts.append(f"<h2>수록 유형 및 문항 수</h2>")
    parts.append(
        f"<div class='intro'>본 교재는 전국 기출 <b>524개 파일 · {total:,}문제({diff}난이도)</b>에서 "
        "빈출 유형을 추출해 공통수학1 교과서 목차 순서로 재배열한 자료입니다. "
        f"분석 기준일: {today}. 유형당 대표 문제 5~12개. 상·킬러 난이도는 의도적으로 제외했습니다.</div>"
    )
    parts.append("<table><thead><tr><th>단원</th><th style='text-align:right'>문항수</th></tr></thead><tbody>")
    for chap in CHAPTER_ORDER:
        c = sum(v for (ch, _t), v in stats_by_chapter_type.items() if ch == chap)
        if c == 0:
            continue
        parts.append("<tr>")
        parts.append(f"<td class='chap'>{chap}</td>")
        parts.append(f"<td class='cnt'>{c}</td>")
        parts.append("</tr>")
    parts.append("</tbody></table>")
    parts.append("</section>")

    # 본문: 단원별로 섹션. 유형 세분화는 생략(현재 자동분류 품질 한계).
    current_chap = None
    cells: list[str] = []
    total_idx = 0

    def flush_grid():
        nonlocal cells
        if cells:
            parts.append("<div class='problem-grid'>")
            parts.extend(cells)
            parts.append("</div>")
            cells = []

    for it in items:
        chap = it["chapter"]
        if chap != current_chap:
            flush_grid()
            parts.append(
                f"<section class='chapter-title'>"
                f"<div class='kicker'>CHAPTER</div>"
                f"<h2>{chap}</h2>"
                f"<div class='rule'></div>"
                f"</section>"
            )
            current_chap = chap
        total_idx += 1
        img_path = Path(it["image_path"])
        uri = img_data_uri(img_path) if img_path.exists() else ""
        cells.append(
            f"<div class='problem-cell'>"
            f"<div class='pnum'>문제 {total_idx:03d}</div>"
            f"<img src='{uri}' alt='문제 이미지' />"
            f"</div>"
        )
    flush_grid()

    # 빠른정답 placeholder
    parts.append(
        "<section class='section-divider'><h2>빠른 정답</h2>"
        "<p>FAST ANSWER KEY</p></section>"
        "<div class='placeholder-note'>"
        "빠른 정답은 원본 PDF의 정답 영역에서 추출해 <b>Phase 2</b>에서 자동 생성됩니다. "
        "(문항 번호 → ①~⑤ 형식)<br/><br/>"
        "오늘 버전은 문항 본문만 포함된 1차 편집본입니다."
        "</div>"
    )

    # 해설 placeholder
    parts.append(
        "<section class='section-divider'><h2>해설</h2>"
        "<p>SOLUTIONS</p></section>"
        "<div class='placeholder-note'>"
        "해설은 원본 PDF 해설 페이지를 문항별로 크롭·매칭해 <b>Phase 2</b>에서 삽입됩니다.<br/><br/>"
        "해설 포함 여부는 원본 PDF마다 다르며, 누락분은 이영우T 직접 작성 또는 HWPX 원본 재변환으로 보완합니다."
        "</div>"
    )

    parts.append("</body></html>")
    return "".join(parts)


def main() -> None:
    sel = json.loads(SELECTION.read_text(encoding="utf-8"))
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for diff in ["하", "중"]:
            items = sel[diff]["items"]
            stats: dict = defaultdict(int)
            for it in items:
                stats[(it["chapter"], it["type"])] += 1
            html_str = build_html(diff, items, stats)
            html_path = OUT_DIR / f"book_{diff}.html"
            pdf_path = OUT_DIR / f"book_{diff}.pdf"
            html_path.write_text(html_str, encoding="utf-8")
            print(f"HTML 저장: {html_path} ({len(items)} 문제)")
            page = browser.new_page()
            page.set_content(html_str, wait_until="load")
            page.pdf(
                path=str(pdf_path),
                format="A4",
                print_background=True,
                margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            )
            page.close()
            print(f"PDF  저장: {pdf_path}  size={pdf_path.stat().st_size/1024:.0f} KB")
        browser.close()


if __name__ == "__main__":
    main()
