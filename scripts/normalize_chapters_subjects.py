#!/usr/bin/env python3
"""중단원·과목 정규화:
1. 삼각함수 계열 chapter 4종을 curriculum 표준 표기로 통일
2. (구 교육과정) subject=수상/수하 행을 chapter 기준으로 공수1/공수2 재분류

사용:
    python3 scripts/normalize_chapters_subjects.py --dry-run
    python3 scripts/normalize_chapters_subjects.py
    python3 scripts/normalize_chapters_subjects.py --cloud --dry-run
    python3 scripts/normalize_chapters_subjects.py --cloud
"""
from __future__ import annotations

import argparse
import os
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


# [A] chapter rename 매핑 (사용자 지시)
CHAPTER_RENAME = {
    "삼각함수": "일반각과 호도법",
    "삼각함수의 그래프": "삼각함수와 그래프",
    "삼각형에의 활용": "사인법칙과 코사인법칙",
    "삼각함수의 활용": "사인법칙과 코사인법칙",
}

# [B] 공수1 chapters — 다항식 + 방정식과 부등식 + 경우의 수 (+ 행렬)
PYO1_CHAPTERS = {
    "다항식의 연산", "항등식과 나머지정리", "인수분해", "항등식",
    "복소수", "이차방정식", "이차함수", "고차방정식", "연립방정식",
    "부등식", "이차부등식", "여러가지 방정식", "여러가지부등식",
    "여러 가지 부등식",
    "경우의 수", "순열", "조합",
    "행렬의 뜻", "행렬의 연산",
}

# [B] 공수2 chapters — 도형의 방정식 + 집합과 명제 + 함수
PYO2_CHAPTERS = {
    "평면좌표", "직선의 방정식", "원의 방정식", "도형의 이동",
    "집합", "명제", "절대부등식",
    "함수", "합성함수", "역함수",
    "유리식과 유리함수", "무리식과 무리함수",
}


def run(conn, ph: str, dry_run: bool):
    cur = conn.cursor() if not hasattr(conn, "execute") else conn

    print("[A] 삼각함수 chapter 정규화")
    a_total = 0
    for src, dst in CHAPTER_RENAME.items():
        c = conn.execute(
            f"SELECT COUNT(*) FROM questions WHERE chapter={ph}", (src,)
        ).fetchone()[0]
        print(f"  {src!r:25s} → {dst!r:25s} : {c}건")
        a_total += c
        if not dry_run and c:
            conn.execute(
                f"UPDATE questions SET chapter={ph} WHERE chapter={ph}",
                (dst, src),
            )
    print(f"  합계: {a_total}건\n")

    print("[B] 수상/수하 → 공수1/공수2 재분류 (chapter 기준)")
    for old_subj, new_subj, chap_set in [
        ("수상", "공수1", PYO1_CHAPTERS),
        ("수상", "공수2", PYO2_CHAPTERS),
        ("수하", "공수1", PYO1_CHAPTERS),
        ("수하", "공수2", PYO2_CHAPTERS),
    ]:
        marks = ",".join([ph] * len(chap_set))
        c = conn.execute(
            f"SELECT COUNT(*) FROM questions "
            f"WHERE subject={ph} AND chapter IN ({marks})",
            (old_subj, *chap_set),
        ).fetchone()[0]
        print(f"  subject={old_subj} → {new_subj}: {c}건")
        if not dry_run and c:
            conn.execute(
                f"UPDATE questions SET subject={ph} "
                f"WHERE subject={ph} AND chapter IN ({marks})",
                (new_subj, old_subj, *chap_set),
            )

    # 매핑 안 된 수상/수하 잔여 행 보고
    print("\n[B] 매핑 못 한 수상/수하 잔여 chapter (subject 그대로):")
    for old_subj in ["수상", "수하"]:
        all_chaps = PYO1_CHAPTERS | PYO2_CHAPTERS
        marks = ",".join([ph] * len(all_chaps))
        rows = conn.execute(
            f"SELECT chapter, COUNT(*) c FROM questions "
            f"WHERE subject={ph} AND chapter NOT IN ({marks}) "
            f"GROUP BY chapter ORDER BY c DESC LIMIT 10",
            (old_subj, *all_chaps),
        ).fetchall()
        if rows:
            print(f"  subject={old_subj}:")
            for r in rows:
                print(f"    {r[0]!r:35s} {r[1]}")

    if not dry_run and hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cloud:
        import psycopg2

        class _W:
            def __init__(self, c):
                self._c = c
                self._cur = c.cursor()

            def execute(self, sql, params=()):
                self._cur.execute(sql, params)
                return self._cur

            def commit(self):
                self._c.commit()

        pconn = psycopg2.connect(os.environ["SUPABASE_DB_URL"])
        pconn.autocommit = False
        run(_W(pconn), "%s", args.dry_run)
        pconn.close()
    else:
        db = ROOT / "db" / "mathdb.sqlite"
        conn = sqlite3.connect(db)
        run(conn, "?", args.dry_run)
        conn.close()


if __name__ == "__main__":
    main()
