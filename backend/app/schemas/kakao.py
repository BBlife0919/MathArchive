from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class StudentOption(BaseModel):
    student_id: int
    name: str


class CreateDraftRequest(BaseModel):
    student_id: int
    target_phone: str
    template_code: str = "WEEKLY_REPORT_V1"
    scheduled_at: str


class DraftItem(BaseModel):
    queue_id: int
    student_id: int
    student_name: str
    target_phone: str
    ai_draft: Optional[str] = None
    instructor_note: Optional[str] = None
    scheduled_at: str


class ApproveDraftRequest(BaseModel):
    instructor_note: str


class ApprovedItem(BaseModel):
    queue_id: int
    scheduled_at: str
    student_name: str
    target_phone: str
    instructor_note: Optional[str] = None


class SendLogItem(BaseModel):
    queue_id: int
    status: str
    student_name: str
    target_phone: str
    sent_at: Optional[str] = None
    solapi_msg_id: Optional[str] = None
    error_log: Optional[str] = None


class MessageResponse(BaseModel):
    ok: bool
    message: Optional[str] = None
