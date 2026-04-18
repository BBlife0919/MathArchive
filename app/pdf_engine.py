"""시험지·교재 PDF 생성 엔진 (Playwright + KaTeX).

설계:
- 문제 텍스트 → HTML 변환 (수식 `$...$`은 placeholder로 격리 후 복원)
- 2단 레이아웃: 한 단에 최대 2문제(반/반), 긴 문제·상 난이도는 단 전체 차지
- 배치 로직: Python에서 "열(column) 단위"로 문제를 패킹한 뒤 2열씩 페이지 구성
"""
from __future__ import annotations

import base64
import io
import json
import mimetypes
import re
import html as _html
from pathlib import Path
from typing import Iterable

import markdown as _md
from playwright.sync_api import sync_playwright


EXAM_TYPE_KO = {"a": "중간", "b": "기말"}


# ── 출처 포맷 ───────────────────────────────────────────────
def format_source(q: dict, include_difficulty: bool = False) -> str:
    """출처 메타 문자열.

    include_difficulty=True → 교재 모드. `[상] [가림고] 2025년 1학기 중간 1번`
    False → 시험지 모드. 난이도 prefix 없음.
    """
    exam = EXAM_TYPE_KO.get(q.get("exam_type"), q.get("exam_type") or "")
    parts: list[str] = []
    if include_difficulty and q.get("difficulty"):
        parts.append(f"[{q['difficulty']}]")
    parts.append(f"[{q.get('school', '?')}]")
    if q.get("year") and q.get("semester"):
        parts.append(f"{q['year']}년 {q['semester']}학기")
    if exam:
        parts.append(exam)
    parts.append(f"{q.get('question_number', '')}번")
    return " ".join(parts)


def format_choices(choices_json) -> str:
    if not choices_json:
        return ""
    if isinstance(choices_json, str):
        try:
            choices = json.loads(choices_json)
        except Exception:
            return ""
    else:
        choices = choices_json
    if not choices:
        return ""
    circle = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}
    return "&nbsp;&nbsp;&nbsp;".join(
        f"{circle.get(c.get('number'), c.get('number'))} {c.get('text', '')}"
        for c in choices
    )


# ── HTML-safe 변환 (수식 보호) ────────────────────────────
def _escape_pseudo_tags(s: str) -> str:
    """`<보기>` 같이 실제 HTML 태그가 아닌 꺾쇠를 escape."""
    return re.sub(r"<(?!/?[a-zA-Z])", "&lt;", s)


def _with_math_protected(text: str, transform) -> str:
    """$...$ 수식을 placeholder로 격리한 채 transform 적용 후 복원.

    수식 안의 `_`, `<`, `\\` 등이 Markdown·HTML escape에 휩쓸리는 것 차단.
    """
    maths: list[str] = []

    def _ph(i):
        return f"@XMATHX{i}@"

    def _stash(m):
        maths.append(m.group(0))
        return _ph(len(maths) - 1)

    stashed = re.sub(r"\$[^$\n]+?\$", _stash, text)
    rendered = transform(stashed)
    for i, m in enumerate(maths):
        rendered = rendered.replace(_ph(i), m)
    return rendered


def _render_box_content(body: str) -> str:
    """박스 내부 Markdown → HTML. 수식은 placeholder 격리로 보호."""
    body = body.strip()

    def _md_transform(s):
        s = _escape_pseudo_tags(s)
        return _md.markdown(s, extensions=["tables", "nl2br"])

    rendered = _with_math_protected(body, _md_transform)
    # 빈 셀만 있는 행 제거
    rendered = re.sub(r"<tr>(?:\s*<t[dh][^>]*>\s*</t[dh]>\s*)+</tr>", "", rendered)
    TABLE_STYLE = "border-collapse:collapse; width:auto; margin:0 auto;"
    rendered = rendered.replace("<table>", f'<table style="{TABLE_STYLE}">')
    rendered = re.sub(
        r"<(td|th)>",
        r'<\1 style="border:1px solid #ddd; padding:4pt 8pt;">',
        rendered,
    )
    return rendered


