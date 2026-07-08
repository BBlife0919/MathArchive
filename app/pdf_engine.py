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
    # 선지 번호가 1부터 시작하지 않으면 잘못 파싱된 조각 → 숨김 (서술형 등)
    nums = [c.get("number") for c in choices if isinstance(c, dict) and c.get("number")]
    if nums and 1 not in nums:
        return ""
    circle = {1: "①", 2: "②", 3: "③", 4: "④", 5: "⑤"}

    def _ct(c):
        # 선지 text도 본문과 동일한 수식 정규화 (행렬 행 구분자 등)
        return _normalize_math_text(c.get("text", "") or "")

    if book_mode:
        # 가로 flex — .q-choices 의 gap으로 간격 조정
        return "".join(
            f'<span class="choice">'
            f'<span class="circ">{circle.get(c.get("number"), c.get("number"))}</span>'
            f'{_ct(c)}'
            f'</span>'
            for c in choices
        )
    return "&nbsp;&nbsp;&nbsp;".join(
        f"{circle.get(c.get('number'), c.get('number'))} {_ct(c)}"
        for c in choices
    )


def _choice_col_class(choices_json) -> str:
    """선지 배열 클래스. 기본 3/2(cols3), 선지가 길면 2/2/1(cols2)."""
    try:
        choices = json.loads(choices_json) if isinstance(choices_json, str) else choices_json
    except Exception:
        return "cols3"
    if not choices:
        return "cols3"

    def vlen(t):
        t = t or ""
        # 분수/루트/적분 등은 시각적으로 넓어 가중치
        wide = len(re.findall(r"\\d?frac|\\sqrt|\\sum|\\int|\\lim", t))
        s = re.sub(r"\\[a-zA-Z]+|[${}\\^_~\\\\]|\s", "", t)
        # 한글·쉼표·부등호는 폭 가중치 (한 줄 못 들어가는 케이스 방지)
        han = len(re.findall(r"[ㄱ-ㅎ가-힣]", t))
        punct = t.count(",") + t.count("≤") + t.count("≥")
        return len(s) + wide * 4 + han * 1 + punct * 1

    return "cols2" if max(vlen(c.get("text", "")) for c in choices) > 10 else "cols3"


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
        # 수식 안 `<`,`>`,`&` 는 HTML escape — 브라우저가 `a<t<b` 의 `<` 를
        # 태그 시작으로 오인해 DOM/레이아웃이 깨지는 것 방지.
        # KaTeX auto-render 는 textContent(엔티티 디코딩됨)를 읽으므로 렌더 정상.
        safe = m.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        rendered = rendered.replace(_ph(i), safe)
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


_BOGI_HDR = re.compile(r"<\s*보\s*기\s*>")
_BOGI_ITEM = re.compile(r"^\s*([ㄱ-ㅎ])\s*[.ㆍ]")
_HANGUL_IDX = {c: i for i, c in enumerate("ㄱㄴㄷㄹㅁㅂㅅㅇ")}


def _unwrap_bogi_table(inner: str) -> str:
    """박스 안 <보기>가 빈 셀 많은 마크다운 표로 감싸진 경우 → 평문으로 언랩.

    진짜 데이터 표(정규분포표 등 — 보기/ㄱㄴㄷ 없음)는 그대로 둔다.
    """
    if "|" not in inner or "---" not in inner:
        return inner
    cells = []
    for line in inner.split("\n"):
        s = line.strip()
        if not s.startswith("|"):
            continue
        if set(s) <= set("|-: "):       # 구분선
            continue
        for c in s.split("|")[1:-1]:
            c = c.strip()
            if c:
                cells.append(c)
    frags = []
    for c in cells:
        frags += [f.strip() for f in re.split(r"<br\s*/?>", c) if f.strip()]
    items = [f for f in frags if _BOGI_ITEM.match(f)]
    has_hdr = any(_BOGI_HDR.search(f) for f in frags)
    if not items and not has_hdr:
        return inner                     # 진짜 표 → 유지
    items.sort(key=lambda s: _HANGUL_IDX.get(_BOGI_ITEM.match(s).group(1), 99))
    out = (["< 보 기 >"] if has_hdr else []) + items
    return "\n".join(out)


def _normalize_boxes(text: str) -> str:
    """박스 사고 정리: 중첩 평탄화 + 보기-표 언랩 + 반복 박스 제거 + 보기 중복 제거."""
    if "<<BOX_START>>" not in text:
        return text
    # 1) 최외곽 박스만 남기고 내부 마커 제거 (depth 스택)
    out = []
    depth = 0
    for tok in re.split(r"(<<BOX_START>>|<<BOX_END>>)", text):
        if tok == "<<BOX_START>>":
            if depth == 0:
                out.append(tok)
            depth += 1
        elif tok == "<<BOX_END>>":
            depth = max(0, depth - 1)
            if depth == 0:
                out.append(tok)
        else:
            out.append(tok)
    flat = "".join(out)

    # 2) 박스별: 보기-표 언랩 + 박스 내 <보기> 2회↑ 중복 제거
    seen = set()

    def _fix_box(m):
        inner = _unwrap_bogi_table(m.group(1))
        hdrs = [mm.start() for mm in _BOGI_HDR.finditer(inner)]
        if len(hdrs) >= 2:
            inner = inner[:hdrs[1]].rstrip()
        # 반복되는 동일 박스(공백무시)는 두 번째부터 제거
        key = re.sub(r"\s+", "", inner)
        if key and key in seen:
            return ""
        seen.add(key)
        return "<<BOX_START>>" + inner + "<<BOX_END>>"

    flat = re.sub(r"<<BOX_START>>(.*?)<<BOX_END>>", _fix_box, flat, flags=re.DOTALL)

    # 3) 박스 끝난 뒤 같은 <보기> 블록이 plain 으로 반복되면 제거 (박스 밖 중복)
    flat = re.sub(r"(<<BOX_END>>)\s*<\s*보\s*기\s*>.*?(?=<<BOX_START>>|$)",
                  r"\1", flat, flags=re.DOTALL)
    return flat


def _process_boxes(text: str) -> str:
    """<<BOX_START>>...<<BOX_END>> 블록을 HTML 박스로 변환."""
    def _repl(m):
        return f'<div class="cond-box">{_render_box_content(m.group(1))}</div>'
    return re.sub(r"<<BOX_START>>(.*?)<<BOX_END>>", _repl, text, flags=re.DOTALL)


_DOLLAR_RE = re.compile(r"(?<!\\)\$")
_MATH_SPAN_DOTALL = re.compile(r"(?<!\\)\$(.*?)(?<!\\)\$", re.DOTALL)
# 수식 안 함수명 (백슬래시 없이 raw) — KaTeX 파싱 실패 유발
_BARE_FUNC = re.compile(r"(?<![\\A-Za-z])(sin|cos|tan|cot|sec|csc|log|ln|lim|sinh|cosh|tanh)(?![A-Za-z])")
# `\,` 바로 뒤 위/아래첨자 (헐거운 첨자)
_LOOSE_SUP = re.compile(r"\\,\s*(\^|_)")
# 텍스트/연산자 블록 — 이 안의 함수명은 건드리면 안 됨 (\text{sin함수} 등)
_TEXT_BLOCK = re.compile(r"\\(?:text|mathrm|mbox|operatorname)\s*\{[^{}]*\}")


