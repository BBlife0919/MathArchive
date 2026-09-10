#!/usr/bin/env python3
"""DB 클린업 — 파서가 변환 못 한 HWP 비교연산자/화살표 토큰을 LaTeX 으로 치환.

근본 원인: SYMBOL_MAP 이 lowercase `le`/`ge`/`ne` 와 `LEQ`/`GEQ`/`NEQ`
만 다뤘고 `LE`/`GE`/`NE` (대문자 단축형) 와 `rarrow`/`RARROW`/`larrow` 같은
화살표 약어가 누락. 파서는 이미 수정됨. 이 스크립트는 DB 에 이미 들어있는
잔여 토큰만 정리한다.

사용법:
    python3 scripts/fix_unmapped_hwp_tokens.py                     # 로컬 미리보기
    python3 scripts/fix_unmapped_hwp_tokens.py --apply              # 로컬 적용
    python3 scripts/fix_unmapped_hwp_tokens.py --target pg          # 운영 미리보기
    python3 scripts/fix_unmapped_hwp_tokens.py --target pg --apply  # 운영 적용

question_text/solution_text 뿐 아니라 choices(선지) JSON 의 각 항목 text 도
같이 정리한다(본문·해설·선지 3영역 동일 정규화 원칙).
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3

# (pattern, replacement). RULES_BEFORE 는 부착 분리(앞쪽 영숫자 → 공백 삽입)
# RULES_AFTER 는 토큰 치환. 두 단계로 나눠서 안전하게 정리.
#
# LE 보호: LEFT(`FT` 후행) / LEQ(`Q` 후행)
# GE 보호: GEQ(`Q` 후행)
# NE 보호: NEQ(`Q` 후행) / NEG(`G` 후행)

# 1) 토큰 치환: 영숫자 직후가 LE/GE/NE 인 케이스부터 처리 (양쪽 분리 필요)
#    - 양쪽 모두 영숫자 부착: `0LEx` → `0\leq x`
#    - 한쪽만 부착: `,LE\,` (이미 분리), `0LE\,` (앞만 부착) 등 다양
ATTACH_LEFT = [
    # 영숫자 + LE/GE/NE (부착) → 영숫자 + 공백 + LE/GE/NE
    (re.compile(r"(?<=[A-Za-z0-9])LE(?!FT|Q)"), " LE"),
    (re.compile(r"(?<=[A-Za-z0-9])GE(?!Q)"), " GE"),
    (re.compile(r"(?<=[A-Za-z0-9])NE(?!Q|G)"), " NE"),
    # 긴 화살표(lrarrow / LRARROW) 먼저 분리. 그 다음 짧은 화살표는 앞 글자가
    # L/l 일 때 분리하지 않는다(이미 lrarrow/LRARROW 의 일부일 수 있음).
    (re.compile(r"(?<=[A-Za-z0-9])(lrarrow|LRARROW)"), r" \1"),
    (re.compile(r"(?<=[A-Za-z0-9])(?<![Ll])(rarrow|RARROW)"), r" \1"),
    (re.compile(r"(?<=[A-Za-z0-9])(larrow|LARROW)"), r" \1"),
]

REPLACE = [
    # INF/inf → \infty (IN 매핑보다 먼저 매칭돼야 IN+F 로 갈라지지 않음).
    # `\lim _{n -> INF}` 같은 HWP 무한대 토큰 복구.
    (re.compile(r"(?<![A-Za-z\\])INF(?![A-Za-z])"), r"\\infty"),
    (re.compile(r"(?<![A-Za-z\\])inf(?![A-Za-z])"), r"\\infty"),
    # `\sqrt{N} of {M}` / `\sqrt N of M` → `\sqrt[N]{M}` (N 제곱근 M).
    # HWP root 가 `sqrt of` 형태로 잘못 변환된 케이스 복구.
    (re.compile(r"\\sqrt\s*\{([^{}]+)\}\s*of\s*\{([^{}]+)\}"), r"\\sqrt[\1]{\2}"),
    (re.compile(r"\\sqrt\s+(\w+)\s+of\s+(\w+)"), r"\\sqrt[\1]{\2}"),
    # 긴 토큰 먼저 (SMALLINTER 가 SMALL+INTER 로 분리되지 않도록)
    (re.compile(r"(?<![A-Za-z\\])SMALLINTER(?![A-Za-z])"), r"\\cap"),
    (re.compile(r"(?<![A-Za-z\\])SMALLINTER(?=[A-Za-z])"), r"\\cap "),
    (re.compile(r"(?<![A-Za-z\\])SMALLUNION(?![A-Za-z])"), r"\\cup"),
    (re.compile(r"(?<![A-Za-z\\])SMALLUNION(?=[A-Za-z])"), r"\\cup "),
    (re.compile(r"(?<![A-Za-z\\])UNDERBRACE(?![A-Za-z])"), r"\\underbrace"),
    (re.compile(r"(?<![A-Za-z\\])underbrace(?![A-Za-z\\])"), r"\\underbrace"),
    (re.compile(r"(?<![A-Za-z\\])OVERBRACE(?![A-Za-z])"), r"\\overbrace"),
    # OVER (대문자) — `X OVER Y` 형태 → `\frac` 대용 \, over 처리는 파서가 함.
    # 여기선 단순 \\over 로 두고 KaTeX 가 \over 처리하도록.
    (re.compile(r"(?<![A-Za-z\\])OVER(?=[A-Za-z])"), r"\\over "),
    (re.compile(r"(?<![A-Za-z\\])OVER(?![A-Za-z])"), r"\\over"),
    # 위에서 만든(혹은 예전 실행에서 이미 만들어져 DB에 남아있던) bare `\over`
    # 중 좌우가 단순 숫자인 경우만 `\dfrac{a}{b}`로 재교정.
    # bare `\over`는 좌우 경계가 없어 수식 전체(등호·부등호 포함)를 통째로
    # 분자/분모로 삼켜버리는 사고가 있다(예: `P(X\leq4)\leq1 \over2` → 분수선이
    # 부등식 전체를 덮음, 2026-09-10 발견). 숫자만이라도 안전하게 되돌린다.
    # 좌변이 지수/첨자(^6, _6)의 일부면 스킵 — `3^6 \over 2` 를
    # `3^\dfrac{6}{2}`로 잘못 쪼개는 사고 방지(2026-09-10 검수에서 발견).
    (re.compile(r"(?<![\d\^_])(-?\d+)\s*\\over\s*(-?\d+)(?![A-Za-z}\d^])"),
     r"\\dfrac{\1}{\2}"),
    (re.compile(r"(?<![A-Za-z\\])UNDER(?=[A-Za-z])"), r"\\under "),
    (re.compile(r"(?<![A-Za-z\\])UNDER(?![A-Za-z])"), r"\\under"),
    # cap/cup 부착 케이스 (`A CAPB`, `X CUPY`)
    (re.compile(r"(?<![A-Za-z\\])CAP(?=[A-Za-z])"), r"\\cap "),
    (re.compile(r"(?<![A-Za-z\\])CAP(?![A-Za-z])"), r"\\cap"),
    (re.compile(r"(?<![A-Za-z\\])CUP(?=[A-Za-z])"), r"\\cup "),
    (re.compile(r"(?<![A-Za-z\\])CUP(?![A-Za-z])"), r"\\cup"),
    (re.compile(r"(?<![A-Za-z\\])cap(?=[A-Za-z])"), r"\\cap "),
    (re.compile(r"(?<![A-Za-z\\])cup(?=[A-Za-z])"), r"\\cup "),
    # bold mode 제거 (HWP 굵게 토글, KaTeX 무관)
    (re.compile(r"(?<![A-Za-z\\])bold(?![A-Za-z])"), r""),
    (re.compile(r"(?<![A-Za-z\\])BOLD(?![A-Za-z])"), r""),
    (re.compile(r"(?<![A-Za-z\\])IT(?![A-Za-z])"), r""),  # italic toggle
    # HWP 단어 깨짐 패턴 — `triangle` 이 `triang` + `le` 로 쪼개졌고
    # `le` 가 \\leq 로 자동 변환돼 `triang \\leq ABC` 형태로 굳어짐.
    # 이 두 토큰을 하나로 묶어 \\triangle 로 복원.
    # \\mathrm{triang} \\leq 패턴 (mathrm 으로 감싸진 케이스) 우선 처리.
    (re.compile(r"\\mathrm\{triang\}\s*\\leq\s*"), r"\\triangle "),
    (re.compile(r"(?<![A-Za-z\\])triang\s*\\leq\s*"), r"\\triangle "),
    (re.compile(r"(?<![A-Za-z\\])triang(?=\s+[A-Z])"), r"\\triangle"),
    # `\\angle` 도 비슷하게 깨질 수 있음 (`ang` + `le`)
    (re.compile(r"\\mathrm\{ang\}\s*\\leq\s*"), r"\\angle "),
    (re.compile(r"(?<![A-Za-z\\])ang\s*\\leq\s*"), r"\\angle "),
    (re.compile(r"(?<![A-Za-z\\])BIGCAP(?![A-Za-z])"), r"\\bigcap"),
    (re.compile(r"(?<![A-Za-z\\])BIGCUP(?![A-Za-z])"), r"\\bigcup"),
    (re.compile(r"(?<![A-Za-z\\])NOTSUBSET(?![A-Za-z])"), r"\\not\\subset"),
    # LEQ/GEQ/NEQ — 변환 후 영문자 부착 케이스 분리
    (re.compile(r"(?<![A-Za-z\\])LEQ(?=[A-Za-z])"), r"\\leq "),
    (re.compile(r"(?<![A-Za-z\\])LEQ(?![A-Za-z])"), r"\\leq"),
    (re.compile(r"(?<![A-Za-z\\])GEQ(?=[A-Za-z])"), r"\\geq "),
    (re.compile(r"(?<![A-Za-z\\])GEQ(?![A-Za-z])"), r"\\geq"),
    (re.compile(r"(?<![A-Za-z\\])NEQ(?=[A-Za-z])"), r"\\neq "),
    (re.compile(r"(?<![A-Za-z\\])NEQ(?![A-Za-z])"), r"\\neq"),
    # LE 다음 영문자 (예: `LE x`, `LEx`): \leq 뒤 공백
    (re.compile(r"(?<![A-Za-z\\])LE(?!FT|Q)(?=[A-Za-z])"), r"\\leq "),
    (re.compile(r"(?<![A-Za-z\\])LE(?!FT|Q)(?![A-Za-z])"), r"\\leq"),
    (re.compile(r"(?<![A-Za-z\\])GE(?!Q)(?=[A-Za-z])"), r"\\geq "),
    (re.compile(r"(?<![A-Za-z\\])GE(?!Q)(?![A-Za-z])"), r"\\geq"),
    (re.compile(r"(?<![A-Za-z\\])NE(?!Q|G)(?=[A-Za-z])"), r"\\neq "),
    (re.compile(r"(?<![A-Za-z\\])NE(?!Q|G)(?![A-Za-z])"), r"\\neq"),
    # 화살표
    (re.compile(r"(?<![A-Za-z\\])rarrow(?=[A-Za-z])"), r"\\rightarrow "),
    (re.compile(r"(?<![A-Za-z\\])rarrow(?![A-Za-z])"), r"\\rightarrow"),
    (re.compile(r"(?<![A-Za-z\\])RARROW(?=[A-Za-z])"), r"\\rightarrow "),
    (re.compile(r"(?<![A-Za-z\\])RARROW(?![A-Za-z])"), r"\\rightarrow"),
    (re.compile(r"(?<![A-Za-z\\])larrow(?=[A-Za-z])"), r"\\leftarrow "),
    (re.compile(r"(?<![A-Za-z\\])larrow(?![A-Za-z])"), r"\\leftarrow"),
    (re.compile(r"(?<![A-Za-z\\])LARROW(?=[A-Za-z])"), r"\\leftarrow "),
    (re.compile(r"(?<![A-Za-z\\])LARROW(?![A-Za-z])"), r"\\leftarrow"),
    (re.compile(r"(?<![A-Za-z\\])lrarrow(?=[A-Za-z])"), r"\\leftrightarrow "),
    (re.compile(r"(?<![A-Za-z\\])lrarrow(?![A-Za-z])"), r"\\leftrightarrow"),
    (re.compile(r"(?<![A-Za-z\\])LRARROW(?=[A-Za-z])"), r"\\leftrightarrow "),
    (re.compile(r"(?<![A-Za-z\\])LRARROW(?![A-Za-z])"), r"\\leftrightarrow"),
    # 집합 / 원소 / 합성함수 — 수식 컨텍스트 (전역 안전)
    # 부착 케이스 (예: `Asubset`, `gCIRCf`) 도 처리 — 문자 사이 공백 삽입
    (re.compile(r"(?<![A-Za-z\\])subset(?=[A-Za-z])"), r"\\subset "),
    (re.compile(r"(?<![A-Za-z\\])subset(?![A-Za-z])"), r"\\subset"),
    (re.compile(r"(?<![A-Za-z\\])SUBSET(?=[A-Za-z])"), r"\\subset "),
    (re.compile(r"(?<![A-Za-z\\])SUBSET(?![A-Za-z])"), r"\\subset"),
    (re.compile(r"(?<![A-Za-z\\])supset(?=[A-Za-z])"), r"\\supset "),
    (re.compile(r"(?<![A-Za-z\\])supset(?![A-Za-z])"), r"\\supset"),
    (re.compile(r"(?<![A-Za-z\\])SUPSET(?=[A-Za-z])"), r"\\supset "),
    (re.compile(r"(?<![A-Za-z\\])SUPSET(?![A-Za-z])"), r"\\supset"),
    (re.compile(r"(?<![A-Za-z\\])notin(?=[A-Za-z])"), r"\\notin "),
    (re.compile(r"(?<![A-Za-z\\])notin(?![A-Za-z])"), r"\\notin"),
    (re.compile(r"(?<![A-Za-z\\])NOTIN(?=[A-Za-z])"), r"\\notin "),
    (re.compile(r"(?<![A-Za-z\\])NOTIN(?![A-Za-z])"), r"\\notin"),
    (re.compile(r"(?<![A-Za-z\\])circ(?=[A-Za-z])"), r"\\circ "),
    (re.compile(r"(?<![A-Za-z\\])circ(?![A-Za-z])"), r"\\circ"),
    (re.compile(r"(?<![A-Za-z\\])CIRC(?=[A-Za-z])"), r"\\circ "),
    (re.compile(r"(?<![A-Za-z\\])CIRC(?![A-Za-z])"), r"\\circ"),
    (re.compile(r"(?<![A-Za-z\\])cdots(?![A-Za-z])"), r"\\cdots"),
    (re.compile(r"(?<![A-Za-z\\])CDOTS(?![A-Za-z])"), r"\\cdots"),
    (re.compile(r"(?<![A-Za-z\\])vdots(?![A-Za-z])"), r"\\vdots"),
    (re.compile(r"(?<![A-Za-z\\])ddots(?![A-Za-z])"), r"\\ddots"),
    # sqrt/over 부착 케이스 — `sqrtx` → `\sqrt x`
    (re.compile(r"(?<![A-Za-z\\])sqrt(?=[A-Za-z])"), r"\\sqrt "),
    (re.compile(r"(?<![A-Za-z\\])SQRT(?=[A-Za-z])"), r"\\sqrt "),
    (re.compile(r"(?<![A-Za-z\\])SQRT(?![A-Za-z])"), r"\\sqrt"),
    # sup + 숫자 → ^{N}  (HWP 수식편집기 superscript: `x sup 3` → `x^{3}`)
    (re.compile(r"\bsup\s+(\d+)\b"), r"^{\1}"),
    # int from A to B → \int_{A}^{B}  (적분 한계: `int from 0 to x` → `\int_{0}^{x}`)
    (re.compile(r"\bint\s+from\s+(\S+)\s+to\s+(\S+)"), r"\\int_{\1}^{\2}"),
    # ANG/ang 단독 → \angle (이미 \angle\b 매핑 있다면 idempotent)
    (re.compile(r"(?<![A-Za-z\\])ANG(?![A-Za-z])"), r"\\angle"),
    (re.compile(r"(?<![A-Za-z\\])ang(?![A-Za-z])"), r"\\angle"),
    # TRIANG/triang 단독 → \triangle
    (re.compile(r"(?<![A-Za-z\\])TRIANG(?![A-Za-z])"), r"\\triangle"),
    (re.compile(r"(?<![A-Za-z\\])triang(?![A-Za-z])"), r"\\triangle"),
    # SMALLPROD/smallprod → \prod
    (re.compile(r"(?<![A-Za-z\\])SMALLPROD(?![A-Za-z])"), r"\\prod"),
    (re.compile(r"(?<![A-Za-z\\])smallprod(?![A-Za-z])"), r"\\prod"),
    # BAR 단독 → \overline (이미 bar{X} 매핑은 별도)
    (re.compile(r"(?<![A-Za-z\\])BAR(?![A-Za-z])"), r"\\overline"),
    # ARROW 단독 → \to
    (re.compile(r"(?<![A-Za-z\\])ARROW(?![A-Za-z])"), r"\\to"),
    # SEARROW → \searrow (남동 화살표)
    (re.compile(r"(?<![A-Za-z\\])SEARROW(?![A-Za-z])"), r"\\searrow"),
    (re.compile(r"(?<![A-Za-z\\])NEARROW(?![A-Za-z])"), r"\\nearrow"),
    (re.compile(r"(?<![A-Za-z\\])SWARROW(?![A-Za-z])"), r"\\swarrow"),
    (re.compile(r"(?<![A-Za-z\\])NWARROW(?![A-Za-z])"), r"\\nwarrow"),
    # LSUB 단독 → _ (subscript). 안전을 위해 다음 글자 매칭만.
    (re.compile(r"(?<![A-Za-z\\])LSUB(?=[A-Za-z0-9])"), r"_"),
    # trig + variable 분리 (sinx → \sin x, cosA → \cos A, lnx → \ln x)
    (re.compile(r"(?<![A-Za-z\\])sin([A-Za-z])(?![A-Za-z])"), r"\\sin \1"),
    (re.compile(r"(?<![A-Za-z\\])cos([A-Za-z])(?![A-Za-z])"), r"\\cos \1"),
    (re.compile(r"(?<![A-Za-z\\])tan([A-Za-z])(?![A-Za-z])"), r"\\tan \1"),
    (re.compile(r"(?<![A-Za-z\\])sec([A-Za-z])(?![A-Za-z])"), r"\\sec \1"),
    (re.compile(r"(?<![A-Za-z\\])csc([A-Za-z])(?![A-Za-z])"), r"\\csc \1"),
    (re.compile(r"(?<![A-Za-z\\])cot([A-Za-z])(?![A-Za-z])"), r"\\cot \1"),
    (re.compile(r"(?<![A-Za-z\\])ln([A-Za-z])(?![A-Za-z])"), r"\\ln \1"),
    (re.compile(r"(?<![A-Za-z\\])log([A-Za-z])(?![A-Za-z])"), r"\\log \1"),
    # trig + theta (costheta, sintheta) — theta 명시
    (re.compile(r"(?<![A-Za-z\\])sintheta(?![A-Za-z])"), r"\\sin\\theta"),
    (re.compile(r"(?<![A-Za-z\\])costheta(?![A-Za-z])"), r"\\cos\\theta"),
    (re.compile(r"(?<![A-Za-z\\])tantheta(?![A-Za-z])"), r"\\tan\\theta"),
    # pix → \pi x (pi + variable)
    (re.compile(r"(?<![A-Za-z\\])pi([A-Za-z])(?![A-Za-z])"), r"\\pi \1"),
]

# 영어 단어와 충돌 위험 있는 토큰 — 수식 ($...$) 안에서만 치환
MATH_ONLY_REPLACE = [
    # `inA`/`inX` 같이 in 뒤에 대문자 변수 붙은 부착 케이스 우선 분리
    (re.compile(r"(?<![A-Za-z\\])in(?=[A-Z])"), r"\\in "),
    (re.compile(r"(?<![A-Za-z\\])IN(?=[A-Z])"), r"\\in "),
    (re.compile(r"(?<![A-Za-z\\])in(?![A-Za-z])"), r"\\in"),
    (re.compile(r"(?<![A-Za-z\\])IN(?![A-Za-z])"), r"\\in"),
    (re.compile(r"(?<![A-Za-z\\])sum(?![A-Za-z])"), r"\\sum"),
    (re.compile(r"(?<![A-Za-z\\])SUM(?![A-Za-z])"), r"\\sum"),
    (re.compile(r"(?<![A-Za-z\\])prod(?![A-Za-z])"), r"\\prod"),
    (re.compile(r"(?<![A-Za-z\\])PROD(?![A-Za-z])"), r"\\prod"),
    (re.compile(r"(?<![A-Za-z\\])int(?![A-Za-z])"), r"\\int"),
    (re.compile(r"(?<![A-Za-z\\])INT(?![A-Za-z])"), r"\\int"),
    (re.compile(r"(?<![A-Za-z\\])forall(?![A-Za-z])"), r"\\forall"),
    (re.compile(r"(?<![A-Za-z\\])FORALL(?![A-Za-z])"), r"\\forall"),
    (re.compile(r"(?<![A-Za-z\\])exists(?![A-Za-z])"), r"\\exists"),
    (re.compile(r"(?<![A-Za-z\\])EXISTS(?![A-Za-z])"), r"\\exists"),
    (re.compile(r"(?<![A-Za-z\\])partial(?![A-Za-z])"), r"\\partial"),
    (re.compile(r"(?<![A-Za-z\\])nabla(?![A-Za-z])"), r"\\nabla"),
    (re.compile(r"(?<![A-Za-z\\])approx(?![A-Za-z])"), r"\\approx"),
    (re.compile(r"(?<![A-Za-z\\])APPROX(?![A-Za-z])"), r"\\approx"),
    (re.compile(r"(?<![A-Za-z\\])equiv(?![A-Za-z])"), r"\\equiv"),
    (re.compile(r"(?<![A-Za-z\\])EQUIV(?![A-Za-z])"), r"\\equiv"),
    (re.compile(r"(?<![A-Za-z\\])sim(?=[A-Za-z])"), r"\\sim "),
    (re.compile(r"(?<![A-Za-z\\])sim(?![A-Za-z])"), r"\\sim"),
    (re.compile(r"(?<![A-Za-z\\])SIM(?=[A-Za-z])"), r"\\sim "),
    (re.compile(r"(?<![A-Za-z\\])SIM(?![A-Za-z])"), r"\\sim"),
    (re.compile(r"(?<![A-Za-z\\])therefore(?![A-Za-z])"), r"\\therefore"),
    (re.compile(r"(?<![A-Za-z\\])THEREFORE(?![A-Za-z])"), r"\\therefore"),
    (re.compile(r"(?<![A-Za-z\\])because(?![A-Za-z])"), r"\\because"),
    (re.compile(r"(?<![A-Za-z\\])BECAUSE(?![A-Za-z])"), r"\\because"),
    (re.compile(r"(?<![A-Za-z\\])div(?![A-Za-z])"), r"\\div"),
    (re.compile(r"(?<![A-Za-z\\])DIV(?![A-Za-z])"), r"\\div"),
    # IT (italic 토글) 대문자 잔재 — 소문자 it 은 parse_hwpx.py 에서 이미
    # 제거되지만 대문자 IT 는 누락돼 "P IT (X=x)" 처럼 노출됨(2026-09-10 발견).
    (re.compile(r"\bIT\s+"), r""),
    (re.compile(r"\bIT(?=[+-])"), r""),
]

# lim 극한 관용구 + 잔여 화살표 — parse_hwpx.py hwp_eq_to_latex() 의 동일 로직
# 재사용(2026-09-09 파서 수정 이전에 적재된 구버전 행에는 미반영이라 DB에
# "lim _{x-> -1}" 처럼 원본 그대로 남아있음). 수식($...$) 영역에서만 적용.
_LIM_VAR = r"[A-Za-z]"
_LIM_PT = r"-?(?:\\infty|inf|[A-Za-z0-9]+)"
_ARROW = r"(?:->|[Rr][Aa][Rr][Rr][Oo][Ww])"


def _lim_repl(m: re.Match) -> str:
    var = m.group("var")
    pt = m.group("pt")
    sign = m.group("sign") or ""
    pt = re.sub(r"(?<![A-Za-z\\])inf(?![A-Za-z])", r"\\infty", pt)
    sup = f"^{{{sign}}}" if sign else ""
    return f"\\lim _{{{var} \\to {pt}{sup}}}"


_LIM_PATTERNS = [
    re.compile(
        rf"lim\s*_\s*\{{\s*(?P<var>{_LIM_VAR})\s*{_ARROW}\s*"
        rf"(?P<pt>{_LIM_PT})\s*(?P<sign>[+-])?\s*\}}"
    ),
    re.compile(
        rf"lim\s*_\s*(?P<var>{_LIM_VAR})\s*{_ARROW}\s*"
        rf"(?P<pt>{_LIM_PT})\s*(?P<sign>[+-])?(?![A-Za-z0-9])"
    ),
]


def _fix_lim_and_arrows(span: str) -> str:
    for pat in _LIM_PATTERNS:
        span = pat.sub(_lim_repl, span)
    # 위 관용구에 안 걸린 나머지 화살표 "->" (lim 아닌 문맥) → \to
    span = re.sub(r"-+>", r" \\to ", span)
    return span


# 이계도함수 등에서 "prime prime"(공백 포함 연속 프라임) → "''" 로 병합.
# KaTeX는 공백으로 분리된 두 개의 독립 위첨자를 Double superscript 에러로
# 처리해 렌더링이 통째로 깨진다(2026-09-10 발견, f''(x) 있는 문제 전반).
_PRIME_RUN = re.compile(r"'(?:\s+')+")


def _transform_math_only(span: str) -> str:
    for pat, repl in MATH_ONLY_REPLACE:
        span = pat.sub(repl, span)
    return span


def _apply_in_math_spans(text: str, transform=_transform_math_only) -> str:
    """수식 ($...$) 안에서만 transform 적용.

    영어 단어(`in`, `sum`, `int` 등)와 충돌을 피하기 위해 수식 영역 한정.
    """
    if "$" not in text:
        return text

    out = []
    i = 0
    in_math = False
    span_start = 0
    while i < len(text):
        if text[i] == "$":
            if in_math:
                # 수식 종료 — span 처리
                span = transform(text[span_start:i])
                out.append(span)
                out.append("$")
                in_math = False
            else:
                # 수식 시작
                out.append("$")
                span_start = i + 1
                in_math = True
            i += 1
        else:
            if not in_math:
                out.append(text[i])
            i += 1
    if in_math:
        # unbalanced $ — 마지막 span 그대로 추가 (변환 안 함)
        out.append(text[span_start:])
    return "".join(out)


def fix_text(text: str) -> str:
    if not text:
        return text
    # 1) 영숫자 부착 분리
    for pat, repl in ATTACH_LEFT:
        prev = None
        cur = text
        # 연쇄 부착(`5LExLEy`) 대비 fix-point 반복
        while prev != cur:
            prev = cur
            cur = pat.sub(repl, cur)
        text = cur
    # 2) 전역 안전 토큰 → LaTeX
    for pat, repl in REPLACE:
        text = pat.sub(repl, text)
    # 2.5) 공백으로 분리된 연속 프라임(') 병합 — Double superscript 방지
    text = _PRIME_RUN.sub(lambda m: "'" * m.group(0).count("'"), text)
    # 3) 영어 단어와 충돌 위험 있는 토큰 — 수식 컨텍스트 한정
    text = _apply_in_math_spans(text, _transform_math_only)
    # 3.5) lim 극한 관용구 + 잔여 화살표 — 수식 컨텍스트 한정
    text = _apply_in_math_spans(text, _fix_lim_and_arrows)
    # 4) 다중 공백 정리
    text = re.sub(r"  +", " ", text)
    return text


def _fix_choices(raw, placeholder: str):
    """choices(JSON) — sqlite 는 문자열, Postgres(jsonb) 는 이미 list/dict.

    반환: (변경여부, DB에 넣을 값). sqlite 는 json 문자열, pg 는 그대로 객체
    (psycopg2.extras.Json 으로 감싸는 건 호출부에서 처리).
    """
    if not raw:
        return False, raw
    is_str = isinstance(raw, str)
    try:
        items = json.loads(raw) if is_str else raw
    except Exception:
        return False, raw
    if not isinstance(items, list):
        return False, raw
    changed = False
    new_items = []
    for it in items:
        if isinstance(it, dict) and isinstance(it.get("text"), str):
            new_text = fix_text(it["text"])
            if new_text != it["text"]:
                changed = True
                it = {**it, "text": new_text}
        new_items.append(it)
    if not changed:
        return False, raw
    return True, (json.dumps(new_items, ensure_ascii=False) if is_str else new_items)


def _run_sqlite(db_path: str, apply: bool, show: int) -> int:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    grand = 0

    for table, idcol, txtcol in [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]:
        rows = cur.execute(f"SELECT {idcol}, {txtcol} FROM {table}").fetchall()
        changed = shown = 0
        for rid, txt in rows:
            new = fix_text(txt or "")
            if new != txt:
                changed += 1
                if shown < show:
                    _print_diff(idcol, rid, txt, new)
                    shown += 1
                if apply:
                    cur.execute(f"UPDATE {table} SET {txtcol}=? WHERE {idcol}=?", (new, rid))
        print(f"[{table}.{txtcol}] 후보 {len(rows)}건 중 변경 {changed}건")
        grand += changed

    rows = cur.execute("SELECT question_id, choices FROM questions").fetchall()
    changed = shown = 0
    for rid, raw in rows:
        did_change, new_val = _fix_choices(raw, "?")
        if did_change:
            changed += 1
            if shown < show:
                print(f"\n  --- questions.choices id={rid} ---")
                print(f"    -{raw[:140]}")
                print(f"    +{new_val[:140]}")
                shown += 1
            if apply:
                cur.execute("UPDATE questions SET choices=? WHERE question_id=?", (new_val, rid))
    print(f"[questions.choices] 후보 {len(rows)}건 중 변경 {changed}건")
    grand += changed

    if apply:
        conn.commit()
    conn.close()
    return grand


def _run_pg(apply: bool, show: int) -> int:
    from pathlib import Path

    import psycopg2
    from psycopg2.extras import Json

    from dotenv import load_dotenv
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")

    import os
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()
    grand = 0

    for table, idcol, txtcol in [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]:
        cur.execute(f"SELECT {idcol}, {txtcol} FROM {table}")
        rows = cur.fetchall()
        changed = shown = 0
        for rid, txt in rows:
            new = fix_text(txt or "")
            if new != txt:
                changed += 1
                if shown < show:
                    _print_diff(idcol, rid, txt, new)
                    shown += 1
                if apply:
                    cur.execute(f"UPDATE {table} SET {txtcol}=%s WHERE {idcol}=%s", (new, rid))
        print(f"[{table}.{txtcol}] 후보 {len(rows)}건 중 변경 {changed}건")
        grand += changed

    cur.execute("SELECT question_id, choices FROM questions")
    rows = cur.fetchall()
    changed = shown = 0
    for rid, raw in rows:
        did_change, new_val = _fix_choices(raw, "%s")
        if did_change:
            changed += 1
            if shown < show:
                print(f"\n  --- questions.choices id={rid} ---")
                print(f"    -{str(raw)[:140]}")
                print(f"    +{str(new_val)[:140]}")
                shown += 1
            if apply:
                cur.execute(
                    "UPDATE questions SET choices=%s WHERE question_id=%s",
                    (Json(new_val), rid),
                )
    print(f"[questions.choices] 후보 {len(rows)}건 중 변경 {changed}건")
    grand += changed

    if apply:
        conn.commit()
    conn.close()
    return grand


def _print_diff(idcol: str, rid, old: str, new: str) -> None:
    diff_lines = []
    for o, n in zip(old.split("\n"), new.split("\n")):
        if o != n:
            diff_lines.append(f"    -{o[:140]}")
            diff_lines.append(f"    +{n[:140]}")
    print(f"\n  --- {idcol}={rid} ---")
    print("\n".join(diff_lines[:6]))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--target", choices=["sqlite", "pg"], default="sqlite")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=3)
    args = ap.parse_args()

    if args.target == "pg":
        grand = _run_pg(args.apply, args.show)
    else:
        grand = _run_sqlite(args.db, args.apply, args.show)

    if args.apply:
        print(f"\n✅ 적용 완료. 총 {grand}건 갱신.")
    else:
        print(f"\n[미리보기] 총 {grand}건 변경 예정.")


if __name__ == "__main__":
    main()
