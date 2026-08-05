from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Response

from ..deps import get_current_user
from ..schemas.auth import (
    LoginRequest, MeResponse, MessageResponse, PasswordResetConfirm,
    PasswordResetRequest, SignupRequest,
)
from ..services import auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/signup", response_model=MessageResponse)
def signup(req: SignupRequest):
    ok, msg = auth_service.signup(req.name, req.username, req.password, req.email)
    return MessageResponse(ok=ok, message=msg)


@router.post("/login", response_model=MeResponse)
def login(req: LoginRequest, response: Response):
    ok, msg, user = auth_service.login(req.username, req.password)
    if not ok or not user:
        return MeResponse(logged_in=False)

    token = auth_service.encode_session_token(user["user_id"])
    response.set_cookie(
        key=auth_service.SESSION_COOKIE_NAME,
        value=token,
        max_age=auth_service.SESSION_TTL_DAYS * 86400,
        httponly=True,
        samesite="lax",
        secure=auth_service.cookie_secure(),
    )
    return MeResponse(logged_in=True, user=user)


@router.post("/logout", response_model=MessageResponse)
def logout(response: Response):
    response.delete_cookie(auth_service.SESSION_COOKIE_NAME)
    return MessageResponse(ok=True, message="로그아웃되었습니다.")


@router.get("/me", response_model=MeResponse)
def me(user: Optional[dict] = Depends(get_current_user)):
    if not user:
        return MeResponse(logged_in=False)
    return MeResponse(logged_in=True, user=user)


@router.post("/request-password-reset", response_model=MessageResponse)
def request_password_reset(req: PasswordResetRequest):
    ok, msg = auth_service.request_password_reset(req.email)
    return MessageResponse(ok=ok, message=msg)


@router.post("/reset-password", response_model=MessageResponse)
def reset_password(req: PasswordResetConfirm):
    ok, msg = auth_service.consume_reset_token(req.token, req.new_password)
    return MessageResponse(ok=ok, message=msg)
