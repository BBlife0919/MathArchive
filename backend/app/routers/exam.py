from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from ..deps import require_approved
from ..schemas.exam import ExamPdfRequest
from ..services import pdf_service

router = APIRouter(
    prefix="/api/exam", tags=["exam"],
    dependencies=[Depends(require_approved)],
)


@router.post("/pdf")
def exam_pdf(req: ExamPdfRequest):
    # 동기 def — Playwright(sync_playwright)가 블로킹 호출이라 FastAPI 의
    # threadpool 로 오프로드되어야 다른 요청(로그인 등)을 막지 않는다.
    pdf_bytes = pdf_service.build_exam_pdf(
        req.question_ids,
        title=req.title,
        include_source=req.include_source,
        subtitle=req.subtitle,
        include_logo=req.include_logo,
        overrides=req.overrides,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="exam.pdf"'},
    )