def _process_boxes(text: str) -> str:
    """<<BOX_START>>...<<BOX_END>> 블록을 HTML 박스로 변환."""
    def _repl(m):
        return f'<div class="cond-box">{_render_box_content(m.group(1))}</div>'
    return re.sub(r"<<BOX_START>>(.*?)<<BOX_END>>", _repl, text, flags=re.DOTALL)


def render_question_body(text: str) -> str:
    """문제 본문 텍스트 → HTML. 박스·수식 보호된 상태."""
    text = re.sub(r"<<IMG:image\d+>>", "[그림]", text)
    text = re.sub(r"\n{2,}", "\n\n", text)

    parts: list[str] = []
    last = 0

    def _plain(s):
        return _with_math_protected(
            s, lambda x: _escape_pseudo_tags(x).replace("\n", "<br>")
        )

    for m in re.finditer(r"<<BOX_START>>(.*?)<<BOX_END>>", text, re.DOTALL):
        pre = text[last:m.start()]
        if pre:
            parts.append(_plain(pre))
        parts.append(f'<div class="cond-box">{_render_box_content(m.group(1))}</div>')
        last = m.end()
    post = text[last:]
    if post:
        parts.append(_plain(post))
    html = "".join(parts)
    # <br> 스팸 정리
    html = re.sub(r'(?:<br>\s*){2,}(<div class="cond-box">)', r'<br>\1', html)
    html = re.sub(r'(</div>)(?:\s*<br>){2,}', r'\1<br>', html)
    return html


# ── 길이 판정 (단 1/2 칸 vs 단 전체) ────────────────────────
def estimate_layout(q: dict, force_full: bool = False) -> str:
    """'half' (단의 절반) 또는 'full' (단 하나를 통째로)."""
    if force_full:
        return "full"
    if q.get("difficulty") in ("상", "킬"):
        return "full"
    text = q.get("question_text") or ""
    char_count = len(re.sub(r"\$[^$]+\$", "#", text))  # 수식은 1자로 축약 후 세기
    score = char_count
    if "<<BOX_START>>" in text:
        score += 200
    if "<<IMG:" in text:
        score += 300
    # 보수적 임계값: Streamlit 단 폭 기준 약 400자가 전체 폭의 절반 높이 수준
    return "full" if score > 400 else "half"


# ── 페이지·단 패킹 ───────────────────────────────────────
def paginate(questions: list[dict], overrides: dict[int, str] | None = None) -> list[list[list[tuple[dict, str]]]]:
    """문제를 [page][col][slot=(q, layout)] 구조로 패킹.

    각 page는 최대 2열, 각 열은 최대 weight 2 (half=1, full=2).
    overrides: question_id → 'half'/'full' 강제 지정.
    """
    overrides = overrides or {}
    pages: list = []
    current_page: list = []
    current_col: list = []
    col_weight = 0

    def _flush_col():
        nonlocal current_col, col_weight, current_page
        if current_col:
            current_page.append(current_col)
            current_col = []
            col_weight = 0

    def _flush_page():
        nonlocal current_page
        _flush_col()
        if current_page:
            pages.append(current_page)
            current_page = []

    for q in questions:
        qid = q.get("question_id")
        force = overrides.get(qid)
        layout = estimate_layout(q, force_full=(force == "full"))
        if force == "half":
            layout = "half"
        weight = 2 if layout == "full" else 1
        if col_weight + weight > 2:
            _flush_col()
            if len(current_page) >= 2:
                _flush_page()
        current_col.append((q, layout))
        col_weight += weight
    _flush_page()
    return pages


