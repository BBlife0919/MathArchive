from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response

from ..deps import require_approved
from ..schemas.clinic import (
    ClinicEntryRequest, ClinicEntryResponse, ClinicMetaResponse, ErrorCodeItem,
    PendingRetry, PrescriptionPdfRequest, QuestionSearchResult,
)
from ..services import clinic_service

router = APIRouter(
    prefix="/api/clinic", tags=["clinic"],
    dependencies=[Depends(require_approved)],
)


@router.get("/meta", response_model=ClinicMetaResponse)
def get_meta():
    return ClinicMetaResponse(
        error_codes=[
            ErrorCodeItem(code=c, display=clinic_service.ERROR_CODE_DISPLAY.get(c, c))
            for c in clinic_service.ERROR_CODES
        ],
    )


@router.get("/search-questions", response_model=list[QuestionSearchResult])
def search_questions(keyword: str = ""):
    if not keyword.strip():
        return []
    return clinic_service.search_questions(keyword.strip())


@router.post("/entries", response_model=ClinicEntryResponse)
def create_entry(req: ClinicEntryRequest):
    if req.source_mode == "db" and req.wrong_question_id is None:
        raise HTTPException(422, "DB 모드에서는 wrong_question_id 가 필요합니다.")
    if req.source_mode == "external" and not (req.external_label or "").strip():
        raise HTTPException(422, "외부 문제 모드에서는 external_label 이 필요합니다.")
    try:
        result = clinic_service.create_entry(
            student_id=req.student_id, source_mode=req.source_mode,
            wrong_question_id=req.wrong_question_id,
            external_label=(req.external_label or "").strip() or None,
            error_code=req.error_code, keyword=req.keyword,
            wrong_date_iso=req.wrong_date,
        )
    except clinic_service.InsufficientSimilarQuestions as e:
        raise HTTPException(422, str(e))
    return ClinicEntryResponse(**result)


@router.post("/prescription-pdf")
def prescription_pdf(req: PrescriptionPdfRequest):
    pdf_bytes = clinic_service.build_prescription_pdf(req.question_ids, req.title, req.subtitle)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="prescription.pdf"'},
    )


@router.get("/pending-retries", response_model=list[PendingRetry])
def get_pending_retries():
    return clinic_service.pending_retries()[:20]
