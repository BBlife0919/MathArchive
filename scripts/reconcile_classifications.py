"""두 분류 에이전트 결과를 비교하고 사용자 리뷰용 CSV 생성.

- 일치 항목 → 자동 채택
- 불일치 항목 → 둘 다 후보로 표기, REVIEW 플래그
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 4:
        print("usage: reconcile.py <a.json> <b.json> <out.csv>", file=sys.stderr)
        return 1
    a = json.loads(Path(sys.argv[1]).read_text())["questions"]
    b = json.loads(Path(sys.argv[2]).read_text())["questions"]
    out_path = Path(sys.argv[3])
    a_by = {x["q"]: x for x in a}
    b_by = {x["q"]: x for x in b}
    rows = []
    n_review = 0
    for q in sorted(set(list(a_by) + list(b_by))):
        ax = a_by.get(q, {})
        bx = b_by.get(q, {})
        chapter = ax.get("chapter") if ax.get("chapter") == bx.get("chapter") else f"{ax.get('chapter')} | {bx.get('chapter')}"
        difficulty = ax.get("difficulty") if ax.get("difficulty") == bx.get("difficulty") else f"{ax.get('difficulty')} | {bx.get('difficulty')}"
        if ax.get("matched_yutype") == bx.get("matched_yutype"):
            ytype = str(ax.get("matched_yutype"))
        else:
            ytype = f"{ax.get('matched_yutype')} | {bx.get('matched_yutype')}"
        if ax.get("grade") == bx.get("grade"):
            grade = ax.get("grade")
        else:
            grade = f"{ax.get('grade')} | {bx.get('grade')}"
        review = ("|" in chapter) or ("|" in difficulty) or ("|" in ytype) or ("|" in str(grade))
        if review:
            n_review += 1
        rows.append({
            "q": q,
            "chapter": chapter,
            "difficulty": difficulty,
            "matched_yutype": ytype,
            "grade": grade,
            "review": "Y" if review else "",
            "rationale_A": ax.get("rationale", ""),
            "rationale_B": bx.get("rationale", ""),
        })
    with out_path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["q","chapter","difficulty","matched_yutype","grade","review","rationale_A","rationale_B"])
        w.writeheader()
        w.writerows(rows)
    auto = len(rows) - n_review
    print(f"reconciled: {auto}/{len(rows)} auto-confirmed, {n_review} need review")
    print(f"wrote: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
