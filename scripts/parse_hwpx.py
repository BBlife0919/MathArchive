#!/usr/bin/env python3
"""HWPX 파일 파서 — 수학 기출문제 문항 분리 및 구조화 (v2)

v2 변경사항:
- 최상위 <p>만 순회 (endNote 내부 중복 순회 제거)
- endNote = 해설/정답, 나머지 = 문제본문 (XML 구조 기반 분리)
- tbl(조건박스/보기박스), pic(그림) 등 모든 첨부자료를 문항에 포함
- 수식 변환 버그 수정 (sqrt-N, cases 중첩, BOX, oversqrt 등)

사용법:
    python scripts/parse_hwpx.py raw/파일명.hwpx              # 단일 파일
    python scripts/parse_hwpx.py raw/파일명.hwpx -o out.json   # 출력 지정
    python scripts/parse_hwpx.py raw/파일명.hwpx --debug       # 디버그 모드
"""

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# ── 네임스페이스 ──────────────────────────────────────────────
NS_SEC = "{http://www.hancom.co.kr/hwpml/2011/section}"
NS_PAR = "{http://www.hancom.co.kr/hwpml/2011/paragraph}"
NS_CORE = "{http://www.hancom.co.kr/hwpml/2011/core}"


# ── HWP Equation → LaTeX 변환 ────────────────────────────────
GREEK_MAP = {
    "alpha": r"\alpha", "beta": r"\beta", "gamma": r"\gamma",
    "delta": r"\delta", "epsilon": r"\epsilon", "zeta": r"\zeta",
    "eta": r"\eta", "theta": r"\theta", "iota": r"\iota",
    "kappa": r"\kappa", "lambda": r"\lambda", "mu": r"\mu",
    "nu": r"\nu", "xi": r"\xi", "pi": r"\pi",
    "rho": r"\rho", "sigma": r"\sigma", "tau": r"\tau",
    "upsilon": r"\upsilon", "phi": r"\phi", "chi": r"\chi",
    "psi": r"\psi", "omega": r"\omega",
    "Alpha": r"\Alpha", "Beta": r"\Beta", "Gamma": r"\Gamma",
    "Delta": r"\Delta", "Theta": r"\Theta", "Lambda": r"\Lambda",
    "Pi": r"\Pi", "Sigma": r"\Sigma", "Phi": r"\Phi",
    "Omega": r"\Omega",
}

SYMBOL_MAP = {
    "TIMES": r"\times", "times": r"\times",
    "CDOT": r"\cdot", "cdot": r"\cdot",
    "DIV": r"\div",
    "PM": r"\pm", "pm": r"\pm",
    "MP": r"\mp",
    "LEQ": r"\leq", "leq": r"\leq", "le": r"\leq",
    "GEQ": r"\geq", "geq": r"\geq", "ge": r"\geq",
    "NEQ": r"\neq", "neq": r"\neq", "ne": r"\neq",
    "APPROX": r"\approx",
    "EQUIV": r"\equiv",
    "SIM": r"\sim",
    "THEREFORE": r"\therefore", "therefore": r"\therefore",
    "BECAUSE": r"\because",
    "TRIANGLE": r"\triangle",
    "ANGLE": r"\angle",
    "PERP": r"\perp", "perp": r"\perp",
    "PARALLEL": r"\parallel",
    "INFTY": r"\infty", "infty": r"\infty",
    "BULLET": r"\bullet",
    "CDOTS": r"\cdots", "cdots": r"\cdots",
    "LDOTS": r"\ldots", "ldots": r"\ldots",
    "VDOTS": r"\vdots",
    "DDOTS": r"\ddots",
    "FORALL": r"\forall",
    "EXISTS": r"\exists",
    "IN": r"\in",
    "SUBSET": r"\subset",
    "SUPSET": r"\supset",
    "CUP": r"\cup",
    "CAP": r"\cap",
    "EMPTYSET": r"\emptyset",
    "RIGHTARROW": r"\rightarrow",
    "LEFTARROW": r"\leftarrow",
    "LEFTRIGHTARROW": r"\leftrightarrow",
}

# LaTeX 명령으로 보존해야 하는 화이트리스트
_LATEX_KEEP = {
    "frac", "sqrt", "overline", "underline", "left", "right",
    "times", "cdot", "div", "pm", "mp", "leq", "geq", "neq",
    "approx", "equiv", "sim", "therefore", "because",
    "triangle", "angle", "perp", "parallel", "infty",
    "alpha", "beta", "gamma", "delta", "epsilon", "zeta",
    "eta", "theta", "iota", "kappa", "lambda", "mu",
    "nu", "xi", "pi", "rho", "sigma", "tau",
    "upsilon", "phi", "chi", "psi", "omega",
    "Gamma", "Delta", "Theta", "Lambda", "Pi", "Sigma", "Phi", "Omega",
    "mathrm", "mathbf", "mathit", "mathbb", "begin", "end",
    "rightarrow", "leftarrow", "leftrightarrow",
    "cdots", "ldots", "vdots", "ddots", "bullet",
    "in", "subset", "supset", "cup", "cap", "emptyset",
    "forall", "exists", "hat", "vec", "dot", "ddot", "tilde",
    "overrightarrow", "overleftarrow",
    "circ", "degree", "neq", "ne", "le", "ge", "boxed",
}


def _balance_braces(t: str) -> str:
    """괄호 짝 보정: 매칭 안 되는 '}'를 제거하고 남은 '{'에 '}'를 추가."""
    bad = []
    depth = 0
    for i, ch in enumerate(t):
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth == 0:
                bad.append(i)
            else:
                depth -= 1
    if bad:
        arr = list(t)
        for i in reversed(bad):
            del arr[i]
        t = "".join(arr)
    depth = 0
    for ch in t:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
    if depth > 0:
        t = t + ("}" * depth)
    return t


