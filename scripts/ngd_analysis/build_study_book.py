"""
공수1 빈출 유형 정리 교재 (중/하 분책).

원칙:
- 한 페이지에 한 유형 — 페이지 중복/겹침 금지
- 세련된 한글 폰트 (Apple SD Gothic Neo)
- 수식: KaTeX로 렌더링 (LaTeX inline `$...$`)
- 상단: 유형번호, 유형명, 단원, 난이도, 빈출 강도(★★★/★★/★)
- 본문: 대표 문제 1개 (문항 텍스트 + 선택지 + 출처)
- 하단: "이 유형의 체크포인트" 1~2줄
"""

from __future__ import annotations

import base64
import json
import sqlite3
from pathlib import Path

from playwright.sync_api import sync_playwright

NGD_DIR = Path("/Users/youngwoolee/MathDB/scripts/ngd_analysis")
DB = "/Users/youngwoolee/MathDB/db/mathdb.sqlite"
OUT_DIR = Path("/Users/youngwoolee/MathDB/output/study_book")
OUT_DIR.mkdir(parents=True, exist_ok=True)

CHAPTER_ORDER = [
    "다항식의 연산",
    "항등식과 나머지정리",
    "인수분해",
    "복소수",
    "이차방정식",
    "이차함수",
]

CSS = """
@page { size: A4; margin: 18mm 18mm 18mm 18mm; }
@page cover { margin: 0; }

html {
  font-family: "Apple SD Gothic Neo", "AppleSDGothicNeo-Regular", "Pretendard", "Noto Sans KR", sans-serif;
  font-feature-settings: "ss01" on, "ss02" on;
}
body { margin: 0; color: #1a1a1a; line-height: 1.6; }

/* --- 표지 --- */
.cover {
  page: cover; height: 295mm; position: relative;
  background: linear-gradient(160deg, #103a63 0%, #1d6fb7 60%, #4aa3e0 100%);
  color: #fff; page-break-after: always;
  overflow: hidden;
}
.cover .hairline { position:absolute; top:28mm; left:28mm; right:28mm; height:1px; background:rgba(255,255,255,.35); }
.cover h1 {
  font-size: 56pt; font-weight: 900; letter-spacing: -2px;
  text-align: left; margin: 60mm 28mm 4mm; line-height: 1.05;
}
.cover .subtitle { margin: 0 28mm; font-size: 20pt; font-weight: 500; color: #f3dc8a; letter-spacing: 1px; }
.cover .tagline { margin: 14mm 28mm 0; font-size: 12pt; font-weight: 400; color: #e6f0fb; max-width: 120mm; line-height: 1.7; }
.cover .diff-badge {
  position: absolute; right: 28mm; top: 32mm;
  width: 38mm; text-align: center;
  padding: 5mm 0; font-size: 22pt; font-weight: 800;
  border: 2px solid #f3dc8a; color: #f3dc8a; border-radius: 3mm;
}
.cover .instructor {
  position: absolute; left: 28mm; bottom: 18mm;
  font-size: 16pt; font-weight: 700; color: #f3dc8a;
}
.cover .instructor small { display:block; font-size: 10pt; color: #cfe0f5; font-weight: 400; margin-top: 2mm; letter-spacing: 1px; }
.cover .meta {
  position:absolute; right:28mm; bottom:18mm; text-align:right;
  font-size:9.5pt; color:#cfe0f5;
}

/* --- 목차 --- */
.toc { page-break-after: always; }
.toc h2 { font-size: 22pt; color: #103a63; margin: 0 0 4mm; font-weight: 800; letter-spacing: -0.5px; }
.toc .intro {
  margin-bottom: 10mm; padding: 8mm; background: #f4f8fd;
  border-left: 4px solid #1d6fb7; font-size: 11pt; line-height: 1.7;
}
.toc .chap-block { margin-bottom: 6mm; }
.toc .chap-name { font-size: 13pt; font-weight: 800; color: #103a63; border-bottom: 2px solid #103a63; padding-bottom: 2mm; margin-bottom: 3mm; }
.toc ul { list-style: none; padding: 0; margin: 0; }
.toc li { padding: 2mm 0; font-size: 10.5pt; display: flex; justify-content: space-between; border-bottom: 1px dotted #c7d3e6; }
.toc li .name { flex: 1; }
.toc li .freq { color: #666; font-variant-numeric: tabular-nums; margin-left: 6mm; }

/* --- 유형 페이지 --- */
.type-page {
  page-break-before: always;
  padding: 0;
  display: flex; flex-direction: column; min-height: 260mm;
}
.type-head {
  border-top: 3px solid #103a63; border-bottom: 1px solid #103a63;
  padding: 4mm 0 3mm; margin-bottom: 6mm;
}
.type-head .kicker {
  font-size: 10pt; color: #1d6fb7; font-weight: 700; letter-spacing: 2px; text-transform: uppercase;
}
.type-head .title-row { display: flex; align-items: baseline; gap: 6mm; margin-top: 2mm; }
.type-head .tid {
  font-size: 22pt; font-weight: 900; color: #103a63; min-width: 24mm;
}
.type-head .tname {
  font-size: 17pt; font-weight: 800; color: #1a1a1a; letter-spacing: -0.3px;
}
.type-head .tags { margin-top: 2mm; font-size: 10pt; color: #555; display: flex; gap: 4mm; }
.type-head .tag {
  background: #eef3fa; color: #103a63; padding: 1mm 3mm; border-radius: 2mm; font-weight: 600;
}
.type-head .freq { color: #c06000; }

.checkpoint {
  background: #fffaf0; border-left: 3px solid #f0a83b;
  padding: 3mm 5mm; font-size: 10.5pt; line-height: 1.6; color: #5a4218;
  margin-bottom: 8mm;
}
.checkpoint b { color: #c06000; }

.problem {
  flex-grow: 1;
  padding: 2mm 0;
}
.problem .q-prompt {
  font-size: 13pt; line-height: 1.85; margin-bottom: 6mm;
}
.problem .choices {
  font-size: 12pt; line-height: 2.0;
  columns: 1; column-gap: 8mm;
  padding-left: 4mm;
}
.problem .choices .ch-row { display: flex; gap: 3mm; }
.problem .choices .circ { color: #1d6fb7; font-weight: 700; min-width: 5mm; }

.problem-footer {
  margin-top: auto; padding-top: 6mm; border-top: 1px dashed #c7d3e6;
  display: flex; justify-content: space-between;
  font-size: 9.5pt; color: #888;
}

/* 구분 섹션 */
.chapter-divider {
  page-break-before: always;
  height: 260mm;
  display: flex; align-items: center; justify-content: center;
  flex-direction: column;
}
.chapter-divider .kicker { font-size: 11pt; letter-spacing: 4px; color: #888; font-weight: 600; }
.chapter-divider h2 { font-size: 40pt; font-weight: 900; color: #103a63; letter-spacing: -1px; margin: 6mm 0; }
.chapter-divider .rule { width: 60mm; height: 4px; background: #f0a83b; }

/* KaTeX inline 조정 */
.katex { font-size: 1em; }
"""