def _frac_to_dfrac_in_context(s: str) -> str:
    """수학식 안에서 다음 컨텍스트의 `\\frac` → `\\dfrac` (재귀):
       1) `^{...}` 또는 `_{...}` brace 안 (지수/첨자 안 분수가 invisible 되는 케이스)
       2) `\\frac{...}{...}` 의 분자·분모 brace 안 (복합분수 들쭉날쭉 해소)
    Brace depth 추적 (escape `\\\\` 무시) — 정규식으로 못 잡는 nested 처리.
    """
    n = len(s)
    out: list[str] = []
    i = 0
    def _skip_brace(start: int) -> int:
        depth = 1
        j = start
        while j < n and depth > 0:
            if s[j] == "\\" and j + 1 < n:
                j += 2
                continue
            if s[j] == "{":
                depth += 1
            elif s[j] == "}":
                depth -= 1
            j += 1
        return j

    while i < n:
        if s.startswith(r"\frac{", i):
            num_start = i + 6
            num_end = _skip_brace(num_start)
            if num_end <= n and num_end - 1 < n and s[num_end - 1] == "}" and num_end < n and s[num_end] == "{":
                den_start = num_end + 1
                den_end = _skip_brace(den_start)
                num_inner = _frac_to_dfrac_in_context(s[num_start:num_end - 1])
                den_inner = _frac_to_dfrac_in_context(s[den_start:den_end - 1])
                num_inner = num_inner.replace(r"\frac{", r"\dfrac{")
                den_inner = den_inner.replace(r"\frac{", r"\dfrac{")
                out.append(r"\frac{" + num_inner + "}{" + den_inner + "}")
                i = den_end
                continue
        if s[i] in "_^" and i + 1 < n and s[i + 1] == "{":
            inner_end = _skip_brace(i + 2)
            inner = _frac_to_dfrac_in_context(s[i + 2:inner_end - 1])
            inner = inner.replace(r"\frac{", r"\dfrac{")
            out.append(s[i:i + 2] + inner + "}")
            i = inner_end
            continue
        out.append(s[i])
        i += 1
    return "".join(out)


def _normalize_math_inner(s: str) -> str:
    """`$...$` 내부 LaTeX 교정: 함수명 백슬래시 보충 + 헐거운 첨자 정리.

    단, `\\text{...}`/`\\mathrm{...}` 등 블록 내부 라벨은 placeholder 로 격리해
    함수명 변환에서 제외 (예: `\\text{sin함수}` 를 깨뜨리지 않음).
    """
    blocks: list[str] = []

    def _stash(m):
        blocks.append(m.group(0))
        return f"\x00B{len(blocks) - 1}\x00"

    s = _TEXT_BLOCK.sub(_stash, s)
    # HWP 변환 잔재: ANG ≤ X / ANG <= X / ANG \leq X → \angle X (LE 두 글자가 <= 로 잘못 매핑됨)
    s = re.sub(r"\bANGLE\s+", r"\\angle ", s)
    s = re.sub(r"\bANG\s*(?:≤|<=|\\leq)\s*", r"\\angle ", s)
    # sin/cos/tan/log/ln 뒤 pi 가 백슬래시 없이 raw 5글자 식별자로 들어간 케이스
    # ($y=sinpix$ 등): 함수명·그리스·변수 분리
    s = re.sub(r"\b(sin|cos|tan|sec|csc|cot|log|ln)pi([a-zA-Z])\b", r"\\\1\\pi \2", s)
    s = re.sub(r"\b(sin|cos|tan|sec|csc|cot|log|ln)pi\b", r"\\\1\\pi", s)
    # 변수/큰 연산자 + 공백 + 첨자/지수 → 공백 제거 (a _{11}, \sum _{k=1} 등 첨자 분리 방지)
    s = re.sub(r"(\\(?:sum|prod|int|iint|iiint|oint|coprod|bigcup|bigcap|biguplus|bigvee|bigwedge|bigsqcup|bigodot|bigotimes|bigoplus|lim))\s+(?=[_^])", r"\1", s)
    s = re.sub(r"([A-Za-z\}\)\]])\s+(?=[_^])", r"\1", s)
    # matrix 환경 안의 단독 `\ ` → `\\` (LaTeX 행 구분) — KaTeX 행렬 일자 노출 방지
    def _fix_mat(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)
        body = re.sub(r"(?<!\\)\\(?!\\)(?=[\s&])", r"\\\\", body)
        return head + body + tail
    s = re.sub(r"(\\begin\{[pbvVB]?matrix\})(.*?)(\\end\{[pbvVB]?matrix\})",
               _fix_mat, s, flags=re.DOTALL)
    # 큰 연산자(시그마·적분·곱·합집합 등) 있는 수식 → \displaystyle 자동 prefix
    # KaTeX 인라인 textstyle 에서 시그마 본체가 작고 limits 가 옆에 첨자로 붙는 못생김 방지
    # NOTE: `\b` 는 `\sum_` 매치 X (m 다음 _ 가 \w 라 경계 없음) → 명시적 부정 lookahead
    if re.search(r"\\(sum|prod|int|iint|iiint|oint|bigcup|bigcap|coprod|biguplus|bigvee|bigwedge|bigsqcup|bigodot|bigotimes|bigoplus|lim)(?![a-zA-Z])", s):
        if not s.lstrip().startswith("\\displaystyle"):
            s = "\\displaystyle " + s
    # KaTeX inline `$...$` 모드에선 `\displaystyle` 만으로 op-limits 위/아래 보장 X
    # (브라우저별 동작 차이). `\limits` 명시로 강제 — 시그마/곱 등 뒤에 _/^ 있을 때만.
    s = re.sub(
        r"\\(sum|prod|coprod|bigcup|bigcap|biguplus|bigvee|bigwedge|bigsqcup|bigodot|bigotimes|bigoplus)(?=[_^])",
        r"\\\1\\limits",
        s,
    )
    # HWP 변환 잔재: `\sum_x = a ^{b}` 같이 limits 분리된 경우 → `\sum_{x=a}^{b}` 복구
    # `\sum_k=2 ^{30}` → `\sum_{k=2}^{30}` 등 (43번 해설 시그마 위/아래 누락 케이스)
    s = re.sub(
        r"(\\(?:sum|prod|int|coprod|bigcup|bigcap|biguplus|bigvee|bigwedge|bigsqcup|bigodot|bigotimes|bigoplus)(?:\\limits)?)"
        r"_([a-zA-Z])\s*=\s*([0-9a-zA-Z]+)\s*\^\{?([^}\s]+)\}?",
        r"\1_{\2=\3}^{\4}",
        s,
    )
    # 모든 분수는 displaystyle(`\dfrac`)로 통일 — 한글파일/시중 교재 톤 균일성.
    # `\frac` textstyle 사용 시 복합분수 안쪽 분수가 scriptstyle 자동 축소 → invisible.
    # 컨텍스트별 부분 강제(어떤건 \dfrac, 어떤건 \frac)는 들쭉날쭉 원인이므로 X.
    s = s.replace(r"\dfrac", r"\frac")
    s = re.sub(r"\\frac(?![a-zA-Z])", r"\\dfrac", s)
    s = _BARE_FUNC.sub(r"\\\1", s)
    s = _LOOSE_SUP.sub(r"\1", s)
    for i, b in enumerate(blocks):
        s = s.replace(f"\x00B{i}\x00", b)
    return s


