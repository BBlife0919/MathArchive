from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel


class ContentSegment(BaseModel):
    type: Literal["text", "box", "image"]
    md: Optional[str] = None
    url: Optional[str] = None
    ref: Optional[str] = None


class QuestionCard(BaseModel):
    question_id: int
    meta_short: str
    meta_full: str
    school: Optional[str] = None
    chapter: Optional[str] = None
    difficulty: Optional[str] = None
    points: Optional[float] = None
    is_subjective: bool = False
    error_note: Optional[str] = None
    content_segments: list[ContentSegment]
    choices_text: str = ""
    answer: Optional[str] = None
    answer_display: Optional[str] = None
    solution_segments: list[ContentSegment] = []


class SearchRequest(BaseModel):
    quick_search: str = ""
    regions: list[str] = []
    schools: list[str] = []
    grades: list[int] = []
    years: list[int] = []
    semesters: list[int] = []
    exam_types: list[str] = []
    subjects: list[str] = []
    majors: list[str] = []
    minors: list[str] = []
    difficulties: list[str] = []
    question_type: Literal["all", "choice", "subjective"] = "all"
    keyword: str = ""
    page: int = 0
    page_size: int = 15


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[QuestionCard]


class ByIdsRequest(BaseModel):
    question_ids: list[int]


class ByIdsResponse(BaseModel):
    items: list[QuestionCard]


class SearchIdsResponse(BaseModel):
    question_ids: list[int]
