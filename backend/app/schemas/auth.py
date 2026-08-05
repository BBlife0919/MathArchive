from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class SignupRequest(BaseModel):
    name: str
    username: str
    password: str
    email: str


class LoginRequest(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    user_id: int
    username: str
    name: str
    email: str
    approved: bool
    is_admin: bool


class MeResponse(BaseModel):
    logged_in: bool
    user: Optional[UserOut] = None


class MessageResponse(BaseModel):
    ok: bool
    message: str


class PasswordResetRequest(BaseModel):
    email: str


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str
