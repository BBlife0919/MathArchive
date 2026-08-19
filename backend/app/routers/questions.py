from __future__ import annotations

import random

from fastapi import APIRouter, Depends

from .. import legacy_bridge  # noqa: F401
from ..deps import require_approved
from ..schemas.questions import (
    ByIdsRequest, ByIdsResponse, MiniTestRequest, MiniTestResponse,
    SearchIdsResponse, SearchRequest, SearchResponse,
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


def _resolve_matching_meta(req: SearchRequest) -> list[dict]:
    """main.py:889-905 의 "quick search vs multiselect 병합" 로직 그대로 재현.
    question_id+difficulty 쌍 전체를 반환 — /search, /search-ids, /mini-test
    가 동일한 필터 해석을 공유하기 위한 헬퍼.
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
        if not eff_schools:
            # 원본 main.py:903 주석 의도("매칭 0 일 때 결과 0 안내")대로 처리.
            # eff_schools=[] 를 그대로 내려보내면 _build_search_where 가
            # "학교 필터 없음(전체 매칭)"으로 오인해 전체 DB가 나오는 원본의
            # 버그를 여기서 고친다 — 빠른검색 키워드에 매칭되는 학교가 하나도
            # 없으면 검색 자체를 0건으로 조기 반환.
            return []
    else:
        eff_schools = []

    sel_chapters = curr.expand_to_minors(req.subjects, req.majors, req.minors)
    is_subjective = _QUESTION_TYPE_TO_IS_SUBJECTIVE[req.question_type]

    return db_service.search_question_ids(
        tuple(eff_schools), tuple(sel_chapters),
        tuple(req.difficulties), tuple(req.regions),
        years=tuple(eff_years), grades=tuple(eff_grades),
        semesters=tuple(eff_semesters), exam_types=tuple(eff_exam_types),
        is_subjective=is_subjective, keyword=req.keyword,
    )


def _resolve_matching_ids(req: SearchRequest) -> list[int]:
    return [r["question_id"] for r in _resolve_matching_meta(req)]


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


@router.post("/mini-test", response_model=MiniTestResponse)
def mini_test(req: MiniTestRequest):
    """main.py:924-968 의 미니테스트 자동 생성 로직 그대로 포팅.

    '하' 난이도에서 mini_easy_pct 비중만큼, 나머지는 '중'/'상' 에서 채우고
    그래도 모자라면 전체 풀에서 보충. 매 호출마다 새로 랜덤 추출한다.
    """
    all_meta = _resolve_matching_meta(req)
    if not all_meta:
        return MiniTestResponse(question_ids=[], pool_size=0)

    easy_n = round(req.mini_count * req.mini_easy_pct / 100)
    easy_pool = [r["question_id"] for r in all_meta if r["difficulty"] == "하"]
    rest_pool = [r["question_id"] for r in all_meta if r["difficulty"] in ("중", "상")]

    picks: list[int] = []
    if easy_pool:
        picks.extend(random.sample(easy_pool, min(easy_n, len(easy_pool))))
    if rest_pool:
        need = req.mini_count - len(picks)
        picks.extend(random.sample(rest_pool, min(need, len(rest_pool))))
    if len(picks) < req.mini_count:
        all_pool = [r["question_id"] for r in all_meta if r["question_id"] not in picks]
        need = req.mini_count - len(picks)
        if all_pool:
            picks.extend(random.sample(all_pool, min(need, len(all_pool))))

    return MiniTestResponse(question_ids=picks, pool_size=len(all_meta))


@router.post("/by-ids", response_model=ByIdsResponse)
def questions_by_ids(req: ByIdsRequest):
    rows = db_service.fetch_questions_for_preview(req.question_ids, req.preserve_order)
    items = question_builder.build_question_cards(rows)
    return ByIdsResponse(items=items)
