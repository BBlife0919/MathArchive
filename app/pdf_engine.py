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


def format_choices(choices_json, book_mode: bool = False) -> str:
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
    if book_mode:
        # 가로 flex — .q-choices 의 gap으로 간격 조정
        return "".join(
            f'<span class="choice">'
            f'<span class="circ">{circle.get(c.get("number"), c.get("number"))}</span>'
            f'{c.get("text", "")}'
            f'</span>'
            for c in choices
        )
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
@page { size: A4; margin: 10mm 10mm; }
* { box-sizing: border-box; }
body {
    margin: 0;
    font-family: 'Pretendard', 'Pretendard Variable', -apple-system, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    font-size: 10.5pt;
    line-height: 1.5;
    color: #111;
    -webkit-font-smoothing: antialiased;
}
.page {
    min-height: 275mm;
    display: flex;
    flex-direction: column;
    page-break-after: always;
}
.page:last-child { page-break-after: auto; }
.exam-header {
    position: relative;
    display: flex;
    align-items: flex-end;
    justify-content: space-between;
    margin: 3mm 0 12mm 0;
    padding: 0 0 7mm 0;
    gap: 6mm;
    min-height: 34mm;
}
/* 굵은 포인트 바 (Toss/당근 감성) */
.exam-header::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 16mm;
    height: 5px;
    background: #ff6b35;
    border-radius: 100px;
}
.exam-header .title-block {
    flex: 1;
    text-align: left;
}
.exam-header .kicker {
    font-size: 9pt;
    color: #999;
    font-weight: 600;
    letter-spacing: 1.5px;
    margin: 0 0 4.5mm 0;
    display: block;
}
.exam-header .kicker .mark {
    color: #ff6b35;
    font-weight: 800;
    margin-right: 2.5mm;
    letter-spacing: 0;
}
h1.exam-title {
    font-size: 30pt;
    font-weight: 700;
    margin: 0;
    letter-spacing: -1.2px;
    line-height: 1.08;
    color: #0a0a0a;
}
h2.exam-subtitle {
    font-size: 12pt;
    font-weight: 500;
    color: #666;
    margin: 3.5mm 0 0 0;
    line-height: 1.3;
    letter-spacing: -0.3px;
}
.exam-logo {
    max-height: 22mm;
    max-width: 48mm;
    object-fit: contain;
    flex-shrink: 0;
    align-self: flex-start;
}
.page-body {
    flex: 1;
    display: flex;
    gap: 4mm;
}
.col {
    flex: 1;
    min-width: 0;
    display: flex;
    flex-direction: column;
    gap: 3mm;
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

/* ── 교재 전용 스타일 ─────────────────────── */
.section-title {
    font-size: 22pt;
    font-weight: 800;
    margin: 0 0 6mm 0;
    padding-bottom: 3mm;
    border-bottom: 2px solid #103a63;
    color: #103a63;
    letter-spacing: -0.5px;
}
/* 교재 모드 문항 카드 — CC 스타일 차용 */
.slot.book-card {
    border-top: 2px solid #103a63;
    padding-top: 2mm;
}
.slot.book-card .book-header {
    padding-bottom: 1.5mm;
    margin-bottom: 2mm;
    border-bottom: 1px solid #e5e5e5;
}
.slot.book-card .q-number {
    font-size: 15pt;
    font-weight: 900;
    color: #103a63;
    letter-spacing: -0.5px;
    display: inline-block;
    margin-right: 3mm;
    vertical-align: baseline;
}
.slot.book-card .q-kicker {
    font-size: 7.5pt;
    color: #1d6fb7;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5mm;
    display: block;
}
.slot.book-card .q-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5mm;
    margin-top: 1.8mm;
    font-size: 8pt;
}
.slot.book-card .q-tag {
    background: #eef3fa;
    color: #103a63;
    padding: 0.8mm 2.2mm;
    border-radius: 2mm;
    font-weight: 600;
    font-size: 8pt;
    white-space: nowrap;
}
.slot.book-card .q-tag.diff-킬 { background: #ffebe6; color: #a30000; }
.slot.book-card .q-tag.diff-상 { background: #fff5e6; color: #c06000; }
.slot.book-card .q-tag.diff-중 { background: #fff8d6; color: #8a6d00; }
.slot.book-card .q-tag.diff-하 { background: #eaf7ea; color: #2d7a2d; }
.slot.book-card .q-body {
    font-size: 10.5pt;
    line-height: 1.7;
    margin-bottom: 2mm;
}
.slot.book-card .q-choices {
    margin-top: 3mm;
    font-size: 10pt;
    line-height: 1.75;
    display: flex;
    flex-wrap: wrap;
    column-gap: 6mm;
    row-gap: 2mm;
}
.slot.book-card .q-choices .choice {
    white-space: nowrap;
}
.slot.book-card .q-choices .choice .circ {
    color: #1d6fb7;
    font-weight: 700;
    margin-right: 1.5mm;
}
.qa-page { display: block; }  /* 빠른정답 페이지는 flex 해제 */
.sol-page { display: block; }
.quick-answers {
    width: 100%;
    border-collapse: collapse;
    font-size: 11pt;
    margin: 0 auto;
}
.quick-answers td {
    border: 1px solid #c7d3e6;
    padding: 3.5mm 2mm;
    text-align: center;
}
.quick-answers td.qa-num {
    background: #eef3fa;
    font-weight: 700;
    width: 6%;
    color: #103a63;
    letter-spacing: -0.3px;
}
.quick-answers td.qa-ans {
    width: 14%;
    font-weight: 600;
    color: #1a1a1a;
}
.solutions-flow {
    column-count: 2;
    column-gap: 7mm;
    column-rule: 1px dashed #d5d5d5;
}
.sol-item {
    break-inside: avoid;
    margin: 0 0 8mm 0;
    padding: 4mm 4mm 4mm 5mm;
    border-left: 4px solid #1d6fb7;
    background: #fafcff;
    border-radius: 0 1.5mm 1.5mm 0;
}
.sol-header {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 2mm;
    margin-bottom: 3mm;
    padding-bottom: 2.5mm;
    border-bottom: 1px solid #dee6f0;
}
.sol-num {
    font-size: 14pt;
    font-weight: 900;
    color: #103a63;
    letter-spacing: -0.5px;
    line-height: 1;
}
.sol-num-label {
    font-size: 10pt;
    font-weight: 700;
    color: #103a63;
    margin-right: 2mm;
}
.sol-answer-inline {
    background: #1d6fb7;
    color: #fff;
    padding: 0.5mm 2mm;
    border-radius: 1mm;
    font-size: 8.5pt;
    font-weight: 700;
    letter-spacing: 0.3px;
    margin-left: 2mm;
}
.sol-answer-inline b {
    font-weight: 900;
    margin-left: 0.5mm;
}
.sol-question {
    font-size: 10pt;
    color: #333;
    line-height: 1.65;
    margin-bottom: 3mm;
    padding-bottom: 2.5mm;
    border-bottom: 1px dashed #c7d3e6;
}
.sol-body {
    font-size: 10pt;
    line-height: 1.75;
    color: #1a1a1a;
}
.no-sol { color: #aaa; font-style: italic; }
"""

_HTML_WRAP = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">
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
    헤더에서는 중복 제거.
    - 시험지 모드: 기존 `N번 [출처]` 한 줄 헤더
    - 교재 모드(include_difficulty=True): 큰 Q번호 + pill 태그
    """
    body_html = render_question_body(q.get("question_text") or "")
    choices_html = format_choices(q.get("choices"), book_mode=include_difficulty)

    if include_difficulty:
        # 교재 카드 — CC 텍스트북 스타일
        tags: list[str] = []
        if q.get("chapter"):
            tags.append(f'<span class="q-tag">{_html.escape(str(q["chapter"]))}</span>')
        diff = q.get("difficulty")
        if diff:
            tags.append(
                f'<span class="q-tag diff-{_html.escape(str(diff))}">'
                f'{_html.escape(str(diff))}난이도</span>'
            )
        src_parts = []
        if q.get("school"):
            src_parts.append(str(q["school"]))
        if q.get("year") and q.get("semester"):
            exam = EXAM_TYPE_KO.get(q.get("exam_type"), "")
            src_parts.append(f'{q["year"]}년 {q["semester"]}학기 {exam}'.strip())
        if src_parts and include_source:
            tags.append(
                f'<span class="q-tag">{_html.escape(" · ".join(src_parts))}</span>'
            )
        tags_html = (
            '<div class="q-tags">' + "".join(tags) + '</div>' if tags else ""
        )
        return (
            f'<div class="slot book-card {layout}">'
            f'<div class="book-header">'
            f'<span class="q-kicker">PROBLEM</span>'
            f'<span class="q-number">Q{i}</span>'
            f'{tags_html}'
            f'</div>'
            f'<div class="q-body">{body_html}</div>'
            + (f'<div class="q-choices">{choices_html}</div>' if choices_html else "")
            + '</div>'
        )

    # 시험지 모드 (기존 그대로)
    meta = (
        f'<span class="q-meta">{format_source(q, include_difficulty)}</span>'
        if include_source else ""
    )
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


def _render_header(title: str, subtitle: str | None, logo_uri: str | None,
                    kicker_mark: str | None = None,
                    kicker_text: str | None = None) -> str:
    """헤더: 제목/부제는 항상 좌측 정렬, 로고는 우측 정렬(있을 때만).

    제목·부제·로고는 서로 독립적으로 on/off — 로고 없어도 부제 표시 가능.
    kicker_mark: 상단 왼쪽 포인트 텍스트 (예: '#01', 'VOL.01', '2026').
    kicker_text: kicker_mark 오른쪽 본문 텍스트 (예: 'MATH ARCHIVE').
    둘 다 None/빈문자열이면 kicker 라인 전체 생략.
    """
    mark_html = (
        f'<span class="mark">{_html.escape(kicker_mark)}</span>'
        if kicker_mark else ""
    )
    text_html = _html.escape(kicker_text) if kicker_text else ""
    kicker_html = (
        f'<span class="kicker">{mark_html}{text_html}</span>'
        if (kicker_mark or kicker_text) else ""
    )
    title_html = f'<h1 class="exam-title">{_html.escape(title)}</h1>'
    sub_html = (
        f'<h2 class="exam-subtitle">{_html.escape(subtitle)}</h2>'
        if subtitle else ""
    )
    logo_html = (
        f'<img class="exam-logo" src="{logo_uri}" alt="logo">' if logo_uri else ""
    )
    return (
        f'<header class="exam-header">'
        f'<div class="title-block">{kicker_html}{title_html}{sub_html}</div>'
        f'{logo_html}'
        f'</header>'
    )


def _problem_pages_html(questions: list[dict], include_source: bool,
                         overrides: dict | None,
                         header_html: str,
                         include_difficulty: bool = False) -> str:
    """문제 섹션(2단 레이아웃)의 HTML — header_html은 첫 page에만 삽입."""
    pages = paginate(questions, overrides=overrides)
    parts: list[str] = []
    slot_num = 1
    for idx, page in enumerate(pages):
        parts.append('<section class="page">')
        if idx == 0 and header_html:
            parts.append(header_html)
        parts.append('<div class="page-body">')
        cols = list(page)
        while len(cols) < 2:
            cols.append([])
        for col in cols:
            parts.append('<div class="col">')
            for (q, layout) in col:
                parts.append(_render_slot(
                    slot_num, q, layout, include_source, include_difficulty
                ))
                slot_num += 1
            parts.append('</div>')
        parts.append('</div>')  # page-body
        parts.append('</section>')
    return "\n".join(parts)


def build_exam_html(questions: list[dict], title: str, include_source: bool,
                     overrides: dict | None = None,
                     subtitle: str | None = None,
                     logo_path: str | Path | None = None,
                     include_difficulty: bool = False) -> str:
    logo_uri = _logo_data_uri(logo_path)
    header = _render_header(title, subtitle, logo_uri)
    body = _problem_pages_html(
        questions, include_source, overrides, header, include_difficulty
    )
    return _HTML_WRAP.format(title=_html.escape(title), css=_CSS, body=body)


# ── 교재 전용 섹션 ─────────────────────────────────────────
_CIRCLE_ANS = {"1": "①", "2": "②", "3": "③", "4": "④", "5": "⑤"}


def _render_quick_answer_table(questions: list[dict], cols: int = 5) -> str:
    """빠른 정답 표: 5열, 문항 번호 + 정답을 순서대로.

    각 셀 쌍은 `번호 | 답`. 예) 1행 = [1|②, 2|①, 3|③, 4|⑤, 5|④].
    행 수는 문항 수에 따라 자동 (34문항 → 7행, 46문항 → 10행).
    """
    rows: list[str] = []
    n = len(questions)
    for r in range(0, n, cols):
        cells: list[str] = []
        for c in range(cols):
            idx = r + c
            if idx < n:
                q = questions[idx]
                raw = q.get("answer")
                ans = _CIRCLE_ANS.get(str(raw), raw if raw is not None else "-")
                cells.append(
                    f'<td class="qa-num">{idx + 1}</td>'
                    f'<td class="qa-ans">{_html.escape(str(ans))}</td>'
                )
            else:
                cells.append('<td class="qa-num"></td><td class="qa-ans"></td>')
        rows.append(f'<tr>{"".join(cells)}</tr>')
    return (
        '<table class="quick-answers">'
        f'{"".join(rows)}'
        '</table>'
    )


def _render_solution_items(questions: list[dict], include_source: bool,
                            include_difficulty: bool = True) -> str:
    """해설 섹션 아이템들. 각 아이템은 CSS column flow에서 개별 박스.

    헤더: `N번  정답 ②` (한 줄).  메타/난이도 태그 제거 — 출처는 교재 본문에만 노출.
    """
    items: list[str] = []
    for i, q in enumerate(questions, 1):
        sol_raw = q.get("solution_text") or ""
        sol_body = (
            render_question_body(sol_raw) if sol_raw
            else '<p class="no-sol">해설 없음</p>'
        )
        raw_ans = q.get("answer")
        ans = _CIRCLE_ANS.get(str(raw_ans), raw_ans if raw_ans is not None else "-")
        items.append(
            f'<div class="sol-item">'
            f'<div class="sol-header">'
            f'<span class="sol-num">{i}</span>'
            f'<span class="sol-num-label">번</span>'
            f'<span class="sol-answer-inline">정답 <b>{_html.escape(str(ans))}</b></span>'
            f'</div>'
            f'<div class="sol-body">{sol_body}</div>'
            f'</div>'
        )
    return f'<div class="solutions-flow">{"".join(items)}</div>'


def build_book_html(questions: list[dict], title: str, include_source: bool = True,
                     overrides: dict | None = None,
                     subtitle: str | None = None,
                     logo_path: str | Path | None = None,
                     kicker_mark: str | None = None,
                     kicker_text: str | None = None) -> str:
    """교재 HTML: 문제(2단, 난이도 prefix 포함) + 빠른정답 표 + 해설(2단 column-flow)."""
    logo_uri = _logo_data_uri(logo_path)
    header = _render_header(title, subtitle, logo_uri,
                             kicker_mark=kicker_mark,
                             kicker_text=kicker_text)
    problem_html = _problem_pages_html(
        questions, include_source, overrides, header, include_difficulty=True
    )
    qa_html = (
        '<section class="page qa-page">'
        '<h2 class="section-title">빠른 정답</h2>'
        f'{_render_quick_answer_table(questions)}'
        '</section>'
    )
    sol_html = (
        '<section class="page sol-page">'
        '<h2 class="section-title">Solutions</h2>'
        f'{_render_solution_items(questions, include_source, include_difficulty=True)}'
        '</section>'
    )
    body = "\n".join([problem_html, qa_html, sol_html])
    return _HTML_WRAP.format(title=_html.escape(title), css=_CSS, body=body)


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
            margin={"top": "10mm", "bottom": "10mm", "left": "10mm", "right": "10mm"},
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


def generate_book_pdf(questions: list[dict], title: str = "수학 교재",
                      include_source: bool = True,
                      overrides: dict | None = None,
                      subtitle: str | None = None,
                      logo_path: str | Path | None = None,
                      kicker_mark: str | None = None,
                      kicker_text: str | None = None) -> bytes:
    """교재 PDF 생성. 문제 → 빠른정답 표 → 해설 순."""
    html = build_book_html(
        questions, title, include_source=include_source, overrides=overrides,
        subtitle=subtitle, logo_path=logo_path,
        kicker_mark=kicker_mark, kicker_text=kicker_text,
    )
    return html_to_pdf_bytes(html)