# ── HTML 템플릿 ─────────────────────────────────────────────
_CSS = r"""
@page { size: A4; margin: 15mm 12mm; }
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: -apple-system, 'Apple SD Gothic Neo', 'Nanum Gothic', 'Noto Sans KR', sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #111;
}
.page {
    min-height: 267mm;
    display: flex;
    flex-direction: column;
    page-break-after: always;
}
.page:last-child { page-break-after: auto; }
.exam-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin: 0 0 7mm 0;
    padding: 0 0 4mm 0;
    border-bottom: 2.5px solid #222;
    gap: 6mm;
}
.exam-header .title-block {
    flex: 1;
    text-align: center;
}
.exam-header.has-logo .title-block {
    text-align: left;
}
h1.exam-title {
    font-size: 28pt;
    font-weight: 800;
    margin: 0;
    letter-spacing: -0.5px;
    line-height: 1.15;
}
h2.exam-subtitle {
    font-size: 13pt;
    font-weight: 500;
    color: #666;
    margin: 2mm 0 0 0;
    line-height: 1.2;
}
.exam-logo {
    max-height: 20mm;
    max-width: 45mm;
    object-fit: contain;
    flex-shrink: 0;
}
.page-body {
    flex: 1;
    display: flex;
    gap: 6mm;
}
.col {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 5mm;
}
.slot {
    flex: 1;
    overflow: hidden;
    padding-right: 2mm;
    border-right: 1px dashed #e0e0e0;
}
.col:last-child .slot { border-right: none; padding-right: 0; }
.slot.full { flex: 1 1 100%; }
.q-header {
    font-weight: 700;
    margin: 0 0 2mm 0;
    font-size: 10pt;
}
.q-meta {
    color: #999;
    font-size: 8.5pt;
    font-weight: 400;
    margin-left: 4pt;
}
.q-body { margin: 0 0 2mm 0; }
.q-choices {
    margin-top: 6mm;  /* 본문과 선지 사이 한 줄 띄운 느낌 */
    color: #222;
    font-size: 10pt;
}
.cond-box {
    border: 1px solid #ccc;
    background: #fbfbfb;
    padding: 5pt 10pt;
    margin: 3pt 0;
    border-radius: 2pt;
}
.cond-box p { margin: 2pt 0; }
.cond-box p:first-child { margin-top: 0; }
.cond-box p:last-child { margin-bottom: 0; }
.katex { font-size: 1.02em !important; }
.katex-display { margin: 0.4em 0 !important; }
"""

_HTML_WRAP = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
 onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],throwOnError:false}}); window.__katexReady=true;"></script>