def _normalize_math_text(text: str) -> str:
    """수식 `$` 정규화 (의미 보존, 렌더·DB 공용).

    1) 균형 `$...$` 안의 줄바꿈/탭을 공백으로 합침 — 여러 줄로 깨진 수식 복원.
    2) `$...$` 내부 함수명(sin→\\sin)·헐거운 첨자(\\,^→^) 교정 — KaTeX 파싱 실패 방지.
    3) 그래도 `$` 패리티가 홀수인 줄(닫는 달러 누락)은 줄 끝에 `$` 보충.
    """
    text = text or ""

    def _fix(m):
        inner = re.sub(r"[ \t]*\n[ \t]*", " ", m.group(1))
        return "$" + _normalize_math_inner(inner) + "$"

    text = _MATH_SPAN_DOTALL.sub(_fix, text)
    out = []
    for line in text.split("\n"):
        if len(_DOLLAR_RE.findall(line)) % 2 == 1:
            line = line + "$"
        out.append(line)
    text = "\n".join(out)
    # 별개 `$..$` 들이 공백으로 이어진 경우(둘 다 의미 있는 식) → 줄바꿈 분리.
    # 24번 해설 `$=c(...)^2$ $b^3=c^3$ $(b-c)(...)=0$ $\\therefore b=c$` 같이
    # 별개 식이 같은 줄에 표시되어 이상한 등호 체인이 되는 케이스.
    SIGS = ("=", "\\frac", "\\sum", "\\int", "\\prod", "\\lim",
            "\\therefore", "\\because", "\\Rightarrow", "\\Leftrightarrow")
    def _is_substantive(m):
        body = m[1:-1].strip()
        if any(s in body for s in SIGS):
            return True
        return len(body) > 8
    def _split_pair(m):
        a, b = m.group(1), m.group(3)
        return (a + "\n" + b) if (_is_substantive(a) and _is_substantive(b)) else m.group(0)
    prev = None
    while prev != text:
        prev = text
        text = re.sub(r"(\$[^$\n]+\$)([ \t]+)(\$[^$\n]+\$)", _split_pair, text)
    # 한글 ↔ `$독립식$` 가 공백 없이 직접 붙은 케이스도 줄바꿈.
    # 25번 (4)(다) `사인법칙을 이용하면$\\frac{BC}{...}=\\frac{AC}{...}$` 같이
    # 한글 문장 끝에 수식이 바로 이어지는 형태. 독립식 (= or \\frac 등) 만 대상.
    def _has_sig(body):
        return any(s in body for s in SIGS) and len(body) > 5
    def _split_korean_then_math(m):
        before, dollar = m.group(1), m.group(2)
        body = dollar[1:-1]
        return (before + "\n" + dollar) if _has_sig(body) else m.group(0)
    def _split_math_then_korean(m):
        dollar, after = m.group(1), m.group(2)
        body = dollar[1:-1]
        return (dollar + "\n" + after) if _has_sig(body) else m.group(0)
    text = re.sub(r"([가-힣])(\$[^$\n]+\$)", _split_korean_then_math, text)
    text = re.sub(r"(\$[^$\n]+\$)([가-힣])", _split_math_then_korean, text)
    return text


def render_question_body(text: str, images: dict | None = None) -> str:
    """문제 본문 텍스트 → HTML. 박스·수식 보호된 상태.

    images: {'image3': url, ...} 가 주어지면 `<<IMG:imageN>>` 를 실제 <img> 로
    임베드. 없으면(또는 해당 ref 없으면) '[그림]' placeholder 표시.
    """
    text = text or ""
    images = images or {}
    img_restore: dict[str, str] = {}

    def _img_ph(m):
        ref = m.group(1)
        key = f"@XIMGX{len(img_restore)}@"
        url = images.get(ref)
        if url:
            img_restore[key] = (
                f'<img class="q-img" src="{_html.escape(url, quote=True)}" alt="">'
            )
        else:
            img_restore[key] = '<span class="q-img-missing">[그림]</span>'
        return key

    text = re.sub(r"<<IMG:(image\d+)>>", _img_ph, text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    text = _normalize_boxes(text)
    text = _normalize_math_text(text)

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
    for key, tag in img_restore.items():
        html = html.replace(key, tag)
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
    font-family: 'NanumGothic', 'Nanum Gothic', '나눔고딕', 'Pretendard', 'Pretendard Variable', -apple-system, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    font-size: 10pt;
    line-height: 1.5;
    color: #111;
    -webkit-font-smoothing: antialiased;
}
/* 본문 한글: 나눔고딕 10pt */
.q-body, .slot .q-body, .q-choices .choice {
    font-family: 'NanumGothic', 'Nanum Gothic', '나눔고딕', 'Pretendard', sans-serif;
    font-size: 10pt;
}
/* 수식(KaTeX) — 컨테이너에만 사이즈 적용. `.katex *` 로 자식까지 강제하면
   KaTeX 내부 첨자/지수/limits 의 상대 비율이 깨져 시그마는 작고 위/아래는
   본체 크기로 비대칭 확대됨. 컨테이너 사이즈만 지정해 KaTeX 자체 계층 보호. */
.katex, .q-body .katex {
    font-size: 11pt !important;
}
/* 첨자/지수 — KaTeX 내부 .sizing.reset-size*.size* 클래스가 font-size 를
   reset 후 절대값으로 강제하기 때문에 .msupsub 컨테이너에만 적용하면 효과 X.
   자식 모두 !important 로 덮어야 cos^2 / a^2 / 2^{...} 의 지수가 본체 대비
   작아짐. */
/* 첨자/지수 크기 — KaTeX 기본 0.5em (sizing reset-size*.size3) 그대로 사용.
   강제 override 시 부모 컨텍스트 이미 작은 상태에서 또 곱해져 invisible(~2pt) 됨. */
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
    color: #555;
    font-size: 9pt;
    font-weight: 500;
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
/* 박스 안 넓은 표가 컬럼 폭을 넘어 잘리지 않게 — 폭 맞춤 + 폰트 축소 */
.slot.book-kp .cond-box { max-width: 100%; overflow: hidden; }
.slot.book-kp .cond-box table { max-width: 100%; font-size: 0.8em; table-layout: auto; }
.slot.book-kp .cond-box table td,
.slot.book-kp .cond-box table th { padding: 2pt 3pt !important; }
.slot.book-kp .cond-box .katex { font-size: 0.92em !important; }
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

