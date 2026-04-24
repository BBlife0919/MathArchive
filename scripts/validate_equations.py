#!/usr/bin/env python3
"""수식 자동검증 스크립트 — 파싱 결과의 LaTeX 수식 품질을 일괄 검사한다.

사용법:
    python scripts/validate_equations.py                    # raw/ 전체 검사
    python scripts/validate_equations.py raw/파일.hwpx      # 단일 파일
    python scripts/validate_equations.py --report report.json  # JSON 리포트 저장

검사 항목:
    1) $...$ 안에 미변환 HWP 키워드 잔존 (over, sqrt, root, bar, rm, left, right 등)
    2) 괄호 짝 불일치 ({} 열림/닫힘)
    3) 빈 수식 ($$ 또는 $  $)
    4) 수식 밖에 노출된 raw 수식 패턴 (백슬래시 없는 frac, sqrt 등)
"""

import json
import os
import re
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(__file__))
from parse_hwpx import parse_hwpx

# ── 미변환 HWP 키워드 패턴 ────────────────────────────────────
# $...$ 안에서 백슬래시 없이 등장하면 안 되는 키워드들
HWP_KEYWORDS = [
    "over", "sqrt", "root", "bar", "rm", "hat", "vec", "dot", "ddot",
    "tilde", "cases", "pile", "eqalign", "matrix",
    "BOX", "box", "prime",
    # 집합/기호 키워드 (변환 누락 시 literal 노출)
    "vert", "VERT", "mid", "cap", "cup", "emptyset",
    "DIVIDE", "divide",
    # 화살표/극한
    "TO", "to", "from", "FROM",
]

# 단어 경계로 검사 (예: \overline의 over는 OK, 단독 over는 NG)
HWP_KEYWORD_PATTERNS = {}
for kw in HWP_KEYWORDS:
    # 앞에 백슬래시가 없고, 알파벳이 아닌 경계
    HWP_KEYWORD_PATTERNS[kw] = re.compile(
        rf"(?<!\\)(?<![A-Za-z]){re.escape(kw)}(?![A-Za-z])"
    )

# LEFT/RIGHT (대소문자 모두, \left \right 아닌 것)
LEFT_RIGHT_PATTERN = re.compile(r"(?<!\\)\b(LEFT|RIGHT|left|right)\b")

# ── 검증 함수 ────────────────────────────────────────────────

def extract_math_spans(text: str) -> list:
    """텍스트에서 $...$ 수식 영역을 추출한다."""
    spans = []
    for m in re.finditer(r"\$([^$]+)\$", text):
        spans.append({
            "content": m.group(1),
            "start": m.start(),
            "end": m.end(),
        })
    return spans


def check_unmatched_braces(latex: str) -> bool:
    """중괄호 짝이 맞지 않으면 True 반환."""
    depth = 0
    for ch in latex:
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth < 0:
                return True
    return depth != 0


def validate_equation(latex: str) -> list:
    """단일 수식의 문제점을 리스트로 반환한다."""
    issues = []

    # 빈 수식
    if not latex.strip():
        issues.append({"type": "empty", "detail": "빈 수식"})
        return issues

    # 미변환 HWP 키워드
    for kw, pattern in HWP_KEYWORD_PATTERNS.items():
        matches = pattern.findall(latex)
        if matches:
            issues.append({
                "type": "hwp_keyword",
                "keyword": kw,
                "detail": f"미변환 HWP 키워드 '{kw}' 발견",
                "context": latex[:80],
            })

    # LEFT/RIGHT 잔존 (\left, \right가 아닌 것)
    lr_matches = LEFT_RIGHT_PATTERN.findall(latex)
    if lr_matches:
        for lr in set(lr_matches):
            issues.append({
                "type": "hwp_keyword",
                "keyword": lr,
                "detail": f"미변환 LEFT/RIGHT '{lr}' 발견",
                "context": latex[:80],
            })

    # 괄호 짝 불일치
    if check_unmatched_braces(latex):
        issues.append({
            "type": "brace_mismatch",
            "detail": "중괄호 짝 불일치",
            "context": latex[:80],
        })

    # \로 시작하지 않는 frac, sqrt (변환 실패)
    if re.search(r"(?<!\\)frac\{", latex):
        issues.append({
            "type": "raw_command",
            "detail": "백슬래시 없는 frac",
            "context": latex[:80],
        })

    return issues


def validate_text_outside_math(text: str) -> list:
    """수식 바깥 텍스트에서 raw 수식 패턴을 검사한다."""
    issues = []
    # $...$ 제거
    outside = re.sub(r"\$[^$]*\$", "", text)

    # 수식 바깥에 백슬래시 명령이 노출된 경우
    raw_cmds = re.findall(r"\\(frac|sqrt|overline|alpha|beta|gamma|left|right)\b", outside)
    if raw_cmds:
        for cmd in set(raw_cmds):
            issues.append({
                "type": "latex_outside_math",
                "detail": f"수식 바깥에 LaTeX 명령 '\\{cmd}' 노출",
                "context": outside[:80],
            })

    return issues


