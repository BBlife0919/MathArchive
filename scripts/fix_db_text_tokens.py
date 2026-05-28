#!/usr/bin/env python3
"""DB 전체 텍스트 컬럼(question_text / solution_text / choices)에
fix_nested_boxes + fix_unmapped_hwp_tokens 일괄 적용.

검수 페이지의 `auto_fix_structural` 와 동일 로직을 CLI 로 실행.
choices(JSON) 컬럼의 선지 text 까지 함께 처리한다.

사용:
    python3 scripts/fix_db_text_tokens.py             # 로컬 SQLite
    python3 scripts/fix_db_text_tokens.py --cloud     # Supabase Postgres
    python3 scripts/fix_db_text_tokens.py --dry-run   # 변경 행 수만 보고

`--cloud` 는 .env 의 SUPABASE_DB_URL 사용. dry-run 결과 확인 후 본 실행.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from fix_nested_boxes import fix_text as fix_nested  # noqa: E402
from fix_unmapped_hwp_tokens import fix_text as fix_tokens  # noqa: E402

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env")
except ImportError:
    pass


def _fix(text: str) -> str:
    if not text:
        return text
    return fix_tokens(fix_nested(text))


def _apply_to_choices(raw):
    """choices raw → (new_json_str_or_None, changed)."""
    if raw is None:
        return None, False
    if isinstance(raw, (list, dict)):
        choices = raw
    else:
        try:
            choices = json.loads(raw)
        except (TypeError, ValueError):
            return None, False
    if not choices:
        return None, False
    changed = False
    new_list = []
    for c in choices:
        if not isinstance(c, dict):
            new_list.append(c)
            continue
        t = c.get("text") or ""
        nt = _fix(t)
        if nt != t:
            changed = True
        new_c = dict(c)
        new_c["text"] = nt
        new_list.append(new_c)
    if not changed:
        return None, False
    return json.dumps(new_list, ensure_ascii=False), True


def run_sqlite(dry_run: bool):
    db = ROOT / "db" / "mathdb.sqlite"
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row

    n_q = n_ch = n_s = 0
    cur = conn.cursor()

    # question_text + choices
    rows = conn.execute(
        "SELECT question_id, question_text, choices FROM questions"
    ).fetchall()
    print(f"questions 행: {len(rows)}건 스캔")
    for r in rows:
        qid = r["question_id"]
        txt = r["question_text"]
        new_t = _fix(txt) if txt else txt
        if txt and new_t != txt:
            n_q += 1
            if not dry_run:
                cur.execute(
                    "UPDATE questions SET question_text=? WHERE question_id=?",
                    (new_t, qid),
                )
        new_ch, ch_changed = _apply_to_choices(r["choices"])
        if ch_changed:
            n_ch += 1
            if not dry_run:
                cur.execute(
                    "UPDATE questions SET choices=? WHERE question_id=?",
                    (new_ch, qid),
                )

    rows = conn.execute(
        "SELECT solution_id, solution_text FROM solutions"
    ).fetchall()
    print(f"solutions 행: {len(rows)}건 스캔")
    for r in rows:
        sid = r["solution_id"]
        txt = r["solution_text"]
        if not txt:
            continue
        new_t = _fix(txt)
        if new_t != txt:
            n_s += 1
            if not dry_run:
                cur.execute(
                    "UPDATE solutions SET solution_text=? WHERE solution_id=?",
                    (new_t, sid),
                )

    if not dry_run:
        conn.commit()
    conn.close()
    print()
    print(f"{'[DRY-RUN] ' if dry_run else ''}"
          f"수정 행: question_text={n_q}, choices={n_ch}, solution_text={n_s}")


def run_pg(dry_run: bool):
    import psycopg2
    from psycopg2.extras import DictCursor, execute_values

    dsn = os.environ.get("SUPABASE_DB_URL")
    if not dsn:
        sys.exit("SUPABASE_DB_URL 미설정")
    conn = psycopg2.connect(dsn, cursor_factory=DictCursor)
    conn.autocommit = False

    q_updates: list[tuple[int, str]] = []
    ch_updates: list[tuple[int, str]] = []
    s_updates: list[tuple[int, str]] = []

    cur = conn.cursor()
    cur.execute("SELECT question_id, question_text, choices FROM questions")
    rows = cur.fetchall()
    print(f"questions 행: {len(rows)}건 스캔")
    for r in rows:
        qid, txt, ch = r["question_id"], r["question_text"], r["choices"]
        new_t = _fix(txt) if txt else txt
        if txt and new_t != txt:
            q_updates.append((qid, new_t))
        new_ch, changed = _apply_to_choices(ch)
        if changed:
            ch_updates.append((qid, new_ch))

    cur.execute("SELECT solution_id, solution_text FROM solutions")
    rows = cur.fetchall()
    print(f"solutions 행: {len(rows)}건 스캔")
    for r in rows:
        sid, txt = r["solution_id"], r["solution_text"]
        if not txt:
            continue
        new_t = _fix(txt)
        if new_t != txt:
            s_updates.append((sid, new_t))

    print()
    print(f"{'[DRY-RUN] ' if dry_run else ''}"
          f"수정 대상: question_text={len(q_updates)}, "
          f"choices={len(ch_updates)}, solution_text={len(s_updates)}")

    if dry_run:
        conn.close()
        return

    if q_updates:
        execute_values(
            cur,
            "UPDATE questions SET question_text = data.t "
            "FROM (VALUES %s) AS data(id, t) "
            "WHERE questions.question_id = data.id",
            q_updates, template="(%s, %s)", page_size=500,
        )
    if ch_updates:
        execute_values(
            cur,
            "UPDATE questions SET choices = data.t::jsonb "
            "FROM (VALUES %s) AS data(id, t) "
            "WHERE questions.question_id = data.id",
            ch_updates, template="(%s, %s)", page_size=500,
        )
    if s_updates:
        execute_values(
            cur,
            "UPDATE solutions SET solution_text = data.t "
            "FROM (VALUES %s) AS data(id, t) "
            "WHERE solutions.solution_id = data.id",
            s_updates, template="(%s, %s)", page_size=500,
        )
    conn.commit()
    conn.close()
    print("✅ 클라우드 DB 적용 완료")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cloud", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.cloud:
        run_pg(args.dry_run)
    else:
        run_sqlite(args.dry_run)


if __name__ == "__main__":
    main()
