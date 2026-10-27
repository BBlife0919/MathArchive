from __future__ import annotations

from fastapi import APIRouter, Depends

from ..deps import require_approved
from ..schemas.classes import (
    AssignStudentsRequest, ClassBasic, ClassListResponse, ClassStudent,
    ClassStudentsResponse, CreateClassRequest, UpdateClassRequest,
)
from ..services import class_service

router = APIRouter(
    prefix="/api/classes", tags=["classes"],
    dependencies=[Depends(require_approved)],
)


@router.get("", response_model=ClassListResponse)
def get_classes():
    return ClassListResponse(
        classes=[ClassBasic(**row) for row in class_service.list_classes()])


@router.post("", response_model=ClassBasic)
def create_class(req: CreateClassRequest):
    class_id = class_service.create_class(
        req.name.strip(), (req.teacher or "").strip() or None)
    return ClassBasic(class_id=class_id, name=req.name.strip(),
                      teacher=req.teacher, student_count=0)


@router.put("/{class_id}")
def update_class(class_id: int, req: UpdateClassRequest):
    class_service.update_class(class_id, req.name, req.teacher)
    return {"ok": True}


@router.delete("/{class_id}")
def delete_class(class_id: int):
    class_service.delete_class(class_id)
    return {"ok": True}


@router.post("/{class_id}/assign")
def assign_students(class_id: int, req: AssignStudentsRequest):
    class_service.assign_students(class_id, req.student_ids)
    return {"ok": True}


@router.get("/unassigned/students", response_model=ClassStudentsResponse)
def get_unassigned_students():
    # "/{class_id}/students" 보다 먼저 등록해야 한다 — 안 그러면 "unassigned"를
    # class_id(int)로 파싱하려다 422로 막혀 이 라우트에 아예 안 닿는다.
    return ClassStudentsResponse(
        students=[ClassStudent(**row)
                 for row in class_service.list_students_in_class(None)])


@router.get("/{class_id}/students", response_model=ClassStudentsResponse)
def get_class_students(class_id: int):
    return ClassStudentsResponse(
        students=[ClassStudent(**row)
                 for row in class_service.list_students_in_class(class_id)])
