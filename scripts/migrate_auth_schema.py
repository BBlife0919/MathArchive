#!/usr/bin/env python3
"""인증 스키마 마이그레이션 (SQLite/Postgres 양쪽 멱등).

추가 테이블:
- users                  : 회원 마스터 (username, email, password_hash, approved, is_admin)
- password_reset_tokens  : 비번 재설정 토큰

분기:
- 클라우드 (SUPABASE_DB_URL 설정됨) → scripts/auth_schema.sql 적용
- 로컬 SQLite                       → 인라인 DDL_SQLITE 적용 + admin 자동 시드

로컬 admin 시드 환경변수 (없으면 기본값):
  LOCAL_ADMIN_USERNAME  (default: bblife0919)
  LOCAL_ADMIN_NAME      (default: 이영우)
  LOCAL_ADMIN_EMAIL     (default: eum-academy@naver.com)
  LOCAL_ADMIN_PASSWORD  (default: mathdb-local-2026)

실행:
    python scripts/migrate_auth_schema.py
    SUPABASE_DB_URL=postgresql://... python scripts/migrate_auth_schema.py
"""
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_PATH = ROOT / "scripts" / "auth_schema.sql"

sys.path.insert(0, str(ROOT / "app"))

from db import get_connection, is_cloud  # noqa: E402


DDL_SQLITE = [
    """
    CREATE TABLE IF NOT EXISTS users (
        user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
        username       TEXT NOT NULL UNIQUE,
        name           TEXT NOT NULL,
        email          TEXT NOT NULL UNIQUE,
        password_hash  TEXT NOT NULL,
        approved       INTEGER NOT NULL DEFAULT 0,
        is_admin       INTEGER NOT NULL DEFAULT 0,
        created_at     TEXT DEFAULT CURRENT_TIMESTAMP
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)",
    "CREATE INDEX IF NOT EXISTS idx_users_email ON users(email)",
    """
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        token       TEXT PRIMARY KEY,
        user_id     INTEGER NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
        created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
        expires_at  TEXT NOT NULL,
        used        INTEGER NOT NULL DEFAULT 0
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_reset_user ON password_reset_tokens(user_id)",
    "CREATE INDEX IF NOT EXISTS idx_reset_expires ON password_reset_tokens(expires_at)",
]


def _load_env_file() -> None:
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for line in env_path.read_text().splitlines():
        if line.strip().startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        os.environ.setdefault(k.strip(), v.strip())


def _migrate_postgres() -> None:
    """클라우드 경로 — scripts/auth_schema.sql 통째로 적용."""
    dsn = os.environ.get("SUPABASE_DB_URL")
    sql = SQL_PATH.read_text(encoding="utf-8")
    import psycopg2
    conn = psycopg2.connect(dsn)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(sql)
        print(f"[OK] {SQL_PATH.name} 적용 완료 (Supabase Postgres)")
    finally:
        cur.close()
        conn.close()


def _seed_local_admin(conn) -> tuple[bool, str]:
    """로컬 SQLite 전용: 사용자가 0명이면 admin 1명 자동 시드."""
    row = conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()
    count = row["n"] if hasattr(row, "keys") else row[0]
    if count > 0:
        return False, f"users 테이블에 이미 {count}명 등록됨 → 시드 skip"

    username = os.environ.get("LOCAL_ADMIN_USERNAME", "bblife0919")
    name = os.environ.get("LOCAL_ADMIN_NAME", "이영우")
    email = os.environ.get("LOCAL_ADMIN_EMAIL", "eum-academy@naver.com")
    password = os.environ.get("LOCAL_ADMIN_PASSWORD", "mathdb-local-2026")

    from auth import _hash_password
    pw_hash = _hash_password(password)

    conn.execute(
        "INSERT INTO users (username, name, email, password_hash, approved, is_admin) "
        "VALUES (?, ?, ?, ?, 1, 1)",
        (username, name, email, pw_hash),
    )
    return True, f"admin 시드 완료 → id={username} / pw={password}"


def _migrate_sqlite() -> None:
    conn = get_connection()
    for stmt in DDL_SQLITE:
        conn.execute(stmt)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    print("[OK] 인증 스키마 마이그레이션 완료 (로컬 SQLite)")
    print("     - users 테이블 생성/확인")
    print("     - password_reset_tokens 테이블 생성/확인")

    seeded, msg = _seed_local_admin(conn)
    if hasattr(conn, "commit"):
        try:
            conn.commit()
        except Exception:
            pass
    prefix = "[SEED]" if seeded else "[INFO]"
    print(f"     {prefix} {msg}")


def _reset_password(username: str, new_password: str) -> None:
    """기존 사용자의 비번만 갱신 (로컬 SQLite)."""
    os.environ.pop("SUPABASE_DB_URL", None)
    conn = get_connection()
    from auth import _hash_password
    pw_hash = _hash_password(new_password)
    cur = conn.execute(
        "UPDATE users SET password_hash = ? WHERE username = ?",
        (pw_hash, username),
    )
    if hasattr(conn, "commit"):
        conn.commit()
    affected = cur.rowcount if hasattr(cur, "rowcount") else 0
    if affected == 0:
        print(f"[FAIL] username={username} 사용자 없음")
        sys.exit(2)
    print(f"[OK] {username} 비번 변경 완료")


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--local", action="store_true",
                    help="강제로 로컬 SQLite 적용 (SUPABASE_DB_URL 무시)")
    ap.add_argument("--reset-password", action="store_true",
                    help="기존 사용자 비번만 변경 (LOCAL_ADMIN_USERNAME, "
                         "LOCAL_ADMIN_PASSWORD 환경변수 사용)")
    args = ap.parse_args()

    if args.reset_password:
        username = os.environ.get("LOCAL_ADMIN_USERNAME", "bblife0919")
        password = os.environ.get("LOCAL_ADMIN_PASSWORD")
        if not password:
            print("ERROR: LOCAL_ADMIN_PASSWORD 환경변수 필요", file=sys.stderr)
            sys.exit(1)
        _reset_password(username, password)
        return

    if args.local:
        os.environ.pop("SUPABASE_DB_URL", None)
        _migrate_sqlite()
        return

    _load_env_file()
    if is_cloud():
        _migrate_postgres()
    else:
        _migrate_sqlite()


if __name__ == "__main__":
    main()
