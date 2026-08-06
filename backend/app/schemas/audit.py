from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class BareWordItem(BaseModel):
    token: str
    count: int
    is_new: bool
    recommend_action: Optional[str] = None
    recommend_latex: Optional[str] = None
    is_geometry_label: bool


class StructScan(BaseModel):
    box_mismatch: int
    code_block: int
    total_questions: int


class ScanResponse(BaseModel):
    bare_words: list[BareWordItem]
    new_count: int
    struct: StructScan
    has_baseline: bool


class StructuralFixResult(BaseModel):
    questions_fixed: int
    solutions_fixed: int
    choices_fixed: int


class BulkAutoResult(BaseModel):
    mapped: int
    removed: int
    ignored: int
    affected_total: int
    remaining: int
    mapped_examples: list[str]
    ignored_examples: list[str]


class BulkManualItem(BaseModel):
    token: str
    action: str
    latex: str = ""


class BulkManualRequest(BaseModel):
    items: list[BulkManualItem]


class BulkManualResult(BaseModel):
    done: int
    affected: int
    remaining: int


class IgnoreRemainingResult(BaseModel):
    ignored: int


class FlaggedItem(BaseModel):
    flag_id: int
    question_id: int
    flagged_at: Optional[str] = None
    reason: Optional[str] = None
    school: Optional[str] = None
    year: Optional[int] = None
    semester: Optional[int] = None
    exam_type: Optional[str] = None
    question_number: Optional[int] = None
    chapter: Optional[str] = None
    question_text: Optional[str] = None


class FixAllFlaggedResult(BaseModel):
    fixed: int
    failed: int


class MessageResponse(BaseModel):
    ok: bool
    message: Optional[str] = None
