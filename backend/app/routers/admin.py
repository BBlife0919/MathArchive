from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import require_admin
from ..schemas.admin import (
    AdminUser, MessageResponse, PendingUser, SetAdminRequest,
)
from ..services import auth_service

router = APIRouter(
    prefix="/api/admin", tags=["admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/pending-users", response_model=list[PendingUser])
def get_pending_users():
    return auth_service.list_pending_users()


@router.get("/users", response_model=list[AdminUser])
def get_all_users():
    return auth_service.list_all_users()


@router.post("/users/{user_id}/approve", response_model=MessageResponse)
def approve_user(user_id: int):
    ok, warn = auth_service.approve_user(user_id)
    return MessageResponse(ok=ok, message=warn)


@router.post("/users/{user_id}/revoke", response_model=MessageResponse)
def revoke_user(user_id: int):
    auth_service.revoke_user(user_id)
    return MessageResponse(ok=True)


@router.delete("/users/{user_id}", response_model=MessageResponse)
def delete_user(user_id: int):
    auth_service.delete_user(user_id)
    return MessageResponse(ok=True)


@router.post("/users/{user_id}/set-admin", response_model=MessageResponse)
def set_admin(user_id: int, req: SetAdminRequest):
    auth_service.set_admin(user_id, req.is_admin)
    return MessageResponse(ok=True)
