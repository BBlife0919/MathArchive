from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class StudentBasic(BaseModel):
    student_id: int
    name: str
    school: Optional[str] = None
    grade: Optional[int] = None
    class_name: Optional[str] = None
    note: Optional[str] = None


class CreateStudentRequest(BaseModel):
    name: str
    school: Optional[str] = None
    grade: int = Field(default=1, ge=1, le=6)
    class_name: Optional[str] = None


class PrismScore(BaseModel):
    eval_date: str
    score_p: int
    score_r: int
    score_i: int
    score_s: int
    score_m: int
    note: Optional[str] = None


class ClinicErrorCount(BaseModel):
    code: str
    label: str
    count: int
    category: Literal["이해", "수행"]


class SelfPredictEntry(BaseModel):
    log_date: str
    title: Optional[str] = None
    predicted: Optional[int] = None
    actual: Optional[int] = None
    gap: int
    note: Optional[str] = None


class ProgressEntry(BaseModel):
    log_date: str
    category: str
    chapter: Optional[str] = None
    title: Optional[str] = None
    planned: Optional[str] = None
    actual: Optional[str] = None
    score_display: str
    note: Optional[str] = None


class QuantityGradeCount(BaseModel):
    grade: str
    count: int
    pct: Optional[float] = None


class QualitativeEntry(BaseModel):
    eval_date: str
    note_completion: int
    written_completion: int
    textbook_marking: int
    second_solve_reason: int
    note: Optional[str] = None


class LogEntry(BaseModel):
    log_date: str
    log_type: str
    summary: Optional[str] = None
    detail: Optional[str] = None


class StudentDashboard(BaseModel):
    student: StudentBasic
    clinic_count: int
    latest_prism: Optional[PrismScore] = None
    avg_ris: Optional[float] = None
    avg_pm: Optional[float] = None
    prism_history: list[PrismScore] = []
    clinic_error_distribution: list[ClinicErrorCount] = []
    self_predict_entries: list[SelfPredictEntry] = []
    self_predict_chart: list[dict] = []  # [{date, predicted, actual}] 일자별 평균 집약
    self_predict_avg_gap: Optional[float] = None
    self_predict_over_count: int = 0
    self_predict_under_count: int = 0
    progress_entries: list[ProgressEntry] = []
    quantity_grade_counts: list[QuantityGradeCount] = []
    latest_qualitative: Optional[QualitativeEntry] = None
    logs: list[LogEntry] = []


class UpdateStudentBasicRequest(BaseModel):
    school: Optional[str] = None
    grade: int = Field(ge=1, le=6)
    class_name: Optional[str] = None
    note: Optional[str] = None


class PrismEvalRequest(BaseModel):
    eval_date: str
    score_p: int = Field(ge=1, le=5)
    score_r: int = Field(ge=1, le=5)
    score_i: int = Field(ge=1, le=5)
    score_s: int = Field(ge=1, le=5)
    score_m: int = Field(ge=1, le=5)
    note: Optional[str] = None


class SelfPredictRequest(BaseModel):
    log_date: str
    title: Optional[str] = None
    predicted: int = Field(ge=0, le=100)
    actual: int = Field(ge=0, le=100)
    note: Optional[str] = None


class ProgressLogRequest(BaseModel):
    log_date: str
    category: Literal["진도", "숙제", "시험"]
    chapter: Optional[str] = None
    title: Optional[str] = None
    planned: Optional[str] = None
    actual: Optional[str] = None
    score_raw: Optional[int] = None
    score_max: Optional[int] = None
    note: Optional[str] = None


class QuantityAssessmentRequest(BaseModel):
    eval_date: str
    grade: Literal["A", "B", "C", "D"]
    note: Optional[str] = None


class QualitativeAssessmentRequest(BaseModel):
    eval_date: str
    note_completion: int = Field(ge=1, le=5)
    written_completion: int = Field(ge=1, le=5)
    textbook_marking: int = Field(ge=1, le=5)
    second_solve_reason: int = Field(ge=1, le=5)
    note: Optional[str] = None


class ManagementLogRequest(BaseModel):
    log_date: str
    log_type: Literal["보호자", "출결", "메모"]
    summary: Optional[str] = None
    detail: Optional[str] = None


class StudentTemplateItem(BaseModel):
    filename: str
    label: str
    available: bool
    url: Optional[str] = None


class StudentTemplatesResponse(BaseModel):
    items: list[StudentTemplateItem]