def validate_parsed_result(result: dict) -> dict:
    """파싱 결과 전체를 검증하여 리포트를 반환한다."""
    file_source = result["file_source"]
    all_issues = []
    stats = {
        "total_equations": 0,
        "failed_equations": 0,
        "total_questions": result["total_questions"],
    }

    for q in result["questions"]:
        q_num = q["question_number"]

        # question_text, solution_text, choices 모두 검사
        fields = [
            ("question_text", q["question_text"]),
            ("solution_text", q["solution_text"]),
        ]
        for c in q.get("choices", []):
            fields.append((f"choice_{c['number']}", c["text"]))

        for field_name, text in fields:
            if not text:
                continue

            # 수식 내부 검사
            spans = extract_math_spans(text)
            for span in spans:
                stats["total_equations"] += 1
                issues = validate_equation(span["content"])
                if issues:
                    stats["failed_equations"] += 1
                    for iss in issues:
                        iss["file"] = file_source
                        iss["question"] = q_num
                        iss["field"] = field_name
                        all_issues.append(iss)

            # 수식 바깥 검사
            outside_issues = validate_text_outside_math(text)
            for iss in outside_issues:
                iss["file"] = file_source
                iss["question"] = q_num
                iss["field"] = field_name
                all_issues.append(iss)

    return {
        "file": file_source,
        "stats": stats,
        "issues": all_issues,
    }


def aggregate_reports(reports: list) -> dict:
    """여러 파일의 리포트를 집계한다."""
    total_equations = 0
    total_failed = 0
    total_questions = 0
    total_files = len(reports)
    all_issues = []

    keyword_counter = Counter()
    type_counter = Counter()
    file_error_counts = {}

    for r in reports:
        s = r["stats"]
        total_equations += s["total_equations"]
        total_failed += s["failed_equations"]
        total_questions += s["total_questions"]
        file_error_counts[r["file"]] = len(r["issues"])

        for iss in r["issues"]:
            all_issues.append(iss)
            type_counter[iss["type"]] += 1
            if iss["type"] == "hwp_keyword":
                keyword_counter[iss.get("keyword", "unknown")] += 1

    # 패턴별 그룹핑 (대표 예시 포함)
    pattern_groups = defaultdict(list)
    for iss in all_issues:
        key = f"{iss['type']}:{iss.get('keyword', '')}"
        if len(pattern_groups[key]) < 5:  # 패턴당 최대 5개 예시
            pattern_groups[key].append(iss)

    return {
        "summary": {
            "total_files": total_files,
            "total_questions": total_questions,
            "total_equations": total_equations,
            "failed_equations": total_failed,
            "success_rate": f"{(1 - total_failed / max(total_equations, 1)) * 100:.1f}%",
            "total_issues": len(all_issues),
        },
        "by_type": dict(type_counter.most_common()),
        "by_keyword": dict(keyword_counter.most_common()),
        "worst_files": dict(sorted(file_error_counts.items(), key=lambda x: -x[1])[:20]),
        "pattern_groups": {k: v for k, v in pattern_groups.items()},
    }


def print_report(agg: dict):
    """집계 결과를 터미널에 출력한다."""
    s = agg["summary"]
    print("\n" + "=" * 70)
    print("  수식 자동검증 리포트")
    print("=" * 70)
    print(f"\n  파일 수:       {s['total_files']}")
    print(f"  총 문항:       {s['total_questions']}")
    print(f"  총 수식:       {s['total_equations']}")
    print(f"  문제 수식:     {s['failed_equations']}")
    print(f"  성공률:        {s['success_rate']}")
    print(f"  총 이슈:       {s['total_issues']}")

    print("\n  [이슈 유형별]")
    for t, cnt in agg["by_type"].items():
        print(f"    {t:25s}: {cnt:5d}건")

    if agg["by_keyword"]:
        print("\n  [미변환 HWP 키워드별]")
        for kw, cnt in agg["by_keyword"].items():
            print(f"    {kw:15s}: {cnt:5d}건")

    print("\n  [오류 많은 파일 TOP 10]")
    for fname, cnt in list(agg["worst_files"].items())[:10]:
        print(f"    {cnt:4d}건  {fname[:60]}")

    print("\n  [패턴별 대표 예시]")
    for pattern, examples in agg["pattern_groups"].items():
        print(f"\n    --- {pattern} ({len(examples)}건) ---")
        for ex in examples[:3]:
            print(f"    Q{ex['question']:2d} {ex['field']:15s}: {ex.get('context', '')[:70]}")

    print("\n" + "=" * 70)


# ── CLI ──────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser(description="수식 자동검증")
    parser.add_argument("files", nargs="*", help="검사할 HWPX 파일 (없으면 raw/ 전체)")
    parser.add_argument("--raw-dir", default="raw", help="HWPX 디렉토리")
    parser.add_argument("--report", help="JSON 리포트 저장 경로")
    args = parser.parse_args()

    # 대상 파일 목록
    if args.files:
        hwpx_files = args.files
    else:
        hwpx_files = sorted([
            os.path.join(args.raw_dir, f)
            for f in os.listdir(args.raw_dir)
            if f.endswith(".hwpx")
        ])

    if not hwpx_files:
        print("검사할 파일이 없습니다.", file=sys.stderr)
        sys.exit(1)

    print(f"검증 대상: {len(hwpx_files)}개 파일", file=sys.stderr)

    reports = []
    for i, path in enumerate(hwpx_files, 1):
        try:
            result = parse_hwpx(path, image_output_dir=None)
            report = validate_parsed_result(result)
            reports.append(report)
            n_issues = len(report["issues"])
            status = f"  [{i:3d}/{len(hwpx_files)}] {os.path.basename(path)[:50]:50s} → {n_issues:3d}건"
            print(status, file=sys.stderr)
        except Exception as e:
            print(f"  [{i:3d}/{len(hwpx_files)}] ERROR: {path[:50]} → {e}", file=sys.stderr)

    # 집계
    agg = aggregate_reports(reports)

    # 터미널 출력
    print_report(agg)

    # JSON 저장
    if args.report:
        os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
        with open(args.report, "w", encoding="utf-8") as f:
            json.dump(agg, f, ensure_ascii=False, indent=2)
        print(f"\n리포트 저장: {args.report}", file=sys.stderr)


if __name__ == "__main__":
    main()
