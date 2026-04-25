"""DB 연결 추상화 — 로컬 SQLite ↔ 클라우드 Supabase Postgres 자동 전환.

SUPABASE_DB_URL 이 환경변수 또는 Streamlit secrets 에 설정돼 있으면 Postgres,
없으면 로컬 db/mathdb.sqlite 사용.
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

SQLITE_PATH = Path(__file__).resolve().parent.parent / "db" / "mathdb.sqlite"


def _get_pg_url() -> str | None:
    url = os.environ.get("SUPABASE_DB_URL")
    if url:
        return url
    try:
        import streamlit as st
        if hasattr(st, "secrets") and "SUPABASE_DB_URL" in st.secrets:
            return st.secrets["SUPABASE_DB_URL"]
    except Exception:
        pass
    return None


def is_cloud() -> bool:
    return bool(_get_pg_url())


def _qmark_to_pyformat(sql: str) -> str:
    out = []
    in_single = False
    in_double = False
    for c in sql:
        if c == "'" and not in_double:
            in_single = not in_single
            out.append(c)
        elif c == '"' and not in_single:
            in_double = not in_double
            out.append(c)
        elif c == "?" and not in_single and not in_double:
            out.append("%s")
        else:
            out.append(c)
    return "".join(out)


class _PgConnection:
    """psycopg2 wrapper로 sqlite3.Connection.execute() 시그니처 모방."""

    def __init__(self, dsn: str):
        self._dsn = dsn
        self._open()

    def _open(self):
        import psycopg2
        from psycopg2.extras import DictCursor
        self._conn = psycopg2.connect(self._dsn, cursor_factory=DictCursor)
        self._conn.autocommit = True

    def execute(self, sql: str, params=()):
        sql_pg = _qmark_to_pyformat(sql)
        try:
            cur = self._conn.cursor()
            cur.execute(sql_pg, params)
        except Exception:
            try:
                self._conn.close()
            except Exception:
                pass
            self._open()
            cur = self._conn.cursor()
            cur.execute(sql_pg, params)
        return cur


def get_connection():
    pg_url = _get_pg_url()
    if pg_url:
        return _PgConnection(pg_url)
    conn = sqlite3.connect(str(SQLITE_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