<style>{css}</style>
</head><body>
{body}
</body></html>
"""


def _render_slot(i: int, q: dict, layout: str, include_source: bool,
                  include_difficulty: bool = False) -> str:
    """문항 슬롯 HTML.

    배점은 파서가 본문 꼬리에 이미 `[N점]` 형태로 삽입하므로
    헤더에서는 중복 제거 (`N번 [출처]`만).
    """
    meta = (
        f'<span class="q-meta">{format_source(q, include_difficulty)}</span>'
        if include_source else ""
    )
    body_html = render_question_body(q.get("question_text") or "")
    choices_html = format_choices(q.get("choices"))
    return (
        f'<div class="slot {layout}">'
        f'<div class="q-header">{i}번{meta}</div>'
        f'<div class="q-body">{body_html}</div>'
        + (f'<div class="q-choices">{choices_html}</div>' if choices_html else "")
        + '</div>'
    )


def _logo_data_uri(logo_path: str | Path | None) -> str | None:
    """로고 파일을 base64 data URI로 인코딩.

    Playwright는 `page.set_content()`으로 HTML을 inline 주입하므로,
    상대경로/파일경로 이미지를 안정적으로 참조하려면 data URI가 가장 확실.
    """
    if not logo_path:
        return None
    p = Path(logo_path)
    if not p.exists():
        return None
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _render_header(title: str, subtitle: str | None, logo_uri: str | None) -> str:
    has_logo = bool(logo_uri)
    cls = "exam-header has-logo" if has_logo else "exam-header"
    title_html = f'<h1 class="exam-title">{_html.escape(title)}</h1>'
    sub_html = (
        f'<h2 class="exam-subtitle">{_html.escape(subtitle)}</h2>'
        if subtitle else ""
    )
    logo_html = (
        f'<img class="exam-logo" src="{logo_uri}" alt="logo">' if has_logo else ""
    )
    return (
        f'<header class="{cls}">'
        f'<div class="title-block">{title_html}{sub_html}</div>'
        f'{logo_html}'
        f'</header>'
    )


def build_exam_html(questions: list[dict], title: str, include_source: bool,
                     overrides: dict | None = None,
                     subtitle: str | None = None,
                     logo_path: str | Path | None = None,
                     include_difficulty: bool = False) -> str:
    pages = paginate(questions, overrides=overrides)
    logo_uri = _logo_data_uri(logo_path)
    body_parts: list[str] = []
    slot_num = 1
    for idx, page in enumerate(pages):
        body_parts.append('<section class="page">')
        if idx == 0:
            body_parts.append(_render_header(title, subtitle, logo_uri))
        body_parts.append('<div class="page-body">')
        # 모든 페이지는 2단 유지 — col 수가 부족하면 빈 col placeholder로 채움
        # (마지막 페이지에 문제가 적어서 단이 하나만 그려지는 버그 방지)
        cols = list(page)
        while len(cols) < 2:
            cols.append([])
        for col in cols:
            body_parts.append('<div class="col">')
            for (q, layout) in col:
                body_parts.append(_render_slot(
                    slot_num, q, layout, include_source, include_difficulty
                ))
                slot_num += 1
            body_parts.append('</div>')
        body_parts.append('</div>')  # page-body
        body_parts.append('</section>')
    return _HTML_WRAP.format(title=_html.escape(title), css=_CSS, body="\n".join(body_parts))


# ── Playwright 실행 ──────────────────────────────────────
import os
import subprocess


def _launch_browser(p):
    """Playwright 기본 번들 실패 시 시스템 chromium으로 폴백.

    Streamlit Cloud는 `chromium` apt 패키지만 제공하므로
    `/usr/bin/chromium` 경로를 executable_path로 지정.
    """
    try:
        return p.chromium.launch()
    except Exception:
        for candidate in ("/usr/bin/chromium", "/usr/bin/chromium-browser"):
            if os.path.exists(candidate):
                return p.chromium.launch(executable_path=candidate)
        # 마지막 시도: playwright install을 런타임에 (첫 실행 시 100MB 다운로드)
        try:
            subprocess.run(
                ["playwright", "install", "chromium"],
                check=False, timeout=180
            )
            return p.chromium.launch()
        except Exception as e:
            raise RuntimeError(f"Chromium 실행 실패: {e}")


def html_to_pdf_bytes(html: str) -> bytes:
    """HTML을 Playwright+Chromium으로 PDF 바이트 변환."""
    with sync_playwright() as p:
        browser = _launch_browser(p)
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        try:
            page.wait_for_function("window.__katexReady === true", timeout=10000)
        except Exception:
            pass
        pdf_bytes = page.pdf(
            format="A4",
            print_background=True,
            margin={"top": "15mm", "bottom": "15mm", "left": "12mm", "right": "12mm"},
            prefer_css_page_size=True,
        )
        browser.close()
        return pdf_bytes


def generate_exam_pdf(questions: list[dict], title: str = "수학 시험지",
                      include_source: bool = True,
                      overrides: dict | None = None,
                      subtitle: str | None = None,
                      logo_path: str | Path | None = None,
                      include_difficulty: bool = False) -> bytes:
    html = build_exam_html(
        questions, title, include_source, overrides=overrides,
        subtitle=subtitle, logo_path=logo_path,
        include_difficulty=include_difficulty,
    )
    return html_to_pdf_bytes(html)
