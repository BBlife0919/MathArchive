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
    "DIVIDE": r"\div", "divide": r"\div", "DIV": r"\div",
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
    "CUP": r"\cup", "cup": r"\cup",
    "CAP": r"\cap", "cap": r"\cap",
    "EMPTYSET": r"\emptyset", "emptyset": r"\emptyset",
    "RIGHTARROW": r"\rightarrow",
    "LEFTARROW": r"\leftarrow",
    "LEFTRIGHTARROW": r"\leftrightarrow",
    "TO": r"\to", "to": r"\to",
    "VERT": r"|", "vert": r"|",
    "MID": r"\mid", "mid": r"\mid",
}

# LaTeX 명령으로 보존해야 하는 화이트리스트
_LATEX_KEEP = {
    "frac", "dfrac", "tfrac", "cfrac",
    "sqrt", "overline", "underline", "left", "right",
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
    "square", "Box", "phantom",
}


def _strip_hwp_revision_history(script: str) -> str:
    """HWP 수식 개정 이력 래퍼 제거.

    HWP는 같은 수식의 이전 버전을 다음 형태로 중첩 저장한다:
        {{{...{<원본>} to <ws>{<ver_code_1>}} to <ws>{<ver_code_2>}} ... to <ws>{<ver_code_N>}}

    여기서 `<ver_code>`는 소문자+숫자 코드 (예: tgr510471, edr460488).
    N개의 래퍼는 각각 `{`를 하나씩 앞에 붙이고, 뒤에 `} to {ver}`을 하나씩 덧붙인다.
    → 원본 추출: N개의 선행 `{` 제거, 첫 `} to {ver}` 직전까지.
    """
    s = script
    # 이력 코드 개수 카운트
    n_codes = len(re.findall(
        r"\}\s*to\s*[\r\n\s]*\{[a-z][a-z0-9]{3,}\}", s
    ))
    if n_codes == 0:
        return script
    # 선행 whitespace 제거, N개의 '{' 벗기기
    s2 = s.lstrip()
    stripped = 0
    while stripped < n_codes and s2.startswith("{"):
        s2 = s2[1:]
        stripped += 1
    if stripped < n_codes:
        return script  # 구조가 기대와 다름: 원본 반환
    # 첫 `} to {ver_code}` 앞까지를 원본으로
    m = re.search(r"\}\s*to\s*[\r\n\s]*\{[a-z][a-z0-9]{3,}\}", s2)
    if not m:
        return script
    return s2[:m.start()].strip()


def _balance_braces(t: str) -> str:
    """괄호 짝 보정: 매칭 안 되는 '}'를 제거하고 남은 '{'에 '}'를 추가.

    `\\{` 과 `\\}` (delimiter 이스케이프)는 일반 중괄호 카운트에서 제외.
    """
    bad = []
    depth = 0
    i = 0
    while i < len(t):
        ch = t[i]
        # 이스케이프된 delimiter는 건너뜀 (\{, \})
        if ch == "\\" and i + 1 < len(t) and t[i + 1] in ("{", "}"):
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            if depth == 0:
                bad.append(i)
            else:
                depth -= 1
        i += 1
    if bad:
        arr = list(t)
        for i in reversed(bad):
            del arr[i]
        t = "".join(arr)
    # 남은 '{' 에 대한 닫기 추가 (이스케이프 제외 재계산)
    depth = 0
    i = 0
    while i < len(t):
        ch = t[i]
        if ch == "\\" and i + 1 < len(t) and t[i + 1] in ("{", "}"):
            i += 2
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        i += 1
    if depth > 0:
        t = t + ("}" * depth)
    return t


