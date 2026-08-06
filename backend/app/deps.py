from __future__ import annotations

from typing import Optional

from fastapi import Cookie, HTTPException, status

from .services import auth_service


def get_current_user(
    session_token: Optional[str] = Cookie(default=None, alias=auth_service.SESSION_COOKIE_NAME),
) -> Optional[dict]:
    if not session_token:
        return None
    user_id = auth_service.decode_session_token(session_token)
    if not user_id:
        return None
    return auth_service.get_user_by_id(user_id)


def require_login(
    session_token: Optional[str] = Cookie(default=None, alias=auth_service.SESSION_COOKIE_NAME),
) -> dict:
    user = get_current_user(session_token)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "로그인이 필요합니다.")
    return user


def require_approved(
    session_token: Optional[str] = Cookie(default=None, alias=auth_service.SESSION_COOKIE_NAME),
) -> dict:
    user = require_login(session_token)
    if not user["approved"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "관리자 승인 대기 중입니다.")
    return user


def require_admin(
    session_token: Optional[str] = Cookie(default=None, alias=auth_service.SESSION_COOKIE_NAME),
) -> dict:
    user = require_approved(session_token)
    if not user["is_admin"]:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "관리자 전용 페이지입니다.")
    return user
