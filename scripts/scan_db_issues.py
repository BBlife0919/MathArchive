#!/usr/bin/env python3
"""DB 수식 품질 스캔 — 이미 적재된 mathdb.sqlite에서 변환 누락 패턴을 찾는다.

사용법:
    python scripts/scan_db_issues.py                       # 전체 스캔
    python scripts/scan_db_issues.py --top 30              # 상위 30건 표시
    python scripts/scan_db_issues.py --keyword vert        # 특정 키워드만

출력: question_id 별로 의심 패턴 리포트. 사용자가 캡처로 전수조사 안 해도
파서가 놓친 케이스를 즉시 파악 가능.
"""
import argparse
import re
import sqlite3
import sys
from collections import defaultdict

# 수식 내부 ($...$) 에서 백슬래시 없이 나오면 안 되는 HWP 잔여 키워드
SUSPECT_KEYWORDS = [
    "over", "sqrt", "root", "bar", "rm", "hat", "vec", "dot", "tilde",
    "pile", "eqalign",
    "vert", "VERT", "mid",
    "cap", "cup", "emptyset",
    "DIVIDE", "divide",
    "to", "TO", "from", "FROM",
    "box",
    # HWP 수식편집기 비교 연산자·화살표 (대문자 변형 누락 케이스 방어)
    "LE", "GE", "NE", "LEQ", "GEQ", "NEQ",
    "rarrow", "RARROW", "larrow", "LARROW", "lrarrow", "LRARROW",
]

# cases/matrix/BOX는 \begin{}/\end{} 또는 <<BOX_START>>/<<BOX_END>>에 감싸지
# 않은 경우에만 경고 (false positive 회피)
CONTEXTUAL_KEYWORDS = {
    "cases": re.compile(r"(?<![A-Za-z\\])(?<!\\begin\{)(?<!\\end\{)cases"),
    # pmatrix/bmatrix/vmatrix/Bmatrix 내부의 matrix 서브스트링은 오탐 제외
    "matrix": re.compile(r"(?<![A-Za-z\\])(?<!\\begin\{)(?<!\\end\{)matrix"),
    "BOX": re.compile(r"(?<![<_])BOX(?![_>])"),
}

# 단어 경계 체크: 앞에 백슬래시 없고 알파벳 아님, 뒤에 알파벳 아님
# rm은 \mathrm/\rm 내부가 아닐 때만
KEYWORD_PATTERNS = {
    kw: re.compile(rf"(?<!\\)(?<![A-Za-z]){re.escape(kw)}(?![A-Za-z])")
    for kw in SUSPECT_KEYWORDS
}
# rm은 별도로 \mathrm, \rm 뒤가 아닐 때만
KEYWORD_PATTERNS["rm"] = re.compile(
    r"(?<!math)(?<!\\)(?<![A-Za-z])rm(?![a-z])"
)

# 수식 영역 추출
MATH_SPAN = re.compile(r"\$([^$]+)\$")

# \left / \right 불균형
LEFT_PAT = re.compile(r"\\left(?![a-zA-Z])")
RIGHT_PAT = re.compile(r"\\right(?![a-zA-Z])")


