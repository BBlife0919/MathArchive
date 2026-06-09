#!/usr/bin/env python3
"""ANG/ANGLE → \\angle 보정.

HWP 수식편집기 변환에서 'ANGLE A' 가 'ANG <= A' 또는 'ANG ≤ A' 로 깨져
들어옴 — LE 두 글자가 '<=' 로 잘못 매핑된 결과. 전수 보정.

idempotent: 이미 \\angle 인 행은 건너뜀.
"""
from __future__ import annotations

import os
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import psycopg2

# ANG (공백) {<=|≤|\leq} (공백) X  → \angle X
# 캡처: X = 다음 식별자 (대문자 시퀀스, \mathrm{...}, A 등)
PATTERNS = [
    # ANG ≤ XYZ
    (re.compile(r"ANG\s*(?:≤|<=|\\leq)\s*"), r"\\angle "),
    # ANGLE XYZ (이미 ANGLE 형태로 들어왔지만 변환 X)
    (re.compile(r"\bANGLE\s+"), r"\\angle "),
]


def fix_text(t: str) -> str:
    if not t:
        return t
    out = t
    for pat, rep in PATTERNS:
        out = pat.sub(rep, out)
    return out


def main():
    conn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
    conn.autocommit = False
    cur = conn.cursor()

    # questions
    cur.execute("SELECT question_id, question_text FROM questions WHERE question_text ~ 'ANG\\s*(≤|<=|\\\\leq|LE\\s)'")
    qrows = cur.fetchall()
    print(f"Q 후보: {len(qrows)}")
    q_changed = 0
    for qid, t in qrows:
        nt = fix_text(t)
        if nt != t:
            cur.execute("UPDATE questions SET question_text=%s WHERE question_id=%s", (nt, qid))
            q_changed += 1
    print(f"  Q UPDATE: {q_changed}")

    # solutions
    cur.execute("SELECT solution_id, solution_text FROM solutions WHERE solution_text ~ 'ANG\\s*(≤|<=|\\\\leq|LE\\s)'")
    srows = cur.fetchall()
    print(f"S 후보: {len(srows)}")
    s_changed = 0
    for sid, t in srows:
        nt = fix_text(t)
        if nt != t:
            cur.execute("UPDATE solutions SET solution_text=%s WHERE solution_id=%s", (nt, sid))
            s_changed += 1
    print(f"  S UPDATE: {s_changed}")

    conn.commit()
    cur.close()
    conn.close()
    print(f"[OK] 보정 완료: Q {q_changed} + S {s_changed}")


if __name__ == "__main__":
    main()
