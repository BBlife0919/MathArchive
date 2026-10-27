from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ClassBasic(BaseModel):
    class_id: int
    name: str
    teacher: Optional[str] = None
    student_count: int = 0


class ClassListResponse(BaseModel):
    classes: list[ClassBasic]


class CreateClassRequest(BaseModel):
    name: str
    teacher: Optional[str] = None


class UpdateClassRequest(BaseModel):
    name: Optional[str] = None
    teacher: Optional[str] = None


class AssignStudentsRequest(BaseModel):
    student_ids: list[int]


class ClassStudent(BaseModel):
    student_id: int
    name: str
    school: Optional[str] = None
    grade: Optional[int] = None


class ClassStudentsResponse(BaseModel):
    students: list[ClassStudent]