def _strip_outer_braces(tok: str) -> str:
    """operand 토큰의 가장 바깥쪽 {...} 한 겹만 제거."""
    tok = tok.strip()
    if tok.startswith("{") and tok.endswith("}"):
        depth = 0
        for i, ch in enumerate(tok):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0 and i < len(tok) - 1:
                    return tok
        return tok[1:-1]
    return tok


def hwp_eq_to_latex(script: str) -> str:
    """HWP 수식편집기 스크립트를 LaTeX로 변환한다."""
    if not script:
        return ""

    s = script.strip()

    # 0) 전처리: 붙어있는 키워드 분리 (}over{, 2overX, overY 등)
    #    LaTeX 명령(overline, overrightarrow, overleftarrow)은 보존.
    #    좌우 양쪽이 붙어있는 경우: 양쪽에 공백 삽입
    _OVER_KEEP = r"(?!line|right|left)"
    s = re.sub(rf"([A-Za-z0-9}}\)\]])over{_OVER_KEEP}(\{{|\(|\[|\\|-|\d)", r"\1 over \2", s)
    s = re.sub(rf"([A-Za-z0-9}}\)\]])over{_OVER_KEEP}([A-Za-z])(?![A-Za-z])", r"\1 over \2", s)
    #    우측만 붙어있는 경우 (예: `2 overa` → `2 over a`)
    s = re.sub(rf"(?<![A-Za-z])over{_OVER_KEEP}([0-9\(\[])", r"over \1", s)
    s = re.sub(rf"(?<![A-Za-z])over{_OVER_KEEP}([A-Za-z])(?![A-Za-z])", r"over \1", s)

    # 1) LEFT / RIGHT 괄호 (대소문자 모두)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\(", r"\\left(", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\)", r"\\right)", s)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\[", r"\\left[", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\]", r"\\right]", s)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\{", r"\\left\\{", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\}", r"\\right\\}", s)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\|", r"\\left|", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\|", r"\\right|", s)
    # LEFT. / RIGHT. (보이지 않는 delimiter)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\.", r"\\left.", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\.", r"\\right.", s)

    # 2) cases 환경: cases{...#...} → \begin{cases}...\\ ...\end{cases}
    #    중첩 중괄호를 수동 매칭으로 처리
    def _find_matching_brace(text, start):
        """start 위치의 '{'에 대응하는 '}' 위치를 반환."""
        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    return i
        return -1

    # cases 반복 처리
    for _ in range(5):
        m = re.search(r"\bcases\s*\{", s)
        if not m:
            break
        brace_start = m.end() - 1
        brace_end = _find_matching_brace(s, brace_start)
        if brace_end == -1:
            break
        inner = s[brace_start + 1:brace_end]
        lines = inner.split("#")
        converted = " \\\\ ".join(lines)
        s = s[:m.start()] + r"\begin{cases}" + converted + r"\end{cases}" + s[brace_end + 1:]

    # 3) 분수: {num} over {den} → \frac{num}{den} (중첩 허용)
    for _ in range(5):
        new_s = re.sub(
            r"\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*over\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
            r"\\frac{\1}{\2}", s
        )
        if new_s == s:
            break
        s = new_s

    # 3-b) 중괄호 없는 over: 확장된 OPERAND (sqrt/root 포함)
    #      +/- 부호는 분수 밖 연산자이므로 OPERAND에 포함하지 않음
    SQRT_TOK = r"(?:\\?(?:sqrt|root)\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})"
    SQRT_BARE = r"(?:\\?(?:sqrt|root)-?[A-Za-z0-9]+)"  # root3, root-3 등
    SUP_SUB = r"(?:[\^_](?:\{[^{}]*\}|[A-Za-z0-9]))*"  # ^2, ^{n+1}, _k 등
    # over 기반 분수 분자/분모 후보 토큰. LaTeX 명령의 꼬리(line/right/left)를
    # 제외해 `x overline{y}` 같은 입력에서 line이 분모로 잡히는 사고 방지.
    SIMPLE_TOK = rf"(?:(?!(?:line|right|left)\b)[A-Za-z0-9]+{SUP_SUB})"
    BRACE_TOK = r"(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})"
    # 소괄호 그룹 (지수/첨자 후속 허용): (b+c), (b+c)^2 등
    PAREN_TOK = rf"(?:\([^()]*(?:\([^()]*\)[^()]*)*\){SUP_SUB})"
    OPERAND = rf"(?:{SQRT_TOK}|{SQRT_BARE}|{BRACE_TOK}|{PAREN_TOK}|{SIMPLE_TOK})"
    over_no_brace = re.compile(rf"({OPERAND})\s*over\s*({OPERAND})")
    for _ in range(5):
        new_s = over_no_brace.sub(
            lambda m: r"\frac{" + _strip_outer_braces(m.group(1).strip()) +
                      r"}{" + _strip_outer_braces(m.group(2).strip()) + r"}",
            s,
        )
        if new_s == s:
            break
        s = new_s

    # 4) root → sqrt 별칭
    s = re.sub(r"(?<![A-Za-z])root\s*\{", r"sqrt{", s)
    s = re.sub(
        r"(?<![A-Za-z])root\s*(-?\s*[A-Za-z0-9]+)",
        lambda m: r"sqrt{" + m.group(1).replace(" ", "") + r"}",
        s,
    )
    s = re.sub(r"(\d)sqrt\{", r"\1 sqrt{", s)

    # 5) sqrt → \sqrt (중괄호 있는 경우)
    s = re.sub(r"\bsqrt\s*\{", r"\\sqrt{", s)
    # sqrt 중괄호 없는 경우: sqrt(expr), sqrt-N, sqrtN
    s = re.sub(r"\bsqrt\s*\(([^)]+)\)", r"\\sqrt{\1}", s)
    s = re.sub(r"\bsqrt\s*(-[A-Za-z0-9]+)", r"\\sqrt{\1}", s)
    s = re.sub(r"\bsqrt\s+([A-Za-z0-9])", r"\\sqrt{\1}", s)
    # sqrtN (붙어있는 경우)
    s = re.sub(r"\bsqrt([0-9])", r"\\sqrt{\1}", s)

    # 6) bar → overline
    s = re.sub(r"\bbar\s*\{", r"\\overline{", s)
    s = re.sub(
        r"\bbar\s+([A-Za-z]\w*)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )

    # 7) hat, vec, dot, ddot, tilde
    for accent in ["hat", "vec", "dot", "ddot", "tilde"]:
        s = re.sub(rf"\b{accent}\s*\{{", rf"\\{accent}{{", s)

    # 8) rm{...} → \mathrm{...}
    s = re.sub(r"\brm\s*\{", r"\\mathrm{", s)
    s = re.sub(r"\brm\s*([A-Za-z]\w*)", lambda m: f"\\mathrm{{{m.group(1)}}}", s)

    # 9) BOX{...} → \boxed{...}
    s = re.sub(r"\bBOX\s*\{", r"\\boxed{", s)
    s = re.sub(r"\bbox\s*\{", r"\\boxed{", s)

    # 10) prime → '
    s = re.sub(r"\bprime\b", "'", s)

    # 11) it (italic) — LaTeX 수학모드 기본이므로 제거
    s = re.sub(r"\bit\s+", "", s)
    s = re.sub(r"\bit(?=[+-])", "", s)
    s = re.sub(r"\bit\b", "", s)

    # 12) 그리스 문자
    # 전처리: 붙어있는 그리스문자명 분리 (alphabeta → alpha beta)
    _greek_names = sorted(GREEK_MAP.keys(), key=len, reverse=True)
    _greek_pat = "|".join(_greek_names)
    for _ in range(3):  # 3개 이상 연속 대비
        s_new = re.sub(rf"({_greek_pat})({_greek_pat})", r"\1 \2", s)
        if s_new == s:
            break
        s = s_new
    for hwp, latex in GREEK_MAP.items():
        s = re.sub(rf"\b{hwp}\b", lambda m, r=latex: r, s)

    # 13) 기호
    for hwp, latex in SYMBOL_MAP.items():
        s = re.sub(rf"\b{hwp}\b", lambda m, r=latex: r, s)

    # 14) ` → \, (thin space), ~ → 일반 공백
    s = s.replace("`", r"\,")
    s = re.sub(r"~+", " ", s)

    # 15) & 제거, # → \\
    s = s.replace("&", "")
    s = re.sub(r"\s*#\s*", r" \\\\ ", s)

    # 16) 끝에 매달린 단독 백슬래시 제거
    s = re.sub(r"\\(?=\s|$)", "", s)
    s = re.sub(r"\\$", "", s)

    # 17) 괄호 짝 보정
    s = _balance_braces(s)

    # 18) 후처리
    s = _postprocess_latex(s)

    # 19) 남은 over 강제 처리
    s = re.sub(
        r"(\{[^{}]*\}|[A-Za-z0-9+\-]+)\s*over\s*(\{[^{}]*\}|[A-Za-z0-9+\-]+)",
        lambda m: r"\frac{" + _strip_outer_braces(m.group(1)) + r"}{" + _strip_outer_braces(m.group(2)) + r"}",
        s,
    )
    # 최종 방어선: 남은 단독 over 키워드(양옆이 영문자 아님)는 '/'로 변환
    # (중괄호 짝 불균형·다토큰 분모 등 원본이 비정상인 케이스 대비).
    # overline/overrightarrow 등 LaTeX 명령은 영문자 연속이라 매치 안 됨.
    s = re.sub(r"(?<![A-Za-z\\])over(?![A-Za-z])", " / ", s)

    # 20) 남은 bar, root
    s = re.sub(
        r"\bbar\s*([A-Za-z]\w*)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    s = re.sub(
        r"\broot\s*(-?[A-Za-z0-9]+)",
        lambda m: r"\sqrt{" + m.group(1) + r"}",
        s,
    )
    s = re.sub(r"\broot\b", r"\\sqrt", s)

    # 21) 불필요한 다중 공백 정리
    s = re.sub(r"  +", " ", s)

    return s.strip()


def _postprocess_latex(s: str) -> str:
    """변환된 LaTeX 문자열의 잔여 HWP 키워드를 정리한다."""
    s = s.replace(r"\(", "(").replace(r"\)", ")")
    s = s.replace(r"\{", "{").replace(r"\}", "}")

    # tri angle → \triangle
    s = re.sub(r"\btri\s+angle\b", lambda m: r"\triangle", s)
    s = re.sub(r"\bTRI\s+ANGLE\b", lambda m: r"\triangle", s)
    s = re.sub(r"\btri\s*\\angle", lambda m: r"\triangle", s)

    # 소문자 right/left 잔여
    s = re.sub(r"(?<![A-Za-z\\])right(?=\s*[\)\]\|\}])", "", s)
    s = re.sub(r"(?<![A-Za-z\\])left(?=\s*[\(\[\|\{])", "", s)

    # 긴 키워드 우선 변환
    for kw, latex in (
        ("TRIANGLE", r"\triangle "), ("triangle", r"\triangle "),
        ("CDOTS", r"\cdots "), ("cdots", r"\cdots "),
        ("LDOTS", r"\ldots "), ("ldots", r"\ldots "),
    ):
        s = re.sub(rf"(?<![A-Za-z\\]){kw}", lambda m, r=latex: r, s)

    # 결합 키워드 분리
    for kw in ("ANGLE", "TIMES", "CDOT", "RIGHT", "LEFT", "BAR", "RM", "DEG",
               "angle", "times", "cdot", "perp", "infty", "circ"):
        s = re.sub(rf"(?<=[A-Za-z0-9])(?<!\\){kw}", r" " + kw, s)
        s = re.sub(rf"(?<!\\){kw}(?=[A-Za-z0-9])", kw + r" ", s)

    # it 잔여
    s = re.sub(r"\bit(?=[A-Za-z])", "", s)
    s = re.sub(r"\bit\s+", "", s)

    # HWP 기호 키워드 → LaTeX
    KEYWORD_MAP = {
        "ANGLE": r"\angle ", "angle": r"\angle ",
        "TIMES": r"\times ", "times": r"\times ",
        "CDOT": r"\cdot ", "cdot": r"\cdot ",
        "DEG": r"^{\circ}", "deg": r"^{\circ}",
        "circ": r"\circ ",
        "PERP": r"\perp ", "perp": r"\perp ",
        "PARALLEL": r"\parallel ", "parallel": r"\parallel ",
        "INFTY": r"\infty ", "infty": r"\infty ",
        "THEREFORE": r"\therefore ", "therefore": r"\therefore ",
        "BECAUSE": r"\because ", "because": r"\because ",
    }
    for kw, latex in KEYWORD_MAP.items():
        s = re.sub(rf"\b{kw}\b", lambda m, r=latex: r, s)

    # tri \angle 결합 회수
    s = re.sub(r"\btri\s*\\angle", lambda m: r"\triangle", s)

    # over 잔여
    NESTED = r"\{(?:[^{}]|\{[^{}]*\})*\}"
    SQRT_TOK = r"\\?sqrt\{[^{}]*\}"
    OPERAND = rf"(?:{SQRT_TOK}|{NESTED}|[A-Za-z0-9]+)"
    s = re.sub(
        rf"({OPERAND})\s*over\s*({OPERAND})",
        lambda m: r"\frac{" + _strip_outer_braces(m.group(1)) +
                   r"}{" + _strip_outer_braces(m.group(2)) + r"}",
        s,
    )
    # 최종 방어선: 남은 단독 over 키워드(양옆이 영문자 아님)는 '/'로 변환
    # (중괄호 짝 불균형·다토큰 분모 등 원본이 비정상인 케이스 대비).
    # overline/overrightarrow 등 LaTeX 명령은 영문자 연속이라 매치 안 됨.
    s = re.sub(r"(?<![A-Za-z\\])over(?![A-Za-z])", " / ", s)

    # bar/root 잔여
    s = re.sub(
        r"(?i)\bbar(?:\s+|(?=[A-Za-z]))([A-Za-z]\w*)",
        lambda m: r"\overline{" + m.group(1) + "}",
        s,
    )
    s = re.sub(
        r"(?<![A-Za-z])root\s*(-?[A-Za-z0-9]+)",
        lambda m: r"\sqrt{" + m.group(1) + "}",
        s,
    )
    s = re.sub(r"(?<![A-Za-z])root\b", r"\\sqrt", s)

    # times 결합
    s = re.sub(r"(?i)\btimes(?=[A-Za-z])", r"\\times ", s)

    # rm 잔여
    s = re.sub(r"(?i)\brm(?=[A-Za-z])", "", s)
    s = re.sub(r"(?i)\brm\s+(?=\\)", "", s)
    s = re.sub(r"(?i)\brm\b\s*", "", s)

    # RIGHT/LEFT 잔여
    s = re.sub(r"(?i)RIGHT\s*\|", r"\\right|", s)
    s = re.sub(r"(?i)LEFT\s*\|", r"\\left|", s)
    s = re.sub(r"(?i)\bRIGHT\b", "", s)
    s = re.sub(r"(?i)\bLEFT\b", "", s)

    # 비교 연산자
    s = s.replace("!=", r"\neq ")

    # 알 수 없는 백슬래시 명령 정리
    def _strip_unknown(m):
        name = m.group(1)
        return m.group(0) if name in _LATEX_KEEP else name
    s = re.sub(r"\\([A-Za-z]+)", _strip_unknown, s)

    # 중첩 백슬래시 정리
    s = re.sub(r"\\{2,}(?=[A-Za-z])", r"\\", s)

    return s


# ── 파일명 메타데이터 파싱 ────────────────────────────────────
def parse_filename_metadata(filename: str) -> dict:
    """파일명에서 메타데이터를 추출한다."""
    meta = {}
    brackets = re.findall(r"\[([^\]]+)\]", filename)
    if len(brackets) >= 6:
        meta["school_level"] = brackets[0]
        meta["year"] = brackets[1]
        grade_parts = brackets[2].split("-")
        if len(grade_parts) >= 3:
            meta["grade"] = grade_parts[0]
            meta["semester"] = grade_parts[1]
            meta["exam_type"] = grade_parts[2]
        meta["region"] = brackets[3]
        meta["school"] = brackets[4]
        meta["subject"] = brackets[5]
        for b in brackets[6:]:
            if re.search(r"[가-힣].*[-~].*[가-힣]", b):
                meta["chapter_range"] = b
                break
    return meta


# ── XML 파싱: ContentItem ─────────────────────────────────────
class ContentItem:
    """단락 내 하나의 콘텐츠 요소."""
    __slots__ = ("kind", "text", "image_ref", "hwp_eq", "latex")

    def __init__(self, kind, text="", image_ref="", hwp_eq="", latex=""):
        self.kind = kind
        self.text = text
        self.image_ref = image_ref
        self.hwp_eq = hwp_eq
        self.latex = latex

    def __repr__(self):
        if self.kind == "text":
            return f'T:"{self.text[:40]}"'
        if self.kind == "equation":
            return f'EQ:"{self.latex[:40]}"'
        return f'IMG:{self.image_ref}'


def _is_watermark_equation(eq_elem) -> bool:
    """워터마크/로고 수식인지 판별한다."""
    color = eq_elem.attrib.get("textColor", "")
    if color == "#FFFFFF":
        return True
    script_el = eq_elem.find(NS_PAR + "script")
    if script_el is not None and script_el.text:
        raw = script_el.text.strip()
        if "N.G.D" in raw or "무단" in raw or "공동 작업" in raw or "공동 저작" in raw:
            return True
    return False


def _is_watermark_pic(pic_elem) -> bool:
    """워터마크/로고 이미지인지 판별한다."""
    pos_el = pic_elem.find(NS_PAR + "pos")
    if pos_el is not None and pos_el.attrib.get("treatAsChar", "1") == "0":
        return True
    return False


def _process_equation(eq_elem, items):
    """수식 요소를 처리하여 items에 추가한다."""
    if _is_watermark_equation(eq_elem):
        return
    script_el = eq_elem.find(NS_PAR + "script")
    if script_el is None or not script_el.text:
        return
    raw = script_el.text
    raw = re.split(r"\n\s*\n", raw)[0].strip()
    clean = re.sub(r"\s+", "", raw)
    if not clean or re.fullmatch(r"To\d+", clean):
        return
    latex = hwp_eq_to_latex(raw)
    items.append(ContentItem("equation", hwp_eq=raw, latex=latex))


def _process_pic(pic_elem, items):
    """이미지 요소를 처리하여 items에 추가한다."""
    if _is_watermark_pic(pic_elem):
        return
    img_el = pic_elem.find(".//" + NS_CORE + "img")
    if img_el is not None:
        ref = img_el.attrib.get("binaryItemIDRef", "")
        if ref:
            items.append(ContentItem("image", image_ref=ref))


def _process_tbl(tbl_elem, items):
    """테이블 요소를 <tr>/<tc> 구조 그대로 직렬화한다.
    - 행(<tr>) 내 셀(<tc>)은 공백으로 구분하고, 행 끝에만 줄바꿈을 붙여
      조립제법 같은 가로 배치 표가 세로로 무너지는 것을 막는다.
    - <<BOX_START>>/<<BOX_END>> 마커로 감싸 UI에서 박스 표현에 활용."""
    items.append(ContentItem("text", text="\n<<BOX_START>>\n"))
    rows = tbl_elem.findall(NS_PAR + "tr")
    if not rows:
        # 비정상 구조 방어: tr이 없으면 평탄화 처리
        rows_fallback = [tbl_elem]
        use_tr = False
    else:
        rows_fallback = rows
        use_tr = True

    for tr in rows_fallback:
        cells = tr.findall(NS_PAR + "tc") if use_tr else list(tr.iter(NS_PAR + "tc"))
        first_cell = True
        for tc in cells:
            if not first_cell:
                items.append(ContentItem("text", text="  "))
            first_cell = False
            cell_paras = tc.findall(NS_PAR + "subList/" + NS_PAR + "p")
            for pi, p in enumerate(cell_paras):
                if pi > 0:
                    items.append(ContentItem("text", text=" "))
                for run in p.findall(NS_PAR + "run"):
                    _process_run_no_endnote(run, items)
        items.append(ContentItem("text", text="\n"))
    items.append(ContentItem("text", text="<<BOX_END>>\n"))


def _process_run_no_endnote(run_elem, items):
    """<run> 요소를 처리하되, endNote는 건너뛴다."""
    for child in run_elem:
        tag = child.tag.split("}")[-1]

        if tag == "t":
            if child.text:
                items.append(ContentItem("text", text=child.text))

        elif tag == "equation":
            _process_equation(child, items)

        elif tag == "pic":
            _process_pic(child, items)

        elif tag == "rect":
            for dt in child.iter(NS_PAR + "drawText"):
                for sl in dt.iter(NS_PAR + "subList"):
                    for p in sl.findall(NS_PAR + "p"):
                        for run in p.findall(NS_PAR + "run"):
                            _process_run_no_endnote(run, items)
                    items.append(ContentItem("text", text="\n"))

        elif tag == "tbl":
            _process_tbl(child, items)

        elif tag == "ctrl":
            for sub in child:
                stag = sub.tag.split("}")[-1]
                if stag == "endNote":
                    continue  # endNote는 별도 처리
                elif stag == "pic":
                    _process_pic(sub, items)
                elif stag == "equation":
                    _process_equation(sub, items)
                elif stag == "tbl":
                    _process_tbl(sub, items)


def _process_endnote(endnote_elem, answer_items, solution_items):
    """endNote 내부를 처리: 첫 번째 p → 정답, 나머지 → 해설."""
    # subList 직속 <p>만 가져옴 (테이블 셀 내부 <p> 중복 순회 방지)
    inner_ps = list(endnote_elem.findall(NS_PAR + "subList/" + NS_PAR + "p"))
    for idx, p in enumerate(inner_ps):
        target = answer_items if idx == 0 else solution_items
        for run in p.findall(NS_PAR + "run"):
            _process_run_no_endnote(run, target)
        target.append(ContentItem("text", text="\n"))


# ── 콘텐츠 직렬화 ────────────────────────────────────────────
def serialize_items(items: list) -> str:
    """ContentItem 리스트를 문자열로 합친다."""
    parts = []
    last_was_eq = False
    for item in items:
        if item.kind == "text":
            parts.append(item.text)
            if item.text.strip():
                last_was_eq = False
        elif item.kind == "equation":
            rendered = f"${item.latex}$"
            if last_was_eq:
                parts.append(" ")
            parts.append(rendered)
            last_was_eq = True
        elif item.kind == "image":
            parts.append(f"<<IMG:{item.image_ref}>>")
            last_was_eq = False
    return "".join(parts)


def sanitize_outside_math(text: str) -> str:
    """수식($...$) 바깥은 백슬래시 정리, 안쪽은 LaTeX 잔여 정리."""
    parts = re.split(r"(\$[^$]*\$)", text)
    for i, p in enumerate(parts):
        if i % 2 == 0:
            parts[i] = _sanitize_text_node(p)
        else:
            inner = p[1:-1]
            inner = _postprocess_latex(inner)
            open_b = inner.count("{")
            close_b = inner.count("}")
            if open_b > close_b:
                inner = inner + ("}" * (open_b - close_b))
            elif close_b > open_b:
                extra = close_b - open_b
                inner = re.sub(r"\}(?=[^{}]*$)", "", inner, count=extra)
            parts[i] = "$" + inner + "$"
    return "".join(parts)


def _sanitize_text_node(text: str) -> str:
    """본문 텍스트의 HWP 잔여 키워드를 정리한다."""
    def fix(m):
        name = m.group(1)
        if name in _LATEX_KEEP:
            return m.group(0)
        return name
    text = re.sub(r"\\([A-Za-z]+)", fix, text)
    text = re.sub(r"(RIGHT|LEFT)\s*[\)\]\|\}]?", "", text)
    text = re.sub(r"\b(RM|BAR|ANGLE|DEG)\b", "", text)
    text = text.replace(r"\(", "(").replace(r"\)", ")")
    text = text.replace(r"\{", "{").replace(r"\}", "}")
    return text


# ── 문항 구조화: XML 구조 기반 (v2 핵심) ─────────────────────

# 원 번호 → 숫자
CIRCLE_NUM = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}
CIRCLES = ["①", "②", "③", "④", "⑤"]

