from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException

from ..deps import require_approved
from ..schemas.students import (
    ManagementLogRequest, PrismEvalRequest, ProgressLogRequest,
    QualitativeAssessmentRequest, QuantityAssessmentRequest, SelfPredictRequest,
    StudentBasic, StudentDashboard, StudentTemplateItem, StudentTemplatesResponse,
    UpdateStudentBasicRequest,
)
from ..services import student_service

router = APIRouter(
    prefix="/api/students", tags=["students"],
    dependencies=[Depends(require_approved)],
)

# app/pages/2_학생카드.py:131 — output/student_templates/ 의 고정 3종 양식.
TEMPLATES_DIR = Path(__file__).resolve().parents[3] / "output" / "student_templates"
_TEMPLATE_FILES = [
    ("풀이노트_양식.pdf", "풀이노트"),
    ("오답노트_양식.pdf", "오답노트"),
    ("교재표시_규칙.pdf", "교재표시 규칙"),
]


@router.get("", response_model=list[StudentBasic])
def get_students():
    return [StudentBasic(**dict(r)) for r in student_service.list_students()]


@router.get("/templates", response_model=StudentTemplatesResponse)
def get_templates():
    items = []
    for fname, label in _TEMPLATE_FILES:
        available = (TEMPLATES_DIR / fname).exists()
        items.append(StudentTemplateItem(
            filename=fname, label=label, available=available,
            url=f"/static/student_templates/{fname}" if available else None,
        ))
    return StudentTemplatesResponse(items=items)


def _get_dashboard_or_404(sid: int) -> dict:
    dashboard = student_service.get_dashboard(sid)
    if dashboard is None:
        raise HTTPException(404, "학생을 찾을 수 없습니다.")
    return dashboard


@router.get("/{sid}/dashboard", response_model=StudentDashboard)
def get_dashboard(sid: int):
    return _get_dashboard_or_404(sid)


@router.put("/{sid}", response_model=StudentDashboard)
def update_student(sid: int, req: UpdateStudentBasicRequest):
    student_service.update_student_basic(sid, req.school, req.grade, req.class_name, req.note)
    return _get_dashboard_or_404(sid)


@router.post("/{sid}/prism", response_model=StudentDashboard)
def add_prism_eval(sid: int, req: PrismEvalRequest):
    student_service.insert_prism_eval(
        sid, req.eval_date, req.score_p, req.score_r, req.score_i,
        req.score_s, req.score_m, req.note,
    )
    return _get_dashboard_or_404(sid)


@router.post("/{sid}/self-predict", response_model=StudentDashboard)
def add_self_predict(sid: int, req: SelfPredictRequest):
    student_service.insert_self_predict(
        sid, req.log_date, req.title, req.predicted, req.actual, req.note,
    )
    return _get_dashboard_or_404(sid)


@router.post("/{sid}/progress", response_model=StudentDashboard)
def add_progress(sid: int, req: ProgressLogRequest):
    student_service.insert_progress(
        sid, req.log_date, req.category, req.chapter, req.title,
        req.planned, req.actual, req.score_raw, req.score_max, req.note,
    )
    return _get_dashboard_or_404(sid)


@router.post("/{sid}/assessment/quantity", response_model=StudentDashboard)
def add_quantity_assessment(sid: int, req: QuantityAssessmentRequest):
    student_service.insert_quantity_assessment(sid, req.eval_date, req.grade, req.note)
    return _get_dashboard_or_404(sid)


@router.post("/{sid}/assessment/qualitative", response_model=StudentDashboard)
def add_qualitative_assessment(sid: int, req: QualitativeAssessmentRequest):
    student_service.insert_qualitative_assessment(
        sid, req.eval_date, req.note_completion, req.written_completion,
        req.textbook_marking, req.second_solve_reason, req.note,
    )
    return _get_dashboard_or_404(sid)


@router.post("/{sid}/logs", response_model=StudentDashboard)
def add_log(sid: int, req: ManagementLogRequest):
    student_service.insert_log(sid, req.log_date, req.log_type, req.summary, req.detail)
    return _get_dashboard_or_404(sid)
