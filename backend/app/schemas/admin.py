from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class PendingUser(BaseModel):
    user_id: int
    username: str
    name: str
    email: str
    created_at: str


class AdminUser(BaseModel):
    user_id: int
    username: str
    name: str
    email: str
    approved: bool
    is_admin: bool
    created_at: str


class SetAdminRequest(BaseModel):
    is_admin: bool


class MessageResponse(BaseModel):
    ok: bool
    message: Optional[str] = None
