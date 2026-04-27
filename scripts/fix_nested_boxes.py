#!/usr/bin/env python3
"""DB 클린업 — 외곽 rect 가 내부 tbl 을 감싸면서 만든 BOX 중첩 + 셀 덤프 제거.

근본 원인은 parse_hwpx.py 의 rect 핸들러가 내부 tbl 을 감지하지 못해 외곽
BOX 를 추가로 발행하면서, 동시에 drawText subList 를 iter() 로 재귀 순회해
표 셀 값을 본문에 덤프했던 것. 파서는 이미 수정됨. 이 스크립트는 기존 DB 에
들어있는 정확히 그 패턴 — 외곽 BOX 의 비-BOX 컨텐츠가 짧은 단독 수식으로만
구성된 경우 — 만 정리한다. 다른 의미 있는 외곽 BOX(풀이 박스 안의 (가) 박스
같은 케이스)는 건드리지 않는다.

사용법:
    python3 scripts/fix_nested_boxes.py            # 미리보기
    python3 scripts/fix_nested_boxes.py --apply    # 실제 반영
"""
from __future__ import annotations

import argparse
import re
import sqlite3

BOX_START = "<<BOX_START>>"
BOX_END = "<<BOX_END>>"


def _tokenize(text: str):
    return re.split(r"(<<BOX_START>>|<<BOX_END>>)", text)


def _build_tree(parts):
    root = []
    stack = [root]
    for p in parts:
        if p == BOX_START:
            new_box = []
            stack[-1].append(("BOX", new_box))
            stack.append(new_box)
        elif p == BOX_END:
            if len(stack) <= 1:
                return root, False
            stack.pop()
        else:
            stack[-1].append(p)
    if len(stack) != 1:
        return root, False
    return root, True


def _outer_text(items) -> str:
    """박스 내부에서 비-BOX 컨텐츠만 합친 문자열."""
    return "".join(x for x in items if not isinstance(x, tuple))


def _is_shadow_dump(items) -> bool:
    """외곽 BOX 내부의 비-BOX 컨텐츠가 셀 값 덤프(짧은 단독 수식 나열)인가.

    조건: 비-BOX 컨텐츠를 줄 단위로 봤을 때
      - 줄 수 ≥ 3
      - 그 중 70% 이상이 짧은 단독 수식(`^\$[^$]{1,20}\$$`) 또는 빈 줄
      - 텍스트성 한글/문장이 거의 없음
    """
    text = _outer_text(items).strip()
    if not text:
        # 외곽이 완전히 비어있으면 그것도 외곽 BOX 가 잉여라는 신호
        return True
    lines = [ln.strip() for ln in text.split("\n")]
    nonempty = [ln for ln in lines if ln]
    if len(nonempty) < 3:
        return False
    short_math = sum(
        1 for ln in nonempty
        if re.fullmatch(r"\$[^$]{1,20}\$", ln)
    )
    if short_math / len(nonempty) < 0.7:
        return False
    # 한글/영문 단어가 섞여있으면 단순 셀 덤프가 아님.
    # LaTeX 명령(\dfrac, \boxed 등)은 텍스트로 보지 않는다.
    text_stripped = re.sub(r"\$[^$]*\$", " ", text)  # 수식 통째로 제거
    text_stripped = re.sub(r"\\[a-zA-Z]+", " ", text_stripped)
    has_text = bool(re.search(r"[가-힣A-Za-z]{2,}", text_stripped))
    if has_text:
        return False
    return True


_SHADOW_TAIL = re.compile(
    r"(?:\n\s*\$[^$\n]{1,20}\$\s*){3,}\s*$",
    re.MULTILINE,
)


def _strip_shadow_tail(text: str) -> str:
    """텍스트 끝부분에 누적된 셀 덤프(짧은 단독 수식 3+개 연속) 제거."""
    return _SHADOW_TAIL.sub("\n", text)


def _render(items) -> str:
    """트리를 텍스트로 복원.

    1) 외곽 BOX 가 전체적으로 shadow 덤프면 외곽을 벗기고 내부 BOX 만 남김.
    2) 그렇지 않더라도 BOX 내부 끝부분에 셀 덤프가 누적돼 있으면 그 부분만
       잘라낸다 (예: 풀이 본문 + 표 + 셀 덤프 형태).
    """
    out = []
    for x in items:
        if isinstance(x, tuple) and x[0] == "BOX":
            inner_items = x[1]
            has_inner_box = any(
                isinstance(y, tuple) and y[0] == "BOX" for y in inner_items
            )
            if has_inner_box and _is_shadow_dump(inner_items):
                # 외곽 BOX 벗기기 — 내부 BOX 만 살림
                inner_only = [
                    y for y in inner_items
                    if isinstance(y, tuple) and y[0] == "BOX"
                ]
                out.append(_render(inner_only))
            else:
                inner_rendered = _render(inner_items)
                # BOX 안 trailing shadow 만 제거
                inner_rendered = _strip_shadow_tail(inner_rendered)
                out.append(
                    f"\n{BOX_START}\n{inner_rendered}\n{BOX_END}\n"
                )
        else:
            out.append(x)
    return "".join(out)


def fix_text(text: str) -> str:
    if not text or BOX_START not in text:
        return text
    if not re.search(r"<<BOX_START>>(?:[^<]|<(?!<BOX_END>>))*?<<BOX_START>>",
                     text, re.S):
        return text
    parts = _tokenize(text)
    tree, ok = _build_tree(parts)
    if not ok:
        return text
    fixed = _render(tree)
    fixed = re.sub(r"\n{3,}", "\n\n", fixed)
    return fixed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="db/mathdb.sqlite")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--show", type=int, default=0,
                    help="샘플 N건 BEFORE/AFTER 출력")
    args = ap.parse_args()

    conn = sqlite3.connect(args.db)
    cur = conn.cursor()

    targets = [
        ("questions", "question_id", "question_text"),
        ("solutions", "solution_id", "solution_text"),
    ]

    grand = 0
    for table, idcol, txtcol in targets:
        rows = cur.execute(
            f"SELECT {idcol}, {txtcol} FROM {table} "
            f"WHERE {txtcol} LIKE '%<<BOX_START>>%<<BOX_START>>%'"
        ).fetchall()
        print(f"[{table}] 후보 {len(rows)}건")
        changed = 0
        shown = 0
        for rid, txt in rows:
            new = fix_text(txt or "")
            if new != txt:
                changed += 1
                if shown < args.show:
                    print(f"\n  --- {table}.{idcol}={rid} ---")
                    print(f"  BEFORE ({len(txt)}자):\n{txt[:400]}\n...")
                    print(f"  AFTER  ({len(new)}자):\n{new[:400]}")
                    shown += 1
                if args.apply:
                    cur.execute(
                        f"UPDATE {table} SET {txtcol}=? WHERE {idcol}=?",
                        (new, rid),
                    )
        print(f"[{table}] 실제 변경: {changed}/{len(rows)}건")
        grand += changed

    if args.apply:
        conn.commit()
        print(f"\n✅ 적용 완료. 총 {grand}건 갱신.")
    else:
        print(f"\n[미리보기] 총 {grand}건 변경 예정. --apply 옵션으로 반영.")
    conn.close()


if __name__ == "__main__":
    main()
