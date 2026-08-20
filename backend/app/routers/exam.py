from __future__ import annotations

from fastapi import APIRouter, Depends, Response

from ..deps import require_approved
from ..schemas.exam import BookPdfRequest, ExamPdfRequest, LayoutPreviewRequest, LayoutPreviewResponse
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
        preserve_order=req.preserve_order,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="exam.pdf"'},
    )


@router.post("/layout-preview", response_model=LayoutPreviewResponse)
def layout_preview(req: LayoutPreviewRequest):
    # Playwright 없이 순수 파이썬 배치 계산만 하므로 가볍다 — 실시간 미리보기용.
    pages = pdf_service.build_layout_preview(
        req.question_ids,
        overrides=req.overrides,
        preserve_order=req.preserve_order,
    )
    return {"pages": pages}


@router.post("/book-pdf")
def book_pdf(req: BookPdfRequest):
    # 동기 def — 위 exam_pdf 와 동일한 이유(Playwright 블로킹 호출).
    pdf_bytes = pdf_service.build_book_pdf(
        req.question_ids,
        title=req.title,
        include_source=req.include_source,
        subtitle=req.subtitle,
        include_logo=req.include_logo,
        cover_style=req.cover_style,
        cover_kicker=req.cover_kicker,
        cover_big_word=req.cover_big_word,
        cover_footer_main=req.cover_footer_main,
        cover_footer_sub=req.cover_footer_sub,
        dcov_subject=req.dcov_subject,
        dcov_level=req.dcov_level,
        kicker_mark=req.kicker_mark,
        kicker_text=req.kicker_text,
        divider_meta_top=req.divider_meta_top,
        divider_footer_title=req.divider_footer_title,
        divider_footer_sub=req.divider_footer_sub,
        overrides=req.overrides,
        book_mode=req.book_mode,
        flat_layout=req.flat_layout,
        preserve_order=req.preserve_order,
    )
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="book.pdf"'},
    )
