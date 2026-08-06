"""클리닉 서비스 — app/pages/1_클리닉.py 의 SQL·워크플로우를 그대로 재현.

`app/clinic_logic.py`(find_similar_questions/compute_retry_schedule/
insert_clinic_entry/list_pending_retries)는 Streamlit 비의존 순수 함수라
그대로 import 해서 재사용한다.
"""
from __future__ import annotations

from datetime import date

from . import db_service, student_service

import clinic_logic  # type: ignore

ERROR_CODES = clinic_logic.ERROR_CODES
ERROR_CODE_DISPLAY = clinic_logic.ERROR_CODE_DISPLAY


def search_questions(keyword: str) -> list[dict]:
    """app/pages/1_클리닉.py:146-156 그대로 — school/chapter/question_text LIKE 검색."""
    like = f"%{keyword}%"
    rows = db_service.query(
        "SELECT question_id, school, year, semester, exam_type, question_number, "
        "chapter, difficulty, question_text "
        "FROM questions "
        "WHERE school LIKE ? OR chapter LIKE ? OR question_text LIKE ? "
        "ORDER BY question_id DESC LIMIT 20",
        (like, like, like),
    )
    out = []
    for r in rows:
        text = r["question_text"] or ""
        preview = text[:600] + ("…" if len(text) > 600 else "")
        out.append({
            "question_id": r["question_id"], "school": r["school"],
            "year": r["year"], "semester": r["semester"], "exam_type": r["exam_type"],
            "question_number": r["question_number"], "chapter": r["chapter"],
            "difficulty": r["difficulty"], "text_preview": preview,
        })
    return out


class InsufficientSimilarQuestions(Exception):
    def __init__(self, count: int, chapter: str | None):
        self.count = count
        self.chapter = chapter
        super().__init__(
            f"인출 문항이 {count}개만 추출됨 — 같은 단원의 풀이 가능 문제가 "
            f"부족합니다. (chapter: {chapter})"
        )


def create_entry(student_id: int, source_mode: str, wrong_question_id: int | None,
                 external_label: str | None, error_code: str, keyword: str,
                 wrong_date_iso: str) -> dict:
    """app/pages/1_클리닉.py:212-251 의 처방전 생성 흐름 그대로."""
    conn = db_service.get_connection()
    wrong_dt = date.fromisoformat(wrong_date_iso)
    schedule = clinic_logic.compute_retry_schedule(wrong_dt)

    similar_qids: list[int] = []
    if source_mode == "db":
        similar_qids = clinic_logic.find_similar_questions(conn, wrong_question_id)
        if len(similar_qids) < 3:
            chapter_row = db_service.query(
                "SELECT chapter FROM questions WHERE question_id = ?",
                (wrong_question_id,),
            )
            chapter = chapter_row[0]["chapter"] if chapter_row else None
            raise InsufficientSimilarQuestions(len(similar_qids), chapter)

    entry_id = clinic_logic.insert_clinic_entry(
        conn, student_id=student_id,
        wrong_question_id=wrong_question_id if source_mode == "db" else None,
        wrong_date_iso=wrong_date_iso, error_code=error_code, keyword=keyword,
        prescribed_qids=similar_qids,
        external_label=external_label if source_mode == "external" else None,
    )

    student = student_service.get_student(student_id)
    student_name = student["name"] if student else "?"

    prescription_ids = ([wrong_question_id] + similar_qids) if source_mode == "db" else []

    return {
        "entry_id": entry_id,
        "mode": source_mode,
        "prescribed_qids": similar_qids,
        "prescription_question_ids": prescription_ids,
        "schedule": {
            "d3": schedule["d3"].isoformat(), "d7": schedule["d7"].isoformat(),
            "d14": schedule["d14"].isoformat(), "d30": schedule["d30"].isoformat(),
        },
        "student_name": student_name,
        "error_code": error_code,
        "external_label": external_label if source_mode == "external" else None,
    }


def build_prescription_pdf(question_ids: list[int], title: str, subtitle: str) -> bytes:
    """app/pages/1_클리닉.py:254-289 — 오답+인출 문항을 [오답, 인출1, 인출2, 인출3]
    순서 그대로 유지해서 PDF 생성 (일반 시험지와 달리 단원/난이도 재정렬 안 함)."""
    import pdf_engine  # type: ignore

    rows = db_service.fetch_questions_page(question_ids)
    questions = [dict(r) for r in rows]
    return pdf_engine.generate_exam_pdf(
        questions, title=title, include_source=True, overrides={}, subtitle=subtitle,
    )


def _list_pending_retries_raw() -> list[dict]:
    """clinic_logic.list_pending_retries() 와 동일한 SQL·due 판정 로직이지만
    prescribed_qids 컬럼은 조회하지 않는다.

    원본 함수는 Postgres 에서 재현되는 버그가 있다: clinic_entries.prescribed_qids
    가 jsonb 컬럼이라 psycopg2 가 이미 Python list 로 자동 디코딩해서 돌려주는데,
    원본 코드가 그걸 다시 json.loads() 에 넣어 TypeError 로 500 이 난다(SQLite 는
    TEXT 컬럼이라 안 걸림 — 로컬 테스트로는 못 잡고 운영 Postgres 실사용 데이터로만
    재현됨). 이 API 응답에는 애초에 prescribed_qids 가 필요 없어 아예 조회하지 않는
    방식으로 우회 — app/clinic_logic.py 는 손대지 않는다.
    """
    conn = db_service.get_connection()
    rows = conn.execute(
        """
        SELECT e.entry_id, e.student_id, e.wrong_question_id, e.wrong_date,
               e.error_code, e.retry_d3_status, e.retry_d7_status,
               e.retry_d14_status, e.retry_d30_status, e.external_label,
               s.name as student_name
        FROM clinic_entries e
        JOIN students s ON e.student_id = s.student_id
        ORDER BY e.wrong_date DESC
        """
    ).fetchall()

    today = date.today()
    out = []
    for r in rows:
        try:
            wd = date.fromisoformat(str(r["wrong_date"])[:10])
        except (TypeError, ValueError):
            continue
        sched = clinic_logic.compute_retry_schedule(wd)
        due = (
            (r["retry_d3_status"] == "pending" and sched["d3"] <= today)
            or (r["retry_d7_status"] == "pending" and sched["d7"] <= today)
            or (r["retry_d14_status"] == "pending" and sched["d14"] <= today)
            or (r["retry_d30_status"] == "pending" and sched["d30"] <= today)
        )
        if not due:
            continue
        out.append(dict(r))
    return out


def pending_retries() -> list[dict]:
    rows = _list_pending_retries_raw()
    out = []
    for p in rows:
        flags = []
        if p["retry_d3_status"] == "pending":
            flags.append("D+3")
        if p["retry_d7_status"] == "pending":
            flags.append("D+7")
        if p["retry_d14_status"] == "pending":
            flags.append("D+14")
        if p["retry_d30_status"] == "pending":
            flags.append("D+30")
        out.append({
            "entry_id": p["entry_id"], "student_id": p["student_id"],
            "student_name": p["student_name"],
            "wrong_question_id": p["wrong_question_id"],
            "external_label": p["external_label"],
            "wrong_date": str(p["wrong_date"]), "error_code": p["error_code"],
            "due_flags": flags,
        })
    return out
