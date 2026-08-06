"""인증 서비스 — app/auth.py 의 순수 함수(검증·해시·토큰)는 그대로 재사용하고,
`st.session_state`/쿠키에 강결합된 부분(login 의 세션 기록, 쿠키 발급)만
HTTP 쿠키 기반으로 새로 작성한다 (계획서 "C등급" 항목).
"""
from __future__ import annotations

from .. import legacy_bridge  # noqa: F401
from ..config import CORS_ORIGINS  # noqa: F401  (.env 로드 트리거)

import auth as legacy_auth  # type: ignore
from db import is_cloud  # type: ignore

SESSION_COOKIE_NAME = legacy_auth.SESSION_COOKIE_NAME
SESSION_TTL_DAYS = legacy_auth.SESSION_TTL_DAYS


def cookie_secure() -> bool:
    return is_cloud()


def encode_session_token(user_id: int) -> str:
    return legacy_auth._encode_session_token(user_id)


def decode_session_token(token: str) -> int | None:
    return legacy_auth._decode_session_token(token)


def _row_to_user(row) -> dict:
    return {
        "user_id": row["user_id"],
        "username": row["username"],
        "name": row["name"],
        "email": row["email"],
        "approved": bool(row["approved"]),
        "is_admin": bool(row["is_admin"]),
    }


def login(username: str, password: str) -> tuple[bool, str, dict | None]:
    """auth.login() 의 DB 조회+검증 로직 그대로, session_state/쿠키 기록만 제외."""
    for err in (legacy_auth.validate_username(username),
                legacy_auth.validate_password(password)):
        if err:
            return False, err, None

    conn = legacy_auth._conn()
    try:
        cur = conn.execute(
            "SELECT user_id, username, name, email, password_hash, "
            "approved, is_admin FROM users WHERE username = ?",
            (username,),
        )
        row = cur.fetchone()
    except Exception as e:
        return False, f"로그인 실패: {e}", None

    if not row:
        return False, "아이디 또는 비밀번호가 올바르지 않습니다.", None
    if not legacy_auth._check_password(password, row["password_hash"]):
        return False, "아이디 또는 비밀번호가 올바르지 않습니다.", None

    user = _row_to_user(row)
    if not user["approved"]:
        return True, "로그인은 됐지만 아직 관리자 승인 대기 중입니다.", user
    return True, f"환영합니다, {user['name']}님.", user


def get_user_by_id(user_id: int) -> dict | None:
    conn = legacy_auth._conn()
    cur = conn.execute(
        "SELECT user_id, username, name, email, approved, is_admin "
        "FROM users WHERE user_id = ?",
        (user_id,),
    )
    row = cur.fetchone()
    return _row_to_user(row) if row else None


def signup(name: str, username: str, password: str, email: str) -> tuple[bool, str]:
    return legacy_auth.signup(name, username, password, email)


def request_password_reset(email: str) -> tuple[bool, str]:
    return legacy_auth.request_password_reset(email)


def consume_reset_token(token: str, new_password: str) -> tuple[bool, str]:
    return legacy_auth.consume_reset_token(token, new_password)


def _iso(v):
    """다른 서비스와 동일한 함정 — Postgres 는 TIMESTAMPTZ 컬럼을 datetime
    객체로, SQLite 는 문자열로 반환한다."""
    return v.isoformat() if hasattr(v, "isoformat") else v


def list_pending_users() -> list[dict]:
    rows = legacy_auth.list_pending_users()
    for r in rows:
        r["created_at"] = _iso(r["created_at"])
    return rows


def list_all_users() -> list[dict]:
    rows = legacy_auth.list_all_users()
    for r in rows:
        r["created_at"] = _iso(r["created_at"])
        r["approved"] = bool(r["approved"])
        r["is_admin"] = bool(r["is_admin"])
    return rows


def approve_user(user_id: int) -> tuple[bool, str | None]:
    return legacy_auth.approve_user(user_id)


def revoke_user(user_id: int) -> None:
    legacy_auth.revoke_user(user_id)


def delete_user(user_id: int) -> None:
    legacy_auth.delete_user(user_id)


def set_admin(user_id: int, is_admin: bool) -> None:
    legacy_auth.set_admin(user_id, is_admin)
