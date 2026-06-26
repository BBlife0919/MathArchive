#!/usr/bin/env python3
"""첨자/지수 공백 + sinpi 라텍스 정규화 보정.

HWPX 변환 잔재 두 종류:
1) `a _{11}`, `\\sum _{k=1}` 같이 _변수/큰연산자_ + 공백 + `_`/`^` → KaTeX 가
   첨자/limits 로 묶지 않고 _옆_ 에 큰 글씨로 노출. 공백 제거.
2) `sinpix`, `cospi` 같이 함수+그리스+변수 raw 결합 → 5글자 식별자로 렌더.
   `\\sin\\pi x` 로 분리.

본문(question_text)·해설(solution_text)·선지(choices jsonb) 세 영역 모두. idempotent.
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import psycopg2

# 함수+pi+변수 / 함수+pi
RE_FUNC_PI_VAR = re.compile(r"\b(sin|cos|tan|sec|csc|cot|log|ln)pi([a-zA-Z])\b")
RE_FUNC_PI = re.compile(r"\b(sin|cos|tan|sec|csc|cot|log|ln)pi\b")
# 큰 연산자 + 공백 + _/^
BIG_OPS = "sum|prod|int|iint|iiint|oint|coprod|bigcup|bigcap|biguplus|bigvee|bigwedge|bigsqcup|bigodot|bigotimes|bigoplus|lim"
RE_BIG_SPACE_SUB = re.compile(rf"(\\(?:{BIG_OPS}))\s+(?=[_^])")
# 변수/괄호닫기 + 공백 + _/^
RE_VAR_SPACE_SUB = re.compile(r"([A-Za-z\}\)\]])\s+(?=[_^])")


def fix_text(t: str) -> str:
    if not t:
        return t
    out = t
    # 1) sinpix → \sin\pi x
    out = RE_FUNC_PI_VAR.sub(r"\\\1\\pi \2", out)
    out = RE_FUNC_PI.sub(r"\\\1\\pi", out)
    # 2) \sum _{...} → \sum_{...}
    out = RE_BIG_SPACE_SUB.sub(r"\1", out)
    # 3) a _{...} → a_{...}
    out = RE_VAR_SPACE_SUB.sub(r"\1", out)
    return out


def _connect():
    return psycopg2.connect(
        os.environ["SUPABASE_DB_URL"],
        connect_timeout=30,
        keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=3,
        options="-c statement_timeout=180000",
    )


def _bulk_update_text(table, id_col, text_col, where_regex, batch=200, page=2000):
    """페이지네이션 ID 수집 후 배치 UPDATE."""
    ids = []
    offset = 0; fail = 0
    while fail < 5:
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                f"SELECT {id_col} FROM {table} WHERE {text_col} ~ %s "
                f"ORDER BY {id_col} LIMIT %s OFFSET %s",
                (where_regex, page, offset),
            )
            page_ids = [r[0] for r in cur.fetchall()]
            cur.close(); conn.close()
        except Exception as e:
            fail += 1
            print(f"  SELECT offset={offset} 실패({fail}/5): {e}")
            continue
        if not page_ids:
            break
        ids.extend(page_ids); offset += page
        print(f"  {table} 후보 누적: {len(ids)}")
    print(f"  {table}.{text_col} 후보 총: {len(ids)}")

    changed = 0
    for i in range(0, len(ids), batch):
        chunk = ids[i:i+batch]
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                f"SELECT {id_col}, {text_col} FROM {table} WHERE {id_col} = ANY(%s)",
                (chunk,),
            )
            for rid, t in cur.fetchall():
                nt = fix_text(t)
                if nt != t:
                    cur.execute(
                        f"UPDATE {table} SET {text_col}=%s WHERE {id_col}=%s",
                        (nt, rid),
                    )
                    changed += 1
            conn.commit(); cur.close(); conn.close()
            print(f"    batch {i//batch+1}/{(len(ids)+batch-1)//batch}: 누적 {changed}")
        except Exception as e:
            print(f"    batch {i//batch+1} 실패: {e}")
    return changed


def _bulk_update_choices(where_regex, batch=200, page=2000):
    ids = []
    offset = 0; fail = 0
    while fail < 5:
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                "SELECT question_id FROM questions WHERE choices::text ~ %s "
                "ORDER BY question_id LIMIT %s OFFSET %s",
                (where_regex, page, offset),
            )
            page_ids = [r[0] for r in cur.fetchall()]
            cur.close(); conn.close()
        except Exception as e:
            fail += 1
            print(f"  choices SELECT offset={offset} 실패({fail}/5): {e}")
            continue
        if not page_ids:
            break
        ids.extend(page_ids); offset += page
        print(f"  choices 후보 누적: {len(ids)}")
    print(f"  choices 후보 총: {len(ids)}")

    changed = 0
    for i in range(0, len(ids), batch):
        chunk = ids[i:i+batch]
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                "SELECT question_id, choices FROM questions WHERE question_id = ANY(%s)",
                (chunk,),
            )
            for qid, choices in cur.fetchall():
                if not choices:
                    continue
                new_choices = []; any_diff = False
                for ch in choices:
                    if isinstance(ch, dict):
                        old = ch.get("text", "") or ""
                        new = fix_text(old)
                        if new != old:
                            any_diff = True
                            ch = {**ch, "text": new}
                    new_choices.append(ch)
                if any_diff:
                    cur.execute(
                        "UPDATE questions SET choices=%s::jsonb WHERE question_id=%s",
                        (json.dumps(new_choices, ensure_ascii=False), qid),
                    )
                    changed += 1
            conn.commit(); cur.close(); conn.close()
            print(f"    batch {i//batch+1}: 누적 {changed}")
        except Exception as e:
            print(f"    batch {i//batch+1} 실패: {e}")
    return changed


def main():
    # 공백+첨자/지수 패턴 (확실히 잡히는 것만): [A-Za-z\}\)\]] + 공백 + _/^
    # 또는 \sum/... + 공백 + _/^
    # 또는 sinpi/cospi/tanpi
    where = r"([A-Za-z\}\)\]])[ \t]+[_^]|\\(sum|prod|int|iint|oint|coprod|bigcup|bigcap|lim)[ \t]+[_^]|\m(sin|cos|tan|sec|csc|cot|log|ln)pi\M"

    print("[Q] question_text")
    q = _bulk_update_text("questions", "question_id", "question_text", where)
    print(f"  Q UPDATE: {q}")

    print("[S] solution_text")
    s = _bulk_update_text("solutions", "solution_id", "solution_text", where)
    print(f"  S UPDATE: {s}")

    print("[C] choices")
    c = _bulk_update_choices(where)
    print(f"  C UPDATE: {c}")

    print(f"[OK] 완료: Q {q} + S {s} + choices {c} = {q+s+c}")


if __name__ == "__main__":
    main()
