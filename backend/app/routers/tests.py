from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException

from ..deps import require_approved
from ..schemas.tests import (
    AssignTestRequest, AssignTestResponse, CreateTestRequest, GradeTestRequest,
    GradeTestResponse, StudentTestItem, StudentTestListResponse, TestBasic,
    TestDetailResponse, TestListItem, TestListResponse,
)
from ..services import test_service

router = APIRouter(
    prefix="/api/tests", tags=["tests"],
    dependencies=[Depends(require_approved)],
)


@router.post("", response_model=TestBasic)
def create_test(req: CreateTestRequest):
    test_id = test_service.create_test(
        req.title.strip(), req.class_id, req.question_ids,
        (req.chapter_label or "").strip() or None, created_by=None)
    return TestBasic(
        test_id=test_id, title=req.title.strip(), class_id=req.class_id,
        chapter_label=req.chapter_label, question_count=len(req.question_ids))


@router.get("", response_model=TestListResponse)
def list_tests():
    return TestListResponse(
        tests=[TestListItem(**row) for row in test_service.list_all_tests()])


@router.post("/{test_id}/assign", response_model=AssignTestResponse)
def assign_test(test_id: int, req: AssignTestRequest):
    n = test_service.assign_test(test_id, req.student_ids)
    return AssignTestResponse(ok=True, assigned_count=n)


@router.get("/student/{student_id}", response_model=StudentTestListResponse)
def list_student_tests(student_id: int):
    return StudentTestListResponse(
        tests=[StudentTestItem(**row)
              for row in test_service.list_tests_for_student(student_id)])


@router.get("/{test_id}", response_model=TestDetailResponse)
def get_test(test_id: int, student_id: Optional[int] = None):
    detail = test_service.get_test_detail(test_id, student_id)
    if detail is None:
        raise HTTPException(404, "테스트를 찾을 수 없습니다")
    return TestDetailResponse(**detail)


@router.post("/{test_id}/grade", response_model=GradeTestResponse)
def grade_test(test_id: int, req: GradeTestRequest):
    result = test_service.grade_test(
        test_id, req.student_id,
        [{"question_id": a.question_id, "is_correct": a.is_correct}
         for a in req.answers])
    return GradeTestResponse(**result)