/* ── SUMMIT POINT (네이비+골드) 교재 스타일 ───────────── */
/* 색상 변수 — 추후 일괄 변경 용이 */
.book-summit .slot.book-card {
    border-top: 3px solid #d2af6e;       /* gold top bar */
    background: #fcfcfd;
    padding: 4mm 4mm 5mm 4mm;
    margin-bottom: 4mm;
    border-radius: 0 0 2mm 2mm;
}
.book-summit .slot.book-card .book-header {
    border-bottom: 1px solid #e8d9b8;
    padding-bottom: 2mm;
    margin-bottom: 2.5mm;
}
.book-summit .slot.book-card .q-kicker {
    color: #d2af6e;
    letter-spacing: 3px;
    font-size: 7pt;
}
.book-summit .slot.book-card .q-number {
    color: #18264b;
}
.book-summit .slot.book-card .q-tag {
    background: #18264b;
    color: #f0cd87;
    border: none;
}
.book-summit .slot.book-card .q-tag.diff-킬 { background: #6b0d0d; color: #fff; }
.book-summit .slot.book-card .q-tag.diff-상 { background: #8c4a00; color: #fff; }
.book-summit .slot.book-card .q-tag.diff-중 { background: #6a5500; color: #fff; }
.book-summit .slot.book-card .q-tag.diff-하 { background: #1f5a1f; color: #fff; }

/* Key Point 박스 */
.book-summit .summit-kp {
    margin-top: 3mm;
    padding: 2mm 3mm;
    background: #faf8f0;
    border: 1px solid #e6c88c;
    border-radius: 1.5mm;
    display: flex;
    align-items: center;
    gap: 2.5mm;
    min-height: 7mm;
}
.book-summit .summit-kp-label {
    color: #18264b;
    font-weight: 800;
    font-size: 8pt;
    letter-spacing: 1.5px;
    background: #d2af6e;
    color: #18264b;
    padding: 0.6mm 2mm;
    border-radius: 1mm;
    flex-shrink: 0;
}
.book-summit .summit-kp-line {
    flex: 1;
    border-bottom: 1px dashed #c7b890;
    height: 4mm;
}

/* 풀이 메모란 */
.book-summit .summit-memo {
    margin-top: 2.5mm;
    padding: 2mm 1mm 1mm 1mm;
}
.book-summit .summit-memo-line {
    border-bottom: 0.5px solid #b8c2d4;
    height: 6mm;
}

/* 풀이기록 체크박스 (1차/2차/3차) */
.book-summit .summit-tries {
    display: flex;
    gap: 4mm;
    justify-content: flex-end;
    margin-top: 2mm;
    padding-top: 2mm;
    border-top: 1px dotted #d5dde8;
    font-size: 8.5pt;
    color: #5a6378;
}
.book-summit .summit-tries .try-item {
    display: inline-flex;
    align-items: center;
    gap: 1mm;
}
.book-summit .summit-tries .try-box {
    display: inline-block;
    width: 3mm;
    height: 3mm;
    border: 1.2px solid #18264b;
    border-radius: 0.5mm;
}
.book-summit .summit-tries .try-label {
    font-weight: 700;
    color: #18264b;
}

/* ── 챕터 디바이더 페이지 (화이트 + 블루 톤) ─── */
.chapter-divider {
    background: #ffffff !important;
    color: #1f2937;
    page-break-after: always;
    page-break-before: always;
    page-break-inside: avoid;
    position: relative;
    height: 100vh;
    padding: 22mm 20mm !important;
    box-sizing: border-box;
    font-family: 'Pretendard', 'Pretendard Variable', -apple-system, 'Apple SD Gothic Neo', 'Noto Sans KR', sans-serif;
    overflow: hidden;
}
.cd-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    position: relative;
    z-index: 2;
}
.cd-chapter-label {
    font-size: 11pt;
    font-weight: 800;
    letter-spacing: 3pt;
    color: #1e3a8a;
    border-bottom: 2px solid #1e3a8a;
    padding-bottom: 2pt;
}
.cd-meta-top {
    font-size: 10pt;
    font-weight: 700;
    letter-spacing: 1pt;
    color: #475569;
}
.cd-big-num {
    position: absolute;
    top: 42%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 360pt;
    font-weight: 900;
    color: #e2ecfa;
    z-index: 0;
    letter-spacing: -12pt;
    line-height: 1;
    pointer-events: none;
    user-select: none;
}
.cd-body {
    position: relative;
    z-index: 1;
    margin-top: 60mm;
    padding-left: 4mm;
}
.cd-major {
    font-size: 28pt;
    font-weight: 900;
    color: #1e3a8a;
    margin: 0 0 2mm 0;
    letter-spacing: -0.5pt;
}
.cd-major-roman {
    color: #1e3a8a;
    margin-right: 8pt;
}
.cd-major-rule {
    position: relative;
    height: 0.6pt;
    background: #cbd5e1;
    margin: 12mm 0 12mm 0;
}
.cd-major-rule::before, .cd-major-rule::after {
    content: '';
    position: absolute;
    top: 50%;
    transform: translateY(-50%);
    width: 5pt;
    height: 5pt;
    background: #1e3a8a;
    border-radius: 50%;
}
.cd-major-rule::before { left: 0; }
.cd-major-rule::after { right: 0; }
.cd-section-label {
    font-size: 11pt;
    font-weight: 700;
    letter-spacing: 3pt;
    color: #94a3b8;
}
.cd-section-title {
    font-size: 38pt;
    font-weight: 900;
    color: #1f2937;
    margin-top: 4mm;
    letter-spacing: -1pt;
    line-height: 1.1;
}
.cd-footer {
    position: absolute;
    bottom: 18mm;
    left: 22mm;
    right: 20mm;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    z-index: 2;
}
.cd-footer-title {
    font-size: 11pt;
    font-weight: 800;
    color: #1f2937;
    line-height: 1.7;
}
.cd-footer-sub {
    font-size: 10pt;
    font-weight: 500;
    color: #6b7280;
}
.cd-logo-bottom {
    max-width: 26mm;
    max-height: 18mm;
    opacity: 0.92;
}

/* ── 교재 본문 페이지 (image #208 스타일) ─────── */
.bp-page {
    position: relative;
    /* height:100vh(인쇄에서 vh 는 본문영역≈275mm 기준으로 존중·고정) 로 페이지를 꽉 채우고,
       display:flex 컬럼으로 inner flex:1(page-body→col→slot) 이 이 높이까지 자라게 함
       → 슬롯이 페이지 바닥까지 차고 margin-top:auto 가 메모를 바닥에 앵커.
       ※ min-height 로 주면 긴 문제에서 박스가 본문영역을 넘게 자라 빈 페이지 생김 → 반드시 고정 height.
       overflow:hidden 으로 넘치는 메모/본문 끝을 바닥에서 절단. */
    height: 100vh;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    padding: 0 13mm 0 0 !important;  /* 우측 인덱스 자리 확보 (여백 축소) */
    page-break-after: always;
}
.bp-head {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    border-bottom: 0;
    margin: 0 0 8mm 0;
    padding: 0 0 4mm 0;
    font-weight: 800;
}
.bp-head-left {
    font-size: 11pt;
    color: #0f172a;
    letter-spacing: 0.5pt;
}
.bp-head-right {
    font-size: 11pt;
    color: #1e3a8a;
    letter-spacing: 1pt;
}
.bp-head-right .roman {
    color: #1e3a8a;
    margin-right: 6pt;
    font-weight: 900;
}
.bp-side {
    position: absolute;
    top: 22mm;
    right: 0;
    width: 14mm;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4mm;
    z-index: 5;
}
.bp-side-vertical {
    background: #e2e8f0;
    color: #475569;
    font-size: 9pt;
    font-weight: 800;
    letter-spacing: 6pt;
    padding: 6mm 0;
    writing-mode: vertical-rl;
    text-orientation: upright;
    width: 9mm;
    text-align: center;
}
.bp-side-roman {
    background: #1e3a8a;
    color: #ffffff;
    font-size: 22pt;
    font-weight: 900;
    width: 14mm;
    height: 14mm;
    display: flex;
    align-items: center;
    justify-content: center;
}
.bp-side-tail {
    background: #c7d2fe;
    width: 9mm;
    flex: 1;
    min-height: 70mm;
}

/* (구) book-kp 슬롯 CSS 제거 — 아래쪽 통합 정의(.slot.book-kp flex-column)로 일원화 */

/* ── 교재 표지 (image #209 스타일) ─────── */
.book-cover {
    position: relative;
    height: 100vh;
    padding: 25mm 22mm !important;
    page-break-after: always;
    background: #ffffff;
    color: #0f172a;
    box-sizing: border-box;
}
.book-cover .bc-tl, .book-cover .bc-tr,
.book-cover .bc-bl, .book-cover .bc-br {
    position: absolute;
    width: 18mm; height: 18mm;
    border-color: #1e3a8a;
    border-style: solid;
    content: '';
}
.book-cover .bc-tl { top: 8mm; left: 8mm; border-width: 1.2pt 0 0 1.2pt; }
.book-cover .bc-tr { top: 8mm; right: 8mm; border-width: 1.2pt 1.2pt 0 0; }
.book-cover .bc-bl { bottom: 8mm; left: 8mm; border-width: 0 0 1.2pt 1.2pt; }
.book-cover .bc-br { bottom: 8mm; right: 8mm; border-width: 0 1.2pt 1.2pt 0; }
.book-cover .bc-kicker {
    text-align: center;
    font-size: 18pt;
    font-weight: 900;
    letter-spacing: 10pt;
    color: #1e3a8a;
    margin-top: 26mm;
}
.book-cover .bc-kicker-rule {
    width: 22mm;
    height: 1.6pt;
    background: #1e3a8a;
    margin: 4mm auto 0;
}
.book-cover .bc-title-main {
    text-align: center;
    margin-top: 26mm;
    font-size: 64pt;
    font-weight: 900;
    color: #0f172a;
    line-height: 1.1;
    letter-spacing: -2pt;
}
.book-cover .bc-title-mid {
    text-align: center;
    margin-top: 10mm;
    font-size: 18pt;
    font-weight: 900;
    color: #0f172a;
    letter-spacing: 8pt;
}
.book-cover .bc-title-big {
    text-align: center;
    margin-top: 10mm;
    font-size: 96pt;
    font-weight: 900;
    color: #1e3a8a;
    letter-spacing: -2pt;
    line-height: 1;
}
.book-cover .bc-big-rule {
    width: 60mm;
    height: 1pt;
    background: #0f172a;
    margin: 4mm auto 0;
}
/* INSTRUCTOR 박스 */
.book-cover .bc-instructor {
    margin: 18mm auto 0;
    width: 60mm;
    border: 1pt solid #1e3a8a;
    border-radius: 4mm;
    padding: 4mm 0;
    text-align: center;
    font-size: 18pt;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: 2pt;
}
.book-cover .bc-footer {
    position: absolute;
    bottom: 22mm; left: 22mm; right: 22mm;
    display: flex; justify-content: space-between; align-items: flex-end;
}
.book-cover .bc-footer-left {
    font-size: 11pt;
    font-weight: 800;
    color: #1e3a8a;
    line-height: 1.6;
}
.book-cover .bc-footer-left .sub {
    color: #475569;
    font-weight: 600;
    font-size: 10pt;
}
.book-cover .bc-logo {
    max-height: 22mm;
    max-width: 30mm;
}

/* ── 본문 페이지 (image #210, #211 스타일) ─── */
.bp-page .bp-head {
    border-bottom: 1pt solid #cbd5e1;
    padding: 0 0 2mm 0;
    margin: 0 0 6mm 0;
}
.bp-page .bp-head-left {
    color: #0f172a;
    font-weight: 800;
    font-size: 12pt;
    letter-spacing: 1.5pt;
}
.bp-page .bp-head-right {
    color: #0f172a;
    font-weight: 800;
    font-size: 11pt;
    letter-spacing: 0.5pt;
}
.bp-page .bp-head-right .roman {
    color: #0f172a;
    font-weight: 900;
    margin-right: 3pt;
}
/* 우측 인덱스 — PART 박스 (어둠) + 알파벳 박스 (골드) */
.bp-page .bp-side {
    position: absolute;
    top: 22mm;
    right: 2mm;
    width: 10mm;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    gap: 2mm;
    z-index: 5;
}
.bp-page .bp-side .bp-side-part {
    background: #1e293b;
    color: #ffffff;
    font-size: 9pt;
    font-weight: 800;
    letter-spacing: 4pt;
    padding: 10mm 0;
    writing-mode: vertical-rl;
    text-orientation: mixed;
    text-align: center;
    width: 10mm;
}
.bp-page .bp-side .bp-side-letter {
    background: #c8a96a;
    color: #ffffff;
    font-size: 22pt;
    font-weight: 900;
    width: 10mm;
    height: 14mm;
    display: flex;
    align-items: center;
    justify-content: center;
}
.bp-page .bp-side .bp-side-tail {
    width: 1.2pt;
    margin: 0 auto;
    background: #c8a96a;
    flex: 1;
    min-height: 50mm;
}

/* 새 교재 슬롯 — A·01 + 1차/2차/3차/OX + KEY POINT + MEMO */
.slot.book-kp {
    border-right: none !important;
    padding-right: 4mm !important;
    display: flex;
    flex-direction: column;
    /* .slot 기본 flex:1 로 col(=bp-page flex 컬럼) 높이까지 자람.
       margin-top:auto(kp-keypoint)가 메모 블록을 슬롯 바닥=페이지 바닥에 앵커. */
}
/* 헤더: 번호 + 체크박스 박스 두 개 한 줄, 그 아래 본문 풀폭 */
.slot.book-kp .kp-head {
    display: flex;
    flex-direction: column;
    gap: 2mm;
    margin-bottom: 2.5mm;
}
.slot.book-kp .kp-num-block {
    flex-shrink: 0;
    display: flex;
    flex-direction: row;
    align-items: center;
    gap: 3mm;
    flex-wrap: wrap;
}
.slot.book-kp .kp-num {
    font-family: 'Pretendard', sans-serif;
    font-size: 14pt;
    font-weight: 900;
    color: #c8a96a;
    letter-spacing: -0.3pt;
    line-height: 1;
}
.slot.book-kp .kp-checks {
    font-size: 8pt;
    font-weight: 700;
    color: #475569;
    display: flex;
    flex-direction: row;
    gap: 2mm;
}
.slot.book-kp .kp-checks .row {
    display: flex;
    gap: 2mm;
    border: 0.35mm solid #c8a96a;
    background: #fdfaf3;
    border-radius: 1mm;
    padding: 0.8mm 2mm;
}
.slot.book-kp .kp-checks .cb::before {
    content: '☐';
    margin-right: 0.5mm;
    color: #94a3b8;
}
.slot.book-kp .kp-right {
    width: 100%;
}
.slot.book-kp .kp-source {
    font-size: 9pt;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 1.5mm;
}
.slot.book-kp .q-body {
    font-size: 10.5pt;
    line-height: 1.65;
    color: #1f2937;
    min-width: 0;
    overflow: hidden;
}
.slot.book-kp .q-body .katex,
.slot.book-kp .q-body .katex-display {
    max-width: 100%;
    overflow-x: hidden;
}
.slot.book-kp .q-choices .choice .katex {
    max-width: 100%;
    overflow-x: hidden;
}
.slot.book-kp .q-choices {
    margin-top: 3mm;
    font-size: 10pt;
    line-height: 1.7;
    display: flex;
    flex-wrap: wrap;
    column-gap: 3mm;
    row-gap: 2.5mm;
}
/* 기본 3/2 배열 (한 줄에 3개) */
.slot.book-kp .q-choices.cols3 .choice { flex: 0 0 calc(33.333% - 2.2mm); }
/* 선지가 길 때 2/2/1 배열 (한 줄에 2개) */
.slot.book-kp .q-choices.cols2 .choice { flex: 0 0 calc(50% - 1.6mm); }
.slot.book-kp .q-choices .choice {
    white-space: normal;
    overflow-wrap: break-word;
    display: flex;
    align-items: baseline;
}
.slot.book-kp .q-choices .choice .circ {
    color: #111111;
    font-weight: 700;
    margin-right: 1.4mm;
    flex-shrink: 0;
}
.q-img {
    display: block;
    max-width: 88%;
    max-height: 70mm;
    margin: 3mm auto;
    object-fit: contain;
}
.q-img-missing { color: #b00; font-size: 9pt; }
.img-check {
    margin: 2mm 0;
    padding: 1.5mm 3mm;
    background: #fff4e5;
    border: 0.8pt solid #f0a04b;
    border-radius: 1.5mm;
    color: #9a4a00;
    font-size: 8pt;
    font-weight: 700;
}
/* KEY POINT + MEMO 박스 — 슬롯 하단 앵커.
   슬롯이 .bp-page(height:100vh)+flex 체인으로 페이지 바닥까지 늘어나므로
   margin-top:auto 가 KEY POINT+MEMO 블록을 페이지 바닥에 밀착시킴(하단여백 ~10mm).
   본문이 길면 메모 줄이 적게(자동 적응), 넘치면 .bp-page overflow:hidden 이 절단. */
.slot.book-kp .kp-keypoint {
    margin-top: auto;
    padding-top: 8mm;
    display: flex;
    align-items: stretch;
    border-top: 0;
    gap: 0;
}
.slot.book-kp .kp-keypoint .kp-label {
    background: transparent;
    color: #c8a96a;
    font-size: 11pt;
    font-weight: 900;
    letter-spacing: 1.5pt;
    padding: 2.5mm 4mm;
    border: 1pt solid #d6b87a;
    border-right: 0;
    display: flex;
    align-items: center;
}
.slot.book-kp .kp-keypoint .kp-line {
    flex: 1;
    border: 1pt solid #d6b87a;
    padding: 2.5mm 4mm;
    color: #94a3b8;
    font-size: 9pt;
    font-style: italic;
    display: flex;
    align-items: center;
}
.slot.book-kp .kp-memo {
    margin-top: 3mm;
}
.slot.book-kp .kp-memo .kp-memo-label {
    font-size: 9pt;
    font-weight: 800;
    color: #0f172a;
    margin-bottom: 1mm;
    letter-spacing: 1pt;
}
.slot.book-kp .kp-memo .kp-memo-line {
    border-bottom: 0.5pt solid #cbd5e1;
    height: 7mm;
}
"""

_HTML_WRAP = """<!doctype html>
<html lang="ko"><head>
<meta charset="utf-8">
<title>{title}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Nanum+Myeongjo:wght@400;700;800&family=Nanum+Brush+Script&family=Hi+Melody&family=Single+Day&family=East+Sea+Dokdo&family=Nanum+Pen+Script&family=Gaegu:wght@400;700&family=Black+Han+Sans&family=Yeon+Sung&display=swap">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
 onload="renderMathInElement(document.body,{{delimiters:[{{left:'$$',right:'$$',display:true}},{{left:'$',right:'$',display:false}}],throwOnError:false}}); window.__katexReady=true;"></script>
<style>{css}</style>
</head><body class="{body_class}">
{body}
</body></html>
"""


# ── 챕터 디바이더 ─────────────────────────────────────────
ROMAN_NUMERALS = [
    "I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
    "XI", "XII", "XIII", "XIV", "XV",
]


def _minor_to_major(chapter: str) -> str:
    """소단원(중단원, 예: '삼각함수와 그래프') → 대단원(예: '삼각함수').

    curriculum.CURRICULUM 의 역매핑. 매칭 못 찾으면 chapter 그대로 반환.
    """
    try:
        # pdf_engine.py 는 app/ 안에 있으므로 curriculum 모듈도 같은 경로.
        import sys
        from pathlib import Path
        app_dir = str(Path(__file__).resolve().parent)
        if app_dir not in sys.path:
            sys.path.insert(0, app_dir)
        import curriculum as _curr
        for subj, majors in _curr.CURRICULUM.items():
            for major, minors in majors.items():
                if chapter in minors:
                    return major
    except Exception:
        pass
    return chapter or "기타"


def _render_chapter_divider(
    major_no: int, section_no: int,
    major_name: str, minor_name: str,
    meta_top: str = "",
    footer_title: str = "",
    footer_sub: str = "",
    logo_uri: str | None = None,
) -> str:
    """챕터 디바이더 페이지 — 화이트+블루 디자인.

    major_no: 대단원 번호 (I, II, III ...)
    section_no: 대단원 안의 소단원 번호 (1부터)
    major_name: 대단원 명 (예: '삼각함수')
    minor_name: 소단원 명 (예: '삼각함수의 그래프')
    meta_top: 우상단 메타 (예: '대수 1학기 기말 · FINAL')
    footer_title: 좌하단 제목
    footer_sub: 좌하단 부제 (예: '이영우 T')
    logo_uri: 우하단 로고 data URI
    """
    roman = ROMAN_NUMERALS[major_no - 1] if 0 < major_no <= len(ROMAN_NUMERALS) \
        else str(major_no)
    meta_html = (
        f'<span class="cd-meta-top">{_html.escape(meta_top)}</span>'
        if meta_top else ""
    )
    footer_left = ""
    if footer_title or footer_sub:
        footer_left = (
            f'<div class="cd-footer-title">'
            f'{_html.escape(footer_title)}'
            f'{"<br>" if footer_sub else ""}'
            f'<span class="cd-footer-sub">{_html.escape(footer_sub)}</span>'
            f'</div>'
        )
    logo_html = (
        f'<img class="cd-logo-bottom" src="{logo_uri}" alt="logo">'
        if logo_uri else '<span></span>'
    )
    return (
        '<section class="page chapter-divider">'
        '<div class="cd-header">'
        f'<span class="cd-chapter-label">CHAPTER · {major_no:02d}</span>'
        f'{meta_html}'
        '</div>'
        f'<div class="cd-big-num">{major_no:02d}</div>'
        '<div class="cd-body">'
        f'<h2 class="cd-major">'
        f'<span class="cd-major-roman">{roman}.</span>'
        f'{_html.escape(major_name)}'
        f'</h2>'
        '<div class="cd-major-rule"></div>'
        f'<span class="cd-section-label">SECTION · {section_no}</span>'
        f'<h1 class="cd-section-title">{_html.escape(minor_name)}</h1>'
        '</div>'
        '<div class="cd-footer">'
        f'{footer_left or "<span></span>"}'
        f'{logo_html}'
        '</section>'
    )


def _group_by_chapter(questions: list[dict]) -> list[tuple[str, list[dict]]]:
    """순서 보존하면서 같은 chapter 인접 문제 묶음."""
    groups: list[tuple[str, list[dict]]] = []
    for q in questions:
        ch = q.get("chapter") or "기타"
        if groups and groups[-1][0] == ch:
            groups[-1][1].append(q)
        else:
            groups.append((ch, [q]))
    return groups


def _build_chapter_sections(
    questions: list[dict],
) -> list[tuple[int, int, str, str, str, list[dict]]]:
    """문제 리스트를 (major_no, section_no, letter, major, minor, qs) 시퀀스로.

    major_no = 대단원 번호 (PART 1, PART 2 ...).
    section_no = 같은 대단원 안 소단원 번호 (대단원 바뀌면 다시 1).
    letter = 같은 대단원 안 소단원 알파벳 ('A', 'B', 'C' ...).
    """
    groups = _group_by_chapter(questions)
    out: list[tuple[int, int, str, str, str, list[dict]]] = []
    major_no = 0
    section_no = 0
    last_major: str | None = None
    for minor, qs in groups:
        major = _minor_to_major(minor)
        if major != last_major:
            major_no += 1
            section_no = 1
            last_major = major
        else:
            section_no += 1
        letter = chr(ord("A") + section_no - 1) if section_no <= 26 else "?"
        out.append((major_no, section_no, letter, major, minor, qs))
    return out


def _render_slot(i: int, q: dict, layout: str, include_source: bool,
                  include_difficulty: bool = False,
                  letter: str = "") -> str:
    """문항 슬롯 HTML.

    - 시험지 모드: `N번 [출처]` 한 줄 헤더
    - 교재 모드(include_difficulty=True): `A·01` 번호 + 1차/2차/3차/OX
      체크박스 + 출처 한 줄 + 본문 + 선지 + 하단 KEY POINT / MEMO
    letter: 소단원 인덱스 알파벳 (A,B,C). 슬롯 번호 prefix.
    """
    body_html = render_question_body(q.get("question_text") or "", q.get("images"))
    if q.get("img_check"):
        body_html += ('<div class="img-check">⚠ 그림 확인 필요 — 원본이 여러 그림을 '
                      '한 이미지로 합쳐 저장한 문항입니다.</div>')
    choices_html = format_choices(q.get("choices"), book_mode=include_difficulty)

    if include_difficulty:
        # 출처 메타 (image #211 처럼 슬롯 우측 본문 위 한 줄)
        meta_parts = []
        if q.get("year") and q.get("semester"):
            exam = EXAM_TYPE_KO.get(q.get("exam_type"), "")
            meta_parts.append(f'{q["year"]}년 {q["semester"]}학기 {exam}'.strip())
        if q.get("school"):
            meta_parts.append(str(q["school"]))
        diff = q.get("difficulty") or ""
        if diff:
            meta_parts.append(f"[{diff}]")
        meta_html = (
            f'<div class="kp-source">{_html.escape(" · ".join(meta_parts))}</div>'
            if meta_parts and include_source else ""
        )
        slot_label = f'{letter}·{i:02d}' if letter else f'{i:02d}'
        return (
            f'<div class="slot book-kp {layout}">'
            f'<div class="kp-head">'
            f'<div class="kp-num-block">'
            f'<span class="kp-num">{_html.escape(slot_label)}</span>'
            f'<div class="kp-checks">'
            f'<div class="row">'
            f'<span class="cb">1차</span><span class="cb">2차</span>'
            f'<span class="cb">3차</span>'
            f'</div>'
            f'<div class="row">'
            f'<span class="cb">O</span><span class="cb">X</span>'
            f'</div>'
            f'</div>'
            f'</div>'
            f'<div class="kp-right">'
            f'{meta_html}'
            f'<div class="q-body">{body_html}</div>'
            + (f'<div class="q-choices {_choice_col_class(q.get("choices"))}">{choices_html}</div>'
               if choices_html else "")
            + '</div>'
            '</div>'
            # 슬롯 하단 KEY POINT + MEMO
            '<div class="kp-keypoint">'
            '<span class="kp-label">KEY POINT</span>'
            '<span class="kp-line">이 문제 핵심 한 줄로 정리</span>'
            '</div>'
            '<div class="kp-memo">'
            '<div class="kp-memo-label">MEMO</div>'
            + '<div class="kp-memo-line"></div>' * 6
            + '</div>'
            '</div>'
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
                         include_difficulty: bool = False,
                         first_col_extra_html: str = "",
                         per_page_header_fn=None,
                         per_page_footer_fn=None,
                         body_class: str = "",
                         start_slot: int = 1,
                         page_class: str = "",
                         side_html: str = "",
                         slot_letter: str = "") -> str:
    """문제 섹션(2단 레이아웃)의 HTML.

    start_slot: 슬롯 번호 시작값 (책 전체 누적 번호 유지용).
    page_class: section.page 에 추가되는 클래스 (예: 'bp-page').
    side_html: 매 페이지 본문 시작 직전에 삽입되는 절대-위치 aside HTML.
    """
    pages = paginate(questions, overrides=overrides)
    total_pages = len(pages)
    parts: list[str] = []
    slot_num = start_slot
    body_class_attr = f"page-body {body_class}".strip()
    page_class_attr = f"page {page_class}".strip()
    for idx, page in enumerate(pages):
        parts.append(f'<section class="{page_class_attr}">')
        if side_html:
            parts.append(side_html)
        # 동적 페이지 헤더 우선 (모의고사 양식). 없으면 정적 header_html (1쪽만).
        if per_page_header_fn:
            parts.append(per_page_header_fn(idx + 1, total_pages))
        elif idx == 0 and header_html:
            parts.append(header_html)
        parts.append(f'<div class="{body_class_attr}">')
        cols = list(page)
        while len(cols) < 2:
            cols.append([])
        for ci, col in enumerate(cols):
            parts.append('<div class="col">')
            if idx == 0 and ci == 0 and first_col_extra_html:
                parts.append(first_col_extra_html)
            for (q, layout) in col:
                parts.append(_render_slot(
                    slot_num, q, layout, include_source, include_difficulty,
                    letter=slot_letter,
                ))
                slot_num += 1
            parts.append('</div>')
        parts.append('</div>')  # page-body
        # 매 페이지 푸터
        if per_page_footer_fn:
            parts.append(per_page_footer_fn(idx + 1, total_pages))
        parts.append('</section>')
    return "\n".join(parts), slot_num


def _problem_pages_html_simple(*args, **kwargs) -> str:
    """기존 호출자 호환용 — 튜플의 첫 요소(HTML)만 반환."""
    html, _ = _problem_pages_html(*args, **kwargs)
    return html


def build_exam_html(questions: list[dict], title: str, include_source: bool,
                     overrides: dict | None = None,
                     subtitle: str | None = None,
                     logo_path: str | Path | None = None,
                     include_difficulty: bool = False) -> str:
    logo_uri = _logo_data_uri(logo_path)
    header = _render_header(title, subtitle, logo_uri)
    body, _ = _problem_pages_html(
        questions, include_source, overrides, header, include_difficulty
    )
    return _HTML_WRAP.format(
        title=_html.escape(title), css=_CSS, body=body,
        body_class="",
    )


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
            render_question_body(sol_raw, q.get("images_sol") or q.get("images")) if sol_raw
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


def _render_book_cover(
    title_main: str,
    title_mid: str = "",
    big_word: str = "FINAL",
    instructor: str = "",
    kicker_top: str = "MATH WORKBOOK · 2026",
    footer_left_main: str = "",
    footer_left_sub: str = "",
    logo_uri: str | None = None,
) -> str:
    """교재 표지 (image #209 디자인).

    title_main: 큰 메인 제목 (예: 'KERNEL POINT')
    title_mid: 그 아래 자간 넓은 부제 (예: '대수 1학기 기말 내신기출')
    big_word: 큰 파란색 워드 (예: 'FINAL')
    instructor: 둥근 박스 안 강사명 (예: '이영우 T')
    """
    mid_html = (
        f'<div class="bc-title-mid">{_html.escape(title_mid)}</div>'
        if title_mid else ""
    )
    instructor_html = (
        f'<div class="bc-instructor">{_html.escape(instructor)}</div>'
        if instructor else ""
    )
    logo_html = (
        f'<img class="bc-logo" src="{logo_uri}" alt="logo">' if logo_uri else ""
    )
    footer_html = ""
    if footer_left_main or footer_left_sub or logo_uri:
        footer_html = (
            '<div class="bc-footer">'
            '<div class="bc-footer-left">'
            f'{_html.escape(footer_left_main)}'
            f'{"<br>" if footer_left_sub else ""}'
            f'<span class="sub">{_html.escape(footer_left_sub)}</span>'
            '</div>'
            f'{logo_html}'
            '</div>'
        )
    return (
        '<section class="page book-cover">'
        '<span class="bc-tl"></span><span class="bc-tr"></span>'
        '<span class="bc-bl"></span><span class="bc-br"></span>'
        f'<div class="bc-kicker">{_html.escape(kicker_top)}</div>'
        '<div class="bc-kicker-rule"></div>'
        f'<div class="bc-title-main">{_html.escape(title_main)}</div>'
        f'{mid_html}'
        f'<div class="bc-title-big">{_html.escape(big_word)}</div>'
        '<div class="bc-big-rule"></div>'
        f'{instructor_html}'
        f'{footer_html}'
        '</section>'
    )


def _render_book_page_head(running_left: str, part_no: int,
                            major_name: str) -> str:
    """본문 페이지 좌상단 / 우상단 머릿말."""
    return (
        '<header class="bp-head">'
        f'<span class="bp-head-left">{_html.escape(running_left)}</span>'
        '<span class="bp-head-right">'
        f'<span class="roman">PART {part_no}</span>'
        f'· {_html.escape(major_name)}'
        '</span>'
        '</header>'
    )


def _render_book_page_side(part_no: int, letter: str) -> str:
    """본문 페이지 우측 인덱스 바 (PART {n} 어둠박스 + 알파벳 골드박스)."""
    return (
        '<aside class="bp-side">'
        f'<div class="bp-side-part">PART {part_no}</div>'
        f'<div class="bp-side-letter">{_html.escape(letter)}</div>'
        '<div class="bp-side-tail"></div>'
        '</aside>'
    )


def build_book_html(questions: list[dict], title: str, include_source: bool = True,
                     overrides: dict | None = None,
                     subtitle: str | None = None,
                     logo_path: str | Path | None = None,
                     kicker_mark: str | None = None,
                     kicker_text: str | None = None,
                     divider_meta_top: str | None = None,
                     divider_footer_title: str | None = None,
                     divider_footer_sub: str | None = None,
                     cover_kicker: str | None = None,
                     cover_big_word: str | None = None,
                     cover_main_title: str | None = None,
                     cover_tagline: str | None = None,
                     cover_footer_main: str | None = None,
                     cover_footer_sub: str | None = None,
                     page_running_left: str | None = None,
                     extra_css: str = "") -> str:
    """교재 HTML: 표지 → 챕터 디바이더 → 문제 → 빠른정답 → 해설."""
    logo_uri = _logo_data_uri(logo_path)
    # 디바이더 메타 디폴트
    if divider_footer_title is None:
        divider_footer_title = title
    # 표지 (책 가장 앞)
    cover_html = _render_book_cover(
        title_main=cover_main_title or title,
        title_mid=cover_tagline or subtitle or "",
        big_word=cover_big_word or "FINAL",
        instructor=divider_footer_sub or "이영우 T",
        kicker_top=cover_kicker or "MATH WORKBOOK · 2026",
        footer_left_main=cover_footer_main or "Algebra Final Workbook · 2026",
        footer_left_sub=cover_footer_sub or "필수유형으로 끝내는 기말 마무리",
        logo_uri=logo_uri,
    )
    # 챕터별 그룹화 → (major_no, section_no, letter, major, minor, qs) 시퀀스
    sections = _build_chapter_sections(questions)
    body_parts: list[str] = [cover_html]
    running_left = page_running_left or title or "KERNEL POINT"
    for major_no, section_no, letter, major, minor, ch_qs in sections:
        body_parts.append(_render_chapter_divider(
            major_no, section_no, major, minor,
            meta_top=divider_meta_top or "",
            footer_title=divider_footer_title or "",
            footer_sub=divider_footer_sub or "",
            logo_uri=logo_uri,
        ))
        # 매 페이지 헤더/우측 인덱스 클로저
        def _hdr(idx_, total_, _p=major_no, _m=major):
            return _render_book_page_head(running_left, _p, _m)
        side = _render_book_page_side(major_no, letter)
        # 슬롯 번호는 소단원(letter)마다 1부터 다시 시작 (A·01, A·02, ..., B·01)
        body_html, _ = _problem_pages_html(
            ch_qs, include_source, overrides, "",
            include_difficulty=True,
            per_page_header_fn=_hdr,
            page_class="bp-page",
            side_html=side,
            start_slot=1,
            slot_letter=letter,
        )
        body_parts.append(body_html)
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
    body = "\n".join(body_parts + [qa_html, sol_html])
    if extra_css:
        # 본문/선지/KaTeX 는 건드리지 않고 크롬 요소만 재정의하는 스코프 CSS.
        # 메인 <style> 뒤(문서 후미)에 와서 동일 선택자를 오버라이드.
        body += f'\n<style>{extra_css}</style>'
    return _HTML_WRAP.format(
        title=_html.escape(title), css=_CSS, body=body,
        body_class="book-summit",
    )


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
    if os.environ.get("DEBUG_DUMP_HTML"):
        with open("/tmp/last_book.html", "w") as f:
            f.write(html)
    with sync_playwright() as p:
        browser = _launch_browser(p)
        page = browser.new_page()
        page.set_content(html, wait_until="networkidle")
        try:
            page.wait_for_function("window.__katexReady === true", timeout=10000)
        except Exception:
            pass
        # 외부 웹폰트(Google Fonts 등) 로딩 완료 대기 — 안 기다리면 한글 손글씨
        # 폰트가 fallback (시스템 명조) 으로 떨어져 인쇄체처럼 보이는 사고.
        try:
            page.wait_for_function("document.fonts && document.fonts.ready",
                                    timeout=8000)
            page.evaluate("document.fonts.ready")
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


# ── 디자인 적용 시험지 (표지 + 내지) ─────────────────────────
def build_designed_exam_html(questions: list[dict],
                              meta,  # exam_designs.ExamMeta
                              cover_design: str,
                              inner_design: str,
                              include_source: bool = False,
                              overrides: dict | None = None,
                              include_difficulty: bool = False) -> str:
    """표지 + 내지 디자인을 입힌 시험지 HTML 을 만든다.

    cover_design: exam_designs.COVER_DESIGNS 의 키
    inner_design: exam_designs.INNER_DESIGNS 의 키
    meta: exam_designs.ExamMeta 인스턴스
    """
    import exam_designs as _ed

    # 본문 페이지 수를 미리 알아야 내지 #1 의 "총 X쪽" 헤더에 박을 수 있음.
    pages = paginate(questions, overrides=overrides)
    n_body_pages = len(pages)

    # 표지
    cover_spec = _ed.COVER_DESIGNS.get(cover_design)
    cover_html = cover_spec["render"](meta) if cover_spec else ""

    # 내지 디자인 스펙
    inner_spec = _ed.INNER_DESIGNS.get(inner_design)
    inner_header = ""
    inner_col_extra = ""
    per_page_header_fn = None
    per_page_footer_fn = None
    body_class = ""
    if inner_spec:
        needs_count = inner_spec.get("needs_page_count")
        total_pages_for_design = n_body_pages + 1  # 표지 포함
        if needs_count:
            inner_header = inner_spec["first_header"](
                meta, total_pages_for_design
            )
        else:
            inner_header = inner_spec["first_header"](meta)

        col_extra_fn = inner_spec.get("first_col_extra")
        if col_extra_fn:
            if needs_count:
                inner_col_extra = col_extra_fn(meta, total_pages_for_design)
            else:
                inner_col_extra = col_extra_fn(meta)

        # 페이지별 동적 헤더/푸터 (수능형 모의고사) — meta 를 closure 로 캡처
        ppf_header = inner_spec.get("per_page_header_fn")
        if ppf_header:
            per_page_header_fn = (
                lambda idx, total, _fn=ppf_header, _m=meta:
                _fn(_m, idx, total)
            )
        ppf_footer = inner_spec.get("per_page_footer_fn")
        if ppf_footer:
            per_page_footer_fn = (
                lambda idx, total, _fn=ppf_footer, _m=meta:
                _fn(_m, idx, total)
            )
        body_class = inner_spec.get("body_class", "")

    # 본문
    body, _ = _problem_pages_html(
        questions, include_source, overrides,
        inner_header, include_difficulty,
        first_col_extra_html=inner_col_extra,
        per_page_header_fn=per_page_header_fn,
        per_page_footer_fn=per_page_footer_fn,
        body_class=body_class,
    )

    full_body = cover_html + "\n" + body
    css = _CSS + "\n" + _ed.all_design_css()
    return _HTML_WRAP.format(
        title=_html.escape(meta.cover_main_title()),
        css=css, body=full_body, body_class="",
    )


def generate_designed_exam_pdf(questions: list[dict],
                                meta,
                                cover_design: str,
                                inner_design: str,
                                include_source: bool = False,
                                overrides: dict | None = None,
                                include_difficulty: bool = False) -> bytes:
    """디자인 표지+내지 시험지 PDF 생성 진입점."""
    html = build_designed_exam_html(
        questions, meta, cover_design, inner_design,
        include_source=include_source, overrides=overrides,
        include_difficulty=include_difficulty,
    )
    return html_to_pdf_bytes(html)


def generate_book_pdf(questions: list[dict], title: str = "수학 교재",
                      include_source: bool = True,
                      overrides: dict | None = None,
                      subtitle: str | None = None,
                      logo_path: str | Path | None = None,
                      kicker_mark: str | None = None,
                      kicker_text: str | None = None,
                      divider_meta_top: str | None = None,
                      divider_footer_title: str | None = None,
                      divider_footer_sub: str | None = None,
                      cover_kicker: str | None = None,
                      cover_big_word: str | None = None,
                      cover_main_title: str | None = None,
                      cover_tagline: str | None = None,
                      cover_footer_main: str | None = None,
                      cover_footer_sub: str | None = None,
                      page_running_left: str | None = None,
                      extra_css: str = "") -> bytes:
    """교재 PDF 생성. 표지 → 챕터 디바이더 → 문제 → 빠른정답 → 해설 순."""
    html = build_book_html(
        questions, title, include_source=include_source, overrides=overrides,
        subtitle=subtitle, logo_path=logo_path,
        kicker_mark=kicker_mark, kicker_text=kicker_text,
        divider_meta_top=divider_meta_top,
        divider_footer_title=divider_footer_title,
        divider_footer_sub=divider_footer_sub,
        cover_kicker=cover_kicker,
        cover_big_word=cover_big_word,
        cover_main_title=cover_main_title,
        cover_tagline=cover_tagline,
        cover_footer_main=cover_footer_main,
        cover_footer_sub=cover_footer_sub,
        page_running_left=page_running_left,
        extra_css=extra_css,
    )
    return html_to_pdf_bytes(html)