# 중단원명 정규화
CHAPTER_NORMALIZE = {
    "다항함수": "이차함수",
    "항등식과 나머니정리": "항등식과 나머지정리",
    "항등식과 나머지 정리": "항등식과 나머지정리",
    "나머지정리": "항등식과 나머지정리",
    "나머지 정리": "항등식과 나머지정리",
}

POINTS_PATTERN = re.compile(r"\[\s*\$?([\d.]+)\$?\s*점\s*\]")


def parse_answer_value(raw: str) -> dict:
    """정답 문자열을 파싱한다."""
    raw = raw.strip()
    for circle, num in CIRCLE_NUM.items():
        if circle in raw:
            return {"answer": str(num), "answer_type": "choice"}
    m = re.search(r"\$\s*([\d/.\-]+)\s*\$", raw)
    if m:
        return {"answer": m.group(1), "answer_type": "short_answer"}
    m = re.search(r"([\d/.\-]+)", raw)
    if m:
        return {"answer": m.group(1), "answer_type": "short_answer"}
    return {"answer": raw.strip(), "answer_type": "unknown"}


def _split_compressed_values(block: str) -> list:
    """압축된 선택지 값을 분리한다."""
    block = block.strip()
    if not block:
        return []
    vals = re.findall(r"\$([^$]+)\$", block)
    if vals:
        return [f"${v.strip()}$" for v in vals if v.strip()]
    parts = [p.strip() for p in re.split(r"\$\$+|\s{2,}|\t", block) if p.strip()]
    return parts


