from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


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
    exclude_recent_days: Optional[int] = None


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    items: list[QuestionCard]


class ByIdsRequest(BaseModel):
    question_ids: list[int]
    preserve_order: bool = False


class ByIdsResponse(BaseModel):
    items: list[QuestionCard]


class SearchIdsResponse(BaseModel):
    question_ids: list[int]


class MiniTestRequest(SearchRequest):
    # 쉬운문제 비중은 main.py:931-937 슬라이더(0~100, 10% 단위) 그대로.
    # 문항 수는 원래 6~8(15분 컷)이었으나 2026-10-27 요청으로 30까지 확장.
    mini_count: int = Field(default=7, ge=6, le=30)
    mini_easy_pct: int = Field(default=40, ge=0, le=100)


class MiniTestResponse(BaseModel):
    question_ids: list[int]
    pool_size: int


class EvenDistributeRequest(SearchRequest):
    count: int = Field(default=20, ge=1, le=150)
    granularity: Literal["major", "minor"] = "major"
    # "직접 고르기" 모드에서 이미 수동으로 담은 문항 id. 자동배분 풀에서
    # 제외하고, count 에서도 그만큼 뺀 "모자란 개수"만 채운다.
    exclude_ids: list[int] = []


class EvenDistributeResult(BaseModel):
    group: str
    target: int
    picked: int
    pool: int


class EvenDistributeResponse(BaseModel):
    question_ids: list[int]
    results: list[EvenDistributeResult]


class ExamPaperRequest(BaseModel):
    regions: list[str] = []
    schools: list[str] = []
    grades: list[int] = []
    years: list[int] = []
    semesters: list[int] = []
    exam_types: list[str] = []
    subjects: list[str] = []


class ExamPaper(BaseModel):
    school: str
    grade: int
    year: int
    semester: int
    exam_type: str
    subject: Optional[str] = None
    chapter_range: Optional[str] = None
    question_count: int


class ExamPaperListResponse(BaseModel):
    papers: list[ExamPaper]


class ExamPaperIdsRequest(BaseModel):
    school: str
    grade: int
    year: int
    semester: int
    exam_type: str
    subject: Optional[str] = None
    chapter_range: Optional[str] = None
