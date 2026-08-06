from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..deps import require_admin
from ..schemas.kakao import (
    ApprovedItem, ApproveDraftRequest, CreateDraftRequest, DraftItem,
    MessageResponse, SendLogItem, StudentOption,
)
from ..services import kakao_service

router = APIRouter(
    prefix="/api/kakao", tags=["kakao"],
    dependencies=[Depends(require_admin)],
)


@router.get("/students", response_model=list[StudentOption])
def get_students_for_draft():
    return kakao_service.list_students_for_draft()


@router.post("/drafts", response_model=MessageResponse)
def create_draft(req: CreateDraftRequest):
    if not req.target_phone.strip():
        raise HTTPException(422, "학부모 전화번호 입력 필수")
    if not req.scheduled_at.strip():
        raise HTTPException(422, "발송 예정일 입력 필수")
    kakao_service.create_draft(
        req.student_id, req.target_phone.strip(), req.template_code.strip(),
        req.scheduled_at,
    )
    return MessageResponse(ok=True)


@router.get("/drafts", response_model=list[DraftItem])
def get_drafts():
    return kakao_service.list_drafts()


@router.post("/drafts/{queue_id}/approve", response_model=MessageResponse)
def approve_draft(queue_id: int, req: ApproveDraftRequest):
    try:
        kakao_service.approve_draft(queue_id, req.instructor_note)
    except kakao_service.EmptyInstructorNote:
        raise HTTPException(422, "강사 코멘트가 비어있어 승인할 수 없습니다 (PDF §7-3 룰).")
    return MessageResponse(ok=True)


@router.delete("/drafts/{queue_id}", response_model=MessageResponse)
def delete_draft(queue_id: int):
    kakao_service.delete_draft(queue_id)
    return MessageResponse(ok=True)


@router.get("/approved", response_model=list[ApprovedItem])
def get_approved():
    return kakao_service.list_approved()


@router.post("/approved/{queue_id}/revert", response_model=MessageResponse)
def revert_draft(queue_id: int):
    kakao_service.revert_to_draft(queue_id)
    return MessageResponse(ok=True)


@router.get("/send-logs", response_model=list[SendLogItem])
def get_send_logs():
    return kakao_service.list_send_logs()
