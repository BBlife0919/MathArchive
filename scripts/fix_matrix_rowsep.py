#!/usr/bin/env python3
"""행렬 환경의 행 구분자 보정.

`\\begin{pmatrix}...\\end{pmatrix}` 안에서 행 구분이 LaTeX 줄바꿈 `\\\\` 이어야
하는데, HWPX 변환에서 단일 `\\ `(백슬래시 + 공백)으로 저장된 케이스 전수 보정.
{p,b,v,V,B}matrix 모두 대상. idempotent.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import psycopg2

# matrix 환경 안의 ` \ ` (앞뒤 공백, 백슬래시 1개) → ` \\\\ `
# 또는 줄 끝의 `\ ` 같은 패턴도 포함
MATRIX_ENV = re.compile(
    r"(\\begin\{[pbvVB]?matrix\})(.*?)(\\end\{[pbvVB]?matrix\})",
    re.DOTALL,
)
# 한 줄 `\` 이고 그 뒤에 `\` 더 안 오는 경우(즉 `\\` 가 아닌 단독 `\`)
SINGLE_BS = re.compile(r"(?<!\\)\\(?!\\)(?=[\s&])")


def fix_text(t: str) -> str:
    if not t or "matrix" not in t:
        return t

    def _row(m):
        head, body, tail = m.group(1), m.group(2), m.group(3)
        # 단일 백슬래시 → 이중 백슬래시 (행 구분)
        new_body = SINGLE_BS.sub(r"\\\\", body)
        return head + new_body + tail

    return MATRIX_ENV.sub(_row, t)


def main():
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    cur = conn.cursor()

    cur.execute(
        r"SELECT question_id, question_text FROM questions "
        r"WHERE question_text ~ '\\begin\{[pbvVB]?matrix\}'"
    )
    qrows = cur.fetchall()
    print(f"Q 후보: {len(qrows)}")
    q_changed = 0
    for qid, t in qrows:
        nt = fix_text(t)
        if nt != t:
            cur.execute(
                "UPDATE questions SET question_text=%s WHERE question_id=%s",
                (nt, qid),
            )
            q_changed += 1
    print(f"  Q UPDATE: {q_changed}")

    cur.execute(
        r"SELECT solution_id, solution_text FROM solutions "
        r"WHERE solution_text ~ '\\begin\{[pbvVB]?matrix\}'"
    )
    srows = cur.fetchall()
    print(f"S 후보: {len(srows)}")
    s_changed = 0
    for sid, t in srows:
        nt = fix_text(t)
        if nt != t:
            cur.execute(
                "UPDATE solutions SET solution_text=%s WHERE solution_id=%s",
                (nt, sid),
            )
            s_changed += 1
    print(f"  S UPDATE: {s_changed}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"[OK] 보정 완료: Q {q_changed} + S {s_changed}")


if __name__ == "__main__":
    main()