def load_katex_inline() -> tuple[str, str]:
    """KaTeX CSS/JS를 base64로 인라인화해서 오프라인 렌더 보장."""
    return "", ""  # playwright로 처리 — head에 CDN 사용


def render_problem_text(qtext: str) -> str:
    """MathDB의 question_text는 `$...$` LaTeX 포함. HTML-safe하게."""
    # 개행은 <br>로
    import html as htmllib
    out = []
    for ln in qtext.split("\n"):
        out.append(htmllib.escape(ln))
    return "<br>".join(out)


def build_html(diff: str, type_pages: list[dict]) -> str:
    head = f"""<!doctype html><html><head><meta charset='utf-8'>
<title>공수1 3일 완성 기본 {diff}난이도 유형</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
  onload="renderMathInElement(document.body, {{delimiters: [{{left:'$',right:'$',display:false}}, {{left:'\\\\[',right:'\\\\]',display:true}}]}})">
</script>
<style>{CSS}</style></head><body>"""

    # 표지
    tagline = (
        "30~50점대 학생을 위한<br>3일 벼락치기 기본 유형 교재.<br>"
        "시험 직전에 <b>무조건 이거 한 권</b>만 풀면 된다."
    )
    parts = [
        head,
        "<section class='cover'>",
        "<div class='hairline'></div>",
        f"<div class='diff-badge'>{diff}난이도</div>",
        "<h1>공수1<br/>기본 유형<br/>50 FINAL</h1>",
        "<div class='subtitle'>3日 完成 · BASIC</div>",
        f"<div class='tagline'>{tagline}</div>",
        "<div class='instructor'>이영우 T<small>EUM ACADEMY · 이음학원</small></div>",
        "<div class='meta'>광명시 고1 1학기 중간 기출 분석 · NGD 전국단위기출 기반</div>",
        "</section>",
    ]

    # 목차
    parts.append("<section class='toc'>")
    parts.append(f"<h2>이 책을 쓰는 법 — {diff}난이도</h2>")
    parts.append(
        "<div class='intro'>"
        "총 <b>" + str(len(type_pages)) + "개 핵심 유형</b>을 단원 순서로 배치했습니다. "
        "한 페이지에 한 유형, 오른쪽 상단의 '빈출 강도 ★ 수'가 시험장 출현 빈도입니다. "
        "시간이 없다면 ★★★ 유형만 먼저 훑으세요. "
        "각 페이지 맨 위 '체크포인트'를 먼저 읽고 대표 문제를 풀면, 이 유형이 왜 그렇게 풀리는지 감이 옵니다."
        "</div>"
    )
    for chap in CHAPTER_ORDER:
        in_chap = [p for p in type_pages if p["chapter"] == chap]
        if not in_chap:
            continue
        parts.append("<div class='chap-block'>")
        parts.append(f"<div class='chap-name'>{chap}</div>")
        parts.append("<ul>")
        for p in in_chap:
            freq = "★" * p.get("stars", 1)
            parts.append(
                f"<li><span class='name'>{p['tid']}. {p['label']}</span>"
                f"<span class='freq'>{freq} · {p['count']}문항</span></li>"
            )
        parts.append("</ul></div>")
    parts.append("</section>")

    # 본문 페이지
    current_chap = None
    for p in type_pages:
        if p["chapter"] != current_chap:
            # chapter divider
            parts.append(
                "<section class='chapter-divider'>"
                "<div class='kicker'>CHAPTER</div>"
                f"<h2>{p['chapter']}</h2>"
                "<div class='rule'></div>"
                "</section>"
            )
            current_chap = p["chapter"]

        stars = "★" * p.get("stars", 1)
        parts.append("<section class='type-page'>")
        parts.append("<div class='type-head'>")
        parts.append(f"<div class='kicker'>TYPE {p['tid']}</div>")
        parts.append(
            f"<div class='title-row'><div class='tid'>{p['tid']}</div>"
            f"<div class='tname'>{p['label']}</div></div>"
        )
        parts.append(
            f"<div class='tags'>"
            f"<span class='tag'>{p['chapter']}</span>"
            f"<span class='tag'>{diff}난이도</span>"
            f"<span class='tag freq'>빈출 {stars}</span>"
            f"<span class='tag'>모집단 {p['count']}문항</span>"
            f"</div>"
        )
        parts.append("</div>")

        parts.append(
            "<div class='checkpoint'>"
            f"<b>체크포인트</b> — {p.get('checkpoint', p.get('cue', ''))}"
            "</div>"
        )

        parts.append("<div class='problem'>")
        parts.append(f"<div class='q-prompt'>{render_problem_text(p['question_text'])}</div>")
        choices = p.get("choices") or []
        if choices:
            parts.append("<div class='choices'>")
            for i, ch in enumerate(choices, 1):
                circ = "①②③④⑤⑥⑦"[i - 1] if i <= 7 else str(i)
                ch_text = ch.get("text", "") if isinstance(ch, dict) else str(ch)
                ch_html = render_problem_text(ch_text) if ch_text else ""
                parts.append(f"<div class='ch-row'><div class='circ'>{circ}</div><div>{ch_html}</div></div>")
            parts.append("</div>")
        parts.append("</div>")

        src = p.get("source_short", "")
        ans = p.get("answer", "")
        parts.append(
            "<div class='problem-footer'>"
            f"<div>출처 · {src}</div>"
            f"<div>정답 {ans}</div>"
            "</div>"
        )
        parts.append("</section>")

    parts.append("</body></html>")
    return "".join(parts)


def html_to_pdf(html: str, out_path: Path) -> None:
    html_path = out_path.with_suffix(".html")
    html_path.write_text(html)
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(f"file://{html_path}")
        # KaTeX 렌더 대기
        page.wait_for_timeout(1800)
        page.pdf(
            path=str(out_path),
            format="A4",
            print_background=True,
            margin={"top": "0", "right": "0", "bottom": "0", "left": "0"},
            prefer_css_page_size=True,
        )
        browser.close()
    print(f"wrote {out_path}")


def build(diff: str, type_pages: list[dict]) -> None:
    html = build_html(diff, type_pages)
    out = OUT_DIR / f"study_book_{diff}.pdf"
    html_to_pdf(html, out)
