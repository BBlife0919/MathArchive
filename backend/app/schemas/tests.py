from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from .questions import QuestionCard


class CreateTestRequest(BaseModel):
    title: str
    class_id: Optional[int] = None
    question_ids: list[int]
    chapter_label: Optional[str] = None


class TestBasic(BaseModel):
    test_id: int
    title: str
    class_id: Optional[int] = None
    chapter_label: Optional[str] = None
    question_count: int
    created_at: Optional[str] = None


class StudentTestItem(BaseModel):
    test_id: int
    title: str
    chapter_label: Optional[str] = None
    question_count: int
    created_at: Optional[str] = None
    # 이 학생의 채점 상태 — result_id 가 None 이면 아직 채점 전("채점" 버튼),
    # 아니면 score/total 로 점수 표시.
    result_id: Optional[int] = None
    score: Optional[int] = None
    total: Optional[int] = None
    graded_at: Optional[str] = None


class StudentTestListResponse(BaseModel):
    tests: list[StudentTestItem]


class TestDetailResponse(BaseModel):
    test_id: int
    title: str
    chapter_label: Optional[str] = None
    items: list[QuestionCard]
    # 이미 채점된 적 있으면(재채점 시) 기존 O/X 를 모달에 미리 채워준다.
    existing_answers: dict[int, bool] = {}


class GradeAnswer(BaseModel):
    question_id: int
    is_correct: bool


class GradeTestRequest(BaseModel):
    student_id: int
    answers: list[GradeAnswer]


class GradeTestResponse(BaseModel):
    result_id: int
    score: int
    total: int
    wrong_question_ids: list[int]
    # 오답마다 처방된 유사문항 id 모음(중복 제거) — "오답학습지 만들기" 버튼용.
    prescribed_question_ids: list[int]