def extract_choices(text: str) -> list:
    """선택지를 추출한다."""
    found = []
    for c in CIRCLES:
        for m in re.finditer(re.escape(c), text):
            found.append((m.start(), CIRCLE_NUM[c]))
    if not found:
        return []
    found.sort()

    choices = []
    for i, (pos, num) in enumerate(found):
        start = pos + 1
        end = found[i + 1][0] if i + 1 < len(found) else len(text)
        block = text[start:end]
        if i + 1 >= len(found):
            block = block.split("\n")[0]
        vals = _split_compressed_values(block)
        if not vals:
            continue
        next_num = found[i + 1][1] if i + 1 < len(found) else None
        for j, v in enumerate(vals):
            target = num + j
            if next_num is not None and target >= next_num:
                break
            choices.append({"number": target, "text": v})

    seen = {}
    for c in choices:
        seen.setdefault(c["number"], c)
    return [seen[k] for k in sorted(seen)]


def _extract_questions_from_xml(section_root, watermark_images, debug=False):
    """section0.xml의 최상위 <p>를 순회하여 문항 리스트를 반환한다.

    각 문항 = endNote P(정답+해설) + 이후 P들(본문, 조건박스, 그림, 선택지)
    → [중단원]/[난이도]까지 한 세트.
    """
    top_ps = list(section_root.findall(NS_PAR + "p"))

    if debug:
        print(f"[DEBUG] Total top-level <p>: {len(top_ps)}", file=sys.stderr)

    # 1단계: 각 P를 분류하고 콘텐츠 추출
    paragraphs = []  # list of dicts with role, items, etc.

    for p_idx, p_elem in enumerate(top_ps):
        # endNote 존재 여부 확인
        endnote_elem = None
        for run in p_elem.findall(NS_PAR + "run"):
            for child in run:
                tag = child.tag.split("}")[-1]
                if tag == "ctrl":
                    for sub in child:
                        if sub.tag.split("}")[-1] == "endNote":
                            endnote_elem = sub
                            break

        if endnote_elem is not None:
            # endNote가 있는 P: 정답+해설(endNote 내부) + 문제시작(외부)
            answer_items = []
            solution_items = []
            question_items = []

            _process_endnote(endnote_elem, answer_items, solution_items)

            # endNote 외부의 콘텐츠 = 문제 본문 시작
            for run in p_elem.findall(NS_PAR + "run"):
                _process_run_no_endnote(run, question_items)

            # 같은 P 안의 tbl (endNote 안이 아닌 것)
            for run in p_elem.findall(NS_PAR + "run"):
                for child in run:
                    tag = child.tag.split("}")[-1]
                    if tag == "tbl":
                        _process_tbl(child, question_items)
                    elif tag == "ctrl":
                        for sub in child:
                            stag = sub.tag.split("}")[-1]
                            if stag == "tbl":
                                _process_tbl(sub, question_items)

            paragraphs.append({
                "index": p_idx,
                "role": "endnote",
                "answer_items": answer_items,
                "solution_items": solution_items,
                "question_items": question_items,
            })
        else:
            # endNote 없는 일반 P
            items = []
            has_tbl = False
            has_pic = False

            for run in p_elem.findall(NS_PAR + "run"):
                _process_run_no_endnote(run, items)

            # 직접 자식으로 tbl/pic이 있는 경우도 처리
            for child in p_elem:
                tag = child.tag.split("}")[-1]
                if tag == "tbl":
                    has_tbl = True
                    _process_tbl(child, items)
                elif tag == "run":
                    for sub in child:
                        stag = sub.tag.split("}")[-1]
                        if stag == "tbl":
                            has_tbl = True
                        elif stag == "pic":
                            has_pic = True
                        elif stag == "ctrl":
                            for ss in sub:
                                if ss.tag.split("}")[-1] == "tbl":
                                    has_tbl = True
                                elif ss.tag.split("}")[-1] == "pic":
                                    has_pic = True

            items.append(ContentItem("text", text="\n"))

            text = serialize_items(items).strip()

            role = "body"
            if re.match(r"\[중단원\]", text):
                role = "chapter"
            elif re.match(r"\[난이도\]", text):
                role = "difficulty"
            elif re.match(r"\[문제\s*오류\]", text):
                role = "error"
            elif not text:
                role = "empty"

            paragraphs.append({
                "index": p_idx,
                "role": role,
                "items": items,
                "text": text,
                "has_tbl": has_tbl,
                "has_pic": has_pic,
            })

    # 2단계: endNote P를 기준으로 문항 블록 구성
    questions = []
    endnote_indices = [i for i, p in enumerate(paragraphs) if p["role"] == "endnote"]

    for en_pos, en_idx in enumerate(endnote_indices):
        en_para = paragraphs[en_idx]

        # 정답 파싱
        answer_text = serialize_items(en_para["answer_items"]).strip()
        # [정답] 제거
        answer_raw = re.sub(r"\[정답\]\s*", "", answer_text).strip()
        answer_info = parse_answer_value(answer_raw)

        # 해설
        solution_items = en_para["solution_items"]
        solution_text = serialize_items(solution_items).strip()

        # 문제 본문: endNote P의 외부 콘텐츠 + 이후 P들 (다음 endNote 전까지)
        question_items = list(en_para["question_items"])

        # 다음 endNote 위치 (또는 끝)
        next_en_idx = endnote_indices[en_pos + 1] if en_pos + 1 < len(endnote_indices) else len(paragraphs)

        chapter = ""
        difficulty = ""
        error_note = ""
        is_subjective = False
        subjective_num = None
        points = None

        # 이후 P들 순회
        for p_idx in range(en_idx + 1, next_en_idx):
            para = paragraphs[p_idx]
            text = para.get("text", "")

            if para["role"] == "chapter":
                if not chapter:  # 첫 번째 [중단원]만 사용 (편집메모 방지)
                    ch_match = re.search(r"\[중단원\]\s*(.+?)(?:\n|$)", text)
                    if ch_match:
                        chapter = ch_match.group(1).strip()
                        chapter = CHAPTER_NORMALIZE.get(chapter, chapter)
                continue

            if para["role"] == "difficulty":
                diff_match = re.search(r"\[난이도\]\s*(.+?)(?:\n|$)", text)
                if diff_match:
                    difficulty = diff_match.group(1).strip()
                continue

            if para["role"] == "error":
                err_match = re.search(r"\[문제\s*오류\]\s*(.*?)(?:\n|$)", text)
                if err_match:
                    error_note = err_match.group(1).strip()
                continue

            if para["role"] == "empty":
                continue

            # 서답형 감지
            subj_match = re.search(r"\[서[답술]형\s*(\d+)\]", text)
            if subj_match:
                is_subjective = True
                subjective_num = int(subj_match.group(1))
            if re.search(r"서[답술]형\s*문제", text):
                is_subjective = True

            # 본문 P → 문제에 추가
            question_items.extend(para.get("items", []))

        # 문제 텍스트 직렬화
        question_text = serialize_items(question_items).strip()

        # 메타 패턴 제거
        meta_clean = re.compile(
            r"\[중단원\]\s*.+?(?:\n|$)|\[난이도\]\s*.+?(?:\n|$)"
            r"|\[문제\s*오류\].*?(?:\n|$)|\[서[답술]형\s*\d+\]\s*"
            r"|※\s*여기서\s*부터는\s*서[답술]형\s*문제입니다\.?\s*"
        )
        question_text = meta_clean.sub("", question_text).strip()

        # 저작권/프리앰블/편집메모 필터
        junk_pattern = re.compile(
            r"콘텐츠산업|NGD|무단.*복제|제작연월일|네이버카페|공동 저작"
            r"|<편집팀|편집팀\s*오검|오검내역|파일명의\s*단원|해\d+\.\s*-\s*부호"
        )
        if junk_pattern.search(question_text):
            lines = question_text.split("\n")
            filtered = [l for l in lines if not junk_pattern.search(l)]
            question_text = "\n".join(filtered).strip()

        # 배점 추출
        pts_match = POINTS_PATTERN.search(question_text)
        if pts_match:
            points = float(pts_match.group(1))

        # 선택지 추출
        choices = extract_choices(question_text)

        # 본문에서 선택지 제거
        if choices:
            question_text = _strip_choices_from_text(question_text)

        # 이미지 참조 추출
        image_refs = re.findall(r"<<IMG:(image\d+)>>", question_text)
        # 해설에서도 이미지 참조 추출 (해설에 그림이 있을 수 있음)
        sol_image_refs = re.findall(r"<<IMG:(image\d+)>>", solution_text)

        # 워터마크 이미지 제거
        image_refs = [r for r in image_refs if r not in watermark_images]
        sol_image_refs = [r for r in sol_image_refs if r not in watermark_images]

        # 수식 외 영역 정리
        question_text = sanitize_outside_math(question_text)
        solution_text = sanitize_outside_math(solution_text)
        for c in choices:
            c["text"] = sanitize_outside_math(c["text"])

        # 빈 줄 정리
        question_text = re.sub(r"\n{3,}", "\n\n", question_text).strip()
        solution_text = re.sub(r"\n{3,}", "\n\n", solution_text).strip()

        if debug:
            print(f"  Q{len(questions)+1}: answer={answer_info['answer']}, "
                  f"chapter={chapter}, diff={difficulty}, "
                  f"imgs={image_refs}, choices={len(choices)}", file=sys.stderr)

        questions.append({
            "question_number": len(questions) + 1,
            "answer": answer_info["answer"],
            "answer_type": answer_info["answer_type"],
            "is_subjective": is_subjective,
            "subjective_number": subjective_num,
            "points": points,
            "chapter": chapter,
            "difficulty": difficulty,
            "question_text": question_text,
            "solution_text": solution_text,
            "choices": choices,
            "image_refs": image_refs + sol_image_refs,
            "has_image": len(image_refs) > 0,
            "error_note": error_note,
        })

    return questions


