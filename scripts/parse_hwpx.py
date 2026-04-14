#!/usr/bin/env python3
"""HWPX 파일 파서 — 수학 기출문제 문항 분리 및 구조화

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
# 그리스 문자 및 기호 매핑
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
    "LEQ": r"\leq", "leq": r"\leq",
    "GEQ": r"\geq", "geq": r"\geq",
    "NEQ": r"\neq", "neq": r"\neq",
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


def hwp_eq_to_latex(script: str) -> str:
    """HWP 수식편집기 스크립트를 LaTeX로 변환한다."""
    if not script:
        return ""

    s = script.strip()

    # 1) cases 환경: cases{...#...} → \begin{cases}...\\ ...\end{cases}
    def convert_cases(m):
        inner = m.group(1)
        lines = inner.split("#")
        converted = " \\\\ ".join(lines)
        return r"\begin{cases}" + converted + r"\end{cases}"
    s = re.sub(r"cases\s*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}", convert_cases, s)

    # 2) LEFT / RIGHT 괄호 (대소문자 모두 처리)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\(", r"\\left(", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\)", r"\\right)", s)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\[", r"\\left[", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\]", r"\\right]", s)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\{", r"\\left\\{", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\}", r"\\right\\}", s)
    s = re.sub(r"\b[Ll][Ee][Ff][Tt]\s*\|", r"\\left|", s)
    s = re.sub(r"\b[Rr][Ii][Gg][Hh][Tt]\s*\|", r"\\right|", s)

    # 3) 분수: {num} over {den} → \frac{num}{den}
    # 반복 적용 (중첩 분수 처리)
    for _ in range(5):
        new_s = re.sub(
            r"\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}\s*over\s*\{([^{}]*(?:\{[^{}]*\}[^{}]*)*)\}",
            r"\\frac{\1}{\2}", s
        )
        if new_s == s:
            break
        s = new_s

    # 4) sqrt
    s = re.sub(r"\bsqrt\s*\{", r"\\sqrt{", s)

    # 5) bar → overline
    s = re.sub(r"\bbar\s*\{", r"\\overline{", s)

    # 6) hat, vec, dot, ddot, tilde
    for accent in ["hat", "vec", "dot", "ddot", "tilde"]:
        s = re.sub(rf"\b{accent}\s*\{{", rf"\\{accent}{{", s)

    # 7) rm{...} → \mathrm{...}
    s = re.sub(r"\brm\s*\{", r"\\mathrm{", s)
    # rm 뒤에 중괄호 없이 단일 문자/단어가 오는 경우 (rmABC, rm ABC 등)
    s = re.sub(r"\brm\s*([A-Za-z]\w*)", lambda m: f"\\mathrm{{{m.group(1)}}}", s)

    # 8) it (italic) — LaTeX 수학모드 기본이므로 제거
    # it 뒤에 공백+내용, 또는 부호가 바로 오는 경우
    s = re.sub(r"\bit\s+", "", s)
    s = re.sub(r"\bit(?=[+-])", "", s)
    # 단독 it (수식 시작 등)
    s = re.sub(r"\bit\b", "", s)

    # 9) 그리스 문자 (단어 경계로 매칭)
    for hwp, latex in GREEK_MAP.items():
        s = re.sub(rf"\b{hwp}\b", lambda m, r=latex: r, s)

    # 10) 기호
    for hwp, latex in SYMBOL_MAP.items():
        s = re.sub(rf"\b{hwp}\b", lambda m, r=latex: r, s)

    # 11) ` → \, (thin space)
    s = s.replace("`", r"\,")

    # 12) ~ → \  (일반 공백, 연속 ~ 제거)
    s = re.sub(r"~+", " ", s)

    # 13) 불필요한 다중 공백 정리
    s = re.sub(r"  +", " ", s)

    return s.strip()


# ── 파일명 메타데이터 파싱 ────────────────────────────────────
def parse_filename_metadata(filename: str) -> dict:
    """파일명에서 메타데이터를 추출한다.
    예: [고][2025][1-1-a][인천][계양고][공수1][비상][다항식의연산-이차함수][...]
    """
    meta = {}
    brackets = re.findall(r"\[([^\]]+)\]", filename)
    if len(brackets) >= 6:
        meta["school_level"] = brackets[0]  # 고
        meta["year"] = brackets[1]          # 2025
        # 학년-학기-시험유형
        grade_parts = brackets[2].split("-")
        if len(grade_parts) >= 3:
            meta["grade"] = grade_parts[0]
            meta["semester"] = grade_parts[1]
            meta["exam_type"] = grade_parts[2]  # a=중간, b=기말
        meta["region"] = brackets[3]        # 인천
        meta["school"] = brackets[4]        # 계양고
        meta["subject"] = brackets[5]       # 공수1
        # 출판사 (있을 수도 없을 수도)
        # 단원 범위를 찾는다 — "~"나 "-"가 포함된 한글 항목
        for b in brackets[6:]:
            if re.search(r"[가-힣].*[-~].*[가-힣]", b):
                meta["chapter_range"] = b
                break
    return meta


# ── XML 파싱: 단락을 순회하며 콘텐츠 스트림 구축 ──────────────
class ContentItem:
    """단락 내 하나의 콘텐츠 요소."""
    __slots__ = ("kind", "text", "image_ref", "hwp_eq", "latex")

    def __init__(self, kind, text="", image_ref="", hwp_eq="", latex=""):
        self.kind = kind        # "text", "equation", "image"
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


def _process_run(run_elem, items):
    """<run> 요소의 자식들을 순서대로 처리하여 items에 추가한다.

    <run>은 <t>(텍스트), <equation>(수식), <ctrl>(<pic>, <endNote> 등) 등을
    자식으로 가질 수 있다.  endNote/subList 내부의 <p>는 root.iter()가
    별도 순회하므로 여기서는 건너뛴다.
    """
    for child in run_elem:
        tag = child.tag.split("}")[-1]

        if tag == "t":
            if child.text:
                items.append(ContentItem("text", text=child.text))

        elif tag == "equation":
            if _is_watermark_equation(child):
                continue
            script_el = child.find(NS_PAR + "script")
            if script_el is None or not script_el.text:
                continue
            raw = script_el.text
            # 줄바꿈 이후 가비지 제거 (예: "0\n\n...To\n20006")
            raw = re.split(r"\n\s*\n", raw)[0].strip()
            # 가비지 데이터 필터링
            clean = re.sub(r"\s+", "", raw)
            if not clean or re.fullmatch(r"To\d+", clean):
                continue
            latex = hwp_eq_to_latex(raw)
            items.append(ContentItem("equation", hwp_eq=raw, latex=latex))

        elif tag == "pic":
            if _is_watermark_pic(child):
                continue
            img_el = child.find(".//" + NS_CORE + "img")
            if img_el is not None:
                ref = img_el.attrib.get("binaryItemIDRef", "")
                if ref:
                    items.append(ContentItem("image", image_ref=ref))

        elif tag == "rect":
            # drawText 안의 텍스트 (보기 박스 등)
            for dt in child.iter(NS_PAR + "drawText"):
                for sl in dt.iter(NS_PAR + "subList"):
                    for p in sl.findall(NS_PAR + "p"):
                        _process_paragraph_direct(p, items)
                    items.append(ContentItem("text", text="\n"))

        elif tag == "ctrl":
            # <ctrl> 안에 <pic>, <equation> 등이 있을 수 있음
            for sub in child:
                stag = sub.tag.split("}")[-1]
                if stag == "pic":
                    if _is_watermark_pic(sub):
                        continue
                    img_el = sub.find(".//" + NS_CORE + "img")
                    if img_el is not None:
                        ref = img_el.attrib.get("binaryItemIDRef", "")
                        if ref:
                            items.append(ContentItem("image", image_ref=ref))
                elif stag == "equation":
                    if _is_watermark_equation(sub):
                        continue
                    script_el = sub.find(NS_PAR + "script")
                    if script_el is not None and script_el.text:
                        raw = re.split(r"\n\s*\n", script_el.text)[0].strip()
                        clean = re.sub(r"\s+", "", raw)
                        if clean and not re.fullmatch(r"To\d+", clean):
                            latex = hwp_eq_to_latex(raw)
                            items.append(ContentItem(
                                "equation", hwp_eq=raw, latex=latex
                            ))
                # endNote, header, footer → 내부 <p>는 root.iter()가 순회하므로 무시

        elif tag == "tbl":
            # 테이블은 root.iter()가 내부 <p>를 순회하지만,
            # 간단한 인라인 테이블은 직접 처리
            pass


def _process_paragraph_direct(p_elem, items):
    """<p> 요소를 직접 처리한다 (drawText 등 서브구조에서 호출)."""
    for child in p_elem:
        tag = child.tag.split("}")[-1]
        if tag == "run":
            _process_run(child, items)


def walk_paragraphs(section_root):
    """section0.xml의 모든 <p> 요소를 깊이우선 순회하며 ContentItem 리스트를 반환한다.

    root.iter()를 사용하므로 endNote, subList, tbl 내부의 <p>도 자동 순회된다.
    각 단락의 <run> 자식에서 텍스트, 수식, 이미지를 순서대로 추출한다.
    """
    items = []

    for p_elem in section_root.iter(NS_PAR + "p"):
        # <p>의 직접 자식 <run>만 처리 (findall은 직접 자식만 반환)
        for run_elem in p_elem.findall(NS_PAR + "run"):
            _process_run(run_elem, items)
        # 단락 구분 줄바꿈
        items.append(ContentItem("text", text="\n"))

    return items


# ── 콘텐츠 스트림 → 텍스트 직렬화 ────────────────────────────
def serialize_content(items: list, eq_format="latex") -> str:
    """ContentItem 리스트를 하나의 문자열로 합친다.
    수식은 $...$ 또는 원본 형태로 삽입된다.
    이미지는 <<IMG:imageN>> 플레이스홀더로 삽입된다.
    """
    parts = []
    for item in items:
        if item.kind == "text":
            parts.append(item.text)
        elif item.kind == "equation":
            if eq_format == "latex":
                parts.append(f"${item.latex}$")
            else:
                parts.append(f"$${item.hwp_eq}$$")
        elif item.kind == "image":
            parts.append(f"<<IMG:{item.image_ref}>>")
    return "".join(parts)


# ── 문항 분리 및 구조화 ──────────────────────────────────────
ANSWER_PATTERN = re.compile(
    r"\[정답\]\s*(.+?)(?:\n|$)", re.DOTALL
)
# 서답형 정답: [정답] 다음에 수식($...$)이나 숫자가 올 수 있음
ANSWER_SUBJECTIVE = re.compile(
    r"\[정답\]\s*(\$[^$]+\$|[\d/.\-]+)"
)
CHAPTER_PATTERN = re.compile(
    r"\[중단원\]\s*(.+?)(?:\n|$)"
)
DIFFICULTY_PATTERN = re.compile(
    r"\[난이도\]\s*(.+?)(?:\n|$)"
)
ERROR_PATTERN = re.compile(
    r"\[문제\s*오류\]\s*(.*?)(?:\n|$)"
)
SUBJECTIVE_PATTERN = re.compile(
    r"\[서[답술]형\s*(\d+)\]"
)
POINTS_PATTERN = re.compile(
    r"\[\s*\$?([\d.]+)\$?\s*점\s*\]"
)

# 원 번호 → 숫자
CIRCLE_NUM = {"①": 1, "②": 2, "③": 3, "④": 4, "⑤": 5}


def parse_answer_value(raw: str) -> dict:
    """정답 문자열을 파싱한다. 예: '⑤' → {"answer": 5, "answer_type": "choice"}"""
    raw = raw.strip()
    for circle, num in CIRCLE_NUM.items():
        if circle in raw:
            return {"answer": str(num), "answer_type": "choice"}
    # 수식으로 감싸진 숫자 정답: $209$
    m = re.search(r"\$\s*([\d/.\-]+)\s*\$", raw)
    if m:
        return {"answer": m.group(1), "answer_type": "short_answer"}
    # 일반 숫자 정답 (서답형)
    m = re.search(r"([\d/.\-]+)", raw)
    if m:
        return {"answer": m.group(1), "answer_type": "short_answer"}
    return {"answer": raw.strip(), "answer_type": "unknown"}


def extract_choices(text: str) -> list:
    """선택지를 추출한다.

    두 가지 포맷을 처리:
    1) 명시적: ① val1  ② val2  ③ val3  ④ val4  ⑤ val5
    2) 압축형: ① $v1$$v2$$v3$\n④ $v4$$v5$
       (②③⑤가 XML에 없고 수식이 연속으로 나열됨)
    """
    # 먼저 ①~⑤가 모두 텍스트에 있는지 확인
    circle_present = {c: c in text for c in CIRCLE_NUM}
    all_present = all(circle_present.values())

    if all_present:
        # 포맷 1: 명시적 — ①~⑤로 분할
        choices = []
        parts = re.split(r"([①②③④⑤])", text)
        current_num = None
        for part in parts:
            if part in CIRCLE_NUM:
                current_num = CIRCLE_NUM[part]
            elif current_num is not None:
                cleaned = part.strip().split("\n")[0].strip()
                if cleaned:
                    choices.append({"number": current_num, "text": cleaned})
                current_num = None
        return choices

    # 포맷 2: 압축형 — ①과 ④만 존재
    # ① 뒤의 수식들을 개별 선택지로 분리
    choices = []

    # ① ~ ④ 사이 추출
    m1 = re.search(r"①\s*", text)
    m4 = re.search(r"④\s*", text)
    if not m1:
        return choices

    if m4:
        block1 = text[m1.end():m4.start()].strip()
        block2 = text[m4.end():].strip()
        # 줄바꿈 이후 제거 (다음 문항 내용 혼입 방지)
        block2 = block2.split("\n")[0].strip()
    else:
        block1 = text[m1.end():].strip().split("\n")[0].strip()
        block2 = ""

    # 수식($...$)을 기준으로 분리
    def split_values(block):
        """$...$로 감싸인 값들 또는 일반 텍스트 값들을 분리한다."""
        vals = re.findall(r"\$([^$]+)\$", block)
        if vals:
            return [f"${v}$" for v in vals]
        # 수식이 없으면 공백/탭으로 분리
        parts = [p.strip() for p in re.split(r"\s{2,}|\t", block) if p.strip()]
        return parts

    vals1 = split_values(block1)
    vals2 = split_values(block2)

    # ①②③에 값 배정
    for i, val in enumerate(vals1):
        choices.append({"number": i + 1, "text": val})

    # ④⑤에 값 배정
    base = len(vals1) + 1 if vals1 else 4
    if m4:
        base = 4  # ④부터 시작
    for i, val in enumerate(vals2):
        choices.append({"number": base + i, "text": val})

    return choices


def split_solution_and_question(text: str) -> tuple:
    """해설과 문제본문을 분리한다.

    문제본문은 선택지(①) 또는 '?' 또는 '구하시오'를 포함하며,
    일반적으로 블록의 뒷부분에 위치한다.

    반환: (solution_text, question_text)
    """
    lines = text.split("\n")

    # [중단원], [난이도] 이전까지의 본문에서 분리
    body_lines = []
    for line in lines:
        if re.match(r"\[중단원\]", line) or re.match(r"\[난이도\]", line):
            break
        if re.match(r"\[문제\s*오류\]", line):
            break
        body_lines.append(line)

    body = "\n".join(body_lines)

    # 선택지 시작점 찾기: 첫 번째 ① 위치
    choice_match = re.search(r"①", body)

    # 문제본문 시작 휴리스틱:
    # - "?" 가 포함된 문장
    # - "구하시오", "구하여라" 등
    # - 선택지 바로 위 블록
    # 해설에서 문제로 전환되는 지점을 찾는다.

    # 선택지가 있으면 그 위의 문단 블록이 문제
    if choice_match:
        before_choices = body[:choice_match.start()]
        # 빈 줄로 구분된 마지막 블록이 문제
        blocks = re.split(r"\n\s*\n", before_choices)
        if len(blocks) >= 2:
            solution = "\n\n".join(blocks[:-1]).strip()
            question = blocks[-1].strip() + "\n" + body[choice_match.start():].strip()
        else:
            # 블록 구분이 안 되면 전체를 문제로
            solution = ""
            question = body.strip()
    else:
        # 선택지 없음 (서답형) — 빈 줄 기준 마지막 블록이 문제
        blocks = re.split(r"\n\s*\n", body)
        if len(blocks) >= 2:
            solution = "\n\n".join(blocks[:-1]).strip()
            question = blocks[-1].strip()
        else:
            solution = ""
            question = body.strip()

    return solution, question


def split_into_questions(full_text: str, items: list) -> list:
    """[난이도]를 문항 종료 마커로, [정답]을 정답 마커로 사용하여 문항을 분리한다.

    HWPX 구조상 각 문항의 텍스트 흐름:
        [이전 문항 끝 [난이도]]
        (문제 텍스트 일부)          ← endNote 앞의 본문
        [정답] ⑤                    ← endNote 시작
        해설 텍스트...              ← endNote 내용
        (문제 텍스트 나머지 + 선택지) ← endNote 뒤의 본문
        [중단원] ...
        [난이도] ...                ← 현재 문항 끝
    """
    # 1) [난이도] 위치를 찾아 문항 블록 경계 설정
    diff_positions = [m.end() for m in re.finditer(r"\[난이도\]\s*\S+", full_text)]

    # 문항 블록: 이전 [난이도] 끝 ~ 현재 [난이도] 끝
    blocks = []
    prev = 0
    for pos in diff_positions:
        blocks.append(full_text[prev:pos])
        prev = pos
    # 마지막 [난이도] 뒤에 남은 텍스트가 있으면 추가
    if prev < len(full_text):
        remainder = full_text[prev:].strip()
        if remainder and "[정답]" in remainder:
            blocks.append(remainder)

    questions = []
    for block in blocks:
        # [정답]이 없으면 문항이 아님 (프리앰블 등)
        ans_match = ANSWER_PATTERN.search(block)
        if not ans_match:
            continue

        answer_info = parse_answer_value(ans_match.group(1))

        # 메타데이터 추출
        chapter = ""
        ch_match = CHAPTER_PATTERN.search(block)
        if ch_match:
            chapter = ch_match.group(1).strip()

        difficulty = ""
        diff_match = DIFFICULTY_PATTERN.search(block)
        if diff_match:
            difficulty = diff_match.group(1).strip()

        error_note = ""
        err_match = ERROR_PATTERN.search(block)
        if err_match:
            error_note = err_match.group(1).strip()

        subj_match = SUBJECTIVE_PATTERN.search(block)
        is_subjective = subj_match is not None
        # "※ 여기서 부터는 서답형" 패턴으로도 서답형 감지
        if not is_subjective and re.search(r"서[답술]형\s*문제", block):
            is_subjective = True
        subjective_num = int(subj_match.group(1)) if subj_match else None

        points = None
        pts_match = POINTS_PATTERN.search(block)
        if pts_match:
            points = float(pts_match.group(1))

        # 이미지 참조 추출
        image_refs = re.findall(r"<<IMG:(image\d+)>>", block)

        # 2) [정답] 위치를 기준으로 해설과 문제본문 분리
        ans_start = ans_match.start()
        ans_line_end = ans_match.end()

        # [정답] 앞: 문제 텍스트의 앞부분 (endNote 앞의 본문)
        text_before_answer = block[:ans_start].strip()

        # [정답] 뒤 ~ [중단원] 앞: 해설 + 문제 텍스트 뒷부분
        text_after_answer = block[ans_line_end:].strip()

        # [중단원], [난이도], [문제 오류], [서답형] 라인 제거
        meta_pattern = re.compile(
            r"\[중단원\]\s*.+?(?:\n|$)|\[난이도\]\s*.+?(?:\n|$)"
            r"|\[문제\s*오류\].*?(?:\n|$)|\[서[답술]형\s*\d+\]\s*"
            r"|※\s*여기서\s*부터는\s*서[답술]형\s*문제입니다\.?\s*"
        )
        text_after_clean = meta_pattern.sub("", text_after_answer).strip()

        # 해설/문제 분리: [정답] 뒤의 내용에서 선택지(①) 또는 질문("?", "구하")를 찾음
        solution, question_body = split_solution_and_question(text_after_clean)

        # [정답] 앞의 텍스트를 문제본문 앞에 합침
        if text_before_answer:
            # 프리앰블/저작권 텍스트 필터링
            if not re.search(r"콘텐츠산업|NGD|무단.*복제|제작연월일", text_before_answer):
                question_body = text_before_answer + "\n" + question_body

        # 선택지 추출
        choices = extract_choices(question_body)

        questions.append({
            "question_number": len(questions) + 1,
            "answer": answer_info["answer"],
            "answer_type": answer_info["answer_type"],
            "is_subjective": is_subjective,
            "subjective_number": subjective_num,
            "points": points,
            "chapter": chapter,
            "difficulty": difficulty,
            "question_text": question_body.strip(),
            "solution_text": solution.strip(),
            "choices": choices,
            "image_refs": image_refs,
            "has_image": len(image_refs) > 0,
            "error_note": error_note,
        })

    return questions


# ── 이미지 추출 ──────────────────────────────────────────────
def extract_images(hwpx_path: str, image_refs: set, output_dir: str,
                   file_stem: str) -> dict:
    """HWPX에서 문제용 이미지만 추출한다. 반환: {imageN: 저장경로}"""
    mapping = {}
    with zipfile.ZipFile(hwpx_path, "r") as zf:
        for ref in image_refs:
            # BinData/imageN.* 패턴으로 찾기
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


# ── masterpage 이미지 목록 (워터마크 후보) ─────────────────────
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

    # 파일명 메타데이터
    file_meta = parse_filename_metadata(file_stem)

    # 임시 디렉토리에 압축 해제
    tmp_dir = tempfile.mkdtemp(prefix="hwpx_")
    try:
        with zipfile.ZipFile(hwpx_path, "r") as zf:
            zf.extractall(tmp_dir)

        # masterpage 이미지 (워터마크) 목록
        watermark_images = get_masterpage_images(tmp_dir)

        # section0.xml 파싱
        section_path = os.path.join(tmp_dir, "Contents", "section0.xml")
        if not os.path.exists(section_path):
            raise FileNotFoundError(f"section0.xml not found in {hwpx_path}")

        tree = ET.parse(section_path)
        root = tree.getroot()

        # 단락 순회 → 콘텐츠 아이템 리스트
        items = walk_paragraphs(root)

        if debug:
            print(f"[DEBUG] Total content items: {len(items)}", file=sys.stderr)
            for i, item in enumerate(items[:100]):
                print(f"  [{i}] {item}", file=sys.stderr)

        # 직렬화
        full_text = serialize_content(items, eq_format="latex")

        if debug:
            print(f"\n[DEBUG] Full text (first 2000 chars):\n{full_text[:2000]}", file=sys.stderr)

        # 문항 분리
        questions = split_into_questions(full_text, items)

        # 모든 문항에서 참조하는 이미지 수집
        all_image_refs = set()
        for q in questions:
            all_image_refs.update(q["image_refs"])

        # 워터마크 이미지 제거
        all_image_refs -= watermark_images

        # 이미지 추출
        image_mapping = {}
        if image_output_dir and all_image_refs:
            os.makedirs(image_output_dir, exist_ok=True)
            image_mapping = extract_images(
                hwpx_path, all_image_refs, image_output_dir, file_stem
            )

        # 각 문항의 image_refs를 실제 경로로 업데이트
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

    # 출력
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
