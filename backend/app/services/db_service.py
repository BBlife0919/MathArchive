"""DB 조회 서비스 — app/main.py 의 검색/필터 SQL 을 그대로 재사용하되,
Streamlit `@st.cache_data`/`@st.cache_resource` 데코레이터 없이 재구현한다
(계획서 "C등급" 항목 — SQL 문자열 자체는 main.py 와 100% 동일하게 유지).
"""
from __future__ import annotations

import time

from .. import legacy_bridge  # noqa: F401  (app/ 를 sys.path 에 추가)
from ..config import CORS_ORIGINS  # noqa: F401  (.env 로드 트리거)

import db as legacy_db  # type: ignore
import curriculum as curr  # type: ignore
import main as legacy_main  # type: ignore  (순수 함수만 사용: format_choices 등)

_conn = None


def get_connection():
    global _conn
    if _conn is None:
        _conn = legacy_db.get_connection()
    return _conn


def query(sql: str, params=()):
    return get_connection().execute(sql, params).fetchall()


DIFF_VALID = ["하", "중", "상", "킬"]

# ── 필터 옵션 (main.py:161-204 SQL 그대로, TTL 캐시만 수동 구현) ──────
_filter_cache: tuple[float, dict] | None = None
_FILTER_TTL = 600


def load_filter_options() -> dict:
    global _filter_cache
    now = time.time()
    if _filter_cache and now - _filter_cache[0] < _FILTER_TTL:
        return _filter_cache[1]

    sql = """
        SELECT school, chapter, region, year, grade, semester, exam_type
        FROM questions
        GROUP BY school, chapter, region, year, grade, semester, exam_type
    """
    rows = query(sql)
    school_set, region_set = set(), set()
    year_set, grade_set, semester_set, exam_set = set(), set(), set(), set()
    for r in rows:
        if r["school"]:
            school_set.add(r["school"])
        if r["region"]:
            region_set.add(r["region"])
        if r["year"]:
            year_set.add(int(r["year"]))
        if r["grade"]:
            grade_set.add(int(r["grade"]))
        if r["semester"]:
            semester_set.add(int(r["semester"]))
        if r["exam_type"]:
            exam_set.add(r["exam_type"])

    result = {
        "schools": sorted(school_set),
        "regions": sorted(region_set),
        "years": sorted(year_set, reverse=True),
        "grades": sorted(grade_set),
        "semesters": sorted(semester_set),
        "exam_types": sorted(exam_set, key=lambda v: {"a": 0, "b": 1}.get(v, 9)),
        "difficulties": DIFF_VALID,
        "curriculum": curr.CURRICULUM,
    }
    _filter_cache = (now, result)
    return result


# ── 검색 (main.py:252-350 SQL 그대로) ────────────────────────────
def build_search_where(**kwargs):
    return legacy_main._build_search_where(**kwargs)


def parse_quick_search(text: str) -> dict:
    return legacy_main.parse_quick_search(text)


# main.py 원본은 @st.cache_data(ttl=300) 으로 이 조회를 캐싱했다 (원격
# Postgres 왕복 + 15만 행 전체 스캔이라 무캐시 시 요청마다 수 초~수십 초).
# 여기서도 동일 TTL 로 (파라미터 → 결과) 캐시한다.
_SEARCH_IDS_CACHE: dict[tuple, tuple[float, list]] = {}
_SEARCH_IDS_TTL = 300
_SEARCH_IDS_CACHE_MAX = 500  # 필터 조합이 무한히 쌓이는 걸 방지하는 대략적 상한


def search_question_ids(schools, chapters, difficulties, regions,
                        years=(), grades=(), semesters=(), exam_types=(),
                        is_subjective=None, keyword=""):
    cache_key = (
        tuple(schools), tuple(chapters), tuple(difficulties), tuple(regions),
        tuple(years), tuple(grades), tuple(semesters), tuple(exam_types),
        is_subjective, keyword,
    )
    now = time.time()
    cached = _SEARCH_IDS_CACHE.get(cache_key)
    if cached and now - cached[0] < _SEARCH_IDS_TTL:
        return cached[1]

    where, params = legacy_main._build_search_where(
        list(schools), list(chapters), list(difficulties), list(regions),
        years=list(years), grades=list(grades),
        semesters=list(semesters), exam_types=list(exam_types),
        is_subjective=is_subjective, keyword=keyword,
    )
    sql = f"""
        SELECT q.question_id, q.difficulty
        FROM questions q
        WHERE {where}
        ORDER BY q.school, q.year DESC, q.semester, q.exam_type,
                 q.question_number
    """
    result = [dict(r) for r in query(sql, params)]
    if len(_SEARCH_IDS_CACHE) >= _SEARCH_IDS_CACHE_MAX:
        _SEARCH_IDS_CACHE.clear()
    _SEARCH_IDS_CACHE[cache_key] = (now, result)
    return result


def fetch_questions_page(question_ids: list[int]) -> list:
    if not question_ids:
        return []
    placeholders = ",".join("?" * len(question_ids))
    sql = f"""
        SELECT q.question_id, q.file_source, q.school, q.region,
               q.grade, q.year, q.semester, q.exam_type, q.subject,
               q.question_number, q.question_text, q.choices,
               q.answer, q.answer_type, q.points, q.chapter,
               q.difficulty, q.has_image, q.is_subjective, q.error_note,
               s.solution_text
        FROM questions q
        LEFT JOIN solutions s ON q.question_id = s.question_id
        WHERE q.question_id IN ({placeholders})
    """
    rows = query(sql, list(question_ids))
    by_id = {r["question_id"]: r for r in rows}
    return [by_id[qid] for qid in question_ids if qid in by_id]


def fetch_questions_for_preview(question_ids: list[int]) -> list:
    """시험지 미리보기용 — main.py:1244-1269 SQL + 정렬 로직 그대로."""
    if not question_ids:
        return []
    placeholders = ",".join("?" * len(question_ids))
    rows = query(f"""
        SELECT q.question_id, q.file_source, q.school, q.question_number,
               q.year, q.semester, q.exam_type,
               q.question_text, q.choices, q.answer, q.answer_type,
               q.points, q.chapter, q.difficulty, q.is_subjective,
               s.solution_text
        FROM questions q
        LEFT JOIN solutions s ON q.question_id = s.question_id
        WHERE q.question_id IN ({placeholders})
    """, list(question_ids))

    all_minors = curr.all_minor_chapters_in_subjects(curr.subjects())
    chap_idx = {c: i for i, c in enumerate(all_minors)}
    diff_order = {"하": 0, "중": 1, "상": 2, "킬": 3}
    return sorted(
        rows,
        key=lambda r: (
            chap_idx.get(r["chapter"], 9999),
            diff_order.get(r["difficulty"], 99),
            r["question_id"],
        ),
    )


# ── 이미지 맵 (main.py:373-394 SQL 그대로) ───────────────────────
def image_maps_for(question_ids: list[int]) -> dict[int, dict]:
    if not question_ids:
        return {}
    placeholders = ",".join("?" * len(question_ids))
    rows = query(
        f"SELECT question_id, image_ref, image_path FROM images "
        f"WHERE question_id IN ({placeholders})",
        list(question_ids),
    )
    grouped: dict[int, dict] = {qid: {} for qid in question_ids}
    for r in rows:
        if r["image_ref"]:
            grouped[r["question_id"]][r["image_ref"]] = r["image_path"]
    return grouped