def _strip_choices_from_text(text: str) -> str:
    """문제본문에서 선택지 부분(첫 ⃝번호 이후)을 제거한다."""
    m = re.search(r"[①②③④⑤]", text)
    if not m:
        return text.strip()
    return text[:m.start()].rstrip()


# ── 이미지 추출 ──────────────────────────────────────────────
def extract_images(hwpx_path: str, image_refs: set, output_dir: str,
                   file_stem: str) -> dict:
    """HWPX에서 문제용 이미지만 추출한다."""
    mapping = {}
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        for ref in image_refs:
            for name in zf.namelist():
                fname = os.path.basename(name)
                name_stem = os.path.splitext(fname)[0]
                if name_stem == ref and name.startswith("BinData/"):
                    ext = os.path.splitext(fname)[1]
                    out_name = f"{file_stem}_{ref}{ext}"
                    out_path = os.path.join(output_dir, out_name)
                    with zf.open(name) as src, open(out_path, "wb") as dst:
                        dst.write(src.read())
                    mapping[ref] = out_path
                    break
    return mapping


def get_masterpage_images(extract_dir: str) -> set:
    """masterpage0.xml에서 참조되는 이미지 ID를 반환한다."""
    refs = set()
    mp_path = os.path.join(extract_dir, "Contents", "masterpage0.xml")
    if not os.path.exists(mp_path):
        return refs
    content = open(mp_path, "r", encoding="utf-8").read()
    for m in re.findall(r'binaryItemIDRef="(image\d+)"', content):
        refs.add(m)
    return refs


