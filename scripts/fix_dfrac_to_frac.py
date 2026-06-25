#!/usr/bin/env python3
"""\\dfrac → \\frac 일괄 보정.

\\dfrac (displaystyle 강제) 가 첨자/지수 안에서도 displaystyle 크기로 렌더되어
분수만 비정상적으로 크고 괄호/중괄호 자동 확대 유발. \\frac 으로 통일하면
context 에 맞춰 자동 조정됨. idempotent.

본문(question_text)·해설(solution_text)·선지(choices jsonb) 세 영역 모두.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

import psycopg2


def fix_text(t: str) -> str:
    if not t or "\\dfrac" not in t:
        return t
    return t.replace("\\dfrac", "\\frac")


def _connect():
    """keepalive + statement timeout 길게."""
    conn = psycopg2.connect(
        os.environ["SUPABASE_DB_URL"],
        connect_timeout=30,
        keepalives=1, keepalives_idle=30, keepalives_interval=10, keepalives_count=3,
        options="-c statement_timeout=180000",  # 3분
    )
    return conn


def _bulk_update(table, id_col, text_col, batch=200, page=2000):
    """페이지네이션 SELECT + 작은 배치 UPDATE."""
    # 1) 후보 ID 만 페이지네이션으로 수집. % 는 psycopg2 placeholder 충돌 → %%
    ids = []
    offset = 0
    fail = 0
    while fail < 5:
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                f"SELECT {id_col} FROM {table} WHERE {text_col} LIKE %s "
                f"ORDER BY {id_col} LIMIT %s OFFSET %s",
                ("%\\dfrac%", page, offset),
            )
            page_ids = [r[0] for r in cur.fetchall()]
            cur.close(); conn.close()
        except Exception as e:
            fail += 1
            print(f"  SELECT offset={offset} 실패({fail}/5): {e}")
            continue
        if not page_ids:
            break
        ids.extend(page_ids)
        offset += page
        print(f"  {table} 후보 누적: {len(ids)}")
    print(f"  {table}.{text_col} 후보: {len(ids)}")

    # 2) batch 단위로 ID → text 가져와서 보정 + UPDATE
    changed = 0
    for i in range(0, len(ids), batch):
        chunk_ids = ids[i:i+batch]
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                f"SELECT {id_col}, {text_col} FROM {table} "
                f"WHERE {id_col} = ANY(%s)",
                (chunk_ids,),
            )
            rows = cur.fetchall()
            for rid, t in rows:
                nt = fix_text(t)
                if nt != t:
                    cur.execute(f"UPDATE {table} SET {text_col}=%s WHERE {id_col}=%s", (nt, rid))
                    changed += 1
            conn.commit()
            cur.close(); conn.close()
            print(f"    batch {i//batch+1}/{(len(ids)+batch-1)//batch}: 누적 {changed}건")
        except Exception as e:
            print(f"    batch {i//batch+1} 실패: {e}")
    return changed


def main():
    print("[Q] question_text")
    q_changed = _bulk_update("questions", "question_id", "question_text")
    print(f"  Q UPDATE: {q_changed}")

    print("[S] solution_text")
    s_changed = _bulk_update("solutions", "solution_id", "solution_text")
    print(f"  S UPDATE: {s_changed}")

    # choices (jsonb) — 페이지네이션 ID 수집 후 배치 UPDATE
    print("[C] choices")
    c_ids = []
    offset = 0; fail = 0; page = 2000
    while fail < 5:
        try:
            conn = _connect(); cur = conn.cursor()
            cur.execute(
                "SELECT question_id FROM questions WHERE choices::text LIKE %s "
                "ORDER BY question_id LIMIT %s OFFSET %s",
                ("%\\dfrac%", page, offset),
            )
            page_ids = [r[0] for r in cur.fetchall()]
            cur.close(); conn.close()
        except Exception as e:
            fail += 1
            print(f"  SELECT offset={offset} 실패({fail}/5): {e}")
            continue
        if not page_ids:
            break
        c_ids.extend(page_ids)
        offset += page
    print(f"  choices 후보: {len(c_ids)}")
    c_changed = 0
    batch = 200
    for i in range(0, len(c_ids), batch):
        chunk_ids = c_ids[i:i+batch]
        try:
            conn = _connect()
            cur = conn.cursor()
            cur.execute(
                "SELECT question_id, choices FROM questions WHERE question_id = ANY(%s)",
                (chunk_ids,),
            )
            for qid, choices in cur.fetchall():
                if not choices:
                    continue
                new_choices = []
                any_diff = False
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
                    c_changed += 1
            conn.commit()
            cur.close(); conn.close()
            print(f"    batch {i//batch+1}: 누적 {c_changed}건")
        except Exception as e:
            print(f"    batch {i//batch+1} 실패: {e}")
    print(f"  choices UPDATE: {c_changed}")

    print(f"[OK] 보정 완료: Q {q_changed} + S {s_changed} + choices {c_changed}")


if __name__ == "__main__":
    main()
