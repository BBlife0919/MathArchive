from __future__ import annotations

import random

from fastapi import APIRouter, Depends

from .. import legacy_bridge  # noqa: F401
from ..deps import require_approved
from ..schemas.questions import (
    ByIdsRequest, ByIdsResponse, EvenDistributeRequest, EvenDistributeResponse,
    MiniTestRequest, MiniTestResponse, SearchIdsResponse, SearchRequest,
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
    if not sel_chapters and (req.subjects or req.majors or req.minors):
        # 위 학교 케이스와 동일한 함정: expand_to_minors()는 "선택 안 함(전체)"과
        # "선택했는데 커리큘럼에 없는 값이라 매칭 0건"을 똑같이 빈 리스트로
        # 반환한다. 후자를 그대로 두면 _build_search_where가 "단원 필터 없음"
        # 으로 오인해 전체 DB가 나온다 — 실제로 선택을 했는데 하나도 안
        # 걸리면 검색 자체를 0건으로 조기 반환.
        return []
    is_subjective = _QUESTION_TYPE_TO_IS_SUBJECTIVE[req.question_type]

    return db_service.search_question_ids(
        tuple(eff_schools), tuple(sel_chapters),
        tuple(req.difficulties), tuple(req.regions),
        years=tuple(eff_years), grades=tuple(eff_grades),
        semesters=tuple(eff_semesters), exam_types=tuple(eff_exam_types),
        is_subjective=is_subjective, keyword=req.keyword,
        exclude_recent_days=req.exclude_recent_days,
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


def _chapter_to_major_map() -> dict[str, str]:
    """중단원명 → 대단원명 역매핑 (curr.CURRICULUM 정본 기준).

    DB questions.chapter 원본에는 오탈자·구교육과정명 등 커리큘럼과 안 맞는
    값이 약 30% 섞여있음(실측 확인됨) — 이 매핑에 없는 chapter 값은 "어느
    대단원인지 판단 불가"로 취급해 균등배분 그룹핑에서 제외한다(원본 chapter
    distinct 값을 그대로 그룹 키로 쓰면 노이즈가 그룹을 오염시키기 때문).
    """
    mapping: dict[str, str] = {}
    for majors in curr.CURRICULUM.values():
        for major, minors in majors.items():
            for minor in minors:
                mapping[minor] = major
    return mapping


@router.post("/even-distribute", response_model=EvenDistributeResponse)
def even_distribute(req: EvenDistributeRequest):
    """선택 범위 안에서 대단원(또는 중단원) 별로 문항 수를 고르게 나눠 뽑는다.

    mini_test() 와 동일하게 매 호출마다 새로 랜덤 추출한다. 그룹은 항상
    curr.CURRICULUM 정본 기준으로만 정의한다(원본 chapter 값을 그대로 쓰지
    않음 — _chapter_to_major_map() 참고).
    """
    all_meta = _resolve_matching_meta(req)
    if not all_meta:
        return EvenDistributeResponse(question_ids=[], results=[])

    if req.granularity == "major":
        chapter_to_group = _chapter_to_major_map()
    else:
        known_minors = {m for majors in curr.CURRICULUM.values()
                        for minors in majors.values() for m in minors}
        chapter_to_group = {m: m for m in known_minors}

    groups: dict[str, list[int]] = {}
    for r in all_meta:
        group = chapter_to_group.get(r["chapter"])
        if group is None:
            continue
        groups.setdefault(group, []).append(r["question_id"])

    if not groups:
        return EvenDistributeResponse(question_ids=[], results=[])

    ordered_names = sorted(groups.keys())
    n = len(ordered_names)
    base, remainder = divmod(req.count, n)
    # 나머지 몫(+1)을 매번 가나다순 앞쪽 그룹이 고정으로 가져가면 같은 조건으로
    # 반복 생성할 때마다 항상 같은 단원만 1문항씩 더 나오는 편향이 생긴다.
    # 표시 순서(ordered_names)는 그대로 유지하되 보너스 수령 그룹만 매 호출
    # 랜덤으로 뽑는다.
    bonus_names = set(random.sample(ordered_names, remainder)) if remainder else set()

    picks: list[int] = []
    results: list[dict] = []
    for name in ordered_names:
        pool = groups[name]
        target = base + (1 if name in bonus_names else 0)
        take = min(target, len(pool))
        picks.extend(random.sample(pool, take))
        results.append({"group": name, "target": target, "picked": take, "pool": len(pool)})

    return EvenDistributeResponse(question_ids=picks, results=results)


@router.post("/by-ids", response_model=ByIdsResponse)
def questions_by_ids(req: ByIdsRequest):
    rows = db_service.fetch_questions_for_preview(req.question_ids, req.preserve_order)
    items = question_builder.build_question_cards(rows)
    return ByIdsResponse(items=items)