def _balance_left_right(t: str) -> str:
    """\\left / \\right 짝 보정.

    KaTeX는 \\left\\{ ... } 처럼 \\right 없이 닫히면 전체 수식이 빨간 에러로 렌더.
    짝 안 맞는 \\left 는 \\right\\}를 추가, 남는 \\right 는 \\left를 앞에 추가.
    """
    # 단순 카운트: `\left` 와 `\right` 개수
    n_left = len(re.findall(r"\\left(?![a-zA-Z])", t))
    n_right = len(re.findall(r"\\right(?![a-zA-Z])", t))
    if n_left == n_right:
        return t
    if n_left > n_right:
        # 부족한 \right 추가: 마지막 } 직전에 \right\} 삽입하거나 문자열 끝에 추가
        # 가장 안전한 것은 문자열 끝에 \right. 또는 \right\}
        # \left\{ 로 열렸다면 \right\} 를 끝에 추가
        missing = n_left - n_right
        # 가장 바깥쪽 \left 가 어떤 구분자로 열렸는지 확인
        lefts = re.findall(r"\\left\s*(\\[\{\}]|[\(\[\|\.]|\\\|)", t)
        closers = []
        for L in lefts[-missing:]:
            if L in (r"\{", r"\(", "("):
                closers.append(r"\right" + {"(": ")", r"\{": r"\}"}.get(L, ")"))
            elif L == "[":
                closers.append(r"\right]")
            elif L in ("|", r"\|"):
                closers.append(r"\right|")
            elif L == ".":
                closers.append(r"\right.")
            else:
                closers.append(r"\right.")
        return t + "".join(closers)
    else:
        # 남는 \right — 처음에 \left. 를 앞에 추가
        missing = n_right - n_left
        return (r"\left. " * missing) + t


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

    # 0-b) 붙어있는 HWP 키워드 분리 (alphabar → alpha bar, 3alpha → 3 alpha 등)
    #      영숫자·키워드 경계는 Python \b가 검출 못하므로 명시 분리.
    _all_hwp_kw = (
        sorted(GREEK_MAP.keys(), key=len, reverse=True)
        + ["bar", "rm", "RM", "it", "IT", "sqrt", "root", "leq", "geq", "neq",
           "le", "ge", "ne", "cdot", "cdots", "ldots", "vdots",
           "times", "pm", "mp", "infty", "angle", "triangle",
           "perp", "parallel", "therefore", "because",
           "vert", "VERT", "mid", "cap", "cup", "emptyset",
           "to", "TO", "DIVIDE", "divide",
           "LEFT", "RIGHT", "left", "right",
           "TIMES", "CDOT", "ANGLE", "PERP", "INFTY"]
    )
    _kw_pat = "|".join(_all_hwp_kw)
    # 키워드끼리 연속 (alphabar, gammadelta 등) — 여러 번 반복해 3개 이상 대비
    for _ in range(5):
        new = re.sub(rf"({_kw_pat})({_kw_pat})(?![A-Za-z])", r"\1 \2", s)
        if new == s:
            break
        s = new
    # 숫자 + 키워드 (3alpha, 2alphabeta 등) — 숫자 뒤 공백 삽입
    for _ in range(3):
        new = re.sub(rf"(\d)({_kw_pat})(?![A-Za-z])", r"\1 \2", s)
        if new == s:
            break
        s = new

    # 0-b2) 이항 키워드 + 단일 영문자 분리 (vertx → vert x, capx → cap x 등)
    #       집합 기호/절대값에서 자주 발생. 단일 영문자 뒤가 비영문자일 때만.
    _binary_kw = ["vert", "VERT", "cap", "cup", "mid", "emptyset",
                  "to", "TO", "DIVIDE", "divide"]
    _binary_pat = "|".join(_binary_kw)
    # 왼쪽: 영숫자/닫힘괄호 + kw → 공백 분리
    s = re.sub(rf"([A-Za-z0-9\}}\)\]])({_binary_pat})(?![A-Za-z])",
               r"\1 \2", s)
    # 오른쪽: kw + 영숫자 → 공백 분리 (단 후속이 여러 영문자면 단어일 수 있어 보호:
    #        vertical 같은 일반 단어 → 첫 2글자는 분리 안 함)
    s = re.sub(rf"(?<![A-Za-z])({_binary_pat})([A-Za-z])(?![A-Za-z])",
               r"\1 \2", s)
    s = re.sub(rf"(?<![A-Za-z])({_binary_pat})(\d)", r"\1 \2", s)

    # 0-c) 비교 연산자 le/ge/ne 접합 분리 (mle3, lekle1, 2ge5 등)
    #      HWP 수식에서는 이들이 비교기호로만 쓰이므로 영숫자와 붙으면 분리.
    #      단 left/leftarrow/leq/geq/neq/overline 같은 LaTeX·HWP 키워드 보호:
    #      - le 뒤 ft/q: left·leftarrow·leftrightarrow·leq 보호
    #      - ge 뒤 q:   geq 보호
    #      - ne 뒤 q/g: neq·neg 보호
    #      - overline·overrightarrow·overleftarrow: 이름 끝의 `ne`·`line` 보호
    _protected_cmds = [
        "overline", "overrightarrow", "overleftarrow",
        "underline", "underrightarrow", "underleftarrow",
    ]
    _cmd_stash = []
    def _stash_cmd(m):
        _cmd_stash.append(m.group(0))
        return f"\x01CMD{len(_cmd_stash)-1}\x02"
    _cmd_pat = re.compile(
        r"\\?(?:" + "|".join(_protected_cmds) + r")(?![A-Za-z])"
    )
    s = _cmd_pat.sub(_stash_cmd, s)

    for kw, keep in (("leq", ""), ("geq", ""), ("neq", ""),
                      ("le",  "(?!ft|q)"),
                      ("ge",  "(?!q)"),
                      ("ne",  "(?!q|g)")):
        s = re.sub(rf"(?<=[A-Za-z0-9]){kw}{keep}(?![A-Za-z])", rf" {kw}", s)
        s = re.sub(rf"(?<![A-Za-z\\]){kw}{keep}(?=[A-Za-z0-9])", rf"{kw} ", s)

    # 보호된 명령 복원
    for i, v in enumerate(_cmd_stash):
        s = s.replace(f"\x01CMD{i}\x02", v)

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

    # 2-a) eqalign{...} 래퍼 제거 (HWP 수식의 정렬 그룹, LaTeX에선 불필요).
    #      cases 내부에 섞여 나오므로 cases 변환 전에 미리 벗겨둔다.
    while True:
        m = re.search(r"(?<![A-Za-z\\])eqalign\s*\{", s)
        if not m:
            break
        brace_start = m.end() - 1
        brace_end = _find_matching_brace(s, brace_start)
        if brace_end == -1:
            break
        inner = s[brace_start + 1:brace_end]
        s = s[:m.start()] + inner + s[brace_end + 1:]

    # cases 반복 처리
    for _ in range(5):
        m = re.search(r"\bcases\s*\{", s)
        if not m:
            break
        brace_start = m.end() - 1
        brace_end = _find_matching_brace(s, brace_start)
        if brace_end == -1:
            # HWP 원본이 `}` 누락된 경우: 문자열 끝을 경계로 사용
            brace_end = len(s)
            inner = s[brace_start + 1:brace_end]
        else:
            inner = s[brace_start + 1:brace_end]
        # HWP cases의 행 구분자는 `#` 이 기본이지만 일부 강사가 `\\`(실제 두
        # 백슬래시)를 사용. 두 형식 모두 LaTeX `\\`로 변환.
        # 열 구분자는 `&&` — LaTeX에서 `&`로 바꿔 정렬 컬럼 보존.
        lines = re.split(r"#|\\\\", inner)
        converted_lines = []
        for p in lines:
            p = p.strip()
            if not p:
                continue
            # `&&` → ` & ` (열 구분), 잔여 `&` 는 이미 단일이므로 유지
            p = re.sub(r"&&", " & ", p)
            converted_lines.append(p)
        converted = " \\\\ ".join(converted_lines)
        # `{cases{...}}`처럼 바깥 grouping 중괄호가 있는 경우 제거
        # (KaTeX에서 `{\begin{cases}...\end{cases}}`는 blank 그룹으로 인식돼 렌더 깨짐).
        # 단, pre의 `{`와 post의 `}`가 모두 있을 때만 짝 맞춰 제거.
        left_end = m.start()
        right_start = brace_end + 1
        pre = s[:left_end]
        post = s[right_start:]
        pre_rs = pre.rstrip()
        post_ls = post.lstrip()
        if pre_rs.endswith("{") and post_ls.startswith("}"):
            pre = pre[:len(pre_rs) - 1] + pre[len(pre_rs):]
            ws_len = len(post) - len(post_ls)
            post = post[:ws_len] + post_ls[1:]
        s = pre + r"\begin{cases}" + converted + r"\end{cases}" + post

    # 2-b) matrix/pmatrix/bmatrix/vmatrix/Bmatrix 변환
    #      HWP의 행렬 문법 `matrix{a&&b#c&&d}` → `\begin{matrix}a&b\\c&d\end{matrix}`
    #      `\left\{matrix{...}}\right\}` 같은 piecewise는 cases로 변환.
    for env in ("pmatrix", "bmatrix", "vmatrix", "Bmatrix", "matrix"):
        pat = re.compile(rf"(?<![A-Za-z\\])(?:\\)?{env}\s*\{{")
        for _ in range(5):
            m = pat.search(s)
            if not m:
                break
            brace_start = m.end() - 1
            brace_end = _find_matching_brace(s, brace_start)
            if brace_end == -1:
                brace_end = len(s)
                inner = s[brace_start + 1:brace_end]
            else:
                inner = s[brace_start + 1:brace_end]
            # 행: # 또는 \\ 구분자
            rows = re.split(r"#|\\\\", inner)
            # 열: && 또는 & 구분자 (HWP는 && 일반적)
            converted_rows = []
            for row in rows:
                cols = re.split(r"&&|&", row)
                converted_rows.append(" & ".join(c.strip() for c in cols if c.strip()))
            body = " \\\\ ".join(r for r in converted_rows if r)
            # \left\{matrix{...}}\right\} 케이스 — piecewise cases
            pre = s[:m.start()]
            post = s[brace_end + 1:] if brace_end < len(s) else ""
            # \left\{ 바로 앞 + \right\} 바로 뒤면 cases로 승격
            pre_strip = pre.rstrip()
            post_strip = post.lstrip()
            if (pre_strip.endswith(r"\left\{") and
                (post_strip.startswith(r"}\right\}") or post_strip.startswith(r"\right\}"))):
                # cases 환경으로
                pre = pre_strip[:-len(r"\left\{")]
                if post_strip.startswith(r"}\right\}"):
                    post = post_strip[len(r"}\right\}"):]
                else:
                    post = post_strip[len(r"\right\}"):]
                s = pre + r"\begin{cases}" + body + r"\end{cases}" + post
            else:
                s = pre + r"\begin{" + env + "}" + body + r"\end{" + env + "}" + post

    # 3) 분수: {num} over {den} → \frac{num}{den} (중첩 허용)
    for _ in range(5):
        new_s = re.sub(
            r"\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*over\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
            r"\\frac{\1}{\2}", s
        )
        if new_s == s:
            break
        s = new_s

    # 3-a) frac{A}{B} → \frac{A}{B} (HWP가 `frac{..}{..}` 표기하는 변형)
    s = re.sub(
        r"(?<![A-Za-z\\])frac(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})(\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\})",
        r"\\frac\1\2", s,
    )

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
    # sqrt-(expr) → \sqrt{-(expr)}
    s = re.sub(r"\bsqrt\s*-\s*\(([^)]+)\)",
               lambda m: r"\sqrt{-(" + m.group(1) + r")}", s)
    s = re.sub(r"\bsqrt\s*(-[A-Za-z0-9]+)", r"\\sqrt{\1}", s)
    s = re.sub(r"\bsqrt\s+([A-Za-z0-9])", r"\\sqrt{\1}", s)
    # sqrtN (붙어있는 경우)
    s = re.sub(r"\bsqrt([0-9])", r"\\sqrt{\1}", s)
    # sqrt 뒤 \frac 직접 접합 또는 공백 (sqrt\frac·sqrt \frac → \sqrt\frac)
    # KaTeX에서 \sqrt\frac{..}{..}는 \sqrt{\frac{..}{..}}와 동일 렌더.
    s = re.sub(r"(?<![A-Za-z\\])sqrt\s*(?=\\frac)", r"\\sqrt", s)

    # 6) bar → overline
    s = re.sub(r"\bbar\s*\{", r"\\overline{", s)
    s = re.sub(
        r"\bbar\s+([A-Za-z]\w*)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    # bar 뒤 영숫자 직접 접합 (bar2z → \overline{2z})
    s = re.sub(
        r"(?<![A-Za-z\\])bar(?=[0-9])([0-9A-Za-z]+)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    # bar 뒤 공백 + 숫자/혼합 (bar 4i → \overline{4i}, bar 2 → \overline{2})
    s = re.sub(
        r"\bbar\s+([0-9][A-Za-z0-9]*)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    # bar 뒤 `-숫자` (bar-3 → \overline{-3})
    s = re.sub(
        r"\bbar(-[0-9]+)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    s = re.sub(
        r"\bbar\s+(-[0-9]+)",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    # bar 뒤 LaTeX 명령 (bar \frac{..}{..} → \overline{\frac{..}{..}})
    # 공백 있든 없든 모두 처리 (bar\frac... 또는 bar \frac...)
    s = re.sub(
        r"\bbar\s*(\\[A-Za-z]+(?:\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}){1,2})",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )
    # bar + (표현식) — 괄호로 묶인 식
    s = re.sub(
        r"\bbar\s*(\([^()]*\))",
        lambda m: r"\overline{" + m.group(1) + r"}",
        s,
    )

    # 7) hat, vec, dot, ddot, tilde
    for accent in ["hat", "vec", "dot", "ddot", "tilde"]:
        s = re.sub(rf"\b{accent}\s*\{{", rf"\\{accent}{{", s)
        # 중괄호 없이 공백+단일문자 (vec a → \vec{a})
        s = re.sub(
            rf"(?<![A-Za-z\\])(?:\\mathrm\{{)?{accent}(?:\}})?\s+([A-Za-z][A-Za-z0-9]*)",
            lambda m, a=accent: rf"\{a}{{" + m.group(1) + "}",
            s,
        )

    # 8) rm{...} → \mathrm{...}
    s = re.sub(r"\brm\s*\{", r"\\mathrm{", s)
    s = re.sub(r"\brm\s*([A-Za-z]\w*)", lambda m: f"\\mathrm{{{m.group(1)}}}", s)
    # rm 뒤 숫자 직접 접합 (rm200 → 200, 수학모드에서 숫자는 기본 로만체)
    s = re.sub(r"(?<![A-Za-z])rm(?=[0-9])", "", s)

    # 9) BOX{...} → \boxed{...}
    s = re.sub(r"\bBOX\s*\{", r"\\boxed{", s)
    s = re.sub(r"\bbox\s*\{", r"\\boxed{", s)
    # BOX/box 단독(뒤에 { 없음) → \square (빈 네모 기호)
    s = re.sub(r"\b[Bb][Oo][Xx](?![A-Za-z{])", r"\\square ", s)
    # 빈 \boxed{}는 KaTeX에서 거의 안 보일 정도로 작으므로 \square로 교체
    s = re.sub(r"\\boxed\{\s*\}", r"\\square ", s)

    # 10) prime → '
    s = re.sub(r"\bprime\b", "'", s)

    # 11) it (italic) — LaTeX 수학모드 기본이므로 제거
    s = re.sub(r"\bit\s+", "", s)
    s = re.sub(r"\bit(?=[+-])", "", s)
    # it 뒤에 영문자·숫자 둘 다 제거 대상 (3ita → 3a, it2x → 2x, it3 → 3)
    s = re.sub(r"(?<![A-Za-z])it(?=[A-Za-z0-9])", "", s)
    s = re.sub(r"\bit\b", "", s)

    # 11-b) ^/_ 뒤 연속 영숫자 2자 이상은 {..}로 묶어 KaTeX가 다자 지수/첨자로 인식
    #       (HWP 관례: z^97 = z의 97제곱. LaTeX는 z^9 7로 해석하므로 래핑 필요)
    s = re.sub(r"\^([A-Za-z0-9]{2,})(?![A-Za-z0-9])", r"^{\1}", s)
    s = re.sub(r"_([A-Za-z0-9]{2,})(?![A-Za-z0-9])", r"_{\1}", s)

    # 12) 그리스 문자
    # 전처리: 붙어있는 그리스문자명 분리 (alphabeta → alpha beta)
    _greek_names = sorted(GREEK_MAP.keys(), key=len, reverse=True)
    _greek_pat = "|".join(_greek_names)
    for _ in range(3):  # 3개 이상 연속 대비
        s_new = re.sub(rf"({_greek_pat})({_greek_pat})", r"\1 \2", s)
        if s_new == s:
            break
        s = s_new
    # Python \b는 한글(\w 포함)과 영문자 사이 경계를 인식 못해 `beta이` 같은
    # 경우 매치에 실패한다. 영문자 경계만 직접 검사하도록 lookaround로 교체.
    for hwp, latex in GREEK_MAP.items():
        s = re.sub(rf"(?<![A-Za-z\\]){hwp}(?![A-Za-z])",
                   lambda m, r=latex: r, s)

    # 13) 기호
    for hwp, latex in SYMBOL_MAP.items():
        s = re.sub(rf"(?<![A-Za-z\\]){hwp}(?![A-Za-z])",
                   lambda m, r=latex: r, s)

    # 14) ` → \, (thin space), ~ → 일반 공백
    s = s.replace("`", r"\,")
    s = re.sub(r"~+", " ", s)

    # 15) & 제거, # → \\
    # matrix/cases/array 환경 내부의 `&`(열 구분자)는 보존해야 하므로
    # placeholder로 임시 치환 → & 제거 → 복원.
    _env_pat = re.compile(
        r"\\begin\{(matrix|pmatrix|bmatrix|vmatrix|Bmatrix|cases|array)\}"
        r".*?\\end\{\1\}",
        re.DOTALL,
    )
    _env_stash = []
    def _stash(m):
        _env_stash.append(m.group(0))
        return f"\x01ENV{len(_env_stash)-1}\x02"
    s = _env_pat.sub(_stash, s)
    s = s.replace("&", "")
    s = re.sub(r"\s*#\s*", r" \\\\ ", s)
    for i, v in enumerate(_env_stash):
        s = s.replace(f"\x01ENV{i}\x02", v)

    # 16) 끝에 매달린 단독 백슬래시 제거
    s = re.sub(r"\\(?=\s|$)", "", s)
    s = re.sub(r"\\$", "", s)

    # 17) 괄호 짝 보정
    s = _balance_braces(s)

    # 17-b) \left / \right 짝 보정 (KaTeX 렌더 에러 방지)
    s = _balance_left_right(s)

    # 18) 후처리
    s = _postprocess_latex(s)

    # 19) 남은 over 강제 처리 — 이미 변환된 LaTeX 명령(\alpha 등)도 OPERAND로 인식
    s = re.sub(
        r"(\{[^{}]*\}|\\[A-Za-z]+|[A-Za-z0-9+\-]+)\s*over\s*(\{[^{}]*\}|\\[A-Za-z]+|[A-Za-z0-9+\-]+)",
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

    # 21-b) \frac → \dfrac — inline $...$ 안에서도 분수를 크게 (displaystyle) 표시.
    #       교재·시험지 가독성을 위해 DB 전역에 적용.
    s = re.sub(r"\\frac(?=\{)", r"\\dfrac", s)

    # 21-c) backslash 빠진 LaTeX 명령 복원
    #       `overline{...}`, `mathrm{...}`, `sqrt{...}` 같이 `{` 직전인데
    #       앞에 `\` 없는 경우 자동으로 붙임 (KaTeX가 raw 텍스트로 렌더하는 것 방지).
    _BARE_CMDS = ("overline", "underline", "mathrm", "mathbf", "mathit",
                  "mathbb", "overrightarrow", "overleftarrow",
                  "hat", "vec", "tilde", "boxed", "sqrt", "dfrac",
                  "tfrac", "cfrac")
    for cmd in _BARE_CMDS:
        s = re.sub(rf"(?<![A-Za-z\\]){cmd}(?=\{{)", rf"\\{cmd}", s)

    # 22) cases body의 행 구분자 방어적 복구
    #     일부 HWP 원본에서 행구분이 `\\`로 쓰였지만 전처리 중 `\ `(backslash+공백)로
    #     축소돼 cases 변환기의 split을 통과할 수 있음. body 안에서만 `\ ` → `\\\\`.
    def _fix_cases_body(m):
        body = m.group(1)
        body = re.sub(r"(?<!\\)\\ ", r" \\\\ ", body)
        return r"\begin{cases}" + body + r"\end{cases}"
    s = re.sub(
        r"\\begin\{cases\}(.*?)\\end\{cases\}",
        _fix_cases_body, s, flags=re.DOTALL
    )

    return s.strip()


def _postprocess_latex(s: str) -> str:
    """변환된 LaTeX 문자열의 잔여 HWP 키워드를 정리한다."""
    s = s.replace(r"\(", "(").replace(r"\)", ")")
    # `\{`, `\}` 이스케이프는 `\left\{` / `\right\}` delimiter의 일부일 때만 유지.
    # (blanket replace로 벗기면 `\left\{` → `\left{`가 돼 KaTeX에서 delimiter 오류.)
    s = re.sub(r"(?<!\\left)\\\{", "{", s)
    s = re.sub(r"(?<!\\right)\\\}", "}", s)

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
    # \b 대신 영문자 경계만 검사 (한글 인접 시에도 동작)
    for kw, latex in KEYWORD_MAP.items():
        s = re.sub(rf"(?<![A-Za-z\\]){kw}(?![A-Za-z])",
                   lambda m, r=latex: r, s)

    # tri \angle 결합 회수
    s = re.sub(r"\btri\s*\\angle", lambda m: r"\triangle", s)

    # over 잔여 — LaTeX 명령(\alpha)을 포함한 OPERAND
    NESTED = r"\{(?:[^{}]|\{[^{}]*\})*\}"
    SQRT_TOK = r"\\?sqrt\{[^{}]*\}"
    OPERAND = rf"(?:{SQRT_TOK}|{NESTED}|\\[A-Za-z]+|[A-Za-z0-9]+)"
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
    # {bar} 고립 케이스: over 분수 파싱이 분모를 잘못 쪼갠 잔재를 복구.
    #   `\frac{1}{bar} z`  →  `\frac{1}{\overline{z}}`
    s = re.sub(
        r"\{bar\}\s*([A-Za-z0-9]+)",
        lambda m: r"{\overline{" + m.group(1) + "}}",
        s,
    )
    # {bar} + LaTeX 명령 (예: `{bar} \alpha^2` → `{\overline{\alpha^2}}`)
    s = re.sub(
        r"\{bar\}\s*(\\[A-Za-z]+(?:\^[A-Za-z0-9]+|\{[^{}]*\})?)",
        lambda m: r"{\overline{" + m.group(1) + "}}",
        s,
    )
    # frac 두번째 분모가 {bar}{X} 분할된 케이스: `\frac{A}{bar}{B}` → `\frac{A}{\overline{B}}`
    s = re.sub(
        r"\}\{bar\}\{([^{}]+)\}",
        lambda m: r"}{\overline{" + m.group(1) + "}}",
        s,
    )
    # {sqrt} 고립 케이스: `{bar}`와 동일 원인 (over 분수 분모 쪼갬).
    #   `\frac{8}{sqrt} { -2}`  →  `\frac{8}{\sqrt{-2}}`
    # 공백+숫자/단어 형태도 처리: `{sqrt} 2` → `{\sqrt{2}}`
    s = re.sub(
        r"\{sqrt\}\s*\{\s*([^{}]+?)\s*\}",
        lambda m: r"{\sqrt{" + m.group(1).strip() + "}}",
        s,
    )
    s = re.sub(
        r"\{sqrt\}\s+(-?[A-Za-z0-9]+)",
        lambda m: r"{\sqrt{" + m.group(1) + "}}",
        s,
    )
    # {sqrt} + LaTeX 명령 (`{sqrt} \alpha` → `{\sqrt{\alpha}}`)
    s = re.sub(
        r"\{sqrt\}\s*(\\[A-Za-z]+(?:\^[A-Za-z0-9]+|\{[^{}]*\})?)",
        lambda m: r"{\sqrt{" + m.group(1) + "}}",
        s,
    )
    # {box} 고립 → {\boxed{...}} (1단계 중첩 브레이스 허용)
    s = re.sub(
        r"(?<!\\)\bbox\s*\{((?:[^{}]|\{[^{}]*\})*)\}",
        lambda m: r"\boxed{" + m.group(1).strip() + "}",
        s,
    )
    # bar 뒤 숫자 접합 (postprocess 잔여분)
    s = re.sub(
        r"(?<![A-Za-z\\])bar(?=[0-9])([0-9A-Za-z]+)",
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

    # rm 잔여 — HWP는 roman(직립)을 `rm` 접두사로 표기. LaTeX에선 기본 italic이므로
    # 대부분 삭제가 안전. `_`/`{`/숫자 앞, 영문자 뒤 모두 커버.
    # 대문자 RM 먼저 (i 플래그 있지만 명시적)
    s = re.sub(r"(?<![A-Za-z\\])RM(?=[A-Za-z_\{])", "", s)
    s = re.sub(r"(?<![A-Za-z\\])RM\s+(?=[A-Za-z\\])", "", s)
    s = re.sub(r"(?i)(?<![A-Za-z\\])rm(?=[A-Za-z_\{])", "", s)
    s = re.sub(r"(?i)(?<![A-Za-z\\])rm\s+(?=\\)", "", s)
    s = re.sub(r"(?i)(?<![A-Za-z\\])rm\b\s*", "", s)
    # it 접두사도 동일 (italic은 LaTeX 기본이라 삭제)
    s = re.sub(r"(?<![A-Za-z\\])it(?=[A-Za-z_\{])", "", s)
    s = re.sub(r"(?<![A-Za-z\\])it\s+(?=\\)", "", s)

    # RIGHT/LEFT 잔여 — 이미 \left/\right로 변환된 LaTeX 명령은 보존
    s = re.sub(r"(?i)(?<!\\)RIGHT\s*\|", r"\\right|", s)
    s = re.sub(r"(?i)(?<!\\)LEFT\s*\|", r"\\left|", s)
    s = re.sub(r"(?i)(?<!\\)\bRIGHT\b", "", s)
    s = re.sub(r"(?i)(?<!\\)\bLEFT\b", "", s)

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
    # HWP 수식 개정 이력 래퍼 제거 (최우선)
    raw = _strip_hwp_revision_history(raw)
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
    """테이블 요소를 <tr>/<tc> 구조를 보존해 직렬화한다.
    - 다열 표(조립제법/행렬)는 Markdown 파이프 테이블로 변환해 UI에서 격자
      렌더링 + 셀 내 KaTeX 수식 정상 동작을 동시에 보장한다.
    - 1열 표(조건박스/보기박스)는 기존처럼 줄바꿈으로 나열.
    - <<BOX_START>>/<<BOX_END>> 마커로 감싸 UI에서 테두리 표시.
    """
    items.append(ContentItem("text", text="\n<<BOX_START>>\n"))
    rows = tbl_elem.findall(NS_PAR + "tr")
    if not rows:
        # 비정상 구조 방어: tr이 없으면 평탄화 처리
        for tc in tbl_elem.iter(NS_PAR + "tc"):
            for p in tc.findall(NS_PAR + "subList/" + NS_PAR + "p"):
                for run in p.findall(NS_PAR + "run"):
                    _process_run_no_endnote(run, items)
                items.append(ContentItem("text", text="\n"))
        items.append(ContentItem("text", text="<<BOX_END>>\n"))
        return

    # 각 셀 콘텐츠를 미리 문자열로 직렬화
    table_rows = []
    max_cols = 0
    for tr in rows:
        cells = tr.findall(NS_PAR + "tc")
        row_cells = []
        for tc in cells:
            cell_paras = tc.findall(NS_PAR + "subList/" + NS_PAR + "p")
            # 셀 내 각 <p>를 개별 직렬화한 뒤 <br>로 이어 붙인다.
            # (한 셀에 ㄱ./ㄴ./ㄷ. 같은 여러 항목이 별도 p로 들어올 때
            # MD 테이블 셀 내에서 시각적 줄바꿈을 보존하기 위함.)
            para_strs = []
            for pe in cell_paras:
                para_items = []
                for run in pe.findall(NS_PAR + "run"):
                    _process_run_no_endnote(run, para_items)
                s = serialize_items(para_items).strip()
                if s:
                    para_strs.append(s)
            cell_str = "<br>".join(para_strs) if para_strs else ""
            # 테이블 셀 안전 변환: | 이스케이프, 잔여 개행 → 공백
            cell_str = cell_str.replace("|", r"\|").replace("\n", " ")
            row_cells.append(cell_str)
        table_rows.append(row_cells)
        if len(row_cells) > max_cols:
            max_cols = len(row_cells)

    # 선지용 이미지 표 감지:
    #   셀들이 ①②③④⑤ 라벨과 이미지/그래프만 담고 있는 경우 파이프 테이블
    #   대신 inline 선지 나열로 출력. 안 그러면 ①등이 choice 추출기에 의해
    #   파이프 문법까지 선지 텍스트로 흡수됨.
    _all_cells = [c.strip() for row in table_rows for c in row if c.strip()]
    _circ_chars = set("①②③④⑤⑥⑦⑧⑨")
    # 셀 타입 분류
    _cell_is_circle = lambda c: c in _circ_chars
    _cell_is_img = lambda c: bool(
        re.match(r"^(?:&lt;&lt;IMG:[^>]+&gt;&gt;|<<IMG:[^>]+>>)$", c)
    )
    _cell_is_combined = lambda c: bool(re.match(
        r"^[①②③④⑤⑥⑦⑧⑨]\s*(?:<br>)?\s*(?:&lt;&lt;IMG:[^>]+&gt;&gt;|<<IMG:[^>]+>>)$",
        c
    ))
    # 모든 셀이 "원문자 라벨 | 이미지 | 조합" 중 하나, 그리고 원문자가 최소 3개
    n_circles = sum(
        1 for c in _all_cells
        if _cell_is_circle(c) or _cell_is_combined(c)
    )
    _is_choice_grid = (
        bool(_all_cells)
        and n_circles >= 3
        and all(
            _cell_is_circle(c) or _cell_is_img(c) or _cell_is_combined(c)
            for c in _all_cells
        )
    )

    if _is_choice_grid:
        # BOX_START 되돌리기 — 선지 grid는 박스로 감싸지 않음
        if items and items[-1].kind == "text" and items[-1].text.strip() == "<<BOX_START>>":
            items.pop()
        # 원문자 + 인접 이미지 셀을 한 짝으로 묶어 출력
        parts = []
        i = 0
        while i < len(_all_cells):
            c = _all_cells[i]
            if _cell_is_combined(c):
                parts.append(c)
                i += 1
            elif _cell_is_circle(c):
                # 다음 셀이 이미지면 같이 묶음
                if i + 1 < len(_all_cells) and _cell_is_img(_all_cells[i + 1]):
                    parts.append(f"{c} {_all_cells[i + 1]}")
                    i += 2
                else:
                    parts.append(c)
                    i += 1
            else:
                # 고아 이미지 — 이전 원문자에 합치기
                if parts and not parts[-1].endswith(">>"):
                    parts[-1] = f"{parts[-1]} {c}"
                else:
                    parts.append(c)
                i += 1
        items.append(ContentItem("text", text="\n" + "  ".join(parts) + "\n"))
        return

    if max_cols <= 1:
        # 1열 — 기존처럼 줄 단위 나열 (조건박스/보기박스)
        for row in table_rows:
            for cell in row:
                items.append(ContentItem("text", text=(cell or "") + "\n"))
    else:
        # 다열 — Markdown 파이프 테이블로 출력 (첫 행은 빈 헤더)
        header = "|" + "|".join(["   "] * max_cols) + "|"
        sep = "|" + "|".join(["---"] * max_cols) + "|"
        items.append(ContentItem("text", text=header + "\n"))
        items.append(ContentItem("text", text=sep + "\n"))
        for row in table_rows:
            padded = list(row) + [""] * (max_cols - len(row))
            # 빈 셀은 공백 하나로 채워 렌더링 유지
            padded = [c if c else " " for c in padded]
            items.append(ContentItem("text", text="| " + " | ".join(padded) + " |\n"))

    items.append(ContentItem("text", text="<<BOX_END>>\n"))


def _process_run_no_endnote(run_elem, items):
    """<run> 요소를 처리하되, endNote는 건너뛴다."""
    for child in run_elem:
        tag = child.tag.split("}")[-1]

        if tag == "t":
            # <hp:t>는 내부에 <hp:tab> 등 자식을 포함할 수 있고, 탭 뒤 텍스트는
            # 자식의 .tail에 저장된다. .text만 읽으면 `① ㄱ<tab>② ㄴ<tab>③ ㄷ`
            # 같은 한 줄 압축 선지에서 ②③가 손실된다.
            parts = []
            if child.text:
                parts.append(child.text)
            for sub in child:
                if sub.tag.split("}")[-1] == "tab":
                    parts.append("\t")
                if sub.tail:
                    parts.append(sub.tail)
            merged = "".join(parts)
            if merged:
                items.append(ContentItem("text", text=merged))

        elif tag == "equation":
            _process_equation(child, items)

        elif tag == "pic":
            _process_pic(child, items)

        elif tag == "rect":
            # rect = HWP의 조건 박스 (예: (가)(나)(다)). <<BOX_START>>/<<BOX_END>>
            # 마커로 감싸 Streamlit·PDF 양쪽이 박스 UI로 렌더하도록 한다.
            items.append(ContentItem("text", text="\n<<BOX_START>>\n"))
            for dt in child.iter(NS_PAR + "drawText"):
                for sl in dt.iter(NS_PAR + "subList"):
                    for p in sl.findall(NS_PAR + "p"):
                        for run in p.findall(NS_PAR + "run"):
                            _process_run_no_endnote(run, items)
                        # (가)/(나)/(다) 줄이 한 줄로 붙지 않도록 각 p 끝에 줄바꿈.
                        items.append(ContentItem("text", text="\n"))
            items.append(ContentItem("text", text="<<BOX_END>>\n"))

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
            # 빈 수식은 skip — `$$` 연쇄가 후속 $...$ 파싱을 망가뜨림
            if not item.latex or not item.latex.strip():
                continue
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
            # \{, \} (delimiter 이스케이프)는 brace 카운트에서 제외
            counted = re.sub(r"\\[\{\}]", "", inner)
            open_b = counted.count("{")
            close_b = counted.count("}")
            if open_b > close_b:
                inner = inner + ("}" * (open_b - close_b))
            elif close_b > open_b:
                extra = close_b - open_b
                # \} 가 아닌 일반 } 중 문자열 끝 쪽부터 제거
                for _ in range(extra):
                    inner = re.sub(r"(?<!\\)\}(?=[^{}]*$)", "", inner, count=1)
            # 축소된 결과가 비거나 공백만 남으면 `$$` 연쇄 방지 위해 전체 삭제
            if not inner.strip():
                parts[i] = ""
            else:
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


def _normalize_difficulty(raw: str) -> str:
    """난이도 값을 정규화한다.

    우선순위: 킬(최상 포함) > 증(오탈자→중) > 상 > 중 > 하
    변형 흡수: trailing ], ) 제거, 이중마커 포함 문자열 → 가장 강한 단일값.
    """
    if not raw:
        return ""
    s = raw.strip()
    s = re.sub(r"[\]\)\s]+$", "", s).strip()
    if "최상" in s or "킬" in s:
        return "킬"
    if "증" in s:
        return "중"
    if "상" in s:
        return "상"
    if "중" in s:
        return "중"
    if "하" in s:
        return "하"
    return s


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
                    difficulty = _normalize_difficulty(diff_match.group(1))
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

        # 인라인 워터마크 수식 제거 (본문 끝에 붙은 `$bold{\mathrm{NGD}}$` 등).
        # junk_pattern이 줄 단위로 걸러 본문 전체가 날아가는 것을 차단.
        inline_watermark = re.compile(r"\$\s*bold\s*\{\s*\\?mathrm\s*\{\s*NGD\s*\}\s*\}?\s*\}?\s*\$")
        question_text = inline_watermark.sub("", question_text)
        solution_text = inline_watermark.sub("", solution_text)

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

        # 글머리 기호(⦁·●·■) 앞에 줄바꿈을 강제해 한 줄로 붙는 것을 방지.
        # 같은 <p> 안에 여러 항목을 나열한 원본의 시각 구조를 복원.
        question_text = _break_before_bullets(question_text)
        solution_text = _break_before_bullets(solution_text)

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


_BULLET_CHARS = r"⦁●■◆◇▪▫•"
# 한글 자음 항목 기호 (ㄱ./ㄴ./ㄷ./ㄹ./ㅁ./ㅂ./ㅅ./ㅇ./ㅈ./ㅊ./ㅋ./ㅌ./ㅍ./ㅎ.)
_HANGUL_ITEM = r"[ㄱ-ㅎ]\."


def _break_before_bullets(text: str) -> str:
    """글머리 기호 또는 ㄱ./ㄴ./ㄷ. 한글 자음 항목 앞에 줄바꿈 삽입.
    첫 등장은 문장 시작일 수 있으므로 제외.
    BOX 영역(<<BOX_START>>..<<BOX_END>>) 내부는 이미 Markdown 테이블 구조라
    줄바꿈 삽입 시 테이블이 깨지므로 건드리지 않는다 (셀 내 <br>은 파서가 삽입)."""
    if not text:
        return text

    # BOX 블록을 통째로 보존하기 위해 분리 처리
    parts = re.split(r"(<<BOX_START>>.*?<<BOX_END>>)", text, flags=re.S)
    bullet_pat = re.compile(rf"(?<=\S)[ \t]*([{_BULLET_CHARS}])")
    hangul_pat = re.compile(rf"(?<=\S)[ \t]+({_HANGUL_ITEM})")
    out = []
    for seg in parts:
        if seg.startswith("<<BOX_START>>"):
            out.append(seg)
        else:
            seg = bullet_pat.sub(r"\n\1", seg)
            seg = hangul_pat.sub(r"\n\1", seg)
            out.append(seg)
    return "".join(out)


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
