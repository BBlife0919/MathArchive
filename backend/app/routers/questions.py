from __future__ import annotations

from fastapi import APIRouter, Depends

from .. import legacy_bridge  # noqa: F401
from ..deps import require_approved
from ..schemas.questions import (
    ByIdsRequest, ByIdsResponse, SearchIdsResponse, SearchRequest,
    SearchResponse,
)
from ..services import db_service, question_builder

import curriculum as curr  # type: ignore

router = APIRouter(
    prefix="/api/questions", tags=["questions"],
    dependencies=[Depends(require_approved)],
)

_QUESTION_TYPE_TO_IS_SUBJECTIVE = {
    "all": None, "choice": False, "subjective": True,
}


def _resolve_matching_ids(req: SearchRequest) -> list[int]:
    """main.py:889-905 의 "quick search vs multiselect 병합" 로직 그대로 재현.
    /search 와 /search-ids 가 동일한 필터 해석을 공유하기 위한 헬퍼.
    """
    quick = db_service.parse_quick_search(req.quick_search)
    eff_years = req.years or quick["years"]
    eff_grades = req.grades or quick["grades"]
    eff_semesters = req.semesters or quick["semesters"]
    eff_exam_types = req.exam_types or quick["exam_types"]

    if req.schools:
        eff_schools = req.schools
    elif quick["school_kw"]:
        all_schools = db_service.load_filter_options()["schools"]
        eff_schools = [s for s in all_schools if quick["school_kw"] in s]
    else:
        eff_schools = []

    sel_chapters = curr.expand_to_minors(req.subjects, req.majors, req.minors)
    is_subjective = _QUESTION_TYPE_TO_IS_SUBJECTIVE[req.question_type]

    all_meta = db_service.search_question_ids(
        tuple(eff_schools), tuple(sel_chapters),
        tuple(req.difficulties), tuple(req.regions),
        years=tuple(eff_years), grades=tuple(eff_grades),
        semesters=tuple(eff_semesters), exam_types=tuple(eff_exam_types),
        is_subjective=is_subjective, keyword=req.keyword,
    )
    return [r["question_id"] for r in all_meta]


@router.post("/search", response_model=SearchResponse)
def search_questions(req: SearchRequest):
    all_ids = _resolve_matching_ids(req)
    total = len(all_ids)
    start = req.page * req.page_size
    end = start + req.page_size
    page_ids = all_ids[start:end]

    page_rows = db_service.fetch_questions_page(page_ids)
    items = question_builder.build_question_cards(page_rows)

    return SearchResponse(
        total=total, page=req.page, page_size=req.page_size, items=items,
    )


@router.post("/search-ids", response_model=SearchIdsResponse)
def search_question_ids(req: SearchRequest):
    """검색 조건에 맞는 전체 문항 ID (본문 없이 가볍게) — "전체 → 시험지"
    일괄 담기용. main.py:1000-1027 의 all_meta 재사용과 동일한 목적."""
    return SearchIdsResponse(question_ids=_resolve_matching_ids(req))


@router.post("/by-ids", response_model=ByIdsResponse)
def questions_by_ids(req: ByIdsRequest):
    rows = db_service.fetch_questions_for_preview(req.question_ids)
    items = question_builder.build_question_cards(rows)
    return ByIdsResponse(items=items)