# ── 메인 파싱 함수 ───────────────────────────────────────────
def parse_hwpx(hwpx_path: str, image_output_dir: str = None,
               debug: bool = False) -> dict:
    """HWPX 파일 하나를 파싱하여 구조화된 딕셔너리를 반환한다."""
    hwpx_path = os.path.abspath(hwpx_path)
    file_stem = Path(hwpx_path).stem

    file_meta = parse_filename_metadata(file_stem)

    tmp_dir = tempfile.mkdtemp(prefix="hwpx_")
    try:
        with zipfile.ZipFile(hwpx_path, "r") as zf:
            zf.extractall(tmp_dir)

        watermark_images = get_masterpage_images(tmp_dir)

        section_path = os.path.join(tmp_dir, "Contents", "section0.xml")
        if not os.path.exists(section_path):
            raise FileNotFoundError(f"section0.xml not found in {hwpx_path}")

        tree = ET.parse(section_path)
        root = tree.getroot()

        # XML 구조 기반 문항 추출 (v2)
        questions = _extract_questions_from_xml(
            root, watermark_images, debug=debug
        )

        # 모든 문항에서 참조하는 이미지 수집
        all_image_refs = set()
        for q in questions:
            all_image_refs.update(q["image_refs"])
        all_image_refs -= watermark_images

        # 이미지 추출
        image_mapping = {}
        if image_output_dir and all_image_refs:
            os.makedirs(image_output_dir, exist_ok=True)
            image_mapping = extract_images(
                hwpx_path, all_image_refs, image_output_dir, file_stem
            )

        # 이미지 경로 매핑
        for q in questions:
            q["image_paths"] = [
                image_mapping.get(ref, ref)
                for ref in q["image_refs"]
                if ref not in watermark_images
            ]

        return {
            "file_source": os.path.basename(hwpx_path),
            "file_metadata": file_meta,
            "total_questions": len(questions),
            "questions": questions,
        }

    finally:
        shutil.rmtree(tmp_dir, ignore_errors=True)


