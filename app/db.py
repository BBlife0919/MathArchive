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
    """psycopg2 wrapper로 sqlite3.Connection.execute() 시그니처 모방.

    FastAPI 라우트는 동기 함수라 요청마다 별도 스레드에서 실행되는데,
    이 커넥션은 프로세스 전체에서 하나만 공유된다(db_service.py의 전역
    _conn). psycopg2/libpq는 커넥션 하나를 여러 스레드가 동시에 execute()
    하는 걸 보장하지 않아 프로토콜이 꼬여 영구 응답불가 상태(교착)에
    빠질 수 있다(2026-10-21 /api/filters 무한로딩으로 실제 발생 확인).
    execute() 전체를 락으로 감싸 한 번에 한 스레드만 쓰도록 강제한다.
    """

    def __init__(self, dsn: str):
        import threading
        self._dsn = dsn
        self._lock = threading.Lock()
        self._open()

    def _open(self):
        import psycopg2
        from psycopg2.extras import DictCursor
        self._conn = psycopg2.connect(self._dsn, cursor_factory=DictCursor, connect_timeout=10)
        self._conn.autocommit = True

    def execute(self, sql: str, params=()):
        sql_pg = _qmark_to_pyformat(sql)
        with self._lock:
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