def scan_text(text: str) -> list:
    """텍스트 한 조각을 스캔해 의심 패턴 리스트 반환."""
    issues = []
    if not text:
        return issues

    # 0. 구조 무결성 — 수식 검사 전 선행
    # 0-a) <<BOX_START>> / <<BOX_END>> 짝
    n_bs = text.count("<<BOX_START>>")
    n_be = text.count("<<BOX_END>>")
    if n_bs != n_be:
        issues.append((
            "box_mismatch",
            f"start={n_bs}, end={n_be}",
            text[:120],
        ))

    # 0-b) BOX 중첩 — 외곽 rect 가 내부 tbl 을 감싸면서 외곽 BOX 도 함께
    #      발행돼 두 겹이 된 케이스. 표 안 셀 값이 'shadow text' 로 본문에
    #      덤프되는 동시에 일어남.
    if re.search(r"<<BOX_START>>(?:[^<]|<(?!<BOX_END>>))*?<<BOX_START>>",
                 text, re.S):
        issues.append((
            "box_nested",
            "outer rect wrapping inner table",
            text[:120],
        ))

    # 0-c) 표 직후 셀 값이 한 줄에 하나씩 덤프된 패턴 (rect+tbl 중첩의 부산물)
    #      예) 표 마지막 행 다음에 `$e$\n $1$\n $-5$\n ...` 형태로 늘어선 경우.
    #      3개 이상의 짧은 단독 수식 줄이 연속될 때만 보고.
    shadow_run = re.search(
        r"(?:(?:^|\n)\s*\$[^$\n]{1,15}\$\s*){3,}",
        text,
        re.MULTILINE,
    )
    if shadow_run and "<<BOX_END>>" in text[:shadow_run.start()]:
        issues.append((
            "shadow_text_dump",
            "cell values dumped as flat list after table",
            text[max(0, shadow_run.start() - 30):shadow_run.start() + 90],
        ))

    for m in MATH_SPAN.finditer(text):
        span = m.group(1)

        # 1. 미변환 HWP 키워드
        for kw, pat in KEYWORD_PATTERNS.items():
            if pat.search(span):
                issues.append(("keyword", kw, span[:100]))

        # 1-b. 문맥 기반 키워드 (cases/matrix는 \begin{} 밖일 때만)
        for kw, pat in CONTEXTUAL_KEYWORDS.items():
            if pat.search(span):
                issues.append(("keyword", kw, span[:100]))

        # 2. \left / \right 짝 불일치
        n_left = len(LEFT_PAT.findall(span))
        n_right = len(RIGHT_PAT.findall(span))
        if n_left != n_right:
            issues.append((
                "left_right_mismatch",
                f"left={n_left}, right={n_right}",
                span[:100],
            ))

        # 3. 중괄호 짝 불일치 (\{, \} 이스케이프는 제외)
        depth = 0
        i = 0
        while i < len(span):
            ch = span[i]
            if ch == "\\" and i + 1 < len(span) and span[i + 1] in ("{", "}"):
                i += 2
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth < 0:
                    break
            i += 1
        if depth != 0:
            issues.append(("brace_mismatch", f"depth={depth}", span[:100]))

    # 4. 수식 바깥에 백슬래시 LaTeX 명령 노출 (KaTeX가 렌더 못 하고 raw 표시)
    outside = MATH_SPAN.sub("", text)
    raw_cmds = re.findall(
        r"\\(frac|dfrac|sqrt|overline|left|right|neq|leq|geq|alpha|beta|emptyset|cap|cup|vert)\b",
        outside,
    )
    for cmd in set(raw_cmds):
        issues.append(("latex_outside_math", f"\\{cmd}", outside[:100]))

    # 5. 수식 내부에 backslash 없는 LaTeX 명령어 잔존
    #    (예: `$dfrac{a}{b}$` — backslash 빠져서 KaTeX에서 raw 텍스트로 렌더)
    BARE_LATEX_CMDS = [
        "dfrac", "tfrac", "cfrac", "frac",
        "sqrt", "overline", "underline",
        "mathrm", "mathbf", "mathit", "mathbb",
        "overrightarrow", "overleftarrow",
        "hat", "vec", "tilde", "bar",
        "boxed", "left", "right",
    ]
    for m in MATH_SPAN.finditer(text):
        span = m.group(1)
        for cmd in BARE_LATEX_CMDS:
            # 앞에 `\` 없고 알파벳도 아님 (단어 경계 흉내)
            if re.search(rf"(?<![A-Za-z\\]){cmd}\{{", span):
                issues.append(("bare_latex_cmd", cmd, span[:100]))
                break  # 스팬당 1회만 보고

    return issues


def main():
    ap = argparse.ArgumentParser(description="DB 수식 품질 스캔")
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--top", type=int, default=20, help="키워드별 상위 N건 표시")
    ap.add_argument("--keyword", help="특정 키워드만 조회 (예: vert)")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    # questions + solutions 모두 스캔
    rows = cur.execute(
        """SELECT q.question_id, q.file_source, q.question_number,
                  q.question_text, s.solution_text
           FROM questions q
           LEFT JOIN solutions s ON s.question_id = q.question_id"""
    ).fetchall()

    issues_by_type = defaultdict(list)
    total_issues = 0

    for qid, fsrc, qnum, qtext, stext in rows:
        for field, text in (("Q", qtext), ("S", stext)):
            for itype, detail, context in scan_text(text or ""):
                key = f"{itype}:{detail}"
                if args.keyword and args.keyword.lower() not in key.lower():
                    continue
                issues_by_type[key].append({
                    "qid": qid,
                    "file": fsrc[:60],
                    "qnum": qnum,
                    "field": field,
                    "context": context,
                })
                total_issues += 1

    print("=" * 70)
    print(f"DB 수식 품질 스캔 — 총 이슈: {total_issues}건")
    print("=" * 70)
    print()

    # 타입별 요약
    print("[타입별 건수]")
    for key, items in sorted(
        issues_by_type.items(), key=lambda x: -len(x[1])
    ):
        print(f"  {key:40s} {len(items):5d}건")
    print()

    # 타입별 상위 N개 예시
    for key, items in sorted(
        issues_by_type.items(), key=lambda x: -len(x[1])
    ):
        print(f"--- {key} ({len(items)}건) ---")
        for it in items[:args.top]:
            print(f"  qid={it['qid']:5d} [{it['field']}] Q{it['qnum']:3d} "
                  f"{it['file']}")
            print(f"     {it['context']}")
        print()

    conn.close()


if __name__ == "__main__":
    main()
