from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class ErrorCodeItem(BaseModel):
    code: str
    display: str


class ClinicMetaResponse(BaseModel):
    error_codes: list[ErrorCodeItem]


class QuestionSearchResult(BaseModel):
    question_id: int
    school: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None
    exam_type: Optional[str] = None
    question_number: int
    chapter: Optional[str] = None
    difficulty: Optional[str] = None
    text_preview: str


class ClinicEntryRequest(BaseModel):
    student_id: int
    source_mode: Literal["db", "external"]
    wrong_question_id: Optional[int] = None
    external_label: Optional[str] = None
    error_code: str
    keyword: str = ""
    wrong_date: str


class RetrySchedule(BaseModel):
    d3: str
    d7: str
    d14: str
    d30: str


class ClinicEntryResponse(BaseModel):
    entry_id: int
    mode: Literal["db", "external"]
    prescribed_qids: list[int] = []
    prescription_question_ids: list[int] = []
    schedule: RetrySchedule
    student_name: str
    error_code: str
    external_label: Optional[str] = None


class PrescriptionPdfRequest(BaseModel):
    question_ids: list[int]
    title: str
    subtitle: str


class PendingRetry(BaseModel):
    entry_id: int
    student_id: int
    student_name: str
    wrong_question_id: Optional[int] = None
    external_label: Optional[str] = None
    wrong_date: str
    error_code: str
    due_flags: list[str]