# ── CLI ──────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="HWPX 수학 기출문제 파서")
    parser.add_argument("hwpx_file", help="파싱할 HWPX 파일 경로")
    parser.add_argument("-o", "--output", help="출력 JSON 파일 경로")
    parser.add_argument("--image-dir", default="images",
                        help="이미지 추출 디렉토리 (기본: images)")
    parser.add_argument("--debug", action="store_true", help="디버그 출력")
    parser.add_argument("--no-images", action="store_true",
                        help="이미지 추출 건너뛰기")
    args = parser.parse_args()

    if not os.path.exists(args.hwpx_file):
        print(f"Error: 파일을 찾을 수 없습니다: {args.hwpx_file}", file=sys.stderr)
        sys.exit(1)

    img_dir = None if args.no_images else args.image_dir
    result = parse_hwpx(args.hwpx_file, image_output_dir=img_dir,
                        debug=args.debug)

    output_json = json.dumps(result, ensure_ascii=False, indent=2)

    if args.output:
        os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_json)
        print(f"저장 완료: {args.output} ({result['total_questions']}문항)",
              file=sys.stderr)
    else:
        print(output_json)

    # 요약 출력
    print(f"\n=== 파싱 요약 ===", file=sys.stderr)
    print(f"파일: {result['file_source']}", file=sys.stderr)
    print(f"문항 수: {result['total_questions']}", file=sys.stderr)
    for q in result["questions"]:
        subj = f" [서답형{q['subjective_number']}]" if q["is_subjective"] else ""
        err = " [오류]" if q["error_note"] else ""
        img = f" [그림{len(q['image_refs'])}]" if q["has_image"] else ""
        print(
            f"  Q{q['question_number']:2d}: 정답={q['answer']:>3s} "
            f"난이도={q['difficulty']:<2s} "
            f"단원={q['chapter']}"
            f"{subj}{err}{img}",
            file=sys.stderr
        )


if __name__ == "__main__":
    main()
